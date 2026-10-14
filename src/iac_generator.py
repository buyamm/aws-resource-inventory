"""
IaC Generator Module

Generates Terraform (AWS provider ~> 5.0) from collected specs: one module per
region directory, resource arguments mapped from AWS field names, companion
resources for S3 and IAM, import and verification scripts.

Requirements Coverage:
- Requirement 7.1: Generated from cached spec files only
- Requirement 7.2: <terraform-dir>/<region>/<canonical_type>.tf, one module per region
- Requirement 7.3: Per-type argument mapping; every top-level key listed as mapped/unmapped
- Requirement 7.4: import.sh with provider-documented import ids (incl. companions)
- Requirement 7.5: lifecycle.ignore_changes for redacted / unknowable values;
  plan verification decided by `terraform plan -detailed-exitcode` exit code only
- Requirement 7.6: verify_state.sh
- Requirement 7.7: Traceability comments (spec file, ARN, region)
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.parser import ResourceSpec
from src.resource_types import (
    GLOBAL_REGION,
    canonical_type,
    file_id,
    resource_id,
    spec_relpath,
    type_dir,
)

DEFAULT_REGION = "us-east-1"
AWS_PROVIDER_VERSION = "~> 5.0"


# ============================================================================
# Minimal HCL model and renderer
# ============================================================================


class Raw(str):
    """An HCL expression emitted verbatim (references, provider addresses)."""


class Heredoc(str):
    """A multi-line string emitted as an indented heredoc (<<-EOT)."""


@dataclass
class Block:
    name: str
    items: list[Item] = field(default_factory=list)


Item = tuple[str, Any] | Block


def _escape_template(text: str) -> str:
    return text.replace("${", "$${").replace("%{", "%%{")


def hcl_string(value: str) -> str:
    """Quoted HCL string literal (JSON escapes are valid HCL escapes)."""
    return _escape_template(json.dumps(value))


def render_value(value: Any, indent: int) -> str:
    pad = "  " * indent
    if isinstance(value, Raw):
        return str(value)
    if isinstance(value, Heredoc):
        lines = _escape_template(str(value)).splitlines() or [""]
        body = "\n".join(f"{pad}  {line}" if line else "" for line in lines)
        return f"<<-EOT\n{body}\n{pad}EOT"
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return json.dumps(value)
    if isinstance(value, str):
        return hcl_string(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(render_value(v, indent) for v in value) + "]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = [
            f"{pad}  {hcl_string(str(k))} = {render_value(v, indent + 1)}"
            for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))
        ]
        return "{\n" + "\n".join(lines) + f"\n{pad}}}"
    return hcl_string(str(value))


def render_items(items: list[Item], indent: int) -> list[str]:
    pad = "  " * indent
    lines: list[str] = []
    for item in items:
        if isinstance(item, Block):
            lines.append(f"{pad}{item.name} {{")
            lines.extend(render_items(item.items, indent + 1))
            lines.append(f"{pad}}}")
        else:
            name, value = item
            if name.startswith("#"):
                lines.append(f"{pad}{name}")
            else:
                lines.append(f"{pad}{name} = {render_value(value, indent)}")
    return lines


# ============================================================================
# Mapping helpers
# ============================================================================

_PLACEHOLDER = re.compile(r"^\[REDACTED(_[A-Z_]+)?\]$")


def _contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return bool(_PLACEHOLDER.match(value))
    if isinstance(value, dict):
        return any(_contains_placeholder(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_placeholder(v) for v in value)
    if isinstance(value, Block):
        return any(_contains_placeholder(i if isinstance(i, Block) else i[1]) for i in value.items)
    return False


def _tags(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    result: dict[str, str] = {}
    for item in value if isinstance(value, list) else []:
        if isinstance(item, dict):
            key = item.get("Key", item.get("key"))
            if key is not None:
                result[str(key)] = str(item.get("Value", item.get("value", "")))
    return result


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _json_doc(value: Any) -> Heredoc | None:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return Heredoc(value)
    if isinstance(value, (dict, list)):
        return Heredoc(json.dumps(value, indent=2, sort_keys=True))
    return None


@dataclass
class TfResource:
    tf_type: str
    name: str
    items: list[Item]
    import_id: str


@dataclass
class Mapping:
    """Result of mapping one spec: arguments, keys consumed, lifecycle and companions."""

    items: list[Item] = field(default_factory=list)
    mapped: set[str] = field(default_factory=set)
    ignore_changes: list[str] = field(default_factory=list)
    companions: list[TfResource] = field(default_factory=list)
    import_id: str = ""

    def arg(self, name: str, value: Any, *source_keys: str) -> None:
        # Source keys count as mapped even when empty (nothing to emit for them).
        self.mapped.update(source_keys)
        if value is None or value == [] or value == {}:
            return
        self.items.append((name, value))

    def block(self, block: Block, *source_keys: str) -> None:
        self.items.append(block)
        self.mapped.update(source_keys)


def _map_instance(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("ami", s.get("ImageId"), "ImageId")
    m.arg("instance_type", s.get("InstanceType"), "InstanceType")
    m.arg("subnet_id", s.get("SubnetId"), "SubnetId")
    groups = [g.get("GroupId") for g in _list(s.get("SecurityGroups")) if isinstance(g, dict)]
    m.arg("vpc_security_group_ids", [g for g in groups if g], "SecurityGroups")
    m.arg("key_name", s.get("KeyName"), "KeyName")
    profile_arn = _dict(s.get("IamInstanceProfile")).get("Arn")
    if isinstance(profile_arn, str):
        m.arg("iam_instance_profile", profile_arn.split("/")[-1], "IamInstanceProfile")
    m.arg("ebs_optimized", s.get("EbsOptimized"), "EbsOptimized")
    state = _dict(s.get("Monitoring")).get("State")
    if isinstance(state, str):
        m.arg("monitoring", state == "enabled", "Monitoring")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.update({"InstanceId", "VpcId"})
    m.ignore_changes += ["user_data", "user_data_base64"]
    return m


def _map_vpc(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("cidr_block", s.get("CidrBlock"), "CidrBlock")
    m.arg("instance_tenancy", s.get("InstanceTenancy"), "InstanceTenancy")
    m.arg("enable_dns_support", s.get("EnableDnsSupport"), "EnableDnsSupport")
    m.arg("enable_dns_hostnames", s.get("EnableDnsHostnames"), "EnableDnsHostnames")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.add("VpcId")
    return m


def _sg_rule(permission: dict[str, Any], own_group_id: str, kind: str) -> Block:
    rule: list[Item] = []
    protocol = str(permission.get("IpProtocol", "-1"))
    rule.append(("from_port", int(permission.get("FromPort", 0) or 0)))
    rule.append(("to_port", int(permission.get("ToPort", 0) or 0)))
    rule.append(("protocol", protocol))
    ranges = _list(permission.get("IpRanges"))
    v6_ranges = _list(permission.get("Ipv6Ranges"))
    prefixes = _list(permission.get("PrefixListIds"))
    pairs = _list(permission.get("UserIdGroupPairs"))
    cidrs = [r.get("CidrIp") for r in ranges if isinstance(r, dict) and r.get("CidrIp")]
    cidrs6 = [r.get("CidrIpv6") for r in v6_ranges if isinstance(r, dict) and r.get("CidrIpv6")]
    prefix_ids = [p.get("PrefixListId") for p in prefixes if isinstance(p, dict)]
    group_ids = [p.get("GroupId") for p in pairs if isinstance(p, dict) and p.get("GroupId")]
    if cidrs:
        rule.append(("cidr_blocks", cidrs))
    if cidrs6:
        rule.append(("ipv6_cidr_blocks", cidrs6))
    if prefix_ids:
        rule.append(("prefix_list_ids", [p for p in prefix_ids if p]))
    others = [g for g in group_ids if g != own_group_id]
    if others:
        rule.append(("security_groups", others))
    if own_group_id in group_ids:
        rule.append(("self", True))
    descriptions = {
        d.get("Description")
        for d in ranges + v6_ranges + prefixes + pairs
        if isinstance(d, dict) and d.get("Description")
    }
    if len(descriptions) == 1:
        rule.append(("description", descriptions.pop()))
    return Block(kind, rule)


def _map_security_group(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("name", s.get("GroupName"), "GroupName")
    m.arg("description", s.get("Description"), "Description")
    m.arg("vpc_id", s.get("VpcId"), "VpcId")
    own = str(s.get("GroupId", ""))
    for permission in _list(s.get("IpPermissions")):
        if isinstance(permission, dict):
            m.block(_sg_rule(permission, own, "ingress"), "IpPermissions")
    for permission in _list(s.get("IpPermissionsEgress")):
        if isinstance(permission, dict):
            m.block(_sg_rule(permission, own, "egress"), "IpPermissionsEgress")
    m.mapped.update({"IpPermissions", "IpPermissionsEgress", "GroupId"})
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    return m


def _map_lambda(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    function_name = s.get("FunctionName") or resource_id(spec)
    m = Mapping(import_id=str(function_name))
    m.arg("function_name", function_name, "FunctionName")
    m.arg("role", s.get("Role"), "Role")
    if s.get("PackageType") == "Image":
        m.arg("package_type", "Image", "PackageType")
        m.arg("image_uri", "SET_IMAGE_URI_MANUALLY")
        m.ignore_changes.append("image_uri")
    else:
        m.arg("handler", s.get("Handler"), "Handler")
        m.arg("runtime", s.get("Runtime"), "Runtime")
        m.arg("filename", f"lambda_{function_name}.zip")
        m.mapped.add("PackageType")
        m.ignore_changes += ["filename", "source_code_hash"]
    m.arg("memory_size", s.get("MemorySize"), "MemorySize")
    m.arg("timeout", s.get("Timeout"), "Timeout")
    m.arg("description", s.get("Description") or None, "Description")
    m.arg("architectures", s.get("Architectures"), "Architectures")
    layers = [layer.get("Arn") for layer in _list(s.get("Layers")) if isinstance(layer, dict)]
    m.arg("layers", [arn for arn in layers if arn], "Layers")
    variables = _dict(_dict(s.get("Environment")).get("Variables"))
    if variables:
        m.block(Block("environment", [("variables", variables)]), "Environment")
    vpc = _dict(s.get("VpcConfig"))
    if _list(vpc.get("SubnetIds")):
        m.block(
            Block(
                "vpc_config",
                [
                    ("subnet_ids", _list(vpc.get("SubnetIds"))),
                    ("security_group_ids", _list(vpc.get("SecurityGroupIds"))),
                ],
            ),
            "VpcConfig",
        )
    m.mapped.update({"VpcConfig", "FunctionArn"})
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    return m


def _map_db_instance(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("identifier", s.get("DBInstanceIdentifier"), "DBInstanceIdentifier")
    m.arg("engine", s.get("Engine"), "Engine")
    m.arg("engine_version", s.get("EngineVersion"), "EngineVersion")
    m.arg("instance_class", s.get("DBInstanceClass"), "DBInstanceClass")
    m.arg("allocated_storage", s.get("AllocatedStorage"), "AllocatedStorage")
    m.arg("storage_type", s.get("StorageType"), "StorageType")
    m.arg("multi_az", s.get("MultiAZ"), "MultiAZ")
    m.arg("publicly_accessible", s.get("PubliclyAccessible"), "PubliclyAccessible")
    m.arg("storage_encrypted", s.get("StorageEncrypted"), "StorageEncrypted")
    m.arg("kms_key_id", s.get("KmsKeyId"), "KmsKeyId")
    m.arg(
        "db_subnet_group_name",
        _dict(s.get("DBSubnetGroup")).get("DBSubnetGroupName"),
        "DBSubnetGroup",
    )
    groups = [
        g.get("VpcSecurityGroupId")
        for g in _list(s.get("VpcSecurityGroups"))
        if isinstance(g, dict)
    ]
    m.arg("vpc_security_group_ids", [g for g in groups if g], "VpcSecurityGroups")
    m.arg("username", s.get("MasterUsername"), "MasterUsername")
    m.arg("backup_retention_period", s.get("BackupRetentionPeriod"), "BackupRetentionPeriod")
    m.arg("tags", _tags(s.get("TagList")), "TagList")
    m.ignore_changes.append("password")
    return m


def _map_log_group(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("name", s.get("logGroupName") or resource_id(spec), "logGroupName")
    m.arg("retention_in_days", s.get("retentionInDays"), "retentionInDays")
    m.arg("kms_key_id", s.get("kmsKeyId"), "kmsKeyId")
    m.arg("tags", _tags(s.get("tags")), "tags")
    m.mapped.add("arn")
    return m


def _map_state_machine(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("stateMachineArn") or spec.arn))
    m.arg("name", s.get("name") or resource_id(spec), "name")
    m.arg("role_arn", s.get("roleArn"), "roleArn")
    m.arg("definition", _json_doc(s.get("definition")), "definition")
    m.arg("type", s.get("type"), "type")
    m.arg("tags", _tags(s.get("tags")), "tags")
    m.mapped.add("stateMachineArn")
    return m


def _key_names(schema: Any) -> tuple[Any, Any]:
    hash_key = range_key = None
    for key in _list(schema):
        if isinstance(key, dict):
            if key.get("KeyType") == "HASH":
                hash_key = key.get("AttributeName")
            elif key.get("KeyType") == "RANGE":
                range_key = key.get("AttributeName")
    return hash_key, range_key


def _map_dynamodb(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("name", s.get("TableName") or resource_id(spec), "TableName")
    billing = _dict(s.get("BillingModeSummary")).get("BillingMode") or "PROVISIONED"
    m.arg("billing_mode", billing, "BillingModeSummary")
    hash_key, range_key = _key_names(s.get("KeySchema"))
    m.arg("hash_key", hash_key, "KeySchema")
    m.arg("range_key", range_key, "KeySchema")
    throughput = _dict(s.get("ProvisionedThroughput"))
    if billing == "PROVISIONED":
        m.arg("read_capacity", throughput.get("ReadCapacityUnits"))
        m.arg("write_capacity", throughput.get("WriteCapacityUnits"))
    m.mapped.add("ProvisionedThroughput")
    for attribute in _list(s.get("AttributeDefinitions")):
        if isinstance(attribute, dict):
            m.block(
                Block(
                    "attribute",
                    [
                        ("name", attribute.get("AttributeName")),
                        ("type", attribute.get("AttributeType")),
                    ],
                ),
                "AttributeDefinitions",
            )
    for index in _list(s.get("GlobalSecondaryIndexes")):
        if not isinstance(index, dict):
            continue
        gsi_hash, gsi_range = _key_names(index.get("KeySchema"))
        projection = _dict(index.get("Projection"))
        items: list[Item] = [("name", index.get("IndexName")), ("hash_key", gsi_hash)]
        if gsi_range:
            items.append(("range_key", gsi_range))
        items.append(("projection_type", projection.get("ProjectionType", "ALL")))
        if projection.get("NonKeyAttributes"):
            items.append(("non_key_attributes", projection["NonKeyAttributes"]))
        if billing == "PROVISIONED":
            gsi_throughput = _dict(index.get("ProvisionedThroughput"))
            items.append(("read_capacity", gsi_throughput.get("ReadCapacityUnits", 0)))
            items.append(("write_capacity", gsi_throughput.get("WriteCapacityUnits", 0)))
        m.block(Block("global_secondary_index", items), "GlobalSecondaryIndexes")
    stream = _dict(s.get("StreamSpecification"))
    if stream:
        m.arg("stream_enabled", stream.get("StreamEnabled"), "StreamSpecification")
        if stream.get("StreamEnabled"):
            m.arg("stream_view_type", stream.get("StreamViewType"))
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    return m


def _map_s3_bucket(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    bucket = str(s.get("Name") or resource_id(spec))
    m = Mapping(import_id=bucket)
    m.arg("bucket", bucket, "Name")
    m.arg("tags", _tags(_dict(s.get("bucket-tagging")).get("TagSet")), "bucket-tagging")
    ref = Raw(f"aws_s3_bucket.{name}.id")
    status = _dict(s.get("bucket-versioning")).get("Status")
    if status in ("Enabled", "Suspended"):
        m.companions.append(
            TfResource(
                "aws_s3_bucket_versioning",
                name,
                [("bucket", ref), Block("versioning_configuration", [("status", status)])],
                bucket,
            )
        )
        m.mapped.add("bucket-versioning")
    policy = _json_doc(_dict(s.get("bucket-policy")).get("Policy"))
    if policy is not None:
        m.companions.append(
            TfResource("aws_s3_bucket_policy", name, [("bucket", ref), ("policy", policy)], bucket)
        )
        m.mapped.add("bucket-policy")
    configuration = _dict(
        _dict(s.get("bucket-encryption")).get("ServerSideEncryptionConfiguration")
    )
    rule_blocks: list[Item] = []
    for rule in _list(configuration.get("Rules")):
        if not isinstance(rule, dict):
            continue
        default = _dict(rule.get("ApplyServerSideEncryptionByDefault"))
        inner: list[Item] = [("sse_algorithm", default.get("SSEAlgorithm"))]
        if default.get("KMSMasterKeyID"):
            inner.append(("kms_master_key_id", default["KMSMasterKeyID"]))
        items: list[Item] = [Block("apply_server_side_encryption_by_default", inner)]
        if "BucketKeyEnabled" in rule:
            items.append(("bucket_key_enabled", bool(rule["BucketKeyEnabled"])))
        rule_blocks.append(Block("rule", items))
    if rule_blocks:
        m.companions.append(
            TfResource(
                "aws_s3_bucket_server_side_encryption_configuration",
                name,
                [("bucket", ref), *rule_blocks],
                bucket,
            )
        )
        m.mapped.add("bucket-encryption")
    return m


def _companion_name(base: str, suffix: str) -> str:
    return f"{base}_{re.sub(r'[^A-Za-z0-9_-]', '_', suffix)}"


def _map_iam_role(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    role = str(s.get("RoleName") or resource_id(spec))
    m = Mapping(import_id=role)
    m.arg("name", role, "RoleName")
    m.arg("path", s.get("Path"), "Path")
    m.arg(
        "assume_role_policy",
        _json_doc(s.get("AssumeRolePolicyDocument")),
        "AssumeRolePolicyDocument",
    )
    m.arg("description", s.get("Description") or None, "Description")
    m.arg("max_session_duration", s.get("MaxSessionDuration"), "MaxSessionDuration")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.update({"Arn", "AttachedPolicies", "InlinePolicies"})
    for attached in _list(s.get("AttachedPolicies")):
        if isinstance(attached, dict) and attached.get("PolicyArn"):
            policy_arn = str(attached["PolicyArn"])
            m.companions.append(
                TfResource(
                    "aws_iam_role_policy_attachment",
                    _companion_name(name, str(attached.get("PolicyName") or policy_arn)),
                    [("role", Raw(f"aws_iam_role.{name}.name")), ("policy_arn", policy_arn)],
                    f"{role}/{policy_arn}",
                )
            )
    for policy_name, document in sorted(_dict(s.get("InlinePolicies")).items()):
        m.companions.append(
            TfResource(
                "aws_iam_role_policy",
                _companion_name(name, policy_name),
                [
                    ("name", policy_name),
                    ("role", Raw(f"aws_iam_role.{name}.id")),
                    ("policy", _json_doc(document)),
                ],
                f"{role}:{policy_name}",
            )
        )
    return m


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


def _map_generic(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    """Unknown types: emit identifier-like keys verbatim (debug aid only)."""
    m = Mapping(import_id=resource_id(spec))
    for key, value in sorted(s.items()):
        if _IDENTIFIER.match(key):
            m.arg(key, value, key)
    return m


MAPPERS: dict[str, Callable[[dict[str, Any], str, ResourceSpec], Mapping]] = {
    "aws_instance": _map_instance,
    "aws_vpc": _map_vpc,
    "aws_security_group": _map_security_group,
    "aws_lambda_function": _map_lambda,
    "aws_db_instance": _map_db_instance,
    "aws_cloudwatch_log_group": _map_log_group,
    "aws_sfn_state_machine": _map_state_machine,
    "aws_dynamodb_table": _map_dynamodb,
    "aws_s3_bucket": _map_s3_bucket,
    "aws_iam_role": _map_iam_role,
}


def module_name(region: str) -> str:
    """Terraform module / provider alias name of a region directory."""
    return region.replace("-", "_")


# ============================================================================
# Generator
# ============================================================================


class IaCGenerator:
    """Terraform generator for collected ResourceSpecs."""

    def __init__(self, output_dir: str | Path | None = None) -> None:
        self.output_dir = Path(output_dir).resolve() if output_dir else None

    # ------------------------------------------------------------------
    # Names and types
    # ------------------------------------------------------------------

    def _tf_resource_type(self, resource_type: str) -> str:
        known = canonical_type(resource_type)
        if known:
            return known
        normalized = resource_type.lower().strip()
        return normalized if normalized.startswith("aws_") else f"aws_{normalized}"

    @staticmethod
    def _base_name(spec: ResourceSpec) -> str:
        name = file_id(resource_id(spec)).replace(".", "_")
        return name if re.match(r"[A-Za-z_]", name) else f"r_{name}"

    def assign_names(self, specs: list[ResourceSpec]) -> dict[str, str]:
        """Unique Terraform resource names per (region, type), keyed by ARN."""
        used: set[tuple[str, str, str]] = set()
        names: dict[str, str] = {}
        for spec in specs:
            region = spec.region or GLOBAL_REGION
            tf_type = self._tf_resource_type(spec.resource_type)
            base = self._base_name(spec)
            candidate, counter = base, 2
            while (region, tf_type, candidate) in used:
                candidate, counter = f"{base}_{counter}", counter + 1
            used.add((region, tf_type, candidate))
            names[spec.arn] = candidate
        return names

    # ------------------------------------------------------------------
    # Blocks
    # ------------------------------------------------------------------

    def _resources(self, spec: ResourceSpec, name: str) -> tuple[list[TfResource], Mapping]:
        tf_type = self._tf_resource_type(spec.resource_type)
        mapper = MAPPERS.get(tf_type, _map_generic)
        mapping = mapper(spec.specifications or {}, name, spec)
        items: list[Item] = []
        ignore = list(mapping.ignore_changes)
        for item in mapping.items:
            if _contains_placeholder(item if isinstance(item, Block) else item[1]):
                ignore.append(item.name if isinstance(item, Block) else item[0])
                items.append(("# REDACTED: set manually", None))
            items.append(item)
        if ignore:
            items.append(Block("lifecycle", [("ignore_changes", [Raw(i) for i in ignore])]))
        main = TfResource(tf_type, name, items, mapping.import_id or resource_id(spec))
        return [main, *mapping.companions], mapping

    def generate_resource_block(self, spec: ResourceSpec, name: str | None = None) -> str:
        """Terraform for one spec (main resource + companions) with traceability comments."""
        name = name or self._base_name(spec)
        resources, mapping = self._resources(spec, name)
        keys = sorted(spec.specifications or {})
        mapped = [k for k in keys if k in mapping.mapped]
        unmapped = [k for k in keys if k not in mapping.mapped]
        region = spec.region or GLOBAL_REGION
        lines = [
            f"# Resource: {resources[0].tf_type}.{name}",
            f"# Source specification: {spec_relpath(spec)}",
            f"# ARN: {spec.arn}",
            f"# Region: {region}",
        ]
        if mapped:
            lines.append(f"# mapped: {', '.join(mapped)}")
        lines.extend(f"# unmapped: {key}" for key in unmapped)
        for resource in resources:
            lines.append(f'resource "{resource.tf_type}" "{resource.name}" {{')
            lines.extend(render_items(resource.items, 1))
            lines.append("}")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Files
    # ------------------------------------------------------------------

    def _providers_tf(self, regions: list[str]) -> str:
        lines = [
            "terraform {",
            '  required_version = ">= 1.5.0"',
            "  required_providers {",
            "    aws = {",
            '      source  = "hashicorp/aws"',
            f'      version = "{AWS_PROVIDER_VERSION}"',
            "    }",
            "  }",
            "}",
            "",
            "# Default provider: global resources (S3, IAM) use us-east-1",
            'provider "aws" {',
            f'  region = "{DEFAULT_REGION}"',
            "}",
        ]
        for region in regions:
            lines += [
                "",
                'provider "aws" {',
                f'  alias  = "{module_name(region)}"',
                f'  region = "{region}"',
                "}",
            ]
        return "\n".join(lines) + "\n"

    @staticmethod
    def _versions_tf() -> str:
        return (
            "terraform {\n  required_providers {\n    aws = {\n"
            '      source = "hashicorp/aws"\n    }\n  }\n}\n'
        )

    @staticmethod
    def _main_tf(directories: list[str]) -> str:
        lines = ["# One module per region directory (generated by AWS Resource Inventory)"]
        for directory in directories:
            provider = "aws" if directory == GLOBAL_REGION else f"aws.{module_name(directory)}"
            lines += [
                "",
                f'module "{module_name(directory)}" {{',
                f'  source = "./{directory}"',
                "  providers = {",
                f"    aws = {provider}",
                "  }",
                "}",
            ]
        return "\n".join(lines) + "\n"

    def generate_terraform(
        self, specs: list[ResourceSpec], target_dir: str | Path | None = None
    ) -> dict[str, str]:
        """
        Write the Terraform project and return {relative path: content} of every file:
        providers.tf, main.tf, <region>/versions.tf, <region>/<type>.tf, import.sh,
        verify_state.sh.
        """
        dest = Path(target_dir).resolve() if target_dir else (self.output_dir or Path.cwd())
        dest.mkdir(parents=True, exist_ok=True)
        names = self.assign_names(specs)

        groups: dict[tuple[str, str], list[str]] = {}
        for spec in specs:
            key = (spec.region or GLOBAL_REGION, type_dir(spec.resource_type))
            groups.setdefault(key, []).append(self.generate_resource_block(spec, names[spec.arn]))

        files: dict[str, str] = {}
        directories = sorted(
            {region for region, _ in groups}, key=lambda r: (r != GLOBAL_REGION, r)
        )
        for (region, res_type), blocks in sorted(groups.items()):
            files[f"{region}/{res_type}.tf"] = (
                f"# Generated by AWS Resource Inventory\n# Region: {region} | Type: {res_type}\n\n"
                + "\n".join(blocks)
            )
        for directory in directories:
            files[f"{directory}/versions.tf"] = self._versions_tf()
        files["providers.tf"] = self._providers_tf([d for d in directories if d != GLOBAL_REGION])
        files["main.tf"] = self._main_tf(directories)
        files["import.sh"] = self.generate_import_script(specs)
        files["verify_state.sh"] = self.generate_verification_script(specs)

        for rel_path, content in files.items():
            path = dest / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            if rel_path.endswith(".sh"):
                path.chmod(0o755)
        return files

    def generate_import_script(self, specs: list[ResourceSpec]) -> str:
        """One idempotent `terraform import` per generated resource block (Req 7.4)."""
        names = self.assign_names(specs)
        lines = [
            "#!/usr/bin/env bash",
            "# Terraform import commands generated by AWS Resource Inventory (Requirement 7.4).",
            "# Run from the Terraform root after `terraform init`; imported addresses are skipped.",
            "set -euo pipefail",
            "",
        ]
        for spec in specs:
            prefix = f"module.{module_name(spec.region or GLOBAL_REGION)}."
            resources, _ = self._resources(spec, names[spec.arn])
            for resource in resources:
                address = shlex.quote(f"{prefix}{resource.tf_type}.{resource.name}")
                import_id = shlex.quote(resource.import_id)
                lines.append(
                    f"terraform state show {address} >/dev/null 2>&1 || "
                    f"terraform import {address} {import_id}"
                )
        lines += ["", "echo 'Terraform import completed.'"]
        return "\n".join(lines) + "\n"

    def generate_verification_script(self, specs: list[ResourceSpec]) -> str:
        """Script comparing the Terraform configuration with AWS (Req 7.5, 7.6)."""
        return """#!/usr/bin/env bash
# Verify that the generated Terraform matches the actual AWS resources (Requirements 7.5, 7.6).
# Exit codes: 0 = no changes, 2 = changes detected, 1 = error.
set -uo pipefail

if [ ! -d ".terraform" ]; then
  terraform init -input=false || exit 1
fi

terraform plan -detailed-exitcode -no-color -input=false > plan_output.txt 2>&1
PLAN_EXIT=$?
cat plan_output.txt

case $PLAN_EXIT in
  0) echo "SUCCESS: zero changes - Terraform configuration matches AWS."; exit 0 ;;
  2) echo "CHANGES DETECTED: review plan_output.txt."; exit 2 ;;
  *) echo "ERROR: terraform plan failed."; exit 1 ;;
esac
"""

    def verify_terraform_plan(self, tf_dir: str | Path) -> tuple[bool, str]:
        """Run `terraform plan -detailed-exitcode`; decide by exit code only (Req 7.5)."""
        try:
            result = subprocess.run(  # noqa: S603 - fixed terraform command
                ["terraform", "plan", "-detailed-exitcode", "-no-color", "-input=false"],
                cwd=Path(tf_dir),
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return False, "Error: terraform executable not found on PATH."
        output = f"{result.stdout or ''}\n{result.stderr or ''}".strip()
        if result.returncode == 0:
            return True, "Zero changes: Terraform state matches actual AWS resources."
        if result.returncode == 2:
            return False, f"Changes detected in terraform plan:\n{output}"
        return False, f"Error: terraform plan failed with exit code {result.returncode}:\n{output}"
