"""
Resource Type Registry

Single source of truth for the ten Supported_Resource_Types: canonical ids
(= Terraform AWS provider resource type names), accepted aliases, AWS service,
scope, the Specifications field that holds the resource id, and draw.io styles.

Requirements Coverage:
- Requirement 1.3: Supported resource types (EC2, VPC, Security Groups, Lambda, RDS,
  CloudWatch log groups, Step Functions, DynamoDB, S3, IAM roles)
- Requirement 3.2: File naming and directory layout of per-resource output files
- Requirement 6.4: AWS stencil styles for diagrams
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from src.parser import ResourceSpec

GLOBAL_REGION = "global"

_DRAWIO_BASE_STYLE = (
    "sketch=0;outlineConnect=0;fontColor=#232F3E;strokeColor=#ffffff;dashed=0;"
    "verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
    "fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;"
)


def _aws4_style(res_icon: str, fill_color: str) -> str:
    return f"{_DRAWIO_BASE_STYLE}resIcon=mxgraph.aws4.{res_icon};fillColor={fill_color};"


@dataclass(frozen=True)
class ResourceTypeInfo:
    """Static description of one Supported_Resource_Type."""

    type_id: str
    service: str
    scope: Literal["regional", "global"]
    id_field: str
    aliases: tuple[str, ...]
    drawio_style: str
    arn_service: str = ""
    arn_resource: str = ""  # resource part of the ARN with "{id}" for the resource id

    @property
    def terraform_type(self) -> str:
        """Canonical ids are Terraform AWS provider resource type names."""
        return self.type_id


REGISTRY: dict[str, ResourceTypeInfo] = {
    info.type_id: info
    for info in (
        ResourceTypeInfo(
            "aws_instance",
            "ec2",
            "regional",
            "InstanceId",
            ("aws_ec2_instance", "ec2", "ec2_instance"),
            _aws4_style("ec2", "#ED7100"),
            arn_service="ec2",
            arn_resource="instance/{id}",
        ),
        ResourceTypeInfo(
            "aws_vpc",
            "ec2",
            "regional",
            "VpcId",
            ("vpc",),
            _aws4_style("vpc", "#8C4FFF"),
            arn_service="ec2",
            arn_resource="vpc/{id}",
        ),
        ResourceTypeInfo(
            "aws_security_group",
            "ec2",
            "regional",
            "GroupId",
            ("security_group",),
            _aws4_style("network_firewall", "#DD344C"),
            arn_service="ec2",
            arn_resource="security-group/{id}",
        ),
        ResourceTypeInfo(
            "aws_lambda_function",
            "lambda",
            "regional",
            "FunctionName",
            ("lambda", "lambda_function"),
            _aws4_style("lambda", "#ED7100"),
            arn_service="lambda",
            arn_resource="function:{id}",
        ),
        ResourceTypeInfo(
            "aws_db_instance",
            "rds",
            "regional",
            "DBInstanceIdentifier",
            ("aws_rds_instance", "rds"),
            _aws4_style("rds", "#C925D1"),
            arn_service="rds",
            arn_resource="db:{id}",
        ),
        ResourceTypeInfo(
            "aws_cloudwatch_log_group",
            "logs",
            "regional",
            "logGroupName",
            ("log_group",),
            _aws4_style("cloudwatch_2", "#E7157B"),
            arn_service="logs",
            arn_resource="log-group:{id}",
        ),
        ResourceTypeInfo(
            "aws_sfn_state_machine",
            "stepfunctions",
            "regional",
            "name",
            ("aws_step_function", "stepfunctions"),
            _aws4_style("step_functions", "#E7157B"),
            arn_service="states",
            arn_resource="stateMachine:{id}",
        ),
        ResourceTypeInfo(
            "aws_dynamodb_table",
            "dynamodb",
            "regional",
            "TableName",
            ("dynamodb",),
            _aws4_style("dynamodb", "#C925D1"),
            arn_service="dynamodb",
            arn_resource="table/{id}",
        ),
        ResourceTypeInfo(
            "aws_s3_bucket",
            "s3",
            "global",
            "Name",
            ("s3", "s3_bucket"),
            _aws4_style("s3", "#7AA116"),
            arn_service="s3",
            arn_resource="{id}",
        ),
        ResourceTypeInfo(
            "aws_iam_role",
            "iam",
            "global",
            "RoleName",
            ("iam_role",),
            _aws4_style("identity_and_access_management", "#DD344C"),
            arn_service="iam",
            arn_resource="role/{id}",
        ),
    )
}

_ALIASES: dict[str, str] = {
    name: info.type_id for info in REGISTRY.values() for name in (info.type_id, *info.aliases)
}


def canonical_type(name: str | None) -> str | None:
    """Resolve a canonical type id or alias (case-insensitive); None if unknown."""
    if not name:
        return None
    return _ALIASES.get(name.strip().lower())


def build_arn(type_id: str, resource_id: str, region: str, account_id: str) -> str:
    """ARN of a resource in the format discovery records (global types carry no region)."""
    info = REGISTRY[type_id]
    resource = info.arn_resource.format(id=resource_id)
    if info.service == "s3":
        return f"arn:aws:s3:::{resource}"
    if info.scope == "global":
        return f"arn:aws:{info.arn_service}::{account_id}:{resource}"
    return f"arn:aws:{info.arn_service}:{region}:{account_id}:{resource}"


def parse_arn(arn: str) -> tuple[str, str, str] | None:
    """(type_id, resource_id, region) of a Supported_Resource_Type ARN, else None.

    IAM role ids drop the path; log group ids drop a trailing ``:*``; S3 object ARNs
    and unsupported resource kinds return None.
    """
    parts = arn.split(":", 5)
    if len(parts) != 6 or parts[0] != "arn":
        return None
    service, region, resource = parts[2], parts[3], parts[5]
    for info in REGISTRY.values():
        prefix = info.arn_resource.split("{id}")[0]
        if info.arn_service != service or not resource.startswith(prefix):
            continue
        raw_id = resource[len(prefix) :]
        if info.type_id == "aws_cloudwatch_log_group" and raw_id.endswith(":*"):
            raw_id = raw_id[:-2]
        if info.type_id == "aws_iam_role":
            raw_id = raw_id.split("/")[-1]
        elif info.type_id == "aws_s3_bucket" and "/" in raw_id:
            return None
        if not raw_id:
            return None
        return info.type_id, raw_id, GLOBAL_REGION if info.scope == "global" else region
    return None


def arn_resource_segment(arn: str) -> str:
    """Return the trailing resource name of an ARN (after the last ':' and last '/')."""
    tail = arn.split(":")[-1]
    return tail.split("/")[-1] if "/" in tail else tail


def resource_id(spec: ResourceSpec) -> str:
    """The resource id of a spec (Specifications id field, else the ARN's last segment)."""
    info = REGISTRY.get(canonical_type(spec.resource_type) or "")
    if info is not None:
        value = (spec.specifications or {}).get(info.id_field)
        if isinstance(value, str) and value:
            return value
    return arn_resource_segment(spec.arn)


def file_id(raw_id: str) -> str:
    """Filesystem-safe id: characters outside [A-Za-z0-9_.-] become '_' (Req 3.2)."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", raw_id).strip("_") or "resource"


def spec_relpath(spec: ResourceSpec) -> str:
    """Path of the per-resource JSON file relative to Output_Dir (posix separators)."""
    region = spec.region or GLOBAL_REGION
    return f"{type_dir(spec.resource_type)}/{region}/{file_id(resource_id(spec))}.json"


def type_dir(resource_type: str) -> str:
    """Directory name for a resource type: canonical id when known, else the raw name."""
    return canonical_type(resource_type) or resource_type or "unknown"
