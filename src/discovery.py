"""
Resource Discovery Module

This module provides the ResourceDiscovery class which enumerates AWS regions
and discovers resources of the minimum supported types across all of them,
in parallel, with graceful handling of inaccessible regions.

Requirements Coverage:
- Requirement 1.1: List all supported AWS resource types across all regions
- Requirement 1.2: Collect ARN, region, and basic metadata for all resources
- Requirement 1.3: Support EC2, S3, Lambda, RDS, VPC, Security Groups, IAM,
  CloudWatch log groups, Step Functions, and DynamoDB
- Requirement 1.4: Log the error and continue with other regions when a
  region is inaccessible
- Requirement 1.5: Discovery completes within 5 minutes for up to 1000
  resources
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Data Model
# ============================================================================


@dataclass
class DiscoveredResource:
    """
    A minimal description of a discovered AWS resource (Requirement 1.2).

    Attributes
    ----------
    resource_type: Internal resource type identifier, e.g. "aws_instance".
    resource_id: The AWS-assigned identifier/name for the resource.
    arn: The resource ARN (constructed if the API does not return one).
    region: The AWS region the resource was discovered in ("global" for
        account-wide services such as S3 and IAM).
    tags: Any tags attached to the resource, when available.
    """

    resource_type: str
    resource_id: str
    arn: str
    region: str
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class DiscoveryError:
    """A single discovery failure, scoped to a region and resource type."""

    region: str
    resource_type: str
    message: str

    def __str__(self) -> str:
        return f"[{self.region}] {self.resource_type}: {self.message}"


# ============================================================================
# Resource type -> (service, list method) definitions
# ============================================================================


def _extract_ec2_instances(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instance_id = instance["InstanceId"]
            tags = {t["Key"]: t["Value"] for t in instance.get("Tags", [])}
            resources.append(
                DiscoveredResource(
                    resource_type="aws_instance",
                    resource_id=instance_id,
                    arn=f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}",
                    region=region,
                    tags=tags,
                )
            )
    return resources


def _extract_vpcs(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for vpc in response.get("Vpcs", []):
        vpc_id = vpc["VpcId"]
        tags = {t["Key"]: t["Value"] for t in vpc.get("Tags", [])}
        resources.append(
            DiscoveredResource(
                resource_type="aws_vpc",
                resource_id=vpc_id,
                arn=f"arn:aws:ec2:{region}:{account_id}:vpc/{vpc_id}",
                region=region,
                tags=tags,
            )
        )
    return resources


def _extract_security_groups(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for sg in response.get("SecurityGroups", []):
        group_id = sg["GroupId"]
        tags = {t["Key"]: t["Value"] for t in sg.get("Tags", [])}
        resources.append(
            DiscoveredResource(
                resource_type="aws_security_group",
                resource_id=group_id,
                arn=f"arn:aws:ec2:{region}:{account_id}:security-group/{group_id}",
                region=region,
                tags=tags,
            )
        )
    return resources


def _extract_lambda_functions(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for fn in response.get("Functions", []):
        name = fn["FunctionName"]
        arn = fn.get("FunctionArn", f"arn:aws:lambda:{region}:{account_id}:function:{name}")
        resources.append(
            DiscoveredResource(
                resource_type="aws_lambda_function",
                resource_id=name,
                arn=arn,
                region=region,
            )
        )
    return resources


def _extract_rds_instances(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for db in response.get("DBInstances", []):
        db_id = db["DBInstanceIdentifier"]
        arn = db.get("DBInstanceArn", f"arn:aws:rds:{region}:{account_id}:db:{db_id}")
        resources.append(
            DiscoveredResource(
                resource_type="aws_db_instance",
                resource_id=db_id,
                arn=arn,
                region=region,
            )
        )
    return resources


def _extract_log_groups(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for lg in response.get("logGroups", []):
        name = lg["logGroupName"]
        # DescribeLogGroups returns "...:log-group:<name>:*"; drop the ":*" suffix.
        arn = lg.get("arn", f"arn:aws:logs:{region}:{account_id}:log-group:{name}")
        if arn.endswith(":*"):
            arn = arn[:-2]
        resources.append(
            DiscoveredResource(
                resource_type="aws_cloudwatch_log_group",
                resource_id=name,
                arn=arn,
                region=region,
            )
        )
    return resources


def _extract_state_machines(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for sm in response.get("stateMachines", []):
        name = sm["name"]
        arn = sm.get("stateMachineArn", f"arn:aws:states:{region}:{account_id}:stateMachine:{name}")
        resources.append(
            DiscoveredResource(
                resource_type="aws_sfn_state_machine",
                resource_id=name,
                arn=arn,
                region=region,
            )
        )
    return resources


def _extract_dynamodb_tables(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for name in response.get("TableNames", []):
        resources.append(
            DiscoveredResource(
                resource_type="aws_dynamodb_table",
                resource_id=name,
                arn=f"arn:aws:dynamodb:{region}:{account_id}:table/{name}",
                region=region,
            )
        )
    return resources


def _extract_s3_buckets(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for bucket in response.get("Buckets", []):
        name = bucket["Name"]
        resources.append(
            DiscoveredResource(
                resource_type="aws_s3_bucket",
                resource_id=name,
                arn=f"arn:aws:s3:::{name}",
                region=region,
            )
        )
    return resources


def _extract_iam_roles(
    response: dict[str, Any], region: str, account_id: str = ""
) -> list[DiscoveredResource]:
    resources = []
    for role in response.get("Roles", []):
        name = role["RoleName"]
        arn = role.get("Arn", f"arn:aws:iam::{account_id}:role/{name}")
        resources.append(
            DiscoveredResource(
                resource_type="aws_iam_role",
                resource_id=name,
                arn=arn,
                region=region,
            )
        )
    return resources


# Each entry: (resource_type, service_name, api_method_name, extractor_fn, api_kwargs)
_REGIONAL_DISCOVERERS: list[Any] = [
    ("aws_instance", "ec2", "describe_instances", _extract_ec2_instances, {}),
    ("aws_vpc", "ec2", "describe_vpcs", _extract_vpcs, {}),
    ("aws_security_group", "ec2", "describe_security_groups", _extract_security_groups, {}),
    ("aws_lambda_function", "lambda", "list_functions", _extract_lambda_functions, {}),
    ("aws_db_instance", "rds", "describe_db_instances", _extract_rds_instances, {}),
    ("aws_cloudwatch_log_group", "logs", "describe_log_groups", _extract_log_groups, {}),
    ("aws_sfn_state_machine", "stepfunctions", "list_state_machines", _extract_state_machines, {}),
    ("aws_dynamodb_table", "dynamodb", "list_tables", _extract_dynamodb_tables, {}),
]

# Account-wide ("global") resource types: discovered once, not per-region.
_GLOBAL_DISCOVERERS: list[Any] = [
    ("aws_s3_bucket", "s3", "list_buckets", _extract_s3_buckets, {}),
    ("aws_iam_role", "iam", "list_roles", _extract_iam_roles, {}),
]

# Region used to issue the account-wide ("global") API calls above.
_GLOBAL_REGION_LABEL = "global"
_DEFAULT_GLOBAL_CLIENT_REGION = "us-east-1"


# ============================================================================
# ResourceDiscovery
# ============================================================================


class ResourceDiscovery:
    """
    Discovers AWS resources of the minimum supported types across all regions.

    Parameters
    ----------
    aws_session:
        A boto3.Session-like object exposing ``.client(service_name,
        region_name=...)``. Each call must return a client exposing the
        relevant ``describe_*``/``list_*`` method used by this class.
    regions:
        Optional explicit list of region names to scan. If omitted, regions
        are enumerated via ``ec2.describe_regions()`` (Requirement 1.1).
    max_workers:
        Maximum number of regions discovered concurrently (Requirement 1.5).
    account_id:
        Account id used in ARNs that the list APIs do not return (EC2, DynamoDB).
    progress_callback:
        Optional callback invoked as ``callback(region, completed, total)``
        each time a region finishes discovery, so callers (e.g. the CLI) can
        display progress for long-running discovery operations.
    """

    def __init__(
        self,
        aws_session: Any,
        regions: list[str] | None = None,
        max_workers: int = 10,
        progress_callback: Callable[[str, int, int], None] | None = None,
        account_id: str = "",
    ) -> None:
        self.aws_session = aws_session
        self.account_id = account_id
        self._regions_override = regions
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self._errors: list[DiscoveryError] = []
        self._api_calls = 0
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_regions(self) -> list[str]:
        """
        Return the list of regions to scan (Requirement 1.1).

        Uses the explicit ``regions`` override if provided, otherwise calls
        ``ec2.describe_regions()`` against the default client region.
        """
        if self._regions_override is not None:
            return list(self._regions_override)

        try:
            ec2 = self.aws_session.client("ec2", region_name=_DEFAULT_GLOBAL_CLIENT_REGION)
            response = ec2.describe_regions(AllRegions=False)
            return [r["RegionName"] for r in response.get("Regions", [])]
        except Exception as exc:
            self._log_error(_DEFAULT_GLOBAL_CLIENT_REGION, "describe_regions", str(exc))
            return [_DEFAULT_GLOBAL_CLIENT_REGION]

    def discover_all_resources(self) -> list[DiscoveredResource]:
        """
        Discover all supported resource types across all regions (Req 1.1-1.4).

        Regions are scanned in parallel using a thread pool so that discovery
        across many regions completes quickly (Requirement 1.5). A failure
        discovering one region/resource type is logged and does not prevent
        discovery of the others (Requirement 1.4).
        """
        regions = self.get_regions()
        resources: list[DiscoveredResource] = []
        total_regions = len(regions)
        completed_regions = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._discover_region, region): region for region in regions}
            for future in as_completed(futures):
                region = futures[future]
                try:
                    resources.extend(future.result())
                except Exception as exc:
                    self._log_error(region, "region", str(exc))
                finally:
                    completed_regions += 1
                    if self.progress_callback is not None:
                        self.progress_callback(region, completed_regions, total_regions)

        # Global (account-wide) resources are only discovered once.
        resources.extend(self._discover_global())

        return resources

    def get_api_calls(self) -> int:
        """Number of list/describe API calls (pages) made so far (Requirement 10.2)."""
        return self._api_calls

    def get_errors(self) -> list[DiscoveryError]:
        """Return all discovery errors logged so far (Requirement 1.4)."""
        return list(self._errors)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _discover_region(self, region: str) -> list[DiscoveredResource]:
        """Discover every regional resource type within a single region."""
        resources: list[DiscoveredResource] = []
        for resource_type, service_name, method_name, extractor, kwargs in _REGIONAL_DISCOVERERS:
            resources.extend(
                self._safe_discover(
                    resource_type, service_name, method_name, extractor, region, kwargs
                )
            )
        return resources

    def _discover_global(self) -> list[DiscoveredResource]:
        """Discover account-wide resource types (S3 buckets, IAM roles)."""
        resources: list[DiscoveredResource] = []
        for resource_type, service_name, method_name, extractor, kwargs in _GLOBAL_DISCOVERERS:
            resources.extend(
                self._safe_discover(
                    resource_type,
                    service_name,
                    method_name,
                    extractor,
                    _GLOBAL_REGION_LABEL,
                    kwargs,
                    client_region=_DEFAULT_GLOBAL_CLIENT_REGION,
                )
            )
        return resources

    def _safe_discover(
        self,
        resource_type: str,
        service_name: str,
        method_name: str,
        extractor: Callable[[dict[str, Any], str, str], list[DiscoveredResource]],
        region: str,
        kwargs: dict[str, Any],
        client_region: str | None = None,
    ) -> list[DiscoveredResource]:
        """
        Call a single list/describe API and extract resources, logging and
        swallowing any error so other resource types/regions are unaffected
        (Requirement 1.4).
        """
        try:
            client = self.aws_session.client(service_name, region_name=client_region or region)
            if client.can_paginate(method_name) is True:
                found: list[DiscoveredResource] = []
                for page in client.get_paginator(method_name).paginate(**kwargs):
                    self._count_call()
                    found.extend(extractor(page, region, self.account_id))
                return found
            self._count_call()
            response = getattr(client, method_name)(**kwargs)
            return extractor(response, region, self.account_id)
        except Exception as exc:
            self._log_error(region, resource_type, f"{type(exc).__name__}: {exc}")
            return []

    def _count_call(self) -> None:
        with self._lock:
            self._api_calls += 1

    def _log_error(self, region: str, resource_type: str, message: str) -> None:
        error = DiscoveryError(region=region, resource_type=resource_type, message=message)
        self._errors.append(error)
        logger.warning(str(error))
