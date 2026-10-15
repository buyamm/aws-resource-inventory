"""
Project scope: tag-seeded discovery, default-resource exclusion and the
dependency closure rules.

Requirements Coverage:
- Requirement 13.1: ``--project-tag KEY=VALUE`` (repeatable, AND) seeds discovery from
  ``tag:GetResources``; IAM roles through ``iam:ListRoles`` + ``iam:ListRoleTags``
- Requirement 13.2: Regions = regions holding seeds unless ``--region`` is given;
  global types are seeded from ``us-east-1``
- Requirement 13.3: References inside collected specs pull in the resources they name
- Requirement 13.4: Default VPC, its default security group and service-linked roles
  are excluded unless referenced or ``--include-defaults`` is given
- Requirement 13.5: The scope is recorded in discovery.json, manifest.json and
  collection_report.json
"""

from __future__ import annotations

import logging
import re
import threading
from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from src.discovery import DiscoveredResource, DiscoveryError
from src.parser import ResourceSpec
from src.resource_types import GLOBAL_REGION, REGISTRY, build_arn, parse_arn

logger = logging.getLogger(__name__)

GLOBAL_CLIENT_REGION = "us-east-1"
SERVICE_LINKED_ROLE_PATH = "/aws-service-role/"


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
        return DiscoveredResource(
            resource_type=type_id,
            resource_id=resource_id,
            # Rebuilt so seeds and closure targets share one ARN format (the tagging
            # API may omit the account id of EC2 ARNs).
            arn=(
                arn
                if type_id == "aws_iam_role"
                else build_arn(type_id, resource_id, region, self.account_id)
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
    """Split into (kept, excluded): default VPCs, their default SG, service-linked roles."""
    if include_defaults:
        return list(resources), []
    default_vpcs = {
        (r.region, r.resource_id)
        for r in resources
        if r.resource_type == "aws_vpc" and r.attributes.get("IsDefault") is True
    }

    def is_default(resource: DiscoveredResource) -> bool:
        if resource.resource_type == "aws_vpc":
            return (resource.region, resource.resource_id) in default_vpcs
        if resource.resource_type == "aws_security_group":
            return (
                resource.attributes.get("GroupName") == "default"
                and (
                    resource.region,
                    resource.attributes.get("VpcId"),
                )
                in default_vpcs
            )
        return is_service_linked_role(resource)

    kept = [r for r in resources if not is_default(r)]
    excluded = [r for r in resources if is_default(r)]
    return kept, excluded


# ============================================================================
# Reference rules for the dependency closure (Requirement 13.3)
# ============================================================================

# source type -> [(Specifications path, target type)]; "[]" walks every list element.
# Values are resource ids, names or ARNs; anything parse_arn rejects is ignored.
REFERENCE_RULES: dict[str, list[tuple[str, str]]] = {
    "aws_instance": [
        ("VpcId", "aws_vpc"),
        ("SecurityGroups[].GroupId", "aws_security_group"),
    ],
    "aws_security_group": [
        ("VpcId", "aws_vpc"),
        ("IpPermissions[].UserIdGroupPairs[].GroupId", "aws_security_group"),
        ("IpPermissionsEgress[].UserIdGroupPairs[].GroupId", "aws_security_group"),
    ],
    "aws_lambda_function": [
        ("Role", "aws_iam_role"),
        ("VpcConfig.VpcId", "aws_vpc"),
        ("VpcConfig.SecurityGroupIds[]", "aws_security_group"),
        ("LoggingConfig.LogGroup", "aws_cloudwatch_log_group"),
    ],
    "aws_db_instance": [
        ("VpcSecurityGroups[].VpcSecurityGroupId", "aws_security_group"),
        ("DBSubnetGroup.VpcId", "aws_vpc"),
        ("MonitoringRoleArn", "aws_iam_role"),
        ("AssociatedRoles[].RoleArn", "aws_iam_role"),
    ],
    "aws_sfn_state_machine": [
        ("roleArn", "aws_iam_role"),
        (
            "loggingConfiguration.destinations[].cloudWatchLogsLogGroup.logGroupArn",
            "aws_cloudwatch_log_group",
        ),
    ],
}

_SEGMENT = re.compile(r"^([^\[\]]+)((?:\[\])*)$")


def _walk(value: Any, segments: list[str], path: str) -> Iterator[tuple[str, Any]]:
    if not segments:
        yield path, value
        return
    match = _SEGMENT.match(segments[0])
    if match is None or not isinstance(value, dict) or match.group(1) not in value:
        return
    key, lists = match.group(1), match.group(2).count("[]")
    items: list[tuple[str, Any]] = [(f"{path}.{key}", value[key])]
    for _ in range(lists):
        items = [
            (f"{p}[{i}]", element)
            for p, v in items
            if isinstance(v, list)
            for i, element in enumerate(v)
        ]
    for item_path, item in items:
        yield from _walk(item, segments[1:], item_path)


def _target(
    target_type: str, value: str, spec: ResourceSpec, account_id: str
) -> DiscoveredResource | None:
    if value.startswith("arn:"):
        parsed = parse_arn(value)
        if parsed is None or parsed[0] != target_type:
            return None
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
    for rule_path, target_type in REFERENCE_RULES.get(spec.resource_type, []):
        for path, value in _walk(spec.specifications or {}, rule_path.split("."), "specifications"):
            if not isinstance(value, str) or not value:
                continue
            target = _target(target_type, value, spec, account_id or spec.account_id)
            if target is None or target.arn == spec.arn:
                continue
            entry = targets.setdefault(target.arn, target)
            entry.referenced_by.append(f"{spec.arn}#{path}")
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
