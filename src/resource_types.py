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
        ),
        ResourceTypeInfo(
            "aws_vpc",
            "ec2",
            "regional",
            "VpcId",
            ("vpc",),
            _aws4_style("vpc", "#8C4FFF"),
        ),
        ResourceTypeInfo(
            "aws_security_group",
            "ec2",
            "regional",
            "GroupId",
            ("security_group",),
            _aws4_style("network_firewall", "#DD344C"),
        ),
        ResourceTypeInfo(
            "aws_lambda_function",
            "lambda",
            "regional",
            "FunctionName",
            ("lambda", "lambda_function"),
            _aws4_style("lambda", "#ED7100"),
        ),
        ResourceTypeInfo(
            "aws_db_instance",
            "rds",
            "regional",
            "DBInstanceIdentifier",
            ("aws_rds_instance", "rds"),
            _aws4_style("rds", "#C925D1"),
        ),
        ResourceTypeInfo(
            "aws_cloudwatch_log_group",
            "logs",
            "regional",
            "logGroupName",
            ("log_group",),
            _aws4_style("cloudwatch_2", "#E7157B"),
        ),
        ResourceTypeInfo(
            "aws_sfn_state_machine",
            "stepfunctions",
            "regional",
            "name",
            ("aws_step_function", "stepfunctions"),
            _aws4_style("step_functions", "#E7157B"),
        ),
        ResourceTypeInfo(
            "aws_dynamodb_table",
            "dynamodb",
            "regional",
            "TableName",
            ("dynamodb",),
            _aws4_style("dynamodb", "#C925D1"),
        ),
        ResourceTypeInfo(
            "aws_s3_bucket",
            "s3",
            "global",
            "Name",
            ("s3", "s3_bucket"),
            _aws4_style("s3", "#7AA116"),
        ),
        ResourceTypeInfo(
            "aws_iam_role",
            "iam",
            "global",
            "RoleName",
            ("iam_role",),
            _aws4_style("identity_and_access_management", "#DD344C"),
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
