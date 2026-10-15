"""
Project scope: tag-seeded discovery, default-resource exclusion and the
dependency closure rules.

Requirements Coverage:
- Requirement 13.1: ``--project-tag KEY=VALUE`` (repeatable, AND) seeds discovery from
  ``tag:GetResources``; IAM roles through ``iam:ListRoles`` + ``iam:ListRoleTags``
- Requirement 13.2: Regions = regions holding seeds unless ``--region`` is given;
  global types are seeded from ``us-east-1``
- Requirement 13.3: References inside collected specs pull in the resources they name
- Requirement 13.4: Default VPC, its default security group, default subnets, its route
  tables and internet gateway, and service-linked roles are excluded unless referenced
  or ``--include-defaults`` is given
- Requirement 13.5: The scope is recorded in discovery.json, manifest.json and
  collection_report.json
- Requirement 14.4: Task definition revisions are not seeded from tags; they enter
  through the ECS services that run them
"""

from __future__ import annotations

import logging
import re
import threading
from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, NamedTuple

from src.discovery import DiscoveredResource, DiscoveryError
from src.integrity import iter_property_paths
from src.parser import ResourceSpec
from src.resource_types import (
    GLOBAL_REGION,
    REGISTRY,
    build_arn,
    parse_arn,
    s3_bucket_from_domain,
)

logger = logging.getLogger(__name__)

GLOBAL_CLIENT_REGION = "us-east-1"
SERVICE_LINKED_ROLE_PATH = "/aws-service-role/"
# Every registered revision carries the tags of its family; only the revisions services
# run are wanted, and the closure reaches those from the services (Req 14.4).
TAG_SEED_EXCLUDED_TYPES = frozenset({"aws_ecs_task_definition"})


def parse_project_tags(values: Iterable[str]) -> dict[str, str]:
    """``["k=v", ...]`` -> ``{"k": "v"}``; ValueError on a malformed or repeated key."""
    tags: dict[str, str] = {}
    for value in values:
        key, sep, tag_value = value.partition("=")
        if not sep or not key or not tag_value:
            raise ValueError(f"expected KEY=VALUE, got {value!r}")
        if key in tags:
            raise ValueError(f"tag key {key!r} given more than once")
        tags[key] = tag_value
    return tags


# ============================================================================
# Tag-seeded discovery (Requirements 13.1, 13.2)
# ============================================================================


class TagScopedDiscovery:
    """Discovers the resources carrying every project tag (same interface as ResourceDiscovery).

    Without ``regions`` every enabled region is queried; ``us-east-1`` is always queried,
    and when it was not requested only global-type ARNs are taken from it.
    """

    def __init__(
        self,
        aws_session: Any,
        tags: dict[str, str],
        regions: list[str] | None = None,
        max_workers: int = 10,
        progress_callback: Callable[[str, int, int], None] | None = None,
        account_id: str = "",
    ) -> None:
        self.aws_session = aws_session
        self.tags = dict(tags)
        self.account_id = account_id
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self._regions_override = regions
        self._regions: list[str] | None = None
        self._errors: list[DiscoveryError] = []
        self._api_calls = 0
        self._lock = threading.Lock()

    def get_regions(self) -> list[str]:
        """Regions whose tagging endpoint is queried."""
        if self._regions is None:
            if self._regions_override is not None:
                regions = list(self._regions_override)
            else:
                regions = self._enabled_regions()
            if GLOBAL_CLIENT_REGION not in regions:
                regions.append(GLOBAL_CLIENT_REGION)
            self._regions = regions
        return list(self._regions)

    def discover_all_resources(self) -> list[DiscoveredResource]:
        regions = self.get_regions()
        found: dict[str, DiscoveredResource] = {}
        with ThreadPoolExecutor(max_workers=max(1, self.max_workers)) as executor:
            futures = {executor.submit(self._seed_region, region): region for region in regions}
            for done, future in enumerate(as_completed(futures), start=1):
                for resource in future.result():
                    found.setdefault(resource.arn, resource)
                if self.progress_callback is not None:
                    self.progress_callback(futures[future], done, len(regions))
        for resource in self._seed_roles():
            found.setdefault(resource.arn, resource)
        return sorted(found.values(), key=lambda r: r.arn)

    def get_api_calls(self) -> int:
        return self._api_calls

    def get_errors(self) -> list[DiscoveryError]:
        return list(self._errors)

    def _enabled_regions(self) -> list[str]:
        try:
            ec2 = self.aws_session.client("ec2", region_name=GLOBAL_CLIENT_REGION)
            self._count_call()
            response = ec2.describe_regions(AllRegions=False)
            return [r["RegionName"] for r in response.get("Regions", [])]
        except Exception as exc:
            self._log_error(GLOBAL_CLIENT_REGION, "describe_regions", str(exc))
            return [GLOBAL_CLIENT_REGION]

    def _tag_filters(self) -> list[dict[str, Any]]:
        return [{"Key": key, "Values": [value]} for key, value in self.tags.items()]

    def _seed_region(self, region: str) -> list[DiscoveredResource]:
        global_only = self._regions_override is not None and region not in self._regions_override
        try:
            client = self.aws_session.client("resourcegroupstaggingapi", region_name=region)
            resources = []
            for page in self._pages(client, "get_resources", TagFilters=self._tag_filters()):
                for mapping in page.get("ResourceTagMappingList", []):
                    tags = {t["Key"]: t["Value"] for t in mapping.get("Tags", [])}
                    resource = self._resource(mapping["ResourceARN"], tags)
                    if resource is None:
                        continue
                    if global_only and resource.region != GLOBAL_REGION:
                        continue
                    resources.append(resource)
            return resources
        except Exception as exc:
            self._log_error(region, "tagging", f"{type(exc).__name__}: {exc}")
            return []

    def _seed_roles(self) -> list[DiscoveredResource]:
        """IAM roles are not returned by the tagging API: ListRoles + ListRoleTags."""
        try:
            iam = self.aws_session.client("iam", region_name=GLOBAL_CLIENT_REGION)
            resources = []
            for page in self._pages(iam, "list_roles"):
                for role in page.get("Roles", []):
                    tags = self._role_tags(iam, role["RoleName"])
                    if all(tags.get(k) == v for k, v in self.tags.items()):
                        resource = self._resource(role["Arn"], tags)
                        if resource is not None:
                            resource.attributes = {"Path": role.get("Path", "/")}
                            resources.append(resource)
            return resources
        except Exception as exc:
            self._log_error(GLOBAL_REGION, "aws_iam_role", f"{type(exc).__name__}: {exc}")
            return []

    def _role_tags(self, iam: Any, role_name: str) -> dict[str, str]:
        tags: dict[str, str] = {}
        for page in self._pages(iam, "list_role_tags", RoleName=role_name):
            tags.update({t["Key"]: t["Value"] for t in page.get("Tags", [])})
        return tags

    def _pages(self, client: Any, method: str, **kwargs: Any) -> Iterator[dict[str, Any]]:
        if client.can_paginate(method) is True:
            for page in client.get_paginator(method).paginate(**kwargs):
                self._count_call()
                yield page
        else:
            self._count_call()
            yield getattr(client, method)(**kwargs)

    def _resource(self, arn: str, tags: dict[str, str]) -> DiscoveredResource | None:
        parsed = parse_arn(arn)
        if parsed is None:
            return None
        type_id, resource_id, region = parsed
        if type_id in TAG_SEED_EXCLUDED_TYPES:
            return None
        return DiscoveredResource(
            resource_type=type_id,
            resource_id=resource_id,
            # EC2 ARNs are rebuilt so seeds and closure targets share one ARN format (the
            # tagging API may omit their account id); other ARNs are kept as returned.
            arn=(
                build_arn(type_id, resource_id, region, self.account_id)
                if REGISTRY[type_id].service == "ec2"
                else arn
            ),
            region=region,
            tags=tags,
        )

    def _count_call(self) -> None:
        with self._lock:
            self._api_calls += 1

    def _log_error(self, region: str, resource_type: str, message: str) -> None:
        error = DiscoveryError(region=region, resource_type=resource_type, message=message)
        with self._lock:
            self._errors.append(error)
        logger.warning(str(error))


def seed_regions(resources: Iterable[DiscoveredResource], requested: Iterable[str]) -> list[str]:
    """The run's regions: ``requested`` when given, else the regions holding regional seeds."""
    explicit = sorted(set(requested))
    if explicit:
        return explicit
    return sorted({r.region for r in resources if r.region != GLOBAL_REGION})


# ============================================================================
# Default exclusion (Requirement 13.4)
# ============================================================================


def is_service_linked_role(resource: DiscoveredResource) -> bool:
    if resource.resource_type != "aws_iam_role":
        return False
    path = resource.attributes.get("Path") or ""
    return path.startswith(SERVICE_LINKED_ROLE_PATH) or f":role{SERVICE_LINKED_ROLE_PATH}" in (
        resource.arn
    )


def exclude_defaults(
    resources: list[DiscoveredResource], include_defaults: bool = False
) -> tuple[list[DiscoveredResource], list[DiscoveredResource]]:
    """Split into (kept, excluded) account defaults: default VPCs with their default SG,
    default subnets (``DefaultForAz``), route tables and internet gateway, and
    service-linked roles."""
    if include_defaults:
        return list(resources), []
    default_vpcs = {
        (r.region, r.resource_id)
        for r in resources
        if r.resource_type == "aws_vpc" and r.attributes.get("IsDefault") is True
    }

    def in_default_vpc(resource: DiscoveredResource) -> bool:
        return (resource.region, resource.attributes.get("VpcId")) in default_vpcs

    def is_default(resource: DiscoveredResource) -> bool:
        kind = resource.resource_type
        if kind == "aws_vpc":
            return (resource.region, resource.resource_id) in default_vpcs
        if kind == "aws_security_group":
            return resource.attributes.get("GroupName") == "default" and in_default_vpc(resource)
        if kind == "aws_subnet":
            return resource.attributes.get("DefaultForAz") is True
        if kind == "aws_route_table":
            return in_default_vpc(resource)
        if kind == "aws_internet_gateway":
            vpcs = resource.attributes.get("VpcIds") or []
            return bool(vpcs) and all((resource.region, v) in default_vpcs for v in vpcs)
        return is_service_linked_role(resource)

    kept = [r for r in resources if not is_default(r)]
    excluded = [r for r in resources if is_default(r)]
    return kept, excluded


# ============================================================================
# Reference rules for the dependency closure (Requirement 13.3)
# ============================================================================


class Rule(NamedTuple):
    """``path`` in the source Specifications names a ``target`` resource.

    ``resolve`` maps the raw value to the target's id/name/ARN (or several, for
    comma-separated lists), or None when the value does not name such a resource (e.g.
    a route to ``local``, a non-S3 origin domain, a public container image).
    """

    path: str
    target: str
    resolve: Callable[[str], str | list[str] | None] | None = None


def _prefixed(prefix: str) -> Callable[[str], str | None]:
    return lambda value: value if value.startswith(prefix) else None


def _comma_list(value: str) -> list[str]:
    """Auto Scaling ``VPCZoneIdentifier``: ``"subnet-a,subnet-b"``."""
    return [part.strip() for part in value.split(",") if part.strip()]


_ECR_IMAGE = re.compile(
    r"^(?P<account>\d{12})\.dkr\.ecr\.(?P<region>[a-z0-9-]+)\.amazonaws\.com(?:\.cn)?/"
    r"(?P<repository>[^:@]+)(?:[:@].*)?$"
)


def ecr_repository_arn(image: str) -> str | None:
    """Repository ARN of a private ECR image URI (``<acct>.dkr.ecr.<region>...``), else None."""
    match = _ECR_IMAGE.match(image)
    if match is None:
        return None
    return f"arn:aws:ecr:{match['region']}:{match['account']}:repository/{match['repository']}"


def _arn_only(value: str) -> str | None:
    """Values that name a resource only when they are ARNs (event targets, endpoints)."""
    return value if value.startswith("arn:") else None


def _unqualified_function(value: str) -> str | None:
    """A Lambda ARN without its version/alias qualifier; other ARNs pass unchanged."""
    if not value.startswith("arn:"):
        return None
    parts = value.split(":")
    if len(parts) > 7 and parts[2] == "lambda" and parts[5] == "function":
        return ":".join(parts[:7])
    return value


def _target_rules(path: str, role_path: str) -> list[Rule]:
    """An event target ARN (any supported invocable type) and the role used to invoke it."""
    return [
        Rule(path, "aws_lambda_function", _unqualified_function),
        Rule(path, "aws_sqs_queue", _arn_only),
        Rule(path, "aws_sns_topic", _arn_only),
        Rule(path, "aws_sfn_state_machine", _arn_only),
        Rule(path, "aws_ecs_cluster", _arn_only),
        Rule(role_path, "aws_iam_role"),
    ]


# source type -> rules; "[]" walks every list element. Values are resource ids, names or
# ARNs; anything parse_arn rejects is ignored.
REFERENCE_RULES: dict[str, list[Rule]] = {
    "aws_instance": [
        Rule("VpcId", "aws_vpc"),
        Rule("SubnetId", "aws_subnet"),
        Rule("SecurityGroups[].GroupId", "aws_security_group"),
    ],
    "aws_security_group": [
        Rule("VpcId", "aws_vpc"),
        Rule("IpPermissions[].UserIdGroupPairs[].GroupId", "aws_security_group"),
        Rule("IpPermissionsEgress[].UserIdGroupPairs[].GroupId", "aws_security_group"),
    ],
    "aws_lambda_function": [
        Rule("Role", "aws_iam_role"),
        Rule("VpcConfig.VpcId", "aws_vpc"),
        Rule("VpcConfig.SubnetIds[]", "aws_subnet"),
        Rule("VpcConfig.SecurityGroupIds[]", "aws_security_group"),
        Rule("LoggingConfig.LogGroup", "aws_cloudwatch_log_group"),
    ],
    "aws_db_instance": [
        Rule("VpcSecurityGroups[].VpcSecurityGroupId", "aws_security_group"),
        Rule("DBSubnetGroup.VpcId", "aws_vpc"),
        Rule("DBSubnetGroup.Subnets[].SubnetIdentifier", "aws_subnet"),
        Rule("MonitoringRoleArn", "aws_iam_role"),
        Rule("AssociatedRoles[].RoleArn", "aws_iam_role"),
    ],
    "aws_sfn_state_machine": [
        Rule("roleArn", "aws_iam_role"),
        Rule(
            "loggingConfiguration.destinations[].cloudWatchLogsLogGroup.logGroupArn",
            "aws_cloudwatch_log_group",
        ),
    ],
    "aws_subnet": [Rule("VpcId", "aws_vpc")],
    "aws_route_table": [
        Rule("VpcId", "aws_vpc"),
        Rule("Associations[].SubnetId", "aws_subnet"),
        Rule("Routes[].GatewayId", "aws_internet_gateway", _prefixed("igw-")),
        Rule("Routes[].GatewayId", "aws_vpc_endpoint", _prefixed("vpce-")),
        Rule("Routes[].NatGatewayId", "aws_nat_gateway"),
    ],
    "aws_internet_gateway": [Rule("Attachments[].VpcId", "aws_vpc")],
    "aws_nat_gateway": [Rule("VpcId", "aws_vpc"), Rule("SubnetId", "aws_subnet")],
    "aws_vpc_endpoint": [
        Rule("VpcId", "aws_vpc"),
        Rule("RouteTableIds[]", "aws_route_table"),
        Rule("SubnetIds[]", "aws_subnet"),
        Rule("Groups[].GroupId", "aws_security_group"),
    ],
    "aws_lb": [
        Rule("VpcId", "aws_vpc"),
        Rule("AvailabilityZones[].SubnetId", "aws_subnet"),
        Rule("SecurityGroups[]", "aws_security_group"),
        Rule("Listeners[].ListenerArn", "aws_lb_listener"),
    ],
    "aws_lb_listener": [
        Rule("LoadBalancerArn", "aws_lb"),
        Rule("Certificates[].CertificateArn", "aws_acm_certificate"),
        Rule("DefaultActions[].TargetGroupArn", "aws_lb_target_group"),
        Rule("DefaultActions[].ForwardConfig.TargetGroups[].TargetGroupArn", "aws_lb_target_group"),
    ],
    "aws_lb_target_group": [
        Rule("VpcId", "aws_vpc"),
        Rule("LoadBalancerArns[]", "aws_lb"),
    ],
    # Load balancer origins are named by DNS name only, which does not identify an ARN;
    # they are matched offline by the Analysis_Engine (cdn_origin), not followed here.
    "aws_cloudfront_distribution": [
        Rule(
            "DistributionConfig.Origins.Items[].DomainName",
            "aws_s3_bucket",
            s3_bucket_from_domain,
        ),
        Rule("DistributionConfig.WebACLId", "aws_wafv2_web_acl"),
        Rule("DistributionConfig.ViewerCertificate.ACMCertificateArn", "aws_acm_certificate"),
    ],
    # Compute and data (Requirement 14.4).
    "aws_ecs_service": [
        Rule("clusterArn", "aws_ecs_cluster"),
        Rule("taskDefinition", "aws_ecs_task_definition"),
        Rule("loadBalancers[].targetGroupArn", "aws_lb_target_group"),
        Rule("networkConfiguration.awsvpcConfiguration.subnets[]", "aws_subnet"),
        Rule("networkConfiguration.awsvpcConfiguration.securityGroups[]", "aws_security_group"),
    ],
    "aws_ecs_task_definition": [
        Rule("taskRoleArn", "aws_iam_role"),
        Rule("executionRoleArn", "aws_iam_role"),
        Rule(
            "containerDefinitions[].logConfiguration.options.awslogs-group",
            "aws_cloudwatch_log_group",
        ),
        Rule("containerDefinitions[].image", "aws_ecr_repository", ecr_repository_arn),
    ],
    "aws_autoscaling_group": [
        Rule("LaunchTemplate.LaunchTemplateId", "aws_launch_template"),
        Rule(
            "MixedInstancesPolicy.LaunchTemplate.LaunchTemplateSpecification.LaunchTemplateId",
            "aws_launch_template",
        ),
        Rule("VPCZoneIdentifier", "aws_subnet", _comma_list),
        Rule("TargetGroupARNs[]", "aws_lb_target_group"),
    ],
    "aws_launch_template": [
        Rule("LaunchTemplateData.SecurityGroupIds[]", "aws_security_group"),
        Rule("LaunchTemplateData.NetworkInterfaces[].Groups[]", "aws_security_group"),
        Rule("LaunchTemplateData.NetworkInterfaces[].SubnetId", "aws_subnet"),
    ],
    "aws_elasticache_replication_group": [
        Rule("CacheCluster.SecurityGroups[].SecurityGroupId", "aws_security_group"),
        Rule("CacheSubnetGroup.VpcId", "aws_vpc"),
        Rule("CacheSubnetGroup.Subnets[].SubnetIdentifier", "aws_subnet"),
    ],
    "aws_sns_topic": [
        Rule("Subscriptions[].Endpoint", "aws_sqs_queue", _arn_only),
        Rule("Subscriptions[].Endpoint", "aws_lambda_function", _unqualified_function),
    ],
    "aws_cloudwatch_event_rule": _target_rules("Targets[].Arn", "Targets[].RoleArn"),
    "aws_scheduler_schedule": _target_rules("Target.Arn", "Target.RoleArn"),
}


def _target(
    target_type: str, value: str, spec: ResourceSpec, account_id: str
) -> DiscoveredResource | None:
    if value.startswith("arn:"):
        parsed = parse_arn(value)
        if parsed is None or parsed[0] != target_type:
            return None
        owner = value.split(":")[4]
        if owner and account_id and owner != account_id:
            return None  # another account's resource cannot be collected with these credentials
        _, resource_id, region = parsed
        arn = value[:-2] if value.endswith(":*") else value
        if REGISTRY[target_type].service == "ec2":
            arn = build_arn(target_type, resource_id, region, account_id)
    else:
        region = GLOBAL_REGION if REGISTRY[target_type].scope == "global" else spec.region
        resource_id = value
        arn = build_arn(target_type, resource_id, region, account_id)
    return DiscoveredResource(
        resource_type=target_type, resource_id=resource_id, arn=arn, region=region
    )


def extract_references(spec: ResourceSpec, account_id: str) -> list[DiscoveredResource]:
    """Resources named by ``spec``, one per target ARN, each with its ``referenced_by``."""
    targets: dict[str, DiscoveredResource] = {}
    for rule in REFERENCE_RULES.get(spec.resource_type, []):
        for path, value in iter_property_paths(spec.specifications, rule.path):
            if not isinstance(value, str) or not value:
                continue
            resolved = rule.resolve(value) if rule.resolve else value
            for name in [resolved] if isinstance(resolved, str) else resolved or []:
                if not name:
                    continue
                target = _target(rule.target, name, spec, account_id or spec.account_id)
                if target is None or target.arn == spec.arn:
                    continue
                entry = targets.setdefault(target.arn, target)
                reference = f"{spec.arn}#{path}"
                if reference not in entry.referenced_by:
                    entry.referenced_by.append(reference)
    return list(targets.values())


# ============================================================================
# Scope record (Requirement 13.5)
# ============================================================================


@dataclass(frozen=True)
class ScopeConfig:
    project_tags: dict[str, str]
    include_defaults: bool = False

    @property
    def mode(self) -> str:
        return "project_tag" if self.project_tags else "account"


def scope_document(
    config: ScopeConfig,
    regions: list[str],
    seeds: list[DiscoveredResource],
    excluded: list[DiscoveredResource],
    referenced: list[DiscoveredResource] | None = None,
) -> dict[str, Any]:
    """The ``scope`` block of discovery.json, manifest.json and collection_report.json."""
    pulled_in = {r.arn for r in referenced or []}
    document: dict[str, Any] = {
        "mode": config.mode,
        "project_tags": dict(sorted(config.project_tags.items())),
        "include_defaults": config.include_defaults,
        "regions": list(regions),
        "seed_resources": len(seeds),
        "excluded_defaults": sorted(r.arn for r in excluded if r.arn not in pulled_in),
    }
    if referenced is not None:
        document["referenced"] = [
            {"arn": r.arn, "resource_type": r.resource_type, "referenced_by": r.referenced_by}
            for r in sorted(referenced, key=lambda r: r.arn)
        ]
    return document
