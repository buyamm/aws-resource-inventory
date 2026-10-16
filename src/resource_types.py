"""
Resource Type Registry

Single source of truth for the Supported_Resource_Types: canonical ids
(= Terraform AWS provider resource type names), accepted aliases, AWS service,
scope, the Specifications field that holds the resource id, ARN layout and
draw.io styles.

Requirements Coverage:
- Requirement 1.3: Supported resource types (EC2, VPC, Security Groups, Lambda, RDS,
  CloudWatch log groups, Step Functions, DynamoDB, S3, IAM roles)
- Requirement 3.2: File naming and directory layout of per-resource output files
- Requirement 6.4: AWS stencil styles for diagrams
- Requirement 14.1: Subnets, route tables, internet/NAT gateways, VPC endpoints,
  CloudFront distributions, load balancers, listeners, target groups, Route 53 zones,
  ACM certificates and WAFv2 web ACLs
- Requirement 14.4: ECS clusters, services and task definitions, ECR repositories,
  Auto Scaling groups, launch templates, ElastiCache replication groups, SQS queues,
  SNS topics, EventBridge rules and EventBridge Scheduler schedules
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


def _aws4_shape(shape: str, fill_color: str) -> str:
    """Resource-level stencil (standalone shape, no service frame)."""
    return (
        "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=none;"
        "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;"
        f"fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.{shape};"
        f"fillColor={fill_color};"
    )


def _aws4_group(stroke_color: str) -> str:
    """Group stencil (subnets are containers in AWS diagrams)."""
    return (
        "points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],"
        "[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;"
        "gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;"
        "pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;"
        f"grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor={stroke_color};"
        f"fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor={stroke_color};"
        "dashed=0;"
    )


NETWORK_COLOR = "#8C4FFF"
SECURITY_COLOR = "#DD344C"
COMPUTE_COLOR = "#ED7100"
DATABASE_COLOR = "#C925D1"
INTEGRATION_COLOR = "#E7157B"


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
    # Regex the resource id parsed from an ARN must match in full ("" = anything).
    id_pattern: str = ""

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
            _aws4_shape("vpc_virtual_private_cloud_vpc", NETWORK_COLOR),
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
            _aws4_shape("role", SECURITY_COLOR),
            arn_service="iam",
            arn_resource="role/{id}",
        ),
        # Network, edge and load balancing (Requirement 14.1). An empty id_field means
        # the resource id is taken from the ARN (see resource_id()).
        ResourceTypeInfo(
            "aws_subnet",
            "ec2",
            "regional",
            "SubnetId",
            ("subnet",),
            _aws4_group("#147EBA"),
            arn_service="ec2",
            arn_resource="subnet/{id}",
        ),
        ResourceTypeInfo(
            "aws_route_table",
            "ec2",
            "regional",
            "RouteTableId",
            ("route_table",),
            _aws4_shape("router", NETWORK_COLOR),
            arn_service="ec2",
            arn_resource="route-table/{id}",
        ),
        ResourceTypeInfo(
            "aws_internet_gateway",
            "ec2",
            "regional",
            "InternetGatewayId",
            ("internet_gateway",),
            _aws4_shape("internet_gateway", NETWORK_COLOR),
            arn_service="ec2",
            arn_resource="internet-gateway/{id}",
        ),
        ResourceTypeInfo(
            "aws_nat_gateway",
            "ec2",
            "regional",
            "NatGatewayId",
            ("nat_gateway",),
            _aws4_shape("nat_gateway", NETWORK_COLOR),
            arn_service="ec2",
            arn_resource="natgateway/{id}",
        ),
        ResourceTypeInfo(
            "aws_vpc_endpoint",
            "ec2",
            "regional",
            "VpcEndpointId",
            ("vpc_endpoint",),
            _aws4_shape("endpoints", NETWORK_COLOR),
            arn_service="ec2",
            arn_resource="vpc-endpoint/{id}",
        ),
        ResourceTypeInfo(
            "aws_cloudfront_distribution",
            "cloudfront",
            "global",
            "Id",
            ("cloudfront", "cloudfront_distribution"),
            _aws4_style("cloudfront", NETWORK_COLOR),
            arn_service="cloudfront",
            arn_resource="distribution/{id}",
        ),
        ResourceTypeInfo(
            "aws_lb",
            "elbv2",
            "regional",
            "",
            ("aws_alb", "alb", "load_balancer"),
            _aws4_shape("application_load_balancer", NETWORK_COLOR),
            arn_service="elasticloadbalancing",
            arn_resource="loadbalancer/{id}",
            id_pattern=r"(app|net|gwy)/[^/]+/[^/]+",
        ),
        ResourceTypeInfo(
            "aws_lb_listener",
            "elbv2",
            "regional",
            "",
            ("aws_alb_listener", "listener"),
            _aws4_style("elastic_load_balancing", NETWORK_COLOR),
            arn_service="elasticloadbalancing",
            arn_resource="listener/{id}",
            id_pattern=r"(app|net|gwy)/[^/]+/[^/]+/[^/]+",
        ),
        ResourceTypeInfo(
            "aws_lb_target_group",
            "elbv2",
            "regional",
            "",
            ("aws_alb_target_group", "target_group"),
            _aws4_style("elastic_load_balancing", NETWORK_COLOR),
            arn_service="elasticloadbalancing",
            arn_resource="targetgroup/{id}",
            id_pattern=r"[^/]+/[^/]+",
        ),
        ResourceTypeInfo(
            "aws_route53_zone",
            "route53",
            "global",
            "",
            ("route53", "route53_zone", "hosted_zone"),
            _aws4_shape("route_53_hosted_zone", NETWORK_COLOR),
            arn_service="route53",
            arn_resource="hostedzone/{id}",
        ),
        ResourceTypeInfo(
            "aws_acm_certificate",
            "acm",
            "regional",
            "",
            ("acm", "acm_certificate", "certificate"),
            _aws4_style("certificate_manager_3", SECURITY_COLOR),
            arn_service="acm",
            arn_resource="certificate/{id}",
        ),
        # CloudFront-scope web ACLs ("global/webacl/...", endpoint us-east-1) get the
        # region "global"; REGIONAL ones keep their region ("regional/webacl/...").
        ResourceTypeInfo(
            "aws_wafv2_web_acl",
            "wafv2",
            "regional",
            "",
            ("waf", "wafv2", "web_acl"),
            _aws4_style("waf", SECURITY_COLOR),
            arn_service="wafv2",
            arn_resource="regional/webacl/{id}",
            id_pattern=r"[^/]+/[^/]+",
        ),
        # Compute and data (Requirement 14.4).
        ResourceTypeInfo(
            "aws_ecs_cluster",
            "ecs",
            "regional",
            "clusterName",
            ("ecs", "ecs_cluster"),
            _aws4_style("ecs", COMPUTE_COLOR),
            arn_service="ecs",
            arn_resource="cluster/{id}",
            id_pattern=r"[^/]+",
        ),
        # Long ARN format only (service/<cluster>/<service>); the id is "<cluster>/<service>".
        ResourceTypeInfo(
            "aws_ecs_service",
            "ecs",
            "regional",
            "",
            ("ecs_service",),
            _aws4_shape("ecs_service", COMPUTE_COLOR),
            arn_service="ecs",
            arn_resource="service/{id}",
            id_pattern=r"[^/]+/[^/]+",
        ),
        ResourceTypeInfo(
            "aws_ecs_task_definition",
            "ecs",
            "regional",
            "",
            ("ecs_task_definition", "task_definition"),
            _aws4_shape("ecs_task", COMPUTE_COLOR),
            arn_service="ecs",
            arn_resource="task-definition/{id}",
            id_pattern=r"[^/:]+:\d+",
        ),
        ResourceTypeInfo(
            "aws_ecr_repository",
            "ecr",
            "regional",
            "repositoryName",
            ("ecr", "ecr_repository"),
            _aws4_style("ecr", COMPUTE_COLOR),
            arn_service="ecr",
            arn_resource="repository/{id}",
        ),
        # ARN: autoScalingGroup:<uuid>:autoScalingGroupName/<name> (see parse_arn/build_arn).
        ResourceTypeInfo(
            "aws_autoscaling_group",
            "autoscaling",
            "regional",
            "AutoScalingGroupName",
            ("asg", "autoscaling_group", "aws_autoscaling"),
            _aws4_shape("auto_scaling_group", COMPUTE_COLOR),
            arn_service="autoscaling",
            arn_resource="autoScalingGroupName/{id}",
        ),
        ResourceTypeInfo(
            "aws_launch_template",
            "ec2",
            "regional",
            "LaunchTemplateId",
            ("launch_template",),
            _aws4_shape("ami", COMPUTE_COLOR),
            arn_service="ec2",
            arn_resource="launch-template/{id}",
        ),
        ResourceTypeInfo(
            "aws_elasticache_replication_group",
            "elasticache",
            "regional",
            "ReplicationGroupId",
            ("elasticache", "aws_elasticache", "replication_group"),
            _aws4_style("elasticache", DATABASE_COLOR),
            arn_service="elasticache",
            arn_resource="replicationgroup:{id}",
            id_pattern=r"[^:/]+",
        ),
        ResourceTypeInfo(
            "aws_sqs_queue",
            "sqs",
            "regional",
            "",
            ("sqs", "sqs_queue", "queue"),
            _aws4_style("sqs", INTEGRATION_COLOR),
            arn_service="sqs",
            arn_resource="{id}",
            id_pattern=r"[^:/]+",
        ),
        ResourceTypeInfo(
            "aws_sns_topic",
            "sns",
            "regional",
            "",
            ("sns", "sns_topic", "topic"),
            _aws4_style("sns", INTEGRATION_COLOR),
            arn_service="sns",
            arn_resource="{id}",
            id_pattern=r"[^:/]+",
        ),
        # Rules on the default bus: id = name; on a custom bus: "<bus>/<name>".
        ResourceTypeInfo(
            "aws_cloudwatch_event_rule",
            "events",
            "regional",
            "",
            ("eventbridge_rule", "event_rule", "cloudwatch_event_rule"),
            _aws4_shape("rule_3", INTEGRATION_COLOR),
            arn_service="events",
            arn_resource="rule/{id}",
            id_pattern=r"[^/]+(/[^/]+)?",
        ),
        ResourceTypeInfo(
            "aws_scheduler_schedule",
            "scheduler",
            "regional",
            "",
            ("scheduler", "schedule", "scheduler_schedule"),
            _aws4_shape("eventbridge_scheduler", INTEGRATION_COLOR),
            arn_service="scheduler",
            arn_resource="schedule/{id}",
            id_pattern=r"[^/]+/[^/]+",
        ),
    )
}

_WAF_GLOBAL_PREFIX = "global/webacl/"
# Auto Scaling group ARNs embed a UUID only the API returns; built ARNs use the IAM
# wildcard form "autoScalingGroup:*:autoScalingGroupName/<name>".
_ASG_PREFIX = "autoScalingGroup:"
# S3 origin domains: <bucket>.s3.amazonaws.com, <bucket>.s3.<region>.amazonaws.com,
# <bucket>.s3-website-<region>.amazonaws.com, <bucket>.s3-website.<region>.amazonaws.com
_S3_DOMAIN = re.compile(r"^(?P<bucket>.+?)\.s3(?:-website)?(?:[.-][a-z0-9-]+)*\.amazonaws\.com$")

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
    if info.service in ("s3", "route53"):
        return f"arn:aws:{info.arn_service}:::{resource}"
    if type_id == "aws_wafv2_web_acl" and region == GLOBAL_REGION:
        return f"arn:aws:wafv2:us-east-1:{account_id}:{_WAF_GLOBAL_PREFIX}{resource_id}"
    if info.scope == "global":
        return f"arn:aws:{info.arn_service}::{account_id}:{resource}"
    if type_id == "aws_autoscaling_group":
        resource = f"{_ASG_PREFIX}*:{resource}"
    return f"arn:aws:{info.arn_service}:{region}:{account_id}:{resource}"


def parse_arn(arn: str) -> tuple[str, str, str] | None:
    """(type_id, resource_id, region) of a Supported_Resource_Type ARN, else None.

    IAM role ids drop the path; log group ids drop a trailing ``:*``; CloudFront-scope
    WAF web ACLs map to region ``global``; Auto Scaling group ids drop the UUID segment;
    S3 object ARNs and unsupported resource kinds (classic load balancers, listener
    rules, old-format ECS service ARNs, SNS subscriptions, ...) return None.
    """
    parts = arn.split(":", 5)
    if len(parts) != 6 or parts[0] != "arn":
        return None
    service, region, resource = parts[2], parts[3], parts[5]
    if service == "wafv2" and resource.startswith(_WAF_GLOBAL_PREFIX):
        resource, region = "regional/webacl/" + resource[len(_WAF_GLOBAL_PREFIX) :], GLOBAL_REGION
    if service == "autoscaling":
        if not resource.startswith(_ASG_PREFIX) or resource.count(":") < 2:
            return None
        resource = resource.split(":", 2)[2]
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
        if not raw_id or (info.id_pattern and not re.fullmatch(info.id_pattern, raw_id)):
            return None
        return info.type_id, raw_id, GLOBAL_REGION if info.scope == "global" else region
    return None


def s3_bucket_from_domain(domain: str) -> str | None:
    """Bucket name of an S3 REST or website endpoint domain (CloudFront origins), else None."""
    match = _S3_DOMAIN.match(domain.lower().rstrip("."))
    return match.group("bucket") if match else None


def arn_resource_segment(arn: str) -> str:
    """Return the trailing resource name of an ARN (after the last ':' and last '/')."""
    tail = arn.split(":")[-1]
    return tail.split("/")[-1] if "/" in tail else tail


def resource_id(spec: ResourceSpec) -> str:
    """The resource id of a spec: its Specifications id field, else the id in its ARN.

    Types without an id field (load balancers, listeners, target groups, Route 53 zones,
    ACM certificates, WAF web ACLs, ECS services and task definitions, SQS queues, SNS
    topics, EventBridge rules and schedules) use the id parse_arn() reads from the ARN,
    e.g. ``app/web-alb/50dc6c495c0c9188``; anything else falls back to the ARN's last segment.
    """
    info = REGISTRY.get(canonical_type(spec.resource_type) or "")
    if info is not None:
        value = (spec.specifications or {}).get(info.id_field) if info.id_field else None
        if isinstance(value, str) and value:
            return value
        parsed = parse_arn(spec.arn)
        if parsed is not None and parsed[0] == info.type_id:
            return parsed[1]
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
