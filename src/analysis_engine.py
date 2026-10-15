"""
Analysis Engine Module

Rule-based analysis of collected Specifications (AWS field names): relationships,
architecture patterns and security findings. Every statement carries Citations
that resolve against the cited spec file, so ``aws-inventory verify`` can check it.

Requirements Coverage:
- Requirement 6.1: Relationships (vpc_connection, iam_role_usage, security_group,
  dynamodb_access, log_group)
- Requirement 6.2: Serverless Application and Compute in VPC patterns; patterns of
  unsupported services are listed as undetectable
- Requirement 6.5: Rule-defined confidence scores and citations
- Requirement 6.6: Overly permissive IAM, public S3 buckets, unrestricted security groups
- Requirement 8.1 / 8.2 / 8.5: Citations with spec file and Spec_Checksum
- Requirement 14.2: subnet_placement, route_table_association, route_target,
  lb_listener, forwards_to, certificate relationships
- Requirement 14.3: cdn_origin, waf_protection, certificate (CloudFront) and dns_alias
  (Route 53 alias) relationships
- Requirement 14.4: ecs_cluster, task_definition, container_image, lb_target,
  launch_template, subscription and event_target relationships, plus placement, security
  group, role and log group relationships of the compute and data types; the
  "Web app: CloudFront + ALB + ECS" and "Static site: S3 + CloudFront" patterns
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.integrity import iter_property_paths, resolve_property_path, spec_checksum
from src.parser import ResourceSpec
from src.resource_types import canonical_type, resource_id, s3_bucket_from_domain, spec_relpath

ADMIN_POLICY_ARN = "arn:aws:iam::aws:policy/AdministratorAccess"
PUBLIC_GRANTEE_GROUPS = ("AllUsers", "AuthenticatedUsers")
OPEN_CIDRS = {"CidrIp": "0.0.0.0/0", "CidrIpv6": "::/0"}

CONFIDENCE = {
    "vpc_connection": 1.0,
    "iam_role_usage": 0.95,
    "security_group": 0.9,
    "dynamodb_access_exact": 1.0,
    "dynamodb_access_substring": 0.85,
    "log_group": 1.0,
    # Direct id / ARN references and exact DNS-name matches (Req 14.2, 14.3).
    "subnet_placement": 1.0,
    "route_table_association": 1.0,
    "route_target": 1.0,
    "lb_listener": 1.0,
    "forwards_to": 1.0,
    "certificate": 1.0,
    "cdn_origin": 1.0,
    "waf_protection": 1.0,
    "dns_alias": 1.0,
    # Compute and data (Req 14.4).
    "ecs_cluster": 1.0,
    "task_definition": 1.0,
    "container_image": 1.0,
    "lb_target": 1.0,
    "launch_template": 1.0,
    "subscription": 1.0,
    "event_target": 1.0,
}

WEB_APP_PATTERN = "Web app: CloudFront + ALB + ECS"
STATIC_SITE_PATTERN = "Static site: S3 + CloudFront"

# (pattern, reason): patterns no rule can detect from the collected data.
UNDETECTABLE_PATTERNS = [
    (
        "API Gateway + Lambda + DynamoDB",
        "API Gateway is not a Supported_Resource_Type; the pattern cannot be detected from "
        "collected data.",
    ),
    (
        "EC2 + Load Balancer",
        "Instances registered directly in a target group (elasticloadbalancing:"
        "DescribeTargetHealth) are not collected; target groups of Auto Scaling groups and "
        "ECS services are reported as lb_target relationships.",
    ),
]

# source type -> (pattern path, _Index table, relationship type): id / ARN references.
_REFERENCE_RELATIONSHIPS: dict[str, list[tuple[str, str, str]]] = {
    "aws_instance": [("SubnetId", "subnets", "subnet_placement")],
    "aws_lambda_function": [("VpcConfig.SubnetIds[]", "subnets", "subnet_placement")],
    "aws_db_instance": [
        ("DBSubnetGroup.Subnets[].SubnetIdentifier", "subnets", "subnet_placement")
    ],
    "aws_nat_gateway": [("SubnetId", "subnets", "subnet_placement")],
    "aws_vpc_endpoint": [("SubnetIds[]", "subnets", "subnet_placement")],
    "aws_internet_gateway": [("Attachments[].VpcId", "vpcs", "vpc_connection")],
    "aws_route_table": [
        ("Associations[].SubnetId", "subnets", "route_table_association"),
        ("Routes[].GatewayId", "internet_gateways", "route_target"),
        ("Routes[].GatewayId", "vpc_endpoints", "route_target"),
        ("Routes[].NatGatewayId", "nat_gateways", "route_target"),
    ],
    "aws_lb": [
        ("AvailabilityZones[].SubnetId", "subnets", "subnet_placement"),
        ("SecurityGroups[]", "security_groups", "security_group"),
    ],
    "aws_lb_listener": [
        ("LoadBalancerArn", "load_balancers", "lb_listener"),
        ("DefaultActions[].TargetGroupArn", "target_groups", "forwards_to"),
        (
            "DefaultActions[].ForwardConfig.TargetGroups[].TargetGroupArn",
            "target_groups",
            "forwards_to",
        ),
        ("Certificates[].CertificateArn", "certificates", "certificate"),
    ],
    "aws_cloudfront_distribution": [
        ("DistributionConfig.WebACLId", "web_acls", "waf_protection"),
        ("DistributionConfig.ViewerCertificate.ACMCertificateArn", "certificates", "certificate"),
    ],
    "aws_ecs_service": [
        ("clusterArn", "ecs_clusters", "ecs_cluster"),
        ("taskDefinition", "task_definitions", "task_definition"),
        ("networkConfiguration.awsvpcConfiguration.subnets[]", "subnets", "subnet_placement"),
        (
            "networkConfiguration.awsvpcConfiguration.securityGroups[]",
            "security_groups",
            "security_group",
        ),
    ],
    "aws_ecs_task_definition": [
        ("taskRoleArn", "roles", "iam_role_usage"),
        ("executionRoleArn", "roles", "iam_role_usage"),
        (
            "containerDefinitions[].logConfiguration.options.awslogs-group",
            "log_groups",
            "log_group",
        ),
    ],
    "aws_autoscaling_group": [
        ("LaunchTemplate.LaunchTemplateId", "launch_templates", "launch_template"),
        (
            "MixedInstancesPolicy.LaunchTemplate.LaunchTemplateSpecification.LaunchTemplateId",
            "launch_templates",
            "launch_template",
        ),
    ],
    "aws_launch_template": [
        ("LaunchTemplateData.SecurityGroupIds[]", "security_groups", "security_group"),
        ("LaunchTemplateData.NetworkInterfaces[].Groups[]", "security_groups", "security_group"),
        ("LaunchTemplateData.NetworkInterfaces[].SubnetId", "subnets", "subnet_placement"),
    ],
    "aws_elasticache_replication_group": [
        ("CacheCluster.SecurityGroups[].SecurityGroupId", "security_groups", "security_group"),
        ("CacheSubnetGroup.Subnets[].SubnetIdentifier", "subnets", "subnet_placement"),
    ],
    "aws_cloudwatch_event_rule": [("Targets[].RoleArn", "roles", "iam_role_usage")],
    "aws_scheduler_schedule": [("Target.RoleArn", "roles", "iam_role_usage")],
}

# source type -> (pattern, relationship type): ARNs matched against every collected spec.
_ARN_TARGET_RELATIONSHIPS: dict[str, list[tuple[str, str]]] = {
    "aws_cloudwatch_event_rule": [("Targets[].Arn", "event_target")],
    "aws_scheduler_schedule": [("Target.Arn", "event_target")],
    "aws_sns_topic": [("Subscriptions[].Endpoint", "subscription")],
}

# source type -> pattern of target group ARNs: the target group sends traffic to the source.
_LB_TARGET_PATHS = {
    "aws_ecs_service": "loadBalancers[].targetGroupArn",
    "aws_autoscaling_group": "TargetGroupARNs[]",
}


# ============================================================================
# Data model
# ============================================================================


@dataclass
class Citation:
    """Reference from an analysis statement to a value in a spec file (Req 8.2)."""

    resource_arn: str
    spec_file: str
    property_path: str
    source_checksum: str
    evidence_value: Any

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResourceRelationship:
    """Directed relationship between two collected resources (Req 6.1)."""

    from_arn: str
    to_arn: str
    relationship_type: str
    confidence: float = 1.0
    citations: list[Citation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArchitecturePattern:
    """Detected pattern; confidence = min of the supporting relationships (Req 6.5)."""

    pattern_name: str
    description: str
    participating_resources: list[str]
    confidence: float
    citations: list[Citation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SecurityFinding:
    """Suspicious configuration (Req 6.6)."""

    severity: str  # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    finding_type: str
    resource_arn: str
    description: str
    evidence: str
    citation: Citation

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisReport:
    relationships: list[ResourceRelationship]
    patterns: list[ArchitecturePattern]
    security_findings: list[SecurityFinding]
    summary_markdown: str
    undetectable_patterns: list[dict[str, str]] = field(default_factory=list)
    resource_count: int = 0
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Content of ``analysis/analysis.json``."""
        return {
            "generated_at": self.generated_at,
            "resource_count": self.resource_count,
            "relationships": [r.to_dict() for r in self.relationships],
            "patterns": [p.to_dict() for p in self.patterns],
            "security_findings": [f.to_dict() for f in self.security_findings],
            "undetectable_patterns": list(self.undetectable_patterns),
        }


# ============================================================================
# Helpers
# ============================================================================


def _addressable(key: str) -> bool:
    return bool(key) and not any(ch in key for ch in ".[]")


def cite(spec: ResourceSpec, property_path: str) -> Citation:
    """Citation of ``property_path`` in ``spec``; the evidence is resolved from the spec."""
    document = {"specifications": spec.specifications}
    return Citation(
        resource_arn=spec.arn,
        spec_file=spec_relpath(spec),
        property_path=property_path,
        source_checksum=spec.metadata.checksum or spec_checksum(spec.specifications),
        evidence_value=resolve_property_path(document, property_path),
    )


def _type(spec: ResourceSpec) -> str:
    return canonical_type(spec.resource_type) or spec.resource_type


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _get(mapping: Any, *keys: str) -> Any:
    current = mapping
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _short(arn: str) -> str:
    tail = arn.split(":")[-1]
    return tail.split("/")[-1] if "/" in tail else tail


def _unqualified(arn: str) -> str:
    """A Lambda function ARN without its version/alias qualifier; other ARNs unchanged."""
    parts = arn.split(":")
    if len(parts) > 7 and parts[2] == "lambda" and parts[5] == "function":
        return ":".join(parts[:7])
    return arn


def _image_repository(image: Any) -> str:
    """Repository URI of a container image reference (tag or digest removed)."""
    text = str(image).split("@")[0]
    head, _, tag = text.rpartition(":")
    return head if head and "/" not in tag else text


def _dns(name: Any) -> str:
    """Comparable DNS name: lower case, no trailing dot, no ``dualstack.`` prefix."""
    text = str(name).lower().rstrip(".")
    return text[len("dualstack.") :] if text.startswith("dualstack.") else text


class _Index:
    """Lookup tables from ids/names/ARNs to collected specs."""

    def __init__(self, specs: Iterable[ResourceSpec]) -> None:
        self.vpcs: dict[str, ResourceSpec] = {}
        self.security_groups: dict[str, ResourceSpec] = {}
        self.roles: dict[str, ResourceSpec] = {}
        self.tables: dict[str, ResourceSpec] = {}
        self.table_names: list[tuple[str, ResourceSpec]] = []
        self.log_groups: dict[str, ResourceSpec] = {}
        # Network, load balancing and edge types (Req 14.2, 14.3), keyed by id or ARN.
        self.subnets: dict[str, ResourceSpec] = {}
        self.internet_gateways: dict[str, ResourceSpec] = {}
        self.nat_gateways: dict[str, ResourceSpec] = {}
        self.vpc_endpoints: dict[str, ResourceSpec] = {}
        self.load_balancers: dict[str, ResourceSpec] = {}
        self.target_groups: dict[str, ResourceSpec] = {}
        self.certificates: dict[str, ResourceSpec] = {}
        self.web_acls: dict[str, ResourceSpec] = {}
        self.buckets: dict[str, ResourceSpec] = {}
        # Normalized DNS names of load balancers and CloudFront distributions.
        self.lb_dns: dict[str, ResourceSpec] = {}
        self.distribution_dns: dict[str, ResourceSpec] = {}
        # Compute and data types (Req 14.4).
        self.ecs_clusters: dict[str, ResourceSpec] = {}
        self.task_definitions: dict[str, ResourceSpec] = {}
        self.launch_templates: dict[str, ResourceSpec] = {}
        self.repository_uris: dict[str, ResourceSpec] = {}
        self.by_arn: dict[str, ResourceSpec] = {}
        by_id = {
            "aws_subnet": self.subnets,
            "aws_internet_gateway": self.internet_gateways,
            "aws_nat_gateway": self.nat_gateways,
            "aws_vpc_endpoint": self.vpc_endpoints,
            "aws_launch_template": self.launch_templates,
        }
        by_arn = {
            "aws_lb": self.load_balancers,
            "aws_lb_target_group": self.target_groups,
            "aws_acm_certificate": self.certificates,
            "aws_wafv2_web_acl": self.web_acls,
            "aws_ecs_cluster": self.ecs_clusters,
            "aws_ecs_task_definition": self.task_definitions,
        }
        for spec in specs:
            self.by_arn[spec.arn] = spec
            s = spec.specifications or {}
            kind = _type(spec)
            if kind in by_id:
                by_id[kind][resource_id(spec)] = spec
            elif kind in by_arn:
                by_arn[kind][spec.arn] = spec
            if kind == "aws_lb" and isinstance(s.get("DNSName"), str):
                self.lb_dns[_dns(s["DNSName"])] = spec
            elif kind == "aws_cloudfront_distribution" and isinstance(s.get("DomainName"), str):
                self.distribution_dns[_dns(s["DomainName"])] = spec
            elif kind == "aws_s3_bucket":
                self.buckets[resource_id(spec)] = spec
            elif kind == "aws_ecr_repository" and isinstance(s.get("repositoryUri"), str):
                self.repository_uris[s["repositoryUri"]] = spec
            if kind == "aws_vpc" and isinstance(s.get("VpcId"), str):
                self.vpcs[s["VpcId"]] = spec
            elif kind == "aws_security_group" and isinstance(s.get("GroupId"), str):
                self.security_groups[s["GroupId"]] = spec
            elif kind == "aws_iam_role":
                self.roles[spec.arn] = spec
                self.roles[resource_id(spec)] = spec
            elif kind == "aws_dynamodb_table":
                name = resource_id(spec)
                self.tables[name] = spec
                self.tables[spec.arn] = spec
                if isinstance(s.get("TableArn"), str):
                    self.tables[s["TableArn"]] = spec
                self.table_names.append((name, spec))
            elif kind == "aws_cloudwatch_log_group":
                self.log_groups[resource_id(spec)] = spec


# ============================================================================
# Engine
# ============================================================================


class AnalysisEngine:
    """Infers relationships, patterns and security findings with citations."""

    # ------------------------------------------------------------------
    # Relationships (Requirement 6.1)
    # ------------------------------------------------------------------

    def identify_relationships(self, specs: list[ResourceSpec]) -> list[ResourceRelationship]:
        index = _Index(specs)
        found: dict[tuple[str, str, str], ResourceRelationship] = {}

        def add(
            source: ResourceSpec,
            target: ResourceSpec,
            kind: str,
            confidence: float,
            citations: list[Citation],
        ) -> None:
            if target.arn == source.arn:
                return
            key = (source.arn, target.arn, kind)
            if key not in found:
                found[key] = ResourceRelationship(
                    source.arn, target.arn, kind, confidence, citations
                )

        for spec in sorted(specs, key=lambda s: s.arn):
            s = spec.specifications or {}
            kind = _type(spec)

            # vpc_connection
            vpc_paths = {
                "aws_instance": ("VpcId",),
                "aws_security_group": ("VpcId",),
                "aws_lambda_function": ("VpcConfig", "VpcId"),
                "aws_db_instance": ("DBSubnetGroup", "VpcId"),
                "aws_subnet": ("VpcId",),
                "aws_route_table": ("VpcId",),
                "aws_nat_gateway": ("VpcId",),
                "aws_vpc_endpoint": ("VpcId",),
                "aws_lb": ("VpcId",),
                "aws_lb_target_group": ("VpcId",),
                "aws_elasticache_replication_group": ("CacheSubnetGroup", "VpcId"),
            }.get(kind)
            if vpc_paths:
                vpc_id = _get(s, *vpc_paths)
                if isinstance(vpc_id, str) and vpc_id in index.vpcs:
                    target = index.vpcs[vpc_id]
                    add(
                        spec,
                        target,
                        "vpc_connection",
                        CONFIDENCE["vpc_connection"],
                        [
                            cite(spec, "specifications." + ".".join(vpc_paths)),
                            cite(target, "specifications.VpcId"),
                        ],
                    )

            # iam_role_usage
            role_ref, role_path = None, ""
            if kind == "aws_lambda_function" and isinstance(s.get("Role"), str):
                role_ref, role_path = s["Role"], "specifications.Role"
            elif kind == "aws_sfn_state_machine" and isinstance(s.get("roleArn"), str):
                role_ref, role_path = s["roleArn"], "specifications.roleArn"
            elif kind == "aws_instance" and isinstance(_get(s, "IamInstanceProfile", "Arn"), str):
                # Instance profile name == role name (the convention used by the console)
                role_ref = _short(s["IamInstanceProfile"]["Arn"])
                role_path = "specifications.IamInstanceProfile.Arn"
            if role_ref:
                role_target = index.roles.get(role_ref) or index.roles.get(_short(role_ref))
                if role_target is not None:
                    add(
                        spec,
                        role_target,
                        "iam_role_usage",
                        CONFIDENCE["iam_role_usage"],
                        [cite(spec, role_path)],
                    )

            # security_group
            sg_refs: list[tuple[Any, str]] = []
            if kind == "aws_instance":
                sg_refs = [
                    (g.get("GroupId"), f"specifications.SecurityGroups[{i}].GroupId")
                    for i, g in enumerate(_as_list(s.get("SecurityGroups")))
                    if isinstance(g, dict)
                ]
            elif kind == "aws_lambda_function":
                sg_refs = [
                    (g, f"specifications.VpcConfig.SecurityGroupIds[{i}]")
                    for i, g in enumerate(_as_list(_get(s, "VpcConfig", "SecurityGroupIds")))
                ]
            elif kind == "aws_db_instance":
                sg_refs = [
                    (
                        g.get("VpcSecurityGroupId"),
                        f"specifications.VpcSecurityGroups[{i}].VpcSecurityGroupId",
                    )
                    for i, g in enumerate(_as_list(s.get("VpcSecurityGroups")))
                    if isinstance(g, dict)
                ]
            for group_id, path in sg_refs:
                if isinstance(group_id, str) and group_id in index.security_groups:
                    add(
                        spec,
                        index.security_groups[group_id],
                        "security_group",
                        CONFIDENCE["security_group"],
                        [cite(spec, path)],
                    )

            if kind == "aws_lambda_function":
                self._lambda_relationships(spec, index, add)
            self._reference_relationships(spec, kind, index, add)
            self._compute_relationships(spec, kind, index, add)
            if kind == "aws_cloudfront_distribution":
                self._origin_relationships(spec, index, add)
            elif kind == "aws_route53_zone":
                self._alias_relationships(spec, index, add)

        return list(found.values())

    @staticmethod
    def _compute_relationships(spec: ResourceSpec, kind: str, index: _Index, add: Any) -> None:
        """Relationships of the compute and data types that need more than a lookup (Req 14.4)."""
        specs = spec.specifications or {}
        # Target group -> ECS service / Auto Scaling group, cited at the referencing property.
        pattern = _LB_TARGET_PATHS.get(kind)
        for path, arn in iter_property_paths(specs, pattern) if pattern else ():
            target_group = index.target_groups.get(arn) if isinstance(arn, str) else None
            if target_group is not None:
                add(target_group, spec, "lb_target", CONFIDENCE["lb_target"], [cite(spec, path)])
        # Event targets and SNS subscriptions name any collected resource by ARN.
        for pattern, relationship in _ARN_TARGET_RELATIONSHIPS.get(kind, []):
            for path, arn in iter_property_paths(specs, pattern):
                target = index.by_arn.get(_unqualified(arn)) if isinstance(arn, str) else None
                if target is not None:
                    add(spec, target, relationship, CONFIDENCE[relationship], [cite(spec, path)])
        if kind == "aws_autoscaling_group" and isinstance(specs.get("VPCZoneIdentifier"), str):
            for subnet_id in specs["VPCZoneIdentifier"].split(","):
                subnet = index.subnets.get(subnet_id.strip())
                if subnet is not None:
                    citations = [cite(spec, "specifications.VPCZoneIdentifier")]
                    add(spec, subnet, "subnet_placement", 1.0, citations)
        elif kind == "aws_ecs_task_definition":
            for path, image in iter_property_paths(specs, "containerDefinitions[].image"):
                repository = index.repository_uris.get(_image_repository(image))
                if repository is not None:
                    citations = [cite(spec, path), cite(repository, "specifications.repositoryUri")]
                    add(spec, repository, "container_image", 1.0, citations)
        elif kind == "aws_launch_template":
            # Instance profile name == role name (the convention used for EC2 instances).
            profile = _get(specs, "LaunchTemplateData", "IamInstanceProfile") or {}
            for key in ("Arn", "Name"):
                value = profile.get(key) if isinstance(profile, dict) else None
                role = index.roles.get(_short(value)) if isinstance(value, str) else None
                if role is not None:
                    path = f"specifications.LaunchTemplateData.IamInstanceProfile.{key}"
                    add(
                        spec,
                        role,
                        "iam_role_usage",
                        CONFIDENCE["iam_role_usage"],
                        [cite(spec, path)],
                    )
                    break

    @staticmethod
    def _reference_relationships(spec: ResourceSpec, kind: str, index: _Index, add: Any) -> None:
        """Id / ARN references of _REFERENCE_RELATIONSHIPS (Req 14.2, 14.3)."""
        for pattern, table, relationship in _REFERENCE_RELATIONSHIPS.get(kind, []):
            targets: dict[str, ResourceSpec] = getattr(index, table)
            for path, value in iter_property_paths(spec.specifications, pattern):
                if isinstance(value, str) and value in targets:
                    add(
                        spec,
                        targets[value],
                        relationship,
                        CONFIDENCE[relationship],
                        [cite(spec, path)],
                    )

    @staticmethod
    def _origin_relationships(spec: ResourceSpec, index: _Index, add: Any) -> None:
        """CloudFront origins: S3 bucket by origin domain, load balancer by DNS name."""
        pattern = "DistributionConfig.Origins.Items[].DomainName"
        for path, domain in iter_property_paths(spec.specifications, pattern):
            if not isinstance(domain, str):
                continue
            bucket = index.buckets.get(s3_bucket_from_domain(domain) or "")
            if bucket is not None:
                citations = [cite(spec, path), cite(bucket, "specifications.Name")]
                add(spec, bucket, "cdn_origin", CONFIDENCE["cdn_origin"], citations)
            lb = index.lb_dns.get(_dns(domain))
            if lb is not None:
                citations = [cite(spec, path), cite(lb, "specifications.DNSName")]
                add(spec, lb, "cdn_origin", CONFIDENCE["cdn_origin"], citations)

    @staticmethod
    def _alias_relationships(spec: ResourceSpec, index: _Index, add: Any) -> None:
        """Route 53 alias records pointing at a CloudFront distribution or load balancer."""
        pattern = "ResourceRecordSets[].AliasTarget.DNSName"
        for path, dns_name in iter_property_paths(spec.specifications, pattern):
            name = _dns(dns_name)
            for target, target_path in (
                (index.distribution_dns.get(name), "specifications.DomainName"),
                (index.lb_dns.get(name), "specifications.DNSName"),
            ):
                if target is not None:
                    citations = [cite(spec, path), cite(target, target_path)]
                    add(spec, target, "dns_alias", CONFIDENCE["dns_alias"], citations)

    @staticmethod
    def _lambda_relationships(spec: ResourceSpec, index: _Index, add: Any) -> None:
        s = spec.specifications or {}
        variables = _get(s, "Environment", "Variables")
        if isinstance(variables, dict):
            for name, value in sorted(variables.items()):
                if not isinstance(value, str) or not value:
                    continue
                path = (
                    f"specifications.Environment.Variables.{name}"
                    if _addressable(name)
                    else "specifications.Environment.Variables"
                )
                if value in index.tables:
                    add(
                        spec,
                        index.tables[value],
                        "dynamodb_access",
                        CONFIDENCE["dynamodb_access_exact"],
                        [cite(spec, path)],
                    )
                    continue
                for table_name, table in index.table_names:
                    if len(table_name) > 3 and table_name in value:
                        add(
                            spec,
                            table,
                            "dynamodb_access",
                            CONFIDENCE["dynamodb_access_substring"],
                            [cite(spec, path)],
                        )
        function_name = s.get("FunctionName")
        if isinstance(function_name, str):
            log_group = index.log_groups.get(f"/aws/lambda/{function_name}")
            if log_group is not None:
                add(
                    spec,
                    log_group,
                    "log_group",
                    CONFIDENCE["log_group"],
                    [
                        cite(spec, "specifications.FunctionName"),
                        cite(log_group, "specifications.logGroupName"),
                    ],
                )

    # ------------------------------------------------------------------
    # Patterns (Requirements 6.2, 6.5)
    # ------------------------------------------------------------------

    def detect_patterns(
        self,
        specs: list[ResourceSpec],
        relationships: list[ResourceRelationship] | None = None,
    ) -> list[ArchitecturePattern]:
        rels = relationships if relationships is not None else self.identify_relationships(specs)
        by_arn = {spec.arn: spec for spec in specs}
        patterns: list[ArchitecturePattern] = []

        for spec in sorted(specs, key=lambda s: s.arn):
            kind = _type(spec)
            outgoing = [r for r in rels if r.from_arn == spec.arn]
            if kind == "aws_lambda_function":
                support = [
                    r
                    for r in outgoing
                    if r.relationship_type in ("iam_role_usage", "dynamodb_access")
                ]
                if support:
                    roles = [
                        _short(r.to_arn) for r in support if r.relationship_type == "iam_role_usage"
                    ]
                    tables = [
                        _short(r.to_arn)
                        for r in support
                        if r.relationship_type == "dynamodb_access"
                    ]
                    parts = []
                    if roles:
                        parts.append(f"runs with IAM role {', '.join(repr(x) for x in roles)}")
                    if tables:
                        parts.append(
                            "references DynamoDB table(s) "
                            f"{', '.join(repr(x) for x in tables)} in its environment variables"
                        )
                    patterns.append(
                        self._pattern(
                            "Serverless Application",
                            f"Lambda function '{resource_id(spec)}' " + " and ".join(parts) + ".",
                            spec,
                            support,
                        )
                    )
            elif kind == "aws_instance":
                support = [r for r in outgoing if r.relationship_type == "vpc_connection"]
                if support:
                    vpc = by_arn.get(support[0].to_arn)
                    vpc_name = resource_id(vpc) if vpc else _short(support[0].to_arn)
                    patterns.append(
                        self._pattern(
                            "Compute in VPC",
                            f"EC2 instance '{resource_id(spec)}' runs in VPC '{vpc_name}'.",
                            spec,
                            support,
                        )
                    )
            elif kind == "aws_cloudfront_distribution":
                patterns += self._edge_patterns(spec, rels, by_arn)
        return patterns

    def _edge_patterns(
        self,
        distribution: ResourceSpec,
        rels: list[ResourceRelationship],
        by_arn: dict[str, ResourceSpec],
    ) -> list[ArchitecturePattern]:
        """Static site (S3 origin) and web app (LB origin -> listener -> TG -> ECS service)."""

        def name(arn: str) -> str:
            target = by_arn.get(arn)
            return resource_id(target) if target else _short(arn)

        def outgoing(arn: str, kind: str) -> list[ResourceRelationship]:
            return [r for r in rels if r.from_arn == arn and r.relationship_type == kind]

        patterns: list[ArchitecturePattern] = []
        label = resource_id(distribution)
        for origin in outgoing(distribution.arn, "cdn_origin"):
            origin_spec = by_arn.get(origin.to_arn)
            if origin_spec is not None and _type(origin_spec) == "aws_s3_bucket":
                patterns.append(
                    self._pattern(
                        STATIC_SITE_PATTERN,
                        f"CloudFront distribution '{label}' serves content from S3 bucket "
                        f"'{name(origin.to_arn)}'.",
                        distribution,
                        [origin],
                    )
                )
                continue
            listeners = [
                r
                for r in rels
                if r.to_arn == origin.to_arn and r.relationship_type == "lb_listener"
            ]
            for listener in listeners:
                for forward in outgoing(listener.from_arn, "forwards_to"):
                    for target in outgoing(forward.to_arn, "lb_target"):
                        service = by_arn.get(target.to_arn)
                        if service is None or _type(service) != "aws_ecs_service":
                            continue
                        patterns.append(
                            self._pattern(
                                WEB_APP_PATTERN,
                                f"CloudFront distribution '{label}' sends requests to load "
                                f"balancer '{name(origin.to_arn)}', whose listener forwards "
                                f"to target group '{name(forward.to_arn)}' serving ECS "
                                f"service '{name(target.to_arn)}'.",
                                distribution,
                                [origin, listener, forward, target],
                            )
                        )
        return patterns

    @staticmethod
    def _pattern(
        name: str, description: str, spec: ResourceSpec, support: list[ResourceRelationship]
    ) -> ArchitecturePattern:
        participants = [spec.arn]
        for rel in support:
            # Sources other than the anchor (e.g. the listener of lb_listener) take part too.
            for arn in (rel.to_arn, rel.from_arn):
                if arn not in participants:
                    participants.append(arn)
        citations: list[Citation] = []
        for rel in support:
            citations.extend(rel.citations)
        return ArchitecturePattern(
            pattern_name=name,
            description=description,
            participating_resources=participants,
            confidence=min(r.confidence for r in support),
            citations=citations,
        )

    # ------------------------------------------------------------------
    # Security findings (Requirement 6.6)
    # ------------------------------------------------------------------

    def flag_suspicious_patterns(self, specs: list[ResourceSpec]) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        for spec in sorted(specs, key=lambda s: s.arn):
            kind = _type(spec)
            if kind == "aws_iam_role":
                findings.extend(self._iam_findings(spec))
            elif kind == "aws_s3_bucket":
                findings.extend(self._s3_findings(spec))
            elif kind == "aws_security_group":
                findings.extend(self._security_group_findings(spec))
        return findings

    @staticmethod
    def _iam_findings(spec: ResourceSpec) -> list[SecurityFinding]:
        s = spec.specifications or {}
        name = resource_id(spec)
        findings: list[SecurityFinding] = []
        policies = s.get("InlinePolicies")
        if isinstance(policies, dict):
            for policy_name, document in sorted(policies.items()):
                statements = _get(document, "Statement")
                base = (
                    f"specifications.InlinePolicies.{policy_name}.Statement"
                    if _addressable(policy_name)
                    else "specifications.InlinePolicies"
                )
                as_list = isinstance(statements, list)
                for i, statement in enumerate(_as_list(statements)):
                    if not isinstance(statement, dict) or statement.get("Effect") != "Allow":
                        continue
                    if "*" in _as_list(statement.get("Action")) and "*" in _as_list(
                        statement.get("Resource")
                    ):
                        path = f"{base}[{i}]" if as_list and _addressable(policy_name) else base
                        findings.append(
                            SecurityFinding(
                                severity="CRITICAL",
                                finding_type="OVERLY_PERMISSIVE_IAM_POLICY",
                                resource_arn=spec.arn,
                                description=(
                                    f"IAM role '{name}' inline policy '{policy_name}' allows "
                                    "Action '*' on Resource '*'."
                                ),
                                evidence="Statement: Effect=Allow, Action=*, Resource=*",
                                citation=cite(spec, path),
                            )
                        )
        for i, attached in enumerate(_as_list(s.get("AttachedPolicies"))):
            if isinstance(attached, dict) and attached.get("PolicyArn") == ADMIN_POLICY_ARN:
                findings.append(
                    SecurityFinding(
                        severity="CRITICAL",
                        finding_type="OVERLY_PERMISSIVE_IAM_POLICY",
                        resource_arn=spec.arn,
                        description=f"IAM role '{name}' has the AWS managed policy AdministratorAccess attached.",
                        evidence=f"PolicyArn: {ADMIN_POLICY_ARN}",
                        citation=cite(spec, f"specifications.AttachedPolicies[{i}]"),
                    )
                )
        return findings

    @staticmethod
    def _s3_findings(spec: ResourceSpec) -> list[SecurityFinding]:
        s = spec.specifications or {}
        name = resource_id(spec)
        findings: list[SecurityFinding] = []
        for i, grant in enumerate(_as_list(_get(s, "bucket-acl", "Grants"))):
            uri = _get(grant, "Grantee", "URI")
            if isinstance(uri, str) and uri.rsplit("/", 1)[-1] in PUBLIC_GRANTEE_GROUPS:
                findings.append(
                    SecurityFinding(
                        severity="HIGH",
                        finding_type="PUBLIC_S3_BUCKET",
                        resource_arn=spec.arn,
                        description=(
                            f"S3 bucket '{name}' ACL grants {grant.get('Permission')} "
                            f"to the {uri.rsplit('/', 1)[-1]} group."
                        ),
                        evidence=f"Grantee URI: {uri}",
                        citation=cite(spec, f"specifications.bucket-acl.Grants[{i}]"),
                    )
                )
                break
        policy_text = _get(s, "bucket-policy", "Policy")
        if isinstance(policy_text, str):
            try:
                policy = json.loads(policy_text)
            except json.JSONDecodeError:
                policy = {}
            for statement in _as_list(_get(policy, "Statement")):
                if not isinstance(statement, dict) or statement.get("Effect") != "Allow":
                    continue
                principal = statement.get("Principal")
                aws_principal = (
                    _as_list(principal.get("AWS")) if isinstance(principal, dict) else []
                )
                if principal == "*" or "*" in aws_principal:
                    findings.append(
                        SecurityFinding(
                            severity="HIGH",
                            finding_type="PUBLIC_S3_BUCKET",
                            resource_arn=spec.arn,
                            description=f"S3 bucket '{name}' policy allows any principal ('*').",
                            evidence=f"Principal: {json.dumps(principal)}",
                            citation=cite(spec, "specifications.bucket-policy.Policy"),
                        )
                    )
                    break
        return findings

    @staticmethod
    def _security_group_findings(spec: ResourceSpec) -> list[SecurityFinding]:
        s = spec.specifications or {}
        name = resource_id(spec)
        findings: list[SecurityFinding] = []
        for p, permission in enumerate(_as_list(s.get("IpPermissions"))):
            if not isinstance(permission, dict):
                continue
            protocol = permission.get("IpProtocol")
            if protocol == "-1":
                ports = "all traffic"
            elif permission.get("FromPort") == permission.get("ToPort"):
                ports = f"{protocol} port {permission.get('FromPort')}"
            else:
                ports = f"{protocol} ports {permission.get('FromPort')}-{permission.get('ToPort')}"
            for range_key, cidr_key in (("IpRanges", "CidrIp"), ("Ipv6Ranges", "CidrIpv6")):
                for r, ip_range in enumerate(_as_list(permission.get(range_key))):
                    cidr = _get(ip_range, cidr_key)
                    if cidr == OPEN_CIDRS[cidr_key]:
                        findings.append(
                            SecurityFinding(
                                severity="HIGH",
                                finding_type="UNRESTRICTED_SECURITY_GROUP_ACCESS",
                                resource_arn=spec.arn,
                                description=f"Security group '{name}' allows ingress from {cidr} on {ports}.",
                                evidence=f"Ingress {cidr} on {ports}",
                                citation=cite(
                                    spec, f"specifications.IpPermissions[{p}].{range_key}[{r}]"
                                ),
                            )
                        )
        return findings

    # ------------------------------------------------------------------
    # Full report
    # ------------------------------------------------------------------

    def analyze(self, specs: list[ResourceSpec]) -> AnalysisReport:
        relationships = self.identify_relationships(specs)
        patterns = self.detect_patterns(specs, relationships)
        findings = self.flag_suspicious_patterns(specs)
        undetectable = [
            {"pattern": pattern, "reason": reason} for pattern, reason in UNDETECTABLE_PATTERNS
        ]
        report = AnalysisReport(
            relationships=relationships,
            patterns=patterns,
            security_findings=findings,
            summary_markdown="",
            undetectable_patterns=undetectable,
            resource_count=len(specs),
            generated_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        report.summary_markdown = render_summary_markdown(report)
        return report


def _cite_marker(citation: Citation) -> str:
    return f"[cite: {citation.spec_file}#{citation.property_path} sha256:{citation.source_checksum[:12]}]"


def render_summary_markdown(report: AnalysisReport) -> str:
    """Markdown for ``analysis/analysis.md``; each statement ends with its citation markers."""
    lines = [
        "# Activity Flow & Architecture Analysis",
        "",
        f"**Resources analyzed:** {report.resource_count}  ",
        f"**Relationships identified:** {len(report.relationships)}  ",
        f"**Architecture patterns:** {len(report.patterns)}  ",
        f"**Security findings:** {len(report.security_findings)}",
        "",
        "## Architecture Patterns",
        "",
    ]
    if report.patterns:
        for pattern in report.patterns:
            lines.append(f"### {pattern.pattern_name} (confidence {pattern.confidence:.2f})")
            lines.append(
                f"{pattern.description} " + " ".join(_cite_marker(c) for c in pattern.citations)
            )
            lines.append("")
    else:
        lines.append("No supported pattern was detected in the collected data.")
        lines.append("")
    lines += ["## Relationships", ""]
    for rel in report.relationships:
        lines.append(
            f"- `{rel.from_arn}` → `{rel.to_arn}` ({rel.relationship_type}, confidence "
            f"{rel.confidence:.2f}) " + " ".join(_cite_marker(c) for c in rel.citations)
        )
    if not report.relationships:
        lines.append("No relationships between collected resources were found.")
    lines += ["", "## Security Findings", ""]
    for finding in report.security_findings:
        lines.append(f"### [{finding.severity}] {finding.finding_type}")
        lines.append(f"{finding.description} {_cite_marker(finding.citation)}")
        lines.append("")
    if not report.security_findings:
        lines.append("No finding matched the rules of Requirement 6.6.")
        lines.append("")
    lines += ["## Patterns Not Detectable", ""]
    for item in report.undetectable_patterns:
        lines.append(f"- {item['pattern']}: {item['reason']}")
    lines += [
        "",
        "## Evidence Citations",
        "",
        "| Resource ARN | Spec File | Property Path | Source Checksum | Evidence |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    citations = [c for r in report.relationships for c in r.citations]
    citations += [c for p in report.patterns for c in p.citations]
    citations += [f.citation for f in report.security_findings]
    seen: set[tuple[str, str]] = set()
    for c in citations:
        if (c.spec_file, c.property_path) in seen:
            continue
        seen.add((c.spec_file, c.property_path))
        evidence = json.dumps(c.evidence_value, sort_keys=True).replace("|", "\\|")
        lines.append(
            f"| `{c.resource_arn}` | `{c.spec_file}` | `{c.property_path}` | "
            f"`{c.source_checksum[:12]}` | `{evidence}` |"
        )
    return "\n".join(lines) + "\n"
