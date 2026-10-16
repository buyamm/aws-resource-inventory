"""
IaC Generator Module

Generates a Terraform project (AWS provider ~> 5.0) from collected specs: resources
grouped in modules (network, edge, compute, data, iam, observability) and one root
configuration per environment (envs/<env>/) with providers, S3 backend, import blocks
and a verification script. Resource arguments are mapped from AWS field names.

Requirements Coverage:
- Requirement 7.1: Generated from cached spec files only
- Requirement 7.2: modules/ + envs/<env>/ layout that passes `terraform fmt -check`
- Requirement 7.3: Per-type argument mapping; every top-level key listed as mapped/unmapped
- Requirement 7.4: imports.tf with provider-documented import ids (incl. companions)
- Requirement 7.5: lifecycle.ignore_changes for redacted / unknowable values; plan
  verification by `terraform plan -detailed-exitcode` exit code and the saved plan's actions
- Requirement 7.6: verify_state.sh
- Requirement 7.7: Traceability comments (spec file, ARN, region)
- Requirement 14.1: Mappings for the network, edge and load-balancing types
- Requirement 14.4: Mappings for the compute and data types (EventBridge targets as
  companion resources)
- Requirement 16.1: Module assignment, environment root, providers and default_tags
- Requirement 16.2: Cross-references through outputs/variables; snake_case names
- Requirement 16.3: Security group rules as separate resources
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.parser import ResourceSpec
from src.resource_types import (
    GLOBAL_REGION,
    canonical_type,
    resource_id,
    spec_relpath,
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


def _single_line(value: Any) -> bool:
    """Values `terraform fmt` aligns: everything but multi-line objects (heredocs count)."""
    return not (isinstance(value, dict) and value)


def _aligned(pairs: list[tuple[str, str, bool]], pad: str) -> list[str]:
    """``name = value`` lines; consecutive single-line pairs share one `=` column."""
    lines: list[str] = []
    chain: list[tuple[str, str]] = []

    def flush() -> None:
        width = max((len(name) for name, _ in chain), default=0)
        lines.extend(f"{pad}{name.ljust(width)} = {text}" for name, text in chain)
        chain.clear()

    for name, text, single in pairs:
        if single:
            chain.append((name, text))
        else:
            flush()
            lines.append(f"{pad}{name} = {text}")
    flush()
    return lines


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
        # Raw keys (provider addresses, resource names) are emitted unquoted.
        pairs = [
            (
                str(k) if isinstance(k, Raw) else hcl_string(str(k)),
                render_value(v, indent + 1),
                _single_line(v),
            )
            for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))
        ]
        return "{\n" + "\n".join(_aligned(pairs, pad + "  ")) + f"\n{pad}}}"
    return hcl_string(str(value))


BLANK: tuple[str, Any] = ("", None)


def render_items(items: list[Item], indent: int) -> list[str]:
    """HCL lines in `terraform fmt` layout. ``("", None)`` is a blank line, ``("# ...", None)``
    a comment; both end an alignment group, like blocks and multi-line values."""
    pad = "  " * indent
    lines: list[str] = []
    pairs: list[tuple[str, str, bool]] = []

    def flush() -> None:
        lines.extend(_aligned(pairs, pad))
        pairs.clear()

    for item in items:
        if isinstance(item, Block):
            flush()
            lines.append(f"{pad}{item.name} {{")
            lines.extend(render_items(item.items, indent + 1))
            lines.append(f"{pad}}}")
            continue
        name, value = item
        if not name or name.startswith("#"):
            flush()
            lines.append(f"{pad}{name}" if name else "")
        else:
            pairs.append((name, render_value(value, indent), _single_line(value)))
    flush()
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


def _raw_tags(value: Any) -> dict[str, str]:
    """Tags given as a dict or as ``[{"Key"|"key": k, "Value"|"value": v}]``."""
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    result: dict[str, str] = {}
    for item in value if isinstance(value, list) else []:
        if isinstance(item, dict):
            key = item.get("Key", item.get("key"))
            if key is not None:
                result[str(key)] = str(item.get("Value", item.get("value", "")))
    return result


def _tags(value: Any) -> dict[str, str]:
    """Tags Terraform can manage: ``aws:`` tags belong to AWS and are left out."""
    return {k: v for k, v in _raw_tags(value).items() if not k.startswith("aws:")}


def _spec_tags(specifications: dict[str, Any]) -> dict[str, str]:
    """Every tag of a spec, whatever field the API returns them in."""
    tags: dict[str, str] = {}
    for key in ("Tags", "tags", "TagList"):
        tags.update(_raw_tags(specifications.get(key)))
    tags.update(_raw_tags(_dict(specifications.get("bucket-tagging")).get("TagSet")))
    return tags


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _json_doc(value: Any) -> Heredoc | None:
    if isinstance(value, str) and not value.strip():
        return None  # empty policy attributes (SNS, SQS) mean "not set"
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


def _port_label(value: Any) -> str:
    return "any" if value in (None, -1, "-1") else str(value)


def _sg_rule(
    rule: dict[str, Any], group_ref: Raw, own_group_id: str, account_id: str
) -> list[Item]:
    """Arguments of one ``aws_vpc_security_group_{ingress,egress}_rule`` (Req 16.3)."""
    protocol = str(rule.get("IpProtocol", "-1"))
    reference = _dict(rule.get("ReferencedGroupInfo"))
    group_id = reference.get("GroupId")
    referenced: Any = group_id
    if group_id and group_id == own_group_id:
        referenced = group_ref
    elif group_id and reference.get("UserId") not in (None, "", account_id):
        referenced = f"{reference['UserId']}/{group_id}"
    items: list[Item] = [("security_group_id", group_ref), ("ip_protocol", protocol)]
    if protocol != "-1":
        items += _items(("from_port", rule.get("FromPort")), ("to_port", rule.get("ToPort")))
    items += _items(
        ("cidr_ipv4", rule.get("CidrIpv4")),
        ("cidr_ipv6", rule.get("CidrIpv6")),
        ("prefix_list_id", rule.get("PrefixListId")),
        ("referenced_security_group_id", referenced),
        ("description", rule.get("Description")),
        ("tags", _tags(rule.get("Tags"))),
    )
    return items


def _map_security_group(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("name", s.get("GroupName"), "GroupName")
    m.arg("description", s.get("Description"), "Description")
    m.arg("vpc_id", s.get("VpcId"), "VpcId")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.add("GroupId")
    rules = s.get("SecurityGroupRules")
    if not isinstance(rules, list):
        # Without rule ids the rules cannot be imported: they stay unmanaged.
        return m
    # IpPermissions(Egress) describe the same rules, grouped by permission.
    m.mapped.update({"SecurityGroupRules", "IpPermissions", "IpPermissionsEgress"})
    ref = Raw(f"aws_security_group.{name}.id")
    own = str(s.get("GroupId", ""))
    used: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict) or not rule.get("SecurityGroupRuleId"):
            continue
        kind = "egress" if rule.get("IsEgress") else "ingress"
        protocol = str(rule.get("IpProtocol", "-1"))
        label = f"{kind}_all" if protocol == "-1" else f"{kind}_{protocol}"
        if protocol != "-1":
            low, high = _port_label(rule.get("FromPort")), _port_label(rule.get("ToPort"))
            label += f"_{low}" if low == high else f"_{low}_{high}"
        base = _companion_name(name, label)
        candidate, counter = base, 2
        while candidate in used:
            candidate, counter = f"{base}_{counter}", counter + 1
        used.add(candidate)
        m.companions.append(
            TfResource(
                f"aws_vpc_security_group_{kind}_rule",
                candidate,
                _sg_rule(rule, ref, own, spec.account_id),
                str(rule["SecurityGroupRuleId"]),
            )
        )
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


def snake(text: str) -> str:
    """Lower-case snake_case: runs of other characters become one ``_``."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _companion_name(base: str, suffix: str) -> str:
    return snake(f"{base}_{suffix}") or base


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


# ============================================================================
# Network, edge and load balancing (Requirement 14.1)
# ============================================================================


def _items(*pairs: tuple[str, Any]) -> list[Item]:
    """Block items without absent values (None, "", [] and {} are not emitted)."""
    return [(k, v) for k, v in pairs if v is not None and v != "" and v != [] and v != {}]


def _quantity_items(value: Any) -> list[Any]:
    """``Items`` of CloudFront's ``{"Quantity": n, "Items": [...]}`` lists."""
    return _list(_dict(value).get("Items"))


def _attributes(value: Any) -> dict[str, str]:
    """ELB ``[{"Key": k, "Value": v}]`` attributes as a dict."""
    return {
        str(a["Key"]): str(a.get("Value", ""))
        for a in _list(value)
        if isinstance(a, dict) and "Key" in a
    }


def _int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _bool(value: Any) -> bool | None:
    return {"true": True, "false": False}.get(str(value).lower()) if value is not None else None


def _map_subnet(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("vpc_id", s.get("VpcId"), "VpcId")
    m.arg("cidr_block", s.get("CidrBlock"), "CidrBlock")
    m.arg("availability_zone", s.get("AvailabilityZone"), "AvailabilityZone")
    m.arg("map_public_ip_on_launch", s.get("MapPublicIpOnLaunch"), "MapPublicIpOnLaunch")
    m.arg(
        "assign_ipv6_address_on_creation",
        s.get("AssignIpv6AddressOnCreation"),
        "AssignIpv6AddressOnCreation",
    )
    ipv6 = [
        a.get("Ipv6CidrBlock")
        for a in _list(s.get("Ipv6CidrBlockAssociationSet"))
        if isinstance(a, dict)
        and _dict(a.get("Ipv6CidrBlockState")).get("State", "associated") == "associated"
    ]
    m.arg("ipv6_cidr_block", ipv6[0] if ipv6 else None, "Ipv6CidrBlockAssociationSet")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.update({"SubnetId", "SubnetArn"})
    return m


# Route fields -> Terraform route arguments (a vpce- GatewayId is a GWLB endpoint).
_ROUTE_TARGETS = (
    ("NatGatewayId", "nat_gateway_id"),
    ("TransitGatewayId", "transit_gateway_id"),
    ("VpcPeeringConnectionId", "vpc_peering_connection_id"),
    ("EgressOnlyInternetGatewayId", "egress_only_gateway_id"),
    ("CarrierGatewayId", "carrier_gateway_id"),
    ("LocalGatewayId", "local_gateway_id"),
    ("CoreNetworkArn", "core_network_arn"),
)


def _route_block(route: dict[str, Any]) -> Block | None:
    gateway = str(route.get("GatewayId") or "")
    if gateway == "local" or route.get("Origin") == "EnableVgwRoutePropagation":
        return None
    if gateway.startswith("vpce-") and route.get("DestinationPrefixListId"):
        return None  # gateway endpoint route, managed by aws_vpc_endpoint.route_table_ids
    items = _items(
        ("cidr_block", route.get("DestinationCidrBlock")),
        ("ipv6_cidr_block", route.get("DestinationIpv6CidrBlock")),
        ("destination_prefix_list_id", route.get("DestinationPrefixListId")),
    )
    if gateway.startswith("vpce-"):
        items.append(("vpc_endpoint_id", gateway))
    elif gateway:
        items.append(("gateway_id", gateway))
    items += _items(*((tf, route.get(aws)) for aws, tf in _ROUTE_TARGETS))
    if not any(isinstance(i, tuple) and i[0].endswith(("_id", "_arn")) for i in items):
        items += _items(("network_interface_id", route.get("NetworkInterfaceId")))
    return Block("route", items)


def _map_route_table(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    route_table_id = resource_id(spec)
    m = Mapping(import_id=route_table_id)
    m.arg("vpc_id", s.get("VpcId"), "VpcId")
    for route in _list(s.get("Routes")):
        block = _route_block(route) if isinstance(route, dict) else None
        if block is not None:
            m.block(block)
    m.mapped.add("Routes")
    vgws = [g.get("GatewayId") for g in _list(s.get("PropagatingVgws")) if isinstance(g, dict)]
    m.arg("propagating_vgws", [g for g in vgws if g], "PropagatingVgws")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    ref = Raw(f"aws_route_table.{name}.id")
    for association in _list(s.get("Associations")):
        if not isinstance(association, dict) or association.get("Main"):
            continue
        target = association.get("SubnetId") or association.get("GatewayId")
        if not target:
            continue
        argument = "subnet_id" if association.get("SubnetId") else "gateway_id"
        m.companions.append(
            TfResource(
                "aws_route_table_association",
                _companion_name(name, str(target)),
                [(argument, target), ("route_table_id", ref)],
                f"{target}/{route_table_id}",
            )
        )
    m.mapped.update({"RouteTableId", "Associations"})
    return m


def _map_internet_gateway(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    vpcs = [a.get("VpcId") for a in _list(s.get("Attachments")) if isinstance(a, dict)]
    m.arg("vpc_id", vpcs[0] if vpcs else None, "Attachments")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.add("InternetGatewayId")
    return m


def _map_nat_gateway(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("subnet_id", s.get("SubnetId"), "SubnetId")
    connectivity = s.get("ConnectivityType")
    m.arg(
        "connectivity_type",
        connectivity if connectivity in ("public", "private") else None,
        "ConnectivityType",
    )
    addresses = [a for a in _list(s.get("NatGatewayAddresses")) if isinstance(a, dict)]
    primary = addresses[0] if addresses else {}
    m.arg("allocation_id", primary.get("AllocationId"), "NatGatewayAddresses")
    m.arg("private_ip", primary.get("PrivateIp"))
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.update({"NatGatewayId", "VpcId"})
    return m


def _map_vpc_endpoint(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("vpc_id", s.get("VpcId"), "VpcId")
    m.arg("service_name", s.get("ServiceName"), "ServiceName")
    endpoint_type = s.get("VpcEndpointType")
    m.arg("vpc_endpoint_type", endpoint_type, "VpcEndpointType")
    m.arg("route_table_ids", _list(s.get("RouteTableIds")), "RouteTableIds")
    m.arg("subnet_ids", _list(s.get("SubnetIds")), "SubnetIds")
    groups = [g.get("GroupId") for g in _list(s.get("Groups")) if isinstance(g, dict)]
    m.arg("security_group_ids", [g for g in groups if g], "Groups")
    if endpoint_type == "Interface":
        m.arg("private_dns_enabled", s.get("PrivateDnsEnabled"), "PrivateDnsEnabled")
    m.arg("ip_address_type", s.get("IpAddressType"), "IpAddressType")
    m.arg("policy", _json_doc(s.get("PolicyDocument")), "PolicyDocument")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.add("VpcEndpointId")
    return m


def _map_lb(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("LoadBalancerArn") or spec.arn))
    m.arg("name", s.get("LoadBalancerName"), "LoadBalancerName")
    scheme = s.get("Scheme")
    m.arg("internal", scheme == "internal" if scheme else None, "Scheme")
    m.arg("load_balancer_type", s.get("Type"), "Type")
    subnets = [z.get("SubnetId") for z in _list(s.get("AvailabilityZones")) if isinstance(z, dict)]
    m.arg("subnets", [z for z in subnets if z], "AvailabilityZones")
    m.arg("security_groups", _list(s.get("SecurityGroups")), "SecurityGroups")
    m.arg("ip_address_type", s.get("IpAddressType"), "IpAddressType")
    attributes = _attributes(s.get("Attributes"))
    m.arg(
        "enable_deletion_protection",
        _bool(attributes.get("deletion_protection.enabled")),
        "Attributes",
    )
    m.arg("idle_timeout", _int(attributes.get("idle_timeout.timeout_seconds")))
    m.arg("enable_http2", _bool(attributes.get("routing.http2.enabled")))
    m.arg(
        "drop_invalid_header_fields",
        _bool(attributes.get("routing.http.drop_invalid_header_fields.enabled")),
    )
    if _bool(attributes.get("access_logs.s3.enabled")):
        m.block(
            Block(
                "access_logs",
                _items(
                    ("bucket", attributes.get("access_logs.s3.bucket")),
                    ("prefix", attributes.get("access_logs.s3.prefix")),
                    ("enabled", True),
                ),
            )
        )
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.update({"LoadBalancerArn", "VpcId"})
    return m


def _default_action(action: dict[str, Any]) -> Block:
    kind = action.get("Type")
    items = _items(("type", kind), ("order", action.get("Order")))
    forward = _dict(action.get("ForwardConfig"))
    groups = [g for g in _list(forward.get("TargetGroups")) if isinstance(g, dict)]
    if kind == "forward" and len(groups) > 1:
        targets: list[Item] = [
            Block(
                "target_group",
                _items(("arn", g.get("TargetGroupArn")), ("weight", g.get("Weight"))),
            )
            for g in groups
        ]
        stickiness = _dict(forward.get("TargetGroupStickinessConfig"))
        if stickiness:
            targets.append(
                Block(
                    "stickiness",
                    _items(
                        ("enabled", stickiness.get("Enabled")),
                        ("duration", stickiness.get("DurationSeconds")),
                    ),
                )
            )
        items.append(Block("forward", targets))
    elif kind == "forward":
        arn = action.get("TargetGroupArn") or (groups[0].get("TargetGroupArn") if groups else None)
        items += _items(("target_group_arn", arn))
    redirect = _dict(action.get("RedirectConfig"))
    if redirect:
        items.append(
            Block(
                "redirect",
                _items(
                    ("host", redirect.get("Host")),
                    ("path", redirect.get("Path")),
                    ("port", redirect.get("Port")),
                    ("protocol", redirect.get("Protocol")),
                    ("query", redirect.get("Query")),
                    ("status_code", redirect.get("StatusCode")),
                ),
            )
        )
    fixed = _dict(action.get("FixedResponseConfig"))
    if fixed:
        items.append(
            Block(
                "fixed_response",
                _items(
                    ("content_type", fixed.get("ContentType")),
                    ("message_body", fixed.get("MessageBody")),
                    ("status_code", fixed.get("StatusCode")),
                ),
            )
        )
    return Block("default_action", items)


def _map_lb_listener(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("ListenerArn") or spec.arn))
    m.arg("load_balancer_arn", s.get("LoadBalancerArn"), "LoadBalancerArn")
    m.arg("port", s.get("Port"), "Port")
    m.arg("protocol", s.get("Protocol"), "Protocol")
    m.arg("ssl_policy", s.get("SslPolicy"), "SslPolicy")
    certificates = [c for c in _list(s.get("Certificates")) if isinstance(c, dict)]
    default_certificate = next(
        (c for c in certificates if c.get("IsDefault") is not False),
        certificates[0] if certificates else {},
    )
    m.arg("certificate_arn", default_certificate.get("CertificateArn"), "Certificates")
    alpn = _list(s.get("AlpnPolicy"))
    m.arg("alpn_policy", alpn[0] if alpn else None, "AlpnPolicy")
    for action in _list(s.get("DefaultActions")):
        if isinstance(action, dict):
            m.block(_default_action(action), "DefaultActions")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.add("ListenerArn")
    return m


def _map_lb_target_group(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("TargetGroupArn") or spec.arn))
    m.arg("name", s.get("TargetGroupName"), "TargetGroupName")
    m.arg("port", s.get("Port"), "Port")
    m.arg("protocol", s.get("Protocol"), "Protocol")
    m.arg("protocol_version", s.get("ProtocolVersion"), "ProtocolVersion")
    m.arg("vpc_id", s.get("VpcId"), "VpcId")
    m.arg("target_type", s.get("TargetType"), "TargetType")
    m.arg("ip_address_type", s.get("IpAddressType"), "IpAddressType")
    matcher = _dict(s.get("Matcher"))
    health = _items(
        ("enabled", s.get("HealthCheckEnabled")),
        ("path", s.get("HealthCheckPath")),
        ("port", s.get("HealthCheckPort")),
        ("protocol", s.get("HealthCheckProtocol")),
        ("interval", s.get("HealthCheckIntervalSeconds")),
        ("timeout", s.get("HealthCheckTimeoutSeconds")),
        ("healthy_threshold", s.get("HealthyThresholdCount")),
        ("unhealthy_threshold", s.get("UnhealthyThresholdCount")),
        ("matcher", matcher.get("HttpCode") or matcher.get("GrpcCode")),
    )
    if health:
        m.block(Block("health_check", health))
    m.mapped.update(
        {
            "HealthCheckEnabled",
            "HealthCheckPath",
            "HealthCheckPort",
            "HealthCheckProtocol",
            "HealthCheckIntervalSeconds",
            "HealthCheckTimeoutSeconds",
            "HealthyThresholdCount",
            "UnhealthyThresholdCount",
            "Matcher",
        }
    )
    attributes = _attributes(s.get("Attributes"))
    m.arg(
        "deregistration_delay", attributes.get("deregistration_delay.timeout_seconds"), "Attributes"
    )
    m.arg("slow_start", _int(attributes.get("slow_start.duration_seconds")))
    m.arg("load_balancing_algorithm_type", attributes.get("load_balancing.algorithm.type"))
    if _bool(attributes.get("stickiness.enabled")):
        m.block(
            Block(
                "stickiness",
                _items(
                    ("type", attributes.get("stickiness.type")),
                    ("enabled", True),
                    (
                        "cookie_duration",
                        _int(attributes.get("stickiness.lb_cookie.duration_seconds")),
                    ),
                ),
            )
        )
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.add("TargetGroupArn")
    return m


def _cache_behavior(behavior: dict[str, Any], block_name: str) -> Block:
    methods = _dict(behavior.get("AllowedMethods"))
    items = _items(
        ("path_pattern", behavior.get("PathPattern")),
        ("target_origin_id", behavior.get("TargetOriginId")),
        ("viewer_protocol_policy", behavior.get("ViewerProtocolPolicy")),
        ("allowed_methods", _list(methods.get("Items"))),
        ("cached_methods", _quantity_items(methods.get("CachedMethods"))),
        ("compress", behavior.get("Compress")),
        ("cache_policy_id", behavior.get("CachePolicyId")),
        ("origin_request_policy_id", behavior.get("OriginRequestPolicyId")),
        ("response_headers_policy_id", behavior.get("ResponseHeadersPolicyId")),
        ("min_ttl", behavior.get("MinTTL")),
        ("default_ttl", behavior.get("DefaultTTL")),
        ("max_ttl", behavior.get("MaxTTL")),
    )
    forwarded = _dict(behavior.get("ForwardedValues"))
    if forwarded and not behavior.get("CachePolicyId"):
        cookies = _dict(forwarded.get("Cookies"))
        items.append(
            Block(
                "forwarded_values",
                _items(
                    ("query_string", forwarded.get("QueryString")),
                    ("headers", _quantity_items(forwarded.get("Headers"))),
                    (
                        "query_string_cache_keys",
                        _quantity_items(forwarded.get("QueryStringCacheKeys")),
                    ),
                )
                + [
                    Block(
                        "cookies",
                        _items(
                            ("forward", cookies.get("Forward")),
                            ("whitelisted_names", _quantity_items(cookies.get("WhitelistedNames"))),
                        ),
                    )
                ],
            )
        )
    for association in _quantity_items(behavior.get("LambdaFunctionAssociations")):
        items.append(
            Block(
                "lambda_function_association",
                _items(
                    ("event_type", association.get("EventType")),
                    ("lambda_arn", association.get("LambdaFunctionARN")),
                    ("include_body", association.get("IncludeBody")),
                ),
            )
        )
    for association in _quantity_items(behavior.get("FunctionAssociations")):
        items.append(
            Block(
                "function_association",
                _items(
                    ("event_type", association.get("EventType")),
                    ("function_arn", association.get("FunctionARN")),
                ),
            )
        )
    return Block(block_name, items)


def _origin(origin: dict[str, Any]) -> Block:
    items = _items(
        ("domain_name", origin.get("DomainName")),
        ("origin_id", origin.get("Id")),
        ("origin_path", origin.get("OriginPath")),
        ("origin_access_control_id", origin.get("OriginAccessControlId")),
        ("connection_attempts", origin.get("ConnectionAttempts")),
        ("connection_timeout", origin.get("ConnectionTimeout")),
    )
    for header in _quantity_items(origin.get("CustomHeaders")):
        items.append(
            Block(
                "custom_header",
                _items(("name", header.get("HeaderName")), ("value", header.get("HeaderValue"))),
            )
        )
    if "S3OriginConfig" in origin:
        identity = _dict(origin.get("S3OriginConfig")).get("OriginAccessIdentity", "")
        items.append(Block("s3_origin_config", [("origin_access_identity", identity)]))
    custom = _dict(origin.get("CustomOriginConfig"))
    if custom:
        custom_items = _items(
            ("http_port", custom.get("HTTPPort")),
            ("https_port", custom.get("HTTPSPort")),
            ("origin_protocol_policy", custom.get("OriginProtocolPolicy")),
        )
        if "OriginSslProtocols" in custom:  # required argument, emitted even when empty
            custom_items.append(
                ("origin_ssl_protocols", _quantity_items(custom["OriginSslProtocols"]))
            )
        custom_items += _items(
            ("origin_read_timeout", custom.get("OriginReadTimeout")),
            ("origin_keepalive_timeout", custom.get("OriginKeepaliveTimeout")),
        )
        items.append(Block("custom_origin_config", custom_items))
    return Block("origin", items)


def _map_cloudfront_distribution(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    config = _dict(s.get("DistributionConfig"))
    m.arg("enabled", config.get("Enabled"), "DistributionConfig")
    m.arg("aliases", _quantity_items(config.get("Aliases")))
    m.arg("comment", config.get("Comment") or None)
    m.arg("default_root_object", config.get("DefaultRootObject") or None)
    m.arg("price_class", config.get("PriceClass"))
    m.arg("http_version", config.get("HttpVersion"))
    m.arg("is_ipv6_enabled", config.get("IsIPV6Enabled"))
    m.arg("web_acl_id", config.get("WebACLId") or None)
    for origin in _quantity_items(config.get("Origins")):
        if isinstance(origin, dict):
            m.block(_origin(origin))
    default = _dict(config.get("DefaultCacheBehavior"))
    if default:
        m.block(_cache_behavior(default, "default_cache_behavior"))
    for behavior in _quantity_items(config.get("CacheBehaviors")):
        if isinstance(behavior, dict):
            m.block(_cache_behavior(behavior, "ordered_cache_behavior"))
    for response in _quantity_items(config.get("CustomErrorResponses")):
        m.block(
            Block(
                "custom_error_response",
                _items(
                    ("error_code", response.get("ErrorCode")),
                    ("response_code", _int(response.get("ResponseCode"))),
                    ("response_page_path", response.get("ResponsePagePath")),
                    ("error_caching_min_ttl", response.get("ErrorCachingMinTTL")),
                ),
            )
        )
    logging = _dict(config.get("Logging"))
    if logging.get("Enabled"):
        m.block(
            Block(
                "logging_config",
                _items(
                    ("bucket", logging.get("Bucket")),
                    ("prefix", logging.get("Prefix")),
                    ("include_cookies", logging.get("IncludeCookies")),
                ),
            )
        )
    geo = _dict(_dict(config.get("Restrictions")).get("GeoRestriction"))
    if geo:
        m.block(
            Block(
                "restrictions",
                [
                    Block(
                        "geo_restriction",
                        _items(
                            ("restriction_type", geo.get("RestrictionType")),
                            ("locations", _list(geo.get("Items"))),
                        ),
                    )
                ],
            )
        )
    certificate = _dict(config.get("ViewerCertificate"))
    if certificate.get("ACMCertificateArn") or certificate.get("IAMCertificateId"):
        m.block(
            Block(
                "viewer_certificate",
                _items(
                    ("acm_certificate_arn", certificate.get("ACMCertificateArn")),
                    ("iam_certificate_id", certificate.get("IAMCertificateId")),
                    ("ssl_support_method", certificate.get("SSLSupportMethod")),
                    ("minimum_protocol_version", certificate.get("MinimumProtocolVersion")),
                ),
            )
        )
    elif certificate:
        m.block(Block("viewer_certificate", [("cloudfront_default_certificate", True)]))
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.update({"Id", "ARN"})
    return m


def _record(record: dict[str, Any], zone_ref: Raw) -> list[Item]:
    alias = _dict(record.get("AliasTarget"))
    items: list[Item] = [
        ("zone_id", zone_ref),
        ("name", str(record.get("Name", "")).rstrip(".")),
        ("type", record.get("Type")),
    ]
    items += _items(("set_identifier", record.get("SetIdentifier")))
    if alias:
        items.append(
            Block(
                "alias",
                _items(
                    ("name", alias.get("DNSName")),
                    ("zone_id", alias.get("HostedZoneId")),
                    ("evaluate_target_health", alias.get("EvaluateTargetHealth")),
                ),
            )
        )
    else:
        values = [
            r.get("Value") for r in _list(record.get("ResourceRecords")) if isinstance(r, dict)
        ]
        items += _items(("ttl", record.get("TTL")), ("records", [v for v in values if v]))
    if record.get("Weight") is not None:
        items.append(Block("weighted_routing_policy", [("weight", record["Weight"])]))
    items += _items(("health_check_id", record.get("HealthCheckId")))
    return items


def _map_route53_zone(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    zone_id = resource_id(spec)
    zone_name = str(s.get("Name") or "").rstrip(".")
    m = Mapping(import_id=zone_id)
    m.arg("name", zone_name or None, "Name")
    config = _dict(s.get("Config"))
    m.arg("comment", config.get("Comment") or None, "Config")
    for vpc in _list(s.get("VPCs")):
        if isinstance(vpc, dict):
            m.block(
                Block(
                    "vpc",
                    _items(("vpc_id", vpc.get("VPCId")), ("vpc_region", vpc.get("VPCRegion"))),
                ),
                "VPCs",
            )
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    zone_ref = Raw(f"aws_route53_zone.{name}.zone_id")
    for record in _list(s.get("ResourceRecordSets")):
        if not isinstance(record, dict):
            continue
        record_name = str(record.get("Name", "")).rstrip(".")
        record_type = str(record.get("Type", ""))
        if record_name == zone_name and record_type in ("NS", "SOA"):
            continue  # created and owned by the hosted zone itself
        suffix = f"{record_name}_{record_type}"
        if record.get("SetIdentifier"):
            suffix += f"_{record['SetIdentifier']}"
        relative = "apex" if record_name == zone_name else record_name
        if zone_name and relative.endswith(f".{zone_name}"):
            relative = relative[: -len(zone_name) - 1]
        label = f"{relative.replace('*', 'wildcard')}_{record_type}"
        if record.get("SetIdentifier"):
            label += f"_{record['SetIdentifier']}"
        m.companions.append(
            TfResource(
                "aws_route53_record",
                _companion_name(name, label),
                _record(record, zone_ref),
                f"{zone_id}_{suffix}",
            )
        )
    m.mapped.update({"Id", "ResourceRecordSets"})
    return m


def _map_acm_certificate(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("CertificateArn") or spec.arn))
    if s.get("Type") == "IMPORTED":
        # The private key is never readable through the API.
        m.items.append(("# IMPORTED certificate: set certificate_body and private_key", None))
        m.ignore_changes += ["certificate_body", "private_key", "certificate_chain"]
    else:
        m.arg("domain_name", s.get("DomainName"), "DomainName")
        m.arg(
            "subject_alternative_names",
            _list(s.get("SubjectAlternativeNames")),
            "SubjectAlternativeNames",
        )
        methods = [
            o.get("ValidationMethod")
            for o in _list(s.get("DomainValidationOptions"))
            if isinstance(o, dict) and o.get("ValidationMethod")
        ]
        m.arg("validation_method", methods[0] if methods else None, "DomainValidationOptions")
        m.arg("key_algorithm", s.get("KeyAlgorithm"), "KeyAlgorithm")
        preference = _dict(s.get("Options")).get("CertificateTransparencyLoggingPreference")
        if preference:
            m.block(
                Block("options", [("certificate_transparency_logging_preference", preference)]),
                "Options",
            )
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.update({"CertificateArn", "Type"})
    return m


def _map_wafv2_web_acl(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    scope = "CLOUDFRONT" if spec.region == GLOBAL_REGION else "REGIONAL"
    acl_name = str(s.get("Name") or "")
    m = Mapping(import_id=f"{s.get('Id', '')}/{acl_name}/{scope}")
    m.arg("name", acl_name or None, "Name")
    m.arg("scope", scope)
    m.arg("description", s.get("Description") or None, "Description")
    action = _dict(s.get("DefaultAction"))
    kind = "allow" if "Allow" in action else "block" if "Block" in action else None
    if kind:
        m.block(Block("default_action", [Block(kind, [])]), "DefaultAction")
    visibility = _dict(s.get("VisibilityConfig"))
    if visibility:
        m.block(
            Block(
                "visibility_config",
                _items(
                    ("cloudwatch_metrics_enabled", visibility.get("CloudWatchMetricsEnabled")),
                    ("metric_name", visibility.get("MetricName")),
                    ("sampled_requests_enabled", visibility.get("SampledRequestsEnabled")),
                ),
            ),
            "VisibilityConfig",
        )
    if _list(s.get("Rules")):
        # Rule statements are not mapped; keep them out of the plan.
        m.ignore_changes.append("rule")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.update({"Id", "ARN"})
    return m


# ============================================================================
# Compute and data (Requirement 14.4)
# ============================================================================


def _map_ecs_cluster(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("clusterName") or resource_id(spec)))
    m.arg("name", s.get("clusterName"), "clusterName")
    for setting in _list(s.get("settings")):
        if isinstance(setting, dict) and setting.get("name"):
            m.block(
                Block("setting", [("name", setting["name"]), ("value", setting.get("value"))]),
                "settings",
            )
    m.arg("tags", _tags(s.get("tags")), "tags")
    m.mapped.add("clusterArn")
    return m


def _map_ecs_service(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=resource_id(spec))
    m.arg("name", s.get("serviceName"), "serviceName")
    m.arg("cluster", s.get("clusterArn"), "clusterArn")
    m.arg("task_definition", s.get("taskDefinition"), "taskDefinition")
    m.arg("desired_count", s.get("desiredCount"), "desiredCount")
    strategy = [x for x in _list(s.get("capacityProviderStrategy")) if isinstance(x, dict)]
    for item in strategy:
        m.block(
            Block(
                "capacity_provider_strategy",
                _items(
                    ("capacity_provider", item.get("capacityProvider")),
                    ("weight", item.get("weight")),
                    ("base", item.get("base")),
                ),
            ),
            "capacityProviderStrategy",
        )
    # launch_type and capacity_provider_strategy are mutually exclusive.
    m.arg("launch_type", None if strategy else s.get("launchType"), "launchType")
    if s.get("launchType") == "FARGATE" or strategy:
        m.arg("platform_version", s.get("platformVersion"), "platformVersion")
    m.arg("scheduling_strategy", s.get("schedulingStrategy"), "schedulingStrategy")
    deployment = _dict(s.get("deploymentConfiguration"))
    m.arg("deployment_maximum_percent", deployment.get("maximumPercent"), "deploymentConfiguration")
    m.arg("deployment_minimum_healthy_percent", deployment.get("minimumHealthyPercent"))
    breaker = _dict(deployment.get("deploymentCircuitBreaker"))
    if breaker:
        m.block(
            Block(
                "deployment_circuit_breaker",
                _items(("enable", breaker.get("enable")), ("rollback", breaker.get("rollback"))),
            )
        )
    if _list(s.get("loadBalancers")):
        m.arg(
            "health_check_grace_period_seconds",
            s.get("healthCheckGracePeriodSeconds"),
            "healthCheckGracePeriodSeconds",
        )
    m.arg("enable_execute_command", s.get("enableExecuteCommand"), "enableExecuteCommand")
    m.arg("enable_ecs_managed_tags", s.get("enableECSManagedTags"), "enableECSManagedTags")
    m.arg("propagate_tags", s.get("propagateTags"), "propagateTags")
    for lb in _list(s.get("loadBalancers")):
        if isinstance(lb, dict):
            m.block(
                Block(
                    "load_balancer",
                    _items(
                        ("target_group_arn", lb.get("targetGroupArn")),
                        ("elb_name", lb.get("loadBalancerName")),
                        ("container_name", lb.get("containerName")),
                        ("container_port", lb.get("containerPort")),
                    ),
                ),
                "loadBalancers",
            )
    for registry in _list(s.get("serviceRegistries")):
        if isinstance(registry, dict):
            m.block(
                Block(
                    "service_registries",
                    _items(
                        ("registry_arn", registry.get("registryArn")),
                        ("port", registry.get("port")),
                        ("container_name", registry.get("containerName")),
                        ("container_port", registry.get("containerPort")),
                    ),
                ),
                "serviceRegistries",
            )
    vpc = _dict(_dict(s.get("networkConfiguration")).get("awsvpcConfiguration"))
    if vpc:
        public = vpc.get("assignPublicIp")
        m.block(
            Block(
                "network_configuration",
                _items(
                    ("subnets", _list(vpc.get("subnets"))),
                    ("security_groups", _list(vpc.get("securityGroups"))),
                    ("assign_public_ip", public == "ENABLED" if public else None),
                ),
            ),
            "networkConfiguration",
        )
    role = s.get("roleArn")
    if isinstance(role, str) and "/aws-service-role/" not in role:
        m.arg("iam_role", role, "roleArn")
    m.arg("tags", _tags(s.get("tags")), "tags")
    m.mapped.update({"serviceArn", "roleArn"})
    return m


def _map_ecs_task_definition(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("taskDefinitionArn") or spec.arn))
    m.arg("family", s.get("family"), "family")
    containers = s.get("containerDefinitions")
    if _contains_placeholder(containers):
        # The JSON document holds a redacted value: the argument cannot be compared.
        m.items.append(("# REDACTED: set manually", None))
        m.ignore_changes.append("container_definitions")
    m.arg("container_definitions", _json_doc(containers), "containerDefinitions")
    m.arg("task_role_arn", s.get("taskRoleArn"), "taskRoleArn")
    m.arg("execution_role_arn", s.get("executionRoleArn"), "executionRoleArn")
    m.arg("network_mode", s.get("networkMode"), "networkMode")
    m.arg(
        "requires_compatibilities",
        _list(s.get("requiresCompatibilities")),
        "requiresCompatibilities",
    )
    m.arg("cpu", s.get("cpu"), "cpu")
    m.arg("memory", s.get("memory"), "memory")
    m.arg("ipc_mode", s.get("ipcMode"), "ipcMode")
    m.arg("pid_mode", s.get("pidMode"), "pidMode")
    platform = _dict(s.get("runtimePlatform"))
    if platform:
        m.block(
            Block(
                "runtime_platform",
                _items(
                    ("cpu_architecture", platform.get("cpuArchitecture")),
                    ("operating_system_family", platform.get("operatingSystemFamily")),
                ),
            ),
            "runtimePlatform",
        )
    storage = _dict(s.get("ephemeralStorage"))
    if storage.get("sizeInGiB"):
        m.block(
            Block("ephemeral_storage", [("size_in_gib", storage["sizeInGiB"])]), "ephemeralStorage"
        )
    for volume in _list(s.get("volumes")):
        if not isinstance(volume, dict):
            continue
        items = _items(("name", volume.get("name")))
        items += _items(("host_path", _dict(volume.get("host")).get("sourcePath")))
        efs = _dict(volume.get("efsVolumeConfiguration"))
        if efs:
            items.append(
                Block(
                    "efs_volume_configuration",
                    _items(
                        ("file_system_id", efs.get("fileSystemId")),
                        ("root_directory", efs.get("rootDirectory")),
                        ("transit_encryption", efs.get("transitEncryption")),
                    ),
                )
            )
        m.block(Block("volume", items), "volumes")
    m.arg("tags", _tags(s.get("tags")), "tags")
    m.mapped.update({"taskDefinitionArn", "revision"})
    return m


def _map_ecr_repository(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("repositoryName") or resource_id(spec)))
    m.arg("name", s.get("repositoryName"), "repositoryName")
    m.arg("image_tag_mutability", s.get("imageTagMutability"), "imageTagMutability")
    scanning = _dict(s.get("imageScanningConfiguration"))
    if "scanOnPush" in scanning:
        m.block(
            Block("image_scanning_configuration", [("scan_on_push", scanning["scanOnPush"])]),
            "imageScanningConfiguration",
        )
    encryption = _dict(s.get("encryptionConfiguration"))
    if encryption:
        m.block(
            Block(
                "encryption_configuration",
                _items(
                    ("encryption_type", encryption.get("encryptionType")),
                    ("kms_key", encryption.get("kmsKey")),
                ),
            ),
            "encryptionConfiguration",
        )
    m.arg("tags", _tags(s.get("tags")), "tags")
    m.mapped.update({"repositoryArn", "repositoryUri", "registryId"})
    return m


def _map_autoscaling_group(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("AutoScalingGroupName") or resource_id(spec)))
    m.arg("name", s.get("AutoScalingGroupName"), "AutoScalingGroupName")
    m.arg("min_size", s.get("MinSize"), "MinSize")
    m.arg("max_size", s.get("MaxSize"), "MaxSize")
    m.arg("desired_capacity", s.get("DesiredCapacity"), "DesiredCapacity")
    m.arg("default_cooldown", s.get("DefaultCooldown"), "DefaultCooldown")
    m.arg("health_check_type", s.get("HealthCheckType"), "HealthCheckType")
    m.arg("health_check_grace_period", s.get("HealthCheckGracePeriod"), "HealthCheckGracePeriod")
    zones = str(s.get("VPCZoneIdentifier") or "")
    subnets = [z.strip() for z in zones.split(",") if z.strip()]
    if subnets:
        # The subnets determine the availability zones.
        m.arg("vpc_zone_identifier", subnets, "VPCZoneIdentifier", "AvailabilityZones")
    else:
        m.arg("availability_zones", _list(s.get("AvailabilityZones")), "AvailabilityZones")
    m.arg("target_group_arns", _list(s.get("TargetGroupARNs")), "TargetGroupARNs")
    m.arg("load_balancers", _list(s.get("LoadBalancerNames")), "LoadBalancerNames")
    m.arg("termination_policies", _list(s.get("TerminationPolicies")), "TerminationPolicies")
    m.arg("capacity_rebalance", s.get("CapacityRebalance"), "CapacityRebalance")
    m.arg(
        "protect_from_scale_in",
        s.get("NewInstancesProtectedFromScaleIn"),
        "NewInstancesProtectedFromScaleIn",
    )
    m.arg("max_instance_lifetime", s.get("MaxInstanceLifetime"), "MaxInstanceLifetime")
    template = _dict(s.get("LaunchTemplate"))
    if template:
        m.block(
            Block(
                "launch_template",
                _items(
                    ("id", template.get("LaunchTemplateId")),
                    ("version", template.get("Version")),
                ),
            ),
            "LaunchTemplate",
        )
    for tag in _list(s.get("Tags")):
        if isinstance(tag, dict) and "Key" in tag:
            m.block(
                Block(
                    "tag",
                    [
                        ("key", tag["Key"]),
                        ("value", tag.get("Value", "")),
                        ("propagate_at_launch", bool(tag.get("PropagateAtLaunch", False))),
                    ],
                ),
                "Tags",
            )
    m.mapped.update({"AutoScalingGroupARN", "ServiceLinkedRoleARN"})
    return m


# Resource types Terraform accepts in launch template tag_specifications.
_LT_TAG_RESOURCE_TYPES = {
    "instance",
    "volume",
    "network-interface",
    "spot-instances-request",
    "elastic-gpu",
}


def _map_launch_template(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("LaunchTemplateId") or resource_id(spec)))
    m.arg("name", s.get("LaunchTemplateName"), "LaunchTemplateName")
    data = _dict(s.get("LaunchTemplateData"))
    m.mapped.add("LaunchTemplateData")
    m.arg("image_id", data.get("ImageId"))
    m.arg("instance_type", data.get("InstanceType"))
    m.arg("key_name", data.get("KeyName"))
    m.arg("vpc_security_group_ids", _list(data.get("SecurityGroupIds")))
    m.arg("security_group_names", _list(data.get("SecurityGroups")))
    m.arg("user_data", data.get("UserData"))
    m.arg("ebs_optimized", data.get("EbsOptimized"))
    profile = _dict(data.get("IamInstanceProfile"))
    if profile:
        key = "arn" if profile.get("Arn") else "name"
        m.block(Block("iam_instance_profile", [(key, profile.get("Arn") or profile.get("Name"))]))
    monitoring = _dict(data.get("Monitoring"))
    if "Enabled" in monitoring:
        m.block(Block("monitoring", [("enabled", monitoring["Enabled"])]))
    metadata = _dict(data.get("MetadataOptions"))
    if metadata:
        m.block(
            Block(
                "metadata_options",
                _items(
                    ("http_endpoint", metadata.get("HttpEndpoint")),
                    ("http_tokens", metadata.get("HttpTokens")),
                    ("http_put_response_hop_limit", metadata.get("HttpPutResponseHopLimit")),
                    ("http_protocol_ipv6", metadata.get("HttpProtocolIpv6")),
                    ("instance_metadata_tags", metadata.get("InstanceMetadataTags")),
                ),
            )
        )
    for interface in _list(data.get("NetworkInterfaces")):
        if isinstance(interface, dict):
            m.block(
                Block(
                    "network_interfaces",
                    _items(
                        ("device_index", interface.get("DeviceIndex")),
                        ("subnet_id", interface.get("SubnetId")),
                        ("security_groups", _list(interface.get("Groups"))),
                        ("associate_public_ip_address", interface.get("AssociatePublicIpAddress")),
                        ("delete_on_termination", interface.get("DeleteOnTermination")),
                    ),
                )
            )
    for mapping in _list(data.get("BlockDeviceMappings")):
        if not isinstance(mapping, dict):
            continue
        items = _items(("device_name", mapping.get("DeviceName")))
        ebs = _dict(mapping.get("Ebs"))
        if ebs:
            items.append(
                Block(
                    "ebs",
                    _items(
                        ("volume_size", ebs.get("VolumeSize")),
                        ("volume_type", ebs.get("VolumeType")),
                        ("iops", ebs.get("Iops")),
                        ("throughput", ebs.get("Throughput")),
                        ("encrypted", ebs.get("Encrypted")),
                        ("kms_key_id", ebs.get("KmsKeyId")),
                        ("delete_on_termination", ebs.get("DeleteOnTermination")),
                    ),
                )
            )
        m.block(Block("block_device_mappings", items))
    for tag_spec in _list(data.get("TagSpecifications")):
        # "launch-template" tags are the template's own tags (the tags argument).
        if isinstance(tag_spec, dict) and tag_spec.get("ResourceType") in _LT_TAG_RESOURCE_TYPES:
            m.block(
                Block(
                    "tag_specifications",
                    [
                        ("resource_type", tag_spec["ResourceType"]),
                        ("tags", _tags(tag_spec.get("Tags"))),
                    ],
                )
            )
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    m.mapped.add("LaunchTemplateId")
    return m


def _engine_version(engine: Any, version: Any) -> Any:
    """Redis/Valkey 6+ take ``major.minor`` in Terraform; other versions are kept as returned."""
    text = str(version or "")
    major = text.split(".")[0]
    if engine in ("redis", "valkey") and major.isdigit() and int(major) >= 6:
        return ".".join(text.split(".")[:2])
    return version


def _map_elasticache_replication_group(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    m = Mapping(import_id=str(s.get("ReplicationGroupId") or resource_id(spec)))
    cluster = _dict(s.get("CacheCluster"))
    engine = s.get("Engine") or cluster.get("Engine")
    m.arg("replication_group_id", s.get("ReplicationGroupId"), "ReplicationGroupId")
    m.arg("description", s.get("Description") or None, "Description")
    m.arg("node_type", s.get("CacheNodeType"), "CacheNodeType")
    m.arg("engine", engine, "Engine")
    m.arg("engine_version", _engine_version(engine, cluster.get("EngineVersion")), "CacheCluster")
    groups = [g for g in _list(s.get("NodeGroups")) if isinstance(g, dict)]
    endpoint = _dict(s.get("ConfigurationEndpoint")) or _dict(
        groups[0].get("PrimaryEndpoint") if groups else None
    )
    m.arg("port", endpoint.get("Port"), "NodeGroups", "ConfigurationEndpoint")
    if s.get("ClusterEnabled"):
        m.arg("num_node_groups", len(groups) or None, "ClusterEnabled")
        members = [_list(g.get("NodeGroupMembers")) for g in groups]
        m.arg("replicas_per_node_group", max(len(x) for x in members) - 1 if members else None)
    else:
        m.arg("num_cache_clusters", len(_list(s.get("MemberClusters"))) or None, "MemberClusters")
        m.mapped.add("ClusterEnabled")
    m.mapped.add("MemberClusters")
    m.arg(
        "parameter_group_name",
        _dict(cluster.get("CacheParameterGroup")).get("CacheParameterGroupName"),
    )
    m.arg("subnet_group_name", cluster.get("CacheSubnetGroupName"), "CacheSubnetGroup")
    groups_ids = [
        g.get("SecurityGroupId")
        for g in _list(cluster.get("SecurityGroups"))
        if isinstance(g, dict)
    ]
    m.arg("security_group_ids", [g for g in groups_ids if g])
    m.arg("maintenance_window", cluster.get("PreferredMaintenanceWindow"))
    failover = s.get("AutomaticFailover")
    m.arg(
        "automatic_failover_enabled",
        failover in ("enabled", "enabling") if failover else None,
        "AutomaticFailover",
    )
    multi_az = s.get("MultiAZ")
    m.arg("multi_az_enabled", multi_az == "enabled" if multi_az else None, "MultiAZ")
    m.arg("at_rest_encryption_enabled", s.get("AtRestEncryptionEnabled"), "AtRestEncryptionEnabled")
    m.arg(
        "transit_encryption_enabled",
        s.get("TransitEncryptionEnabled"),
        "TransitEncryptionEnabled",
    )
    m.arg("kms_key_id", s.get("KmsKeyId"), "KmsKeyId")
    m.arg("snapshot_retention_limit", s.get("SnapshotRetentionLimit"), "SnapshotRetentionLimit")
    m.arg("snapshot_window", s.get("SnapshotWindow"), "SnapshotWindow")
    if s.get("DataTiering") == "enabled":
        m.arg("data_tiering_enabled", True, "DataTiering")
    if s.get("AuthTokenEnabled"):
        # The AUTH token is never returned by the API.
        m.items.append(("# AUTH token enabled: set auth_token", None))
        m.ignore_changes.append("auth_token")
    m.mapped.add("AuthTokenEnabled")
    m.arg("tags", _tags(s.get("TagList")), "TagList")
    m.mapped.add("ARN")
    return m


def _attr_int(attributes: dict[str, Any], key: str) -> int | None:
    return _int(attributes.get(key)) if key in attributes else None


def _map_sqs_queue(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    attributes = _dict(s.get("Attributes"))
    m = Mapping(import_id=str(s.get("QueueUrl") or spec.arn))
    m.arg("name", resource_id(spec), "QueueUrl")
    m.mapped.add("Attributes")
    m.arg("fifo_queue", _bool(attributes.get("FifoQueue")) or None)
    m.arg("content_based_deduplication", _bool(attributes.get("ContentBasedDeduplication")))
    m.arg("deduplication_scope", attributes.get("DeduplicationScope"))
    m.arg("fifo_throughput_limit", attributes.get("FifoThroughputLimit"))
    m.arg("delay_seconds", _attr_int(attributes, "DelaySeconds"))
    m.arg("max_message_size", _attr_int(attributes, "MaximumMessageSize"))
    m.arg("message_retention_seconds", _attr_int(attributes, "MessageRetentionPeriod"))
    m.arg("receive_wait_time_seconds", _attr_int(attributes, "ReceiveMessageWaitTimeSeconds"))
    m.arg("visibility_timeout_seconds", _attr_int(attributes, "VisibilityTimeout"))
    m.arg("kms_master_key_id", attributes.get("KmsMasterKeyId"))
    m.arg(
        "kms_data_key_reuse_period_seconds",
        (
            _attr_int(attributes, "KmsDataKeyReusePeriodSeconds")
            if "KmsMasterKeyId" in attributes
            else None
        ),
    )
    m.arg("sqs_managed_sse_enabled", _bool(attributes.get("SqsManagedSseEnabled")))
    m.arg("policy", _json_doc(attributes.get("Policy")))
    m.arg("redrive_policy", _json_doc(attributes.get("RedrivePolicy")))
    m.arg("redrive_allow_policy", _json_doc(attributes.get("RedriveAllowPolicy")))
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    return m


def _map_sns_topic(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    attributes = _dict(s.get("Attributes"))
    m = Mapping(import_id=str(attributes.get("TopicArn") or spec.arn))
    m.arg("name", resource_id(spec), "Attributes")
    m.arg("display_name", attributes.get("DisplayName") or None)
    m.arg("policy", _json_doc(attributes.get("Policy")))
    m.arg("delivery_policy", _json_doc(attributes.get("DeliveryPolicy")))
    m.arg("kms_master_key_id", attributes.get("KmsMasterKeyId"))
    m.arg("fifo_topic", _bool(attributes.get("FifoTopic")) or None)
    m.arg("content_based_deduplication", _bool(attributes.get("ContentBasedDeduplication")))
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    return m


def _event_target(target: dict[str, Any], rule_ref: Raw, bus: str | None) -> list[Item]:
    items: list[Item] = [("rule", rule_ref)]
    items += _items(
        ("event_bus_name", bus),
        ("target_id", target.get("Id")),
        ("arn", target.get("Arn")),
        ("role_arn", target.get("RoleArn")),
        ("input", target.get("Input")),
        ("input_path", target.get("InputPath")),
    )
    transformer = _dict(target.get("InputTransformer"))
    if transformer:
        items.append(
            Block(
                "input_transformer",
                _items(
                    ("input_paths", _dict(transformer.get("InputPathsMap"))),
                    ("input_template", transformer.get("InputTemplate")),
                ),
            )
        )
    ecs = _dict(target.get("EcsParameters"))
    if ecs:
        ecs_items = _items(
            ("task_definition_arn", ecs.get("TaskDefinitionArn")),
            ("task_count", ecs.get("TaskCount")),
            ("launch_type", ecs.get("LaunchType")),
            ("platform_version", ecs.get("PlatformVersion")),
        )
        vpc = _dict(_dict(ecs.get("NetworkConfiguration")).get("awsvpcConfiguration"))
        if vpc:
            public = vpc.get("AssignPublicIp")
            ecs_items.append(
                Block(
                    "network_configuration",
                    _items(
                        ("subnets", _list(vpc.get("Subnets"))),
                        ("security_groups", _list(vpc.get("SecurityGroups"))),
                        ("assign_public_ip", public == "ENABLED" if public else None),
                    ),
                )
            )
        items.append(Block("ecs_target", ecs_items))
    retry = _dict(target.get("RetryPolicy"))
    if retry:
        items.append(
            Block(
                "retry_policy",
                _items(
                    ("maximum_event_age_in_seconds", retry.get("MaximumEventAgeInSeconds")),
                    ("maximum_retry_attempts", retry.get("MaximumRetryAttempts")),
                ),
            )
        )
    dead_letter = _dict(target.get("DeadLetterConfig"))
    if dead_letter.get("Arn"):
        items.append(Block("dead_letter_config", [("arn", dead_letter["Arn"])]))
    return items


def _map_cloudwatch_event_rule(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    bus = s.get("EventBusName")
    custom_bus = bus if bus and bus != "default" else None
    rule = str(s.get("Name") or resource_id(spec).split("/")[-1])
    prefix = f"{custom_bus}/" if custom_bus else ""
    m = Mapping(import_id=f"{prefix}{rule}")
    m.arg("name", rule, "Name")
    m.arg("event_bus_name", custom_bus, "EventBusName")
    m.arg("description", s.get("Description") or None, "Description")
    m.arg("schedule_expression", s.get("ScheduleExpression"), "ScheduleExpression")
    m.arg("event_pattern", _json_doc(s.get("EventPattern")), "EventPattern")
    m.arg("state", s.get("State"), "State")
    m.arg("role_arn", s.get("RoleArn"), "RoleArn")
    m.arg("tags", _tags(s.get("Tags")), "Tags")
    ref = Raw(f"aws_cloudwatch_event_rule.{name}.name")
    for target in _list(s.get("Targets")):
        if isinstance(target, dict) and target.get("Id"):
            m.companions.append(
                TfResource(
                    "aws_cloudwatch_event_target",
                    _companion_name(name, str(target["Id"])),
                    _event_target(target, ref, custom_bus),
                    f"{prefix}{rule}/{target['Id']}",
                )
            )
    m.mapped.update({"Arn", "Targets"})
    return m


def _map_scheduler_schedule(s: dict[str, Any], name: str, spec: ResourceSpec) -> Mapping:
    group = str(s.get("GroupName") or "default")
    m = Mapping(import_id=f"{group}/{s.get('Name') or resource_id(spec).split('/')[-1]}")
    m.arg("name", s.get("Name"), "Name")
    m.arg("group_name", group, "GroupName")
    m.arg("description", s.get("Description") or None, "Description")
    m.arg("schedule_expression", s.get("ScheduleExpression"), "ScheduleExpression")
    m.arg(
        "schedule_expression_timezone",
        s.get("ScheduleExpressionTimezone"),
        "ScheduleExpressionTimezone",
    )
    m.arg("start_date", s.get("StartDate"), "StartDate")
    m.arg("end_date", s.get("EndDate"), "EndDate")
    m.arg("state", s.get("State"), "State")
    m.arg("kms_key_arn", s.get("KmsKeyArn"), "KmsKeyArn")
    window = _dict(s.get("FlexibleTimeWindow"))
    if window:
        m.block(
            Block(
                "flexible_time_window",
                _items(
                    ("mode", window.get("Mode")),
                    ("maximum_window_in_minutes", window.get("MaximumWindowInMinutes")),
                ),
            ),
            "FlexibleTimeWindow",
        )
    target = _dict(s.get("Target"))
    if target:
        items = _items(
            ("arn", target.get("Arn")),
            ("role_arn", target.get("RoleArn")),
            ("input", target.get("Input")),
        )
        retry = _dict(target.get("RetryPolicy"))
        if retry:
            items.append(
                Block(
                    "retry_policy",
                    _items(
                        ("maximum_event_age_in_seconds", retry.get("MaximumEventAgeInSeconds")),
                        ("maximum_retry_attempts", retry.get("MaximumRetryAttempts")),
                    ),
                )
            )
        dead_letter = _dict(target.get("DeadLetterConfig"))
        if dead_letter.get("Arn"):
            items.append(Block("dead_letter_config", [("arn", dead_letter["Arn"])]))
        group_id = _dict(target.get("SqsParameters")).get("MessageGroupId")
        if group_id:
            items.append(Block("sqs_parameters", [("message_group_id", group_id)]))
        m.block(Block("target", items), "Target")
    m.mapped.add("Arn")
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
    "aws_subnet": _map_subnet,
    "aws_route_table": _map_route_table,
    "aws_internet_gateway": _map_internet_gateway,
    "aws_nat_gateway": _map_nat_gateway,
    "aws_vpc_endpoint": _map_vpc_endpoint,
    "aws_lb": _map_lb,
    "aws_lb_listener": _map_lb_listener,
    "aws_lb_target_group": _map_lb_target_group,
    "aws_cloudfront_distribution": _map_cloudfront_distribution,
    "aws_route53_zone": _map_route53_zone,
    "aws_acm_certificate": _map_acm_certificate,
    "aws_wafv2_web_acl": _map_wafv2_web_acl,
    "aws_ecs_cluster": _map_ecs_cluster,
    "aws_ecs_service": _map_ecs_service,
    "aws_ecs_task_definition": _map_ecs_task_definition,
    "aws_ecr_repository": _map_ecr_repository,
    "aws_autoscaling_group": _map_autoscaling_group,
    "aws_launch_template": _map_launch_template,
    "aws_elasticache_replication_group": _map_elasticache_replication_group,
    "aws_sqs_queue": _map_sqs_queue,
    "aws_sns_topic": _map_sns_topic,
    "aws_cloudwatch_event_rule": _map_cloudwatch_event_rule,
    "aws_scheduler_schedule": _map_scheduler_schedule,
}


# ============================================================================
# Project layout: modules/<module>/ and envs/<env>/ (Requirement 16)
# ============================================================================

# Module of every Supported_Resource_Type (companions follow their primary resource).
MODULES: dict[str, tuple[str, ...]] = {
    "iam": ("aws_iam_role",),
    "observability": ("aws_cloudwatch_log_group",),
    "network": (
        "aws_vpc",
        "aws_subnet",
        "aws_route_table",
        "aws_internet_gateway",
        "aws_nat_gateway",
        "aws_vpc_endpoint",
        "aws_security_group",
    ),
    "edge": (
        "aws_route53_zone",
        "aws_acm_certificate",
        "aws_wafv2_web_acl",
        "aws_cloudfront_distribution",
        "aws_lb",
        "aws_lb_target_group",
        "aws_lb_listener",
    ),
    "data": (
        "aws_s3_bucket",
        "aws_dynamodb_table",
        "aws_db_instance",
        "aws_elasticache_replication_group",
        "aws_sqs_queue",
        "aws_sns_topic",
    ),
    "compute": (
        "aws_ecr_repository",
        "aws_launch_template",
        "aws_autoscaling_group",
        "aws_instance",
        "aws_ecs_cluster",
        "aws_ecs_task_definition",
        "aws_ecs_service",
        "aws_lambda_function",
        "aws_sfn_state_machine",
        "aws_cloudwatch_event_rule",
        "aws_scheduler_schedule",
    ),
}
# Dependency order: later modules may read the outputs of earlier ones.
MODULE_ORDER = tuple(MODULES)
FALLBACK_MODULE = "compute"
MODULE_SUMMARIES = {
    "iam": "IAM roles with their attached and inline policies",
    "observability": "CloudWatch log groups",
    "network": (
        "VPCs, subnets, route tables, internet and NAT gateways, VPC endpoints, "
        "security groups and their rules"
    ),
    "edge": "Route 53 zones, ACM certificates, WAF web ACLs, CloudFront and load balancers",
    "data": "S3 buckets, DynamoDB tables, RDS instances, ElastiCache, SQS queues and SNS topics",
    "compute": (
        "ECR, launch templates, Auto Scaling groups, EC2 instances, ECS, Lambda, "
        "Step Functions, EventBridge rules and schedules"
    ),
}
_TYPE_ORDER = {t: i for i, t in enumerate(t for types in MODULES.values() for t in types)}
_MODULE_OF = {t: module for module, types in MODULES.items() for t in types}

# Attribute other resources reference (module outputs expose it, keyed by resource name).
REFERENCE_ATTRIBUTES = {
    "aws_iam_role": "arn",
    "aws_cloudwatch_log_group": "arn",
    "aws_vpc": "id",
    "aws_subnet": "id",
    "aws_route_table": "id",
    "aws_internet_gateway": "id",
    "aws_nat_gateway": "id",
    "aws_vpc_endpoint": "id",
    "aws_security_group": "id",
    "aws_route53_zone": "zone_id",
    "aws_acm_certificate": "arn",
    "aws_wafv2_web_acl": "arn",
    "aws_cloudfront_distribution": "id",
    "aws_lb": "arn",
    "aws_lb_target_group": "arn",
    "aws_lb_listener": "arn",
    "aws_s3_bucket": "id",
    "aws_dynamodb_table": "arn",
    "aws_db_instance": "arn",
    "aws_elasticache_replication_group": "arn",
    "aws_sqs_queue": "arn",
    "aws_sns_topic": "arn",
    "aws_ecr_repository": "arn",
    "aws_launch_template": "id",
    "aws_autoscaling_group": "arn",
    "aws_instance": "id",
    "aws_ecs_cluster": "arn",
    "aws_ecs_task_definition": "arn",
    "aws_ecs_service": "id",
    "aws_lambda_function": "arn",
    "aws_sfn_state_machine": "arn",
    "aws_cloudwatch_event_rule": "arn",
    "aws_scheduler_schedule": "arn",
}
# Only distinctive values become references: ARNs and ids with these prefixes.
_ID_PREFIXES = {
    "aws_vpc": "vpc-",
    "aws_subnet": "subnet-",
    "aws_route_table": "rtb-",
    "aws_internet_gateway": "igw-",
    "aws_nat_gateway": "nat-",
    "aws_vpc_endpoint": "vpce-",
    "aws_security_group": "sg-",
    "aws_launch_template": "lt-",
    "aws_instance": "i-",
}
# Auto Scaling group ARNs built by discovery hold a wildcard instead of the group UUID.
_NOT_REFERENCED = {"aws_autoscaling_group"}

# Types whose Terraform resource has no `tags` argument (provider default_tags skip them).
_UNTAGGED_TYPES = {
    "aws_autoscaling_group",  # tag {} blocks
    "aws_scheduler_schedule",
    "aws_route_table_association",
    "aws_iam_role_policy_attachment",
    "aws_iam_role_policy",
    "aws_s3_bucket_versioning",
    "aws_s3_bucket_policy",
    "aws_s3_bucket_server_side_encryption_configuration",
    "aws_route53_record",
    "aws_cloudwatch_event_target",
}

# Spec fields naming a resource when it has no Name tag.
_NAME_FIELDS = {
    "aws_security_group": "GroupName",
    "aws_lb": "LoadBalancerName",
    "aws_lb_target_group": "TargetGroupName",
    "aws_route53_zone": "Name",
    "aws_acm_certificate": "DomainName",
    "aws_wafv2_web_acl": "Name",
    "aws_ecs_cluster": "clusterName",
    "aws_ecs_service": "serviceName",
    "aws_launch_template": "LaunchTemplateName",
    "aws_cloudwatch_event_rule": "Name",
    "aws_scheduler_schedule": "Name",
}
_PROJECT_TAG_KEYS = {"project", "service", "application", "app"}
_ENVIRONMENT_TAG_KEYS = {"environment", "env"}
DEFAULT_ENVIRONMENT = "default"
TERRAFORM_VERSION = ">= 1.5.0"  # import blocks
_REDACTED_COMMENT = "# REDACTED: set manually"


def module_for(tf_type: str) -> str:
    return _MODULE_OF.get(tf_type, FALLBACK_MODULE)


def output_name(tf_type: str) -> str:
    """Module output (and input variable) holding the references of one type."""
    attribute = REFERENCE_ATTRIBUTES.get(tf_type, "id")
    return f"{tf_type.removeprefix('aws_')}_{'id' if attribute == 'zone_id' else attribute}s"


def _plural(tf_type: str) -> str:
    return tf_type.removeprefix("aws_").replace("_", " ") + "s"


def provider_alias(region: str) -> str:
    return region.replace("-", "_")


def _label(spec: ResourceSpec, tf_type: str) -> str:
    """Human name: Name tag, else a type-specific field, else the resource id."""
    s = spec.specifications or {}
    name: Any = _spec_tags(s).get("Name")
    if not name and tf_type == "aws_lb_listener" and s.get("Protocol") and s.get("Port"):
        name = f"{s['Protocol']}_{s['Port']}"
    if not name and tf_type == "aws_cloudfront_distribution":
        aliases = _quantity_items(_dict(s.get("DistributionConfig")).get("Aliases"))
        name = aliases[0] if aliases else None
    if not name and tf_type in _NAME_FIELDS:
        name = s.get(_NAME_FIELDS[tf_type])
    return name if isinstance(name, str) and name else resource_id(spec)


def _strip_prefixes(name: str, prefixes: tuple[str, ...]) -> str:
    changed = True
    while changed:
        changed = False
        for prefix in prefixes:
            if name == prefix:
                return ""
            if name.startswith(f"{prefix}_"):
                name, changed = name[len(prefix) + 1 :], True
                break
    return name


def _most_common(values: list[str]) -> str | None:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[0][0] if ranked else None


@dataclass
class _Entry:
    """One spec in the project: its module, Terraform resources and mapped keys."""

    spec: ResourceSpec
    module: str
    resources: list[TfResource]
    mapping: Mapping


@dataclass
class _Project:
    environment: str
    region: str
    aliases: list[str]  # regions of the aliased providers
    entries: list[_Entry]
    inputs: dict[str, dict[str, str]]  # module -> {variable: source module}
    outputs: dict[str, dict[str, dict[Any, Any]]]  # module -> {output: {name: expression}}
    module_aliases: dict[str, list[str]]  # module -> aliases its resources use
    default_tags: dict[str, str]
    output_types: dict[str, str]  # output name -> resource type

    def modules(self) -> list[str]:
        present = {entry.module for entry in self.entries}
        return [m for m in MODULE_ORDER if m in present]

    def describe(self, output: str, where: str) -> str:
        tf_type = self.output_types[output]
        attribute = REFERENCE_ATTRIBUTES.get(tf_type, "id")
        label = attribute.upper() if attribute in ("id", "arn") else attribute.replace("_", " ")
        return f"{label}s of the {_plural(tf_type)} {where}, keyed by resource name"


def _arrange(items: list[Item]) -> list[Item]:
    """Meta-arguments, arguments, blocks, tags, lifecycle (blank line between groups);
    a ``# REDACTED`` comment stays above its argument, other notes open the arguments."""
    meta: list[Item] = []
    notes: list[Item] = []
    arguments: list[Item] = []
    blocks: list[Item] = []
    tags: list[Item] = []
    lifecycle: list[Item] = []
    pending: list[Item] = []
    for item in items:
        if isinstance(item, Block):
            group = lifecycle if item.name == "lifecycle" else blocks
        else:
            name = item[0]
            if name == _REDACTED_COMMENT:
                pending.append(item)
                continue
            if name.startswith("#"):
                notes.append(item)
                continue
            group = meta if name == "provider" else tags if name == "tags" else arguments
        group.extend(pending)
        pending.clear()
        group.append(item)
    result: list[Item] = []
    for group in (meta, notes + arguments, blocks, tags, lifecycle):
        if group:
            if result:
                result.append(BLANK)
            result.extend(group)
    return result


def _render_resource(resource: TfResource) -> list[str]:
    lines = [f'resource "{resource.tf_type}" "{resource.name}" {{']
    lines.extend(render_items(_arrange(resource.items), 1))
    lines.append("}")
    return lines


def _file(*blocks: list[str], header: str = "") -> str:
    parts = ["\n".join(block) for block in blocks if block]
    text = "\n\n".join(parts)
    return (f"{header}\n\n" if header else "") + text + "\n"


def _hcl(items: list[Item]) -> list[str]:
    return render_items(items, 0)


def _comment(text: str) -> list[str]:
    return [f"# {line}".rstrip() for line in text.splitlines()]


# ============================================================================
# Generator
# ============================================================================


class IaCGenerator:
    """Terraform generator for collected ResourceSpecs."""

    def __init__(
        self, output_dir: str | Path | None = None, project_tags: dict[str, str] | None = None
    ) -> None:
        self.output_dir = Path(output_dir).resolve() if output_dir else None
        # Tags of the collection scope (manifest.json); their values are name prefixes.
        self.project_tags = dict(project_tags or {})

    # ------------------------------------------------------------------
    # Names and types
    # ------------------------------------------------------------------

    def _tf_resource_type(self, resource_type: str) -> str:
        known = canonical_type(resource_type)
        if known:
            return known
        normalized = resource_type.lower().strip()
        return normalized if normalized.startswith("aws_") else f"aws_{normalized}"

    def _prefixes(self, specs: list[ResourceSpec]) -> tuple[str, ...]:
        """Project and environment names stripped from resource names (longest first)."""
        values = set(self.project_tags.values())
        keys = _PROJECT_TAG_KEYS | _ENVIRONMENT_TAG_KEYS
        for spec in specs:
            for key, value in _spec_tags(spec.specifications or {}).items():
                if key.lower() in keys:
                    values.add(value)
        prefixes = {snake(v) for v in values} - {""}
        return tuple(sorted(prefixes, key=lambda p: (-len(p), p)))

    def environment(self, specs: list[ResourceSpec]) -> str:
        """Environment directory name: the most common `environment` tag value."""
        values = [v for k, v in self.project_tags.items() if k.lower() in _ENVIRONMENT_TAG_KEYS]
        if not values:
            values = [
                v
                for spec in specs
                for k, v in _spec_tags(spec.specifications or {}).items()
                if k.lower() in _ENVIRONMENT_TAG_KEYS
            ]
        value = _most_common(values) or DEFAULT_ENVIRONMENT
        return re.sub(r"[^a-z0-9_-]+", "-", value.lower()).strip("-") or DEFAULT_ENVIRONMENT

    def assign_names(self, specs: list[ResourceSpec]) -> dict[str, str]:
        """snake_case Terraform names, project prefix stripped, unique per type (by ARN)."""
        prefixes = self._prefixes(specs)
        candidates = []
        for spec in specs:
            tf_type = self._tf_resource_type(spec.resource_type)
            base = _strip_prefixes(snake(_label(spec, tf_type)), prefixes) or "main"
            if not re.match(r"[a-z_]", base):
                base = f"r_{base}"
            candidates.append((tf_type, base, spec.arn))
        used: set[tuple[str, str]] = set()
        names: dict[str, str] = {}
        for tf_type, base, arn in sorted(candidates):
            candidate, counter = base, 2
            while (tf_type, candidate) in used:
                candidate, counter = f"{base}_{counter}", counter + 1
            used.add((tf_type, candidate))
            names[arn] = candidate
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
                items.append((_REDACTED_COMMENT, None))
            items.append(item)
        if ignore:
            items.append(Block("lifecycle", [("ignore_changes", [Raw(i) for i in ignore])]))
        main = TfResource(tf_type, name, items, mapping.import_id or resource_id(spec))
        return [main, *mapping.companions], mapping

    @staticmethod
    def _comments(spec: ResourceSpec, main: TfResource, mapping: Mapping) -> list[str]:
        keys = sorted(spec.specifications or {})
        mapped = [k for k in keys if k in mapping.mapped]
        unmapped = [k for k in keys if k not in mapping.mapped]
        lines = [
            f"# Resource: {main.tf_type}.{main.name}",
            f"# Source specification: {spec_relpath(spec)}",
            f"# ARN: {spec.arn}",
            f"# Region: {spec.region or GLOBAL_REGION}",
        ]
        if mapped:
            lines.append(f"# mapped: {', '.join(mapped)}")
        lines.extend(f"# unmapped: {key}" for key in unmapped)
        return lines

    def _render_entry(self, entry: _Entry) -> list[str]:
        lines = self._comments(entry.spec, entry.resources[0], entry.mapping)
        for index, resource in enumerate(entry.resources):
            if index:
                lines.append("")
            lines.extend(_render_resource(resource))
        return lines

    def generate_resource_block(self, spec: ResourceSpec, name: str | None = None) -> str:
        """Terraform for one spec (main resource + companions) with traceability comments."""
        name = name or self.assign_names([spec])[spec.arn]
        resources, mapping = self._resources(spec, name)
        module = module_for(resources[0].tf_type)
        return "\n".join(self._render_entry(_Entry(spec, module, resources, mapping))) + "\n"

    # ------------------------------------------------------------------
    # Project model
    # ------------------------------------------------------------------

    @staticmethod
    def _provider_region(spec: ResourceSpec, tf_type: str) -> str | None:
        """Region of the provider managing a resource; None = any (IAM, Route 53)."""
        if spec.region and spec.region != GLOBAL_REGION:
            return spec.region
        if tf_type in ("aws_s3_bucket", "aws_cloudfront_distribution", "aws_wafv2_web_acl"):
            return DEFAULT_REGION  # S3 buckets keep the us-east-1 provider of earlier releases
        return None

    def _project(self, specs: list[ResourceSpec]) -> _Project:
        names = self.assign_names(specs)
        regional = [s.region for s in specs if s.region and s.region != GLOBAL_REGION]
        region = _most_common(regional) or DEFAULT_REGION

        entries: list[_Entry] = []
        for spec in specs:
            resources, mapping = self._resources(spec, names[spec.arn])
            entries.append(_Entry(spec, module_for(resources[0].tf_type), resources, mapping))
        entries.sort(
            key=lambda e: (
                MODULE_ORDER.index(e.module),
                _TYPE_ORDER.get(e.resources[0].tf_type, len(_TYPE_ORDER)),
                e.resources[0].tf_type,
                e.resources[0].name,
            )
        )
        self._dedupe_companions(entries)

        # Distinctive values of managed resources -> (module, type, name, attribute).
        index: dict[str, tuple[str, str, str, str]] = {}
        for entry in entries:
            main = entry.resources[0]
            attribute = REFERENCE_ATTRIBUTES.get(main.tf_type)
            if attribute is None or main.tf_type in _NOT_REFERENCED:
                continue
            value = entry.spec.arn if attribute == "arn" else resource_id(entry.spec)
            prefix = _ID_PREFIXES.get(main.tf_type, "arn:")
            if value.startswith(prefix):
                index.setdefault(value, (entry.module, main.tf_type, main.name, attribute))

        inputs: dict[str, dict[str, str]] = {}
        for entry in entries:
            needed = inputs.setdefault(entry.module, {})
            for position, resource in enumerate(entry.resources):
                own = (resource.tf_type, resource.name) if position == 0 else None
                resource.items = _resolve(resource.items, index, entry.module, own, needed)

        aliases: set[str] = set()
        module_aliases: dict[str, set[str]] = {}
        for entry in entries:
            provider_region = self._provider_region(entry.spec, entry.resources[0].tf_type)
            if provider_region is None or provider_region == region:
                continue
            alias = provider_alias(provider_region)
            aliases.add(provider_region)
            module_aliases.setdefault(entry.module, set()).add(alias)
            for resource in entry.resources:
                resource.items.insert(0, ("provider", Raw(f"aws.{alias}")))

        default_tags = _common_tags([r for e in entries for r in e.resources])

        outputs: dict[str, dict[str, dict[Any, Any]]] = {}
        output_types: dict[str, str] = {}
        for entry in entries:
            main = entry.resources[0]
            attribute = REFERENCE_ATTRIBUTES.get(main.tf_type, "id")
            output_types[output_name(main.tf_type)] = main.tf_type
            values = outputs.setdefault(entry.module, {}).setdefault(output_name(main.tf_type), {})
            values[Raw(main.name)] = Raw(f"{main.tf_type}.{main.name}.{attribute}")

        return _Project(
            environment=self.environment(specs),
            region=region,
            aliases=sorted(aliases),
            entries=entries,
            inputs={m: v for m, v in inputs.items() if v},
            outputs=outputs,
            module_aliases={m: sorted(a) for m, a in module_aliases.items()},
            default_tags=default_tags,
            output_types=output_types,
        )

    @staticmethod
    def _dedupe_companions(entries: list[_Entry]) -> None:
        used = {(e.resources[0].tf_type, e.resources[0].name) for e in entries}
        for entry in entries:
            for resource in entry.resources[1:]:
                base, counter = resource.name, 2
                while (resource.tf_type, resource.name) in used:
                    resource.name, counter = f"{base}_{counter}", counter + 1
                used.add((resource.tf_type, resource.name))

    # ------------------------------------------------------------------
    # Files
    # ------------------------------------------------------------------

    @staticmethod
    def _versions(aliases: list[str]) -> list[str]:
        provider: dict[Any, Any] = {
            Raw("source"): "hashicorp/aws",
            Raw("version"): AWS_PROVIDER_VERSION,
        }
        if aliases:
            provider[Raw("configuration_aliases")] = [Raw(f"aws.{a}") for a in aliases]
        return _hcl(
            [
                Block(
                    "terraform",
                    [
                        ("required_version", TERRAFORM_VERSION),
                        BLANK,
                        Block("required_providers", [("aws", provider)]),
                    ],
                )
            ]
        )

    def _module_files(self, project: _Project, module: str) -> dict[str, str]:
        entries = [e for e in project.entries if e.module == module]
        header = "\n".join(
            [
                f"# Module {module}",
                f"# {MODULE_SUMMARIES.get(module, 'Other resources')}.",
                "# Generated by AWS Resource Inventory from the collected specifications;",
                "# every resource names its source specification file.",
            ]
        )
        main = _file(*(self._render_entry(e) for e in entries), header=header)

        variables = []
        for variable, source in sorted(project.inputs.get(module, {}).items()):
            description = project.describe(variable, f"managed by the {source} module")
            variables.append(
                _hcl(
                    [
                        Block(
                            f'variable "{variable}"',
                            [("description", description), ("type", Raw("map(string)"))],
                        )
                    ]
                )
            )
        outputs = []
        for name, values in sorted(project.outputs.get(module, {}).items()):
            description = project.describe(name, "in this module")
            outputs.append(
                _hcl([Block(f'output "{name}"', [("description", description), ("value", values)])])
            )
        return {
            f"modules/{module}/main.tf": main,
            f"modules/{module}/variables.tf": (
                _file(*variables) if variables else "# This module has no input variables.\n"
            ),
            f"modules/{module}/outputs.tf": _file(*outputs),
            f"modules/{module}/versions.tf": _file(
                self._versions(project.module_aliases.get(module, []))
            ),
            f"modules/{module}/README.md": self._module_readme(project, module, entries),
        }

    def _module_readme(self, project: _Project, module: str, entries: list[_Entry]) -> str:
        lines = [
            f"# Module `{module}`",
            "",
            f"{MODULE_SUMMARIES.get(module, 'Other resources')}, generated by AWS Resource "
            "Inventory from the collected specifications. Values are the collected ones; "
            "references to resources of other modules are input variables.",
            "",
            "## Resources",
            "",
            "| Address | Source specification | ARN |",
            "|---|---|---|",
        ]
        for entry in entries:
            for resource in entry.resources:
                lines.append(
                    f"| `{resource.tf_type}.{resource.name}` | `{spec_relpath(entry.spec)}` "
                    f"| `{entry.spec.arn}` |"
                )
        inputs = project.inputs.get(module, {})
        lines += ["", "## Inputs", ""]
        if inputs:
            lines += ["| Name | Type | From module |", "|---|---|---|"]
            lines += [f"| `{n}` | `map(string)` | `{s}` |" for n, s in sorted(inputs.items())]
        else:
            lines.append("None.")
        lines += ["", "## Outputs", "", "| Name | Keys |", "|---|---|"]
        for name, values in sorted(project.outputs.get(module, {}).items()):
            keys = ", ".join(f"`{k}`" for k in sorted(str(k) for k in values))
            lines.append(f"| `{name}` | {keys} |")
        usage = [f'module "{module}" {{', f'  source = "../../modules/{module}"']
        if inputs:
            usage.append("")
            width = max(len(n) for n in inputs)
            usage += [f"  {n.ljust(width)} = module.{s}.{n}" for n, s in sorted(inputs.items())]
        usage.append("}")
        lines += ["", "## Usage", "", "```hcl", *usage, "```", ""]
        return "\n".join(lines)

    def _env_files(self, project: _Project) -> dict[str, str]:
        env = project.environment
        modules = project.modules()
        module_blocks = []
        for module in modules:
            items: list[Item] = [("source", f"../../modules/{module}")]
            aliases = project.module_aliases.get(module, [])
            if aliases:
                providers: dict[Any, Any] = {Raw("aws"): Raw("aws")}
                providers.update({Raw(f"aws.{a}"): Raw(f"aws.{a}") for a in aliases})
                items += [BLANK, ("providers", providers)]
            inputs = project.inputs.get(module, {})
            if inputs:
                items.append(BLANK)
                items += [(n, Raw(f"module.{s}.{n}")) for n, s in sorted(inputs.items())]
            module_blocks.append(_hcl([Block(f'module "{module}"', items)]))

        default_tags_block = Block("default_tags", [("tags", Raw("var.default_tags"))])
        providers_blocks = [
            _hcl([Block('provider "aws"', [("region", project.region), BLANK, default_tags_block])])
        ]
        for region in project.aliases:
            providers_blocks.append(
                _hcl(
                    [
                        Block(
                            'provider "aws"',
                            [
                                ("alias", provider_alias(region)),
                                ("region", region),
                                BLANK,
                                default_tags_block,
                            ],
                        )
                    ]
                )
            )

        outputs = []
        for module in modules:
            for name in sorted(project.outputs.get(module, {})):
                description = project.describe(name, f"of module {module}")
                outputs.append(
                    _hcl(
                        [
                            Block(
                                f'output "{name}"',
                                [
                                    ("description", description),
                                    ("value", Raw(f"module.{module}.{name}")),
                                ],
                            )
                        ]
                    )
                )

        imports = []
        for entry in project.entries:
            for resource in entry.resources:
                address = f"module.{entry.module}.{resource.tf_type}.{resource.name}"
                imports.append(
                    _comment(f"{spec_relpath(entry.spec)}")
                    + _hcl([Block("import", [("to", Raw(address)), ("id", resource.import_id)])])
                )

        backend_note = "\n".join(
            [
                "# Remote state in S3; bucket, key and region are given at init time:",
                "#   terraform init \\",
                '#     -backend-config="bucket=<state bucket>" \\',
                f'#     -backend-config="key={env}/terraform.tfstate" \\',
                f'#     -backend-config="region={project.region}" \\',
                '#     -backend-config="use_lockfile=true"   # Terraform >= 1.10',
                "# To try the configuration with local state, add backend_override.tf:",
                '#   terraform { backend "local" {} }',
            ]
        )
        variables = _hcl(
            [
                Block(
                    'variable "default_tags"',
                    [
                        (
                            "description",
                            "Tags every taggable resource of this environment carries "
                            "(provider default_tags)",
                        ),
                        ("type", Raw("map(string)")),
                        ("default", {}),
                    ],
                )
            ]
        )
        tfvars_note = "\n".join(
            [
                "# Tags common to every taggable resource collected for this environment;",
                "# they are left out of the resource blocks and applied by default_tags.",
            ]
        )
        return {
            f"envs/{env}/main.tf": _file(
                *module_blocks,
                header=f"# Environment {env}: one block per module (generated by "
                "AWS Resource Inventory).",
            ),
            f"envs/{env}/providers.tf": _file(*providers_blocks),
            f"envs/{env}/backend.tf": _file(
                _hcl([Block("terraform", [Block('backend "s3"', [("encrypt", True)])])]),
                header=backend_note,
            ),
            f"envs/{env}/versions.tf": _file(self._versions([])),
            f"envs/{env}/variables.tf": _file(variables),
            f"envs/{env}/terraform.tfvars": _file(
                _hcl([("default_tags", project.default_tags)]), header=tfvars_note
            ),
            f"envs/{env}/outputs.tf": _file(*outputs),
            f"envs/{env}/imports.tf": _file(
                *imports,
                header="\n".join(
                    [
                        "# One import block per generated resource (Terraform >= 1.5):",
                        "# `terraform plan` lists them, `terraform apply` records them in state",
                        "# without changing the resources when the plan has no other changes.",
                    ]
                ),
            ),
            f"envs/{env}/verify_state.sh": self.generate_verification_script([]),
        }

    def _readme(self, project: _Project) -> str:
        env = project.environment
        modules = "\n".join(
            f"| `modules/{m}/` | {MODULE_SUMMARIES.get(m, '')} |" for m in project.modules()
        )
        return f"""# Terraform

Generated by AWS Resource Inventory from the collected specifications (`aws-inventory
generate-iac`). Every resource block names its source specification file and ARN.

| Directory | Contents |
|---|---|
{modules}
| `envs/{env}/` | Root configuration: modules, providers, S3 backend, `imports.tf`, `verify_state.sh` |

Each module has `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf` and a `README.md`.
References between resources use Terraform expressions; a resource of another module is
reached through that module's outputs, wired in `envs/{env}/main.tf`.

## Import the existing resources

```bash
cd envs/{env}
terraform init -backend-config="bucket=<state bucket>" \\
  -backend-config="key={env}/terraform.tfstate" -backend-config="region={project.region}"
terraform plan       # expected: N to import, 0 to add, 0 to change, 0 to destroy
terraform apply      # records the imports in state; nothing else changes
./verify_state.sh    # exit 0 = configuration matches AWS
```

Values the collector could not read (redacted secrets, Lambda code, the RDS master
password) are marked `# REDACTED: set manually` or listed in `lifecycle.ignore_changes`.
"""

    def build_files(self, specs: list[ResourceSpec]) -> dict[str, str]:
        """{relative path: content} of the Terraform project (Requirements 7.2, 16.1)."""
        project = self._project(specs)
        files: dict[str, str] = {"README.md": self._readme(project)}
        for module in project.modules():
            files.update(self._module_files(project, module))
        files.update(self._env_files(project))
        return dict(sorted(files.items()))

    def generate_terraform(
        self, specs: list[ResourceSpec], target_dir: str | Path | None = None
    ) -> dict[str, str]:
        """Write the Terraform project and return {relative path: content} of every file:
        README.md, modules/<module>/*, envs/<env>/* (including imports.tf and verify_state.sh).
        """
        dest = Path(target_dir).resolve() if target_dir else (self.output_dir or Path.cwd())
        dest.mkdir(parents=True, exist_ok=True)
        files = self.build_files(specs)
        for rel_path, content in files.items():
            path = dest / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            if rel_path.endswith(".sh"):
                path.chmod(0o755)
        return files

    def generate_imports(self, specs: list[ResourceSpec]) -> str:
        """imports.tf: one `import` block per generated resource (Requirement 7.4)."""
        project = self._project(specs)
        return self._env_files(project)[f"envs/{project.environment}/imports.tf"]

    def generate_verification_script(self, specs: list[ResourceSpec]) -> str:
        """verify_state.sh for envs/<env> (Requirements 7.5, 7.6)."""
        return """#!/usr/bin/env bash
# Verify that the generated Terraform matches the actual AWS resources (Requirements 7.5, 7.6).
# Success: the plan has no changes, or only imports whose configuration already matches.
# Exit codes: 0 = no changes, 2 = changes detected, 1 = error.
set -uo pipefail
cd "$(dirname "$0")"

if [ ! -d ".terraform" ]; then
  terraform init -input=false || exit 1
fi

terraform plan -detailed-exitcode -no-color -input=false -out=verify.tfplan > plan_output.txt 2>&1
PLAN_EXIT=$?
cat plan_output.txt

case $PLAN_EXIT in
  0) echo "SUCCESS: zero changes - Terraform configuration matches AWS."; exit 0 ;;
  2)
    if terraform show -json verify.tfplan | python3 -c 'import json, sys
changes = json.load(sys.stdin).get("resource_changes", [])
sys.exit(0 if all(c["change"]["actions"] == ["no-op"] for c in changes) else 1)'; then
      echo "SUCCESS: zero changes - only imports pending (terraform apply records them)."
      exit 0
    fi
    echo "CHANGES DETECTED: review plan_output.txt."; exit 2 ;;
  *) echo "ERROR: terraform plan failed."; exit 1 ;;
esac
"""

    def verify_terraform_plan(self, tf_dir: str | Path) -> tuple[bool, str]:
        """Run `terraform plan -detailed-exitcode` (Req 7.5): exit code 0 is success; exit
        code 2 is success only when every resource change of the saved plan is a no-op
        (imports whose configuration matches AWS); anything else is an error."""
        cwd = Path(tf_dir)
        try:
            result = subprocess.run(  # noqa: S603 - fixed terraform command
                [
                    "terraform",
                    "plan",
                    "-detailed-exitcode",
                    "-no-color",
                    "-input=false",
                    "-out=verify.tfplan",
                ],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return False, "Error: terraform executable not found on PATH."
        output = f"{result.stdout or ''}\n{result.stderr or ''}".strip()
        if result.returncode == 0:
            return True, "Zero changes: Terraform state matches actual AWS resources."
        if result.returncode != 2:
            return (
                False,
                f"Error: terraform plan failed with exit code {result.returncode}:\n{output}",
            )
        shown = subprocess.run(  # noqa: S603 - fixed terraform command
            ["terraform", "show", "-json", "verify.tfplan"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            changes = json.loads(shown.stdout or "{}").get("resource_changes", [])
        except json.JSONDecodeError:
            changes = None
        if isinstance(changes, list):
            changed = [
                str(c.get("address"))
                for c in changes
                if _dict(c.get("change")).get("actions") != ["no-op"]
            ]
            if not changed:
                pending = sum(1 for c in changes if _dict(c.get("change")).get("importing"))
                return True, f"Zero changes: {pending} imports pending, configuration matches AWS."
            return False, "Changes detected in terraform plan:\n" + "\n".join(changed) + (
                f"\n{output}"
            )
        return False, f"Changes detected in terraform plan:\n{output}"


def _resolve(
    items: list[Item],
    index: dict[str, tuple[str, str, str, str]],
    module: str,
    own: tuple[str, str] | None,
    needed: dict[str, str],
) -> list[Item]:
    """Replace values equal to a managed resource's id/ARN by a reference (Req 16.2):
    ``<type>.<name>.<attribute>`` in the same module, ``var.<output>["<name>"]`` otherwise.
    Map values (tags, environment variables) and JSON documents stay literal."""

    def value(v: Any) -> Any:
        if isinstance(v, (Raw, Heredoc)):
            return v
        if isinstance(v, str):
            target = index.get(v)
            if target is None or (target[1], target[2]) == own:
                return v
            source, tf_type, name, attribute = target
            if source == module:
                return Raw(f"{tf_type}.{name}.{attribute}")
            needed[output_name(tf_type)] = source
            return Raw(f'var.{output_name(tf_type)}["{name}"]')
        if isinstance(v, list):
            return [value(x) for x in v]
        return v

    resolved: list[Item] = []
    for item in items:
        if isinstance(item, Block):
            resolved.append(Block(item.name, _resolve(item.items, index, module, own, needed)))
        elif item[0].startswith("#") or not item[0]:
            resolved.append(item)
        else:
            resolved.append((item[0], value(item[1])))
    return resolved


def _common_tags(resources: list[TfResource]) -> dict[str, str]:
    """Tags every taggable resource carries; removed from the resources (provider
    default_tags apply them). Any taggable resource without them empties the set."""
    taggable = [r for r in resources if r.tf_type not in _UNTAGGED_TYPES]
    common: dict[str, str] | None = None
    for resource in taggable:
        tags: dict[str, str] = {}
        for item in resource.items:
            if not isinstance(item, Block) and item[0] == "tags" and isinstance(item[1], dict):
                tags = item[1]
        common = tags if common is None else {k: v for k, v in common.items() if tags.get(k) == v}
    if not common:
        return {}
    for resource in taggable:
        kept: list[Item] = []
        for item in resource.items:
            if not isinstance(item, Block) and item[0] == "tags" and isinstance(item[1], dict):
                rest = {k: v for k, v in item[1].items() if k not in common}
                if rest:
                    kept.append(("tags", rest))
                continue
            kept.append(item)
        resource.items = kept
    return dict(sorted(common.items()))
