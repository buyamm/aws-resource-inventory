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
- Requirement 14.1: Mappings for the network, edge and load-balancing types
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
        m.companions.append(
            TfResource(
                "aws_route53_record",
                _companion_name(name, suffix.replace(".", "_")),
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
