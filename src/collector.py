"""
Spec Collector Module

Collects the Specifications of a single AWS resource with one boto3 client,
classifying errors and retrying transient failures.

Requirements Coverage:
- Requirement 2.1: Collect the per-type Specifications schema (design.md)
- Requirement 2.2: S3 sub-configurations; missing ones are omitted, not errors
- Requirement 2.3 / 2.4: EC2 instance and Lambda function specifications
- Requirement 2.5: Access-denied calls are not retried, the missing permission is logged
- Requirement 2.6: Full API responses kept in ``raw_response`` keyed by operation
- Requirement 10.2: Every attempted API call is counted
- Requirement 12.1: At most 3 attempts, exponential backoff (1 s, 2 s)
- Requirement 12.2: Failed operations are recorded and collection continues
- Requirement 12.3: Throttling honours the Retry-After header
"""

from __future__ import annotations

import base64
import json
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from botocore.exceptions import (
    ClientError,
    ConnectionClosedError,
    ConnectTimeoutError,
    EndpointConnectionError,
    ReadTimeoutError,
)

from src import __version__
from src.parser import ResourceSpec, Result, SpecMetadata

logger = logging.getLogger(__name__)


# ============================================================================
# Exceptions and error payloads
# ============================================================================


class AccessDeniedError(Exception):
    """An API call was denied because of missing IAM permissions (Req 2.5)."""


class RateLimitError(Exception):
    """AWS throttled a call; ``retry_after`` seconds must pass before retrying (Req 12.3)."""

    def __init__(self, retry_after: float = 1, message: str = "Rate limit exceeded") -> None:
        super().__init__(message)
        self.retry_after = retry_after


@dataclass
class CollectorError:
    """Err payload of a ``collect_*`` Result when the primary call failed (Req 12.2)."""

    message: str
    resource_id: str
    error_type: str = "CollectorError"
    operation: str = ""
    retry_count: int = 0

    def error_message(self) -> str:
        return self.message

    def __str__(self) -> str:
        return f"{self.error_type}[{self.resource_id}]: {self.message}"


class CallStatus(StrEnum):
    """Outcome of one API operation (Req 12.4)."""

    SUCCESS = "success"
    NOT_CONFIGURED = "not_configured"
    DENIED = "denied"
    FAILED = "failed"


@dataclass
class OperationRecord:
    """One attempted API operation for a resource (Req 12.4)."""

    resource_arn: str
    operation: str
    status: CallStatus
    attempts: int
    error_type: str = ""
    detail: str = ""
    timestamp: str = ""


@dataclass
class RetryConfig:
    """Retry policy: ``max_attempts`` in total, delays base, base*multiplier, ... (Req 12.1)."""

    max_attempts: int = 3
    base_delay: float = 1.0
    backoff_multiplier: float = 2.0


# ============================================================================
# Error classification
# ============================================================================

DENIED_CODES = frozenset(
    {
        "AccessDenied",
        "AccessDeniedException",
        "UnauthorizedOperation",
        "AuthorizationError",
        "AuthorizationErrorException",
    }
)
THROTTLE_CODES = frozenset(
    {
        "Throttling",
        "ThrottlingException",
        "RequestLimitExceeded",
        "TooManyRequestsException",
        "SlowDown",
        "ProvisionedThroughputExceededException",
    }
)
NOT_CONFIGURED_CODES = frozenset(
    {
        "NoSuchBucketPolicy",
        "NoSuchTagSet",
        "NoSuchTagSetError",
        "NoSuchWebsiteConfiguration",
        "NoSuchCORSConfiguration",
        "NoSuchLifecycleConfiguration",
        "ServerSideEncryptionConfigurationNotFoundError",
        "NoSuchEntity",
        "ResourceNotFoundException",
    }
)
_TRANSIENT_EXCEPTIONS = (
    EndpointConnectionError,
    ConnectTimeoutError,
    ReadTimeoutError,
    ConnectionClosedError,
)

# Prefix used in IAM action names for each boto3 service name.
IAM_SERVICE_PREFIX = {
    "ec2": "ec2",
    "lambda": "lambda",
    "rds": "rds",
    "logs": "logs",
    "stepfunctions": "states",
    "dynamodb": "dynamodb",
    "s3": "s3",
    "iam": "iam",
}


@dataclass
class _Classified:
    kind: str  # "denied" | "throttle" | "missing" | "transient" | "permanent"
    error_type: str
    retry_after: float | None = None


def classify_exception(exc: BaseException) -> _Classified:
    """Map an exception raised by an API call onto a retry decision (design.md)."""
    if isinstance(exc, AccessDeniedError):
        return _Classified("denied", "AccessDenied")
    if isinstance(exc, RateLimitError):
        return _Classified("throttle", "Throttling", float(exc.retry_after))
    if isinstance(exc, ClientError):
        error = exc.response.get("Error", {})
        code = str(error.get("Code", "ClientError"))
        metadata = exc.response.get("ResponseMetadata", {})
        status = int(metadata.get("HTTPStatusCode", 0) or 0)
        if code in DENIED_CODES:
            return _Classified("denied", "AccessDenied")
        if code in THROTTLE_CODES:
            header = (metadata.get("HTTPHeaders") or {}).get("retry-after")
            retry_after = float(header) if header not in (None, "") else None
            return _Classified("throttle", code, retry_after)
        if code in NOT_CONFIGURED_CODES or code.startswith("NoSuch"):
            return _Classified("missing", code)
        if status >= 500:
            return _Classified("transient", code)
        return _Classified("permanent", code)
    if isinstance(exc, _TRANSIENT_EXCEPTIONS):
        return _Classified("transient", type(exc).__name__)
    # Unknown exceptions (network stacks, mocks) are treated as transient.
    return _Classified("transient", type(exc).__name__)


# ============================================================================
# JSON helpers
# ============================================================================


def jsonable(value: Any) -> Any:
    """Convert boto3 response values (datetime, bytes, ...) into JSON-safe values."""
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    if hasattr(value, "read") and callable(value.read):  # streaming bodies
        return jsonable(value.read())
    return value


def strip_metadata(response: dict[str, Any]) -> dict[str, Any]:
    """Copy of a response without ``ResponseMetadata``."""
    return {k: v for k, v in response.items() if k != "ResponseMetadata"}


def _pascal(method_name: str) -> str:
    return "".join(part.capitalize() for part in method_name.split("_"))


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


# ============================================================================
# Call execution with retry (single retry layer, Req 12.1)
# ============================================================================


@dataclass
class _CallOutcome:
    response: dict[str, Any] | None
    status: CallStatus
    attempts: int
    error_type: str = ""
    message: str = ""


def with_retry(
    call_fn: Callable[[], dict[str, Any]], collector: SpecCollector, resource_id: str
) -> dict[str, Any] | None:
    """Run ``call_fn`` with the collector's retry policy; the response or None."""
    return collector._execute(call_fn, "call", resource_id, service="", primary=True).response


# ============================================================================
# SpecCollector
# ============================================================================


class SpecCollector:
    """
    Collects resource Specifications using one boto3 client (or a mock).

    Every ``collect_*`` method returns ``Result.ok(ResourceSpec)``, or
    ``Result.err(CollectorError)`` when the primary call of the resource failed.
    Secondary calls (tags, attributes, policies) are best-effort.

    Attributes
    ----------
    api_calls:  number of API call attempts made (Req 10.2)
    operations: one :class:`OperationRecord` per API operation (Req 12.4)
    """

    def __init__(self, api_client: Any, retry_config: RetryConfig | None = None) -> None:
        self.api_client = api_client
        self.retry_config = retry_config or RetryConfig()
        self.api_calls = 0
        self.operations: list[OperationRecord] = []
        self._logs: list[str] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_logs(self) -> list[str]:
        """Messages logged during collection (permission and retry messages)."""
        with self._lock:
            return list(self._logs)

    def get_errors(self) -> list[OperationRecord]:
        """Operations that were denied or failed."""
        with self._lock:
            return [
                op for op in self.operations if op.status in (CallStatus.DENIED, CallStatus.FAILED)
            ]

    def collect_resource(
        self, resource_type: str, resource_id: str, arn: str, region: str, account_id: str
    ) -> Result[ResourceSpec, CollectorError]:
        """Dispatch to the ``collect_*`` method of ``resource_type``."""
        method = {
            "aws_instance": self.collect_ec2_spec,
            "aws_vpc": self.collect_vpc_spec,
            "aws_security_group": self.collect_security_group_spec,
            "aws_lambda_function": self.collect_lambda_spec,
            "aws_db_instance": self.collect_db_instance_spec,
            "aws_cloudwatch_log_group": self.collect_log_group_spec,
            "aws_sfn_state_machine": self.collect_state_machine_spec,
            "aws_dynamodb_table": self.collect_dynamodb_spec,
            "aws_s3_bucket": self.collect_s3_specs,
            "aws_iam_role": self.collect_iam_role_spec,
        }.get(resource_type)
        if method is None:
            return Result.err(
                CollectorError(
                    message=f"Unsupported resource type '{resource_type}'",
                    resource_id=resource_id,
                    error_type="UnsupportedResourceType",
                )
            )
        return method(resource_id, region=region, account_id=account_id, arn=arn)

    def collect_ec2_spec(
        self, instance_id: str, region: str = "", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """EC2 instance: ``Instances[0]`` of DescribeInstances (Req 2.3)."""
        arn = arn or f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}"
        ctx = _Context(self, "ec2", arn, instance_id)
        response = ctx.primary("describe_instances", InstanceIds=[instance_id])
        if response is None:
            return ctx.failure()
        instances = [
            inst
            for reservation in response.get("Reservations", [])
            for inst in reservation.get("Instances", [])
            if inst.get("InstanceId") == instance_id
        ]
        if not instances:
            return ctx.not_found()
        return ctx.build("aws_instance", region, account_id, dict(instances[0]))

    def collect_vpc_spec(
        self, vpc_id: str, region: str = "", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """VPC: ``Vpcs[0]`` + EnableDnsSupport / EnableDnsHostnames attributes."""
        arn = arn or f"arn:aws:ec2:{region}:{account_id}:vpc/{vpc_id}"
        ctx = _Context(self, "ec2", arn, vpc_id)
        response = ctx.primary("describe_vpcs", VpcIds=[vpc_id])
        if response is None:
            return ctx.failure()
        vpcs = response.get("Vpcs", [])
        if not vpcs:
            return ctx.not_found()
        specs = dict(vpcs[0])
        for attribute, key in (
            ("enableDnsSupport", "EnableDnsSupport"),
            ("enableDnsHostnames", "EnableDnsHostnames"),
        ):
            attr = ctx.secondary(
                "describe_vpc_attribute", f":{attribute}", VpcId=vpc_id, Attribute=attribute
            )
            if attr is not None:
                specs[key] = bool((attr.get(key) or {}).get("Value"))
        return ctx.build("aws_vpc", region, account_id, specs)

    def collect_security_group_spec(
        self, group_id: str, region: str = "", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """Security group: ``SecurityGroups[0]``."""
        arn = arn or f"arn:aws:ec2:{region}:{account_id}:security-group/{group_id}"
        ctx = _Context(self, "ec2", arn, group_id)
        response = ctx.primary("describe_security_groups", GroupIds=[group_id])
        if response is None:
            return ctx.failure()
        groups = response.get("SecurityGroups", [])
        if not groups:
            return ctx.not_found()
        return ctx.build("aws_security_group", region, account_id, dict(groups[0]))

    def collect_lambda_spec(
        self, function_name: str, region: str = "", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """Lambda: GetFunction ``Configuration`` + ``Tags`` (Req 2.4)."""
        fallback_arn = arn or f"arn:aws:lambda:{region}:{account_id}:function:{function_name}"
        ctx = _Context(self, "lambda", fallback_arn, function_name)
        response = ctx.primary("get_function", FunctionName=function_name)
        if response is None:
            return ctx.failure()
        specs = dict(response.get("Configuration", {}))
        if "Tags" in response:
            specs["Tags"] = response["Tags"]
        ctx.arn = arn or specs.get("FunctionArn") or fallback_arn
        return ctx.build("aws_lambda_function", region, account_id, specs)

    def collect_db_instance_spec(
        self, identifier: str, region: str = "", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """RDS: ``DBInstances[0]``."""
        arn = arn or f"arn:aws:rds:{region}:{account_id}:db:{identifier}"
        ctx = _Context(self, "rds", arn, identifier)
        response = ctx.primary("describe_db_instances", DBInstanceIdentifier=identifier)
        if response is None:
            return ctx.failure()
        instances = response.get("DBInstances", [])
        if not instances:
            return ctx.not_found()
        return ctx.build("aws_db_instance", region, account_id, dict(instances[0]))

    def collect_log_group_spec(
        self, log_group_name: str, region: str = "", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """CloudWatch log group: matching ``logGroups`` entry + ``tags``."""
        arn = arn or f"arn:aws:logs:{region}:{account_id}:log-group:{log_group_name}"
        ctx = _Context(self, "logs", arn, log_group_name)
        response = ctx.primary("describe_log_groups", logGroupNamePrefix=log_group_name)
        if response is None:
            return ctx.failure()
        groups = [
            g for g in response.get("logGroups", []) if g.get("logGroupName") == log_group_name
        ]
        if not groups:
            return ctx.not_found()
        specs = dict(groups[0])
        tags = ctx.secondary("list_tags_log_group", "", logGroupName=log_group_name)
        if tags is not None:
            specs["tags"] = tags.get("tags", {})
        return ctx.build("aws_cloudwatch_log_group", region, account_id, specs)

    def collect_state_machine_spec(
        self, name: str, region: str = "", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """Step Functions: DescribeStateMachine + ``tags``."""
        arn = arn or f"arn:aws:states:{region}:{account_id}:stateMachine:{name}"
        ctx = _Context(self, "stepfunctions", arn, name)
        response = ctx.primary("describe_state_machine", stateMachineArn=arn)
        if response is None:
            return ctx.failure()
        specs = strip_metadata(response)
        tags = ctx.secondary("list_tags_for_resource", "", resourceArn=arn)
        if tags is not None:
            specs["tags"] = tags.get("tags", [])
        return ctx.build("aws_sfn_state_machine", region, account_id, specs)

    def collect_dynamodb_spec(
        self, table_name: str, region: str = "", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """DynamoDB: DescribeTable ``Table`` + ``Tags``."""
        fallback_arn = arn or f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}"
        ctx = _Context(self, "dynamodb", fallback_arn, table_name)
        response = ctx.primary("describe_table", TableName=table_name)
        if response is None:
            return ctx.failure()
        specs = dict(response.get("Table", {}))
        table_arn = specs.get("TableArn") or fallback_arn
        tags = ctx.secondary("list_tags_of_resource", "", ResourceArn=table_arn)
        if tags is not None:
            specs["Tags"] = tags.get("Tags", [])
        return ctx.build("aws_dynamodb_table", region, account_id, specs)

    def collect_s3_specs(
        self, bucket_name: str, region: str = "global", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """
        S3 bucket: ``Name`` + the eight ``bucket-*`` sub-configurations (Req 2.2).

        Every sub-configuration is best-effort: missing ones are omitted, denied
        ones are logged with the missing ``s3:Get*`` permission (Req 2.5).
        """
        arn = arn or f"arn:aws:s3:::{bucket_name}"
        ctx = _Context(self, "s3", arn, bucket_name)
        specs: dict[str, Any] = {"Name": bucket_name}
        for spec_name, method_name in (
            ("bucket-acl", "get_bucket_acl"),
            ("bucket-cors", "get_bucket_cors"),
            ("bucket-encryption", "get_bucket_encryption"),
            ("bucket-lifecycle-configuration", "get_bucket_lifecycle_configuration"),
            ("bucket-policy", "get_bucket_policy"),
            ("bucket-tagging", "get_bucket_tagging"),
            ("bucket-versioning", "get_bucket_versioning"),
            ("bucket-website", "get_bucket_website"),
        ):
            response = ctx.secondary(method_name, "", Bucket=bucket_name)
            if response is not None:
                specs[spec_name] = strip_metadata(response)
        return ctx.build("aws_s3_bucket", region or "global", account_id, specs)

    def collect_iam_role_spec(
        self, role_name: str, region: str = "global", account_id: str = "", arn: str | None = None
    ) -> Result[ResourceSpec, CollectorError]:
        """IAM role: ``Role`` + ``AttachedPolicies`` + ``InlinePolicies``."""
        fallback_arn = arn or f"arn:aws:iam::{account_id}:role/{role_name}"
        ctx = _Context(self, "iam", fallback_arn, role_name)
        response = ctx.primary("get_role", RoleName=role_name)
        if response is None:
            return ctx.failure()
        specs = dict(response.get("Role", {}))
        ctx.arn = arn or specs.get("Arn") or fallback_arn
        attached = ctx.secondary("list_attached_role_policies", "", RoleName=role_name)
        if attached is not None:
            specs["AttachedPolicies"] = attached.get("AttachedPolicies", [])
        inline_names = ctx.secondary("list_role_policies", "", RoleName=role_name)
        if inline_names is not None:
            inline: dict[str, Any] = {}
            for policy_name in inline_names.get("PolicyNames", []):
                policy = ctx.secondary(
                    "get_role_policy", f":{policy_name}", RoleName=role_name, PolicyName=policy_name
                )
                if policy is not None:
                    inline[policy_name] = _policy_document(policy.get("PolicyDocument"))
            specs["InlinePolicies"] = inline
        if isinstance(specs.get("AssumeRolePolicyDocument"), str):
            specs["AssumeRolePolicyDocument"] = _policy_document(specs["AssumeRolePolicyDocument"])
        return ctx.build("aws_iam_role", region or "global", account_id, specs)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _log(self, message: str) -> None:
        with self._lock:
            self._logs.append(message)
        logger.info(message)

    def _record(self, record: OperationRecord) -> None:
        with self._lock:
            self.operations.append(record)

    def _count_call(self) -> None:
        with self._lock:
            self.api_calls += 1

    def _operation_name(self, method_name: str) -> str:
        mapping = getattr(getattr(self.api_client, "meta", None), "method_to_api_mapping", None)
        if isinstance(mapping, dict) and method_name in mapping:
            return str(mapping[method_name])
        return _pascal(method_name)

    def _api_version(self) -> str:
        model = getattr(getattr(self.api_client, "meta", None), "service_model", None)
        version = getattr(model, "api_version", "")
        return version if isinstance(version, str) else ""

    def _execute(
        self,
        call_fn: Callable[[], dict[str, Any]],
        operation: str,
        resource_ref: str,
        service: str,
        primary: bool,
    ) -> _CallOutcome:
        """Run one API operation with the retry policy and classify the outcome."""
        cfg = self.retry_config
        delay = cfg.base_delay
        last: _Classified | None = None
        message = ""
        for attempt in range(1, cfg.max_attempts + 1):
            self._count_call()
            try:
                return _CallOutcome(call_fn(), CallStatus.SUCCESS, attempt)
            except Exception as exc:  # noqa: BLE001 - classified below
                last = classify_exception(exc)
                message = f"{type(exc).__name__}: {exc}"

            if last.kind == "denied":
                prefix = IAM_SERVICE_PREFIX.get(service, service or "aws")
                self._log(
                    f"Permission denied calling {operation} for '{resource_ref}'. "
                    f"Missing {prefix}:{operation} permission."
                )
                return _CallOutcome(None, CallStatus.DENIED, attempt, "AccessDenied", message)
            if last.kind == "missing" and not primary:
                return _CallOutcome(None, CallStatus.NOT_CONFIGURED, attempt, last.error_type)
            if last.kind in ("missing", "permanent"):
                self._log(f"{operation} failed for '{resource_ref}': {message}")
                return _CallOutcome(None, CallStatus.FAILED, attempt, last.error_type, message)
            if attempt == cfg.max_attempts:
                break

            if last.kind == "throttle" and last.retry_after is not None:
                wait = last.retry_after
                self._log(
                    f"Rate limit hit for '{resource_ref}' calling {operation} "
                    f"(attempt {attempt}/{cfg.max_attempts}). Waiting {wait}s (retry-after)."
                )
            else:
                wait = delay
                delay *= cfg.backoff_multiplier
                self._log(
                    f"Transient error for '{resource_ref}' calling {operation} "
                    f"(attempt {attempt}/{cfg.max_attempts}): {message}. Retrying in {wait}s."
                )
            time.sleep(wait)

        self._log(
            f"All {cfg.max_attempts} attempts exhausted for '{resource_ref}' "
            f"calling {operation}: {message}."
        )
        error_type = last.error_type if last else "Unknown"
        return _CallOutcome(None, CallStatus.FAILED, cfg.max_attempts, error_type, message)


def _policy_document(document: Any) -> Any:
    """IAM returns policy documents as dicts (boto3) or URL-encoded JSON strings."""
    if isinstance(document, str):
        from urllib.parse import unquote

        try:
            return json.loads(unquote(document))
        except json.JSONDecodeError:
            return document
    return document


class _Context:
    """Per-resource collection state: records operations and raw responses."""

    def __init__(self, collector: SpecCollector, service: str, arn: str, resource_id: str) -> None:
        self.collector = collector
        self.service = service
        self.arn = arn
        self.resource_id = resource_id
        self.raw: dict[str, Any] = {}
        self.failed: _CallOutcome | None = None
        self.failed_operation = ""
        self.primary_operation = ""

    def _call(self, method_name: str, key_suffix: str, primary: bool, **kwargs: Any) -> Any:
        operation = self.collector._operation_name(method_name)
        if primary:
            self.primary_operation = operation
        method = getattr(self.collector.api_client, method_name)
        outcome = self.collector._execute(
            lambda: method(**kwargs), operation, self.resource_id, self.service, primary
        )
        self.collector._record(
            OperationRecord(
                resource_arn=self.arn,
                operation=operation + key_suffix,
                status=outcome.status,
                attempts=outcome.attempts,
                error_type=outcome.error_type,
                detail=outcome.message,
                timestamp=_utc_now(),
            )
        )
        if outcome.response is None:
            if primary:
                self.failed = outcome
                self.failed_operation = operation
            return None
        response = jsonable(outcome.response)
        self.raw[operation + key_suffix] = response
        return response

    def primary(self, method_name: str, **kwargs: Any) -> Any:
        return self._call(method_name, "", True, **kwargs)

    def secondary(self, method_name: str, key_suffix: str, **kwargs: Any) -> Any:
        return self._call(method_name, key_suffix, False, **kwargs)

    def failure(self) -> Result[ResourceSpec, CollectorError]:
        outcome = self.failed
        assert outcome is not None
        reason = f"after {outcome.attempts} attempts" if outcome.status == CallStatus.FAILED else ""
        return Result.err(
            CollectorError(
                message=f"Failed to collect {self.resource_id} ({self.failed_operation}) "
                f"{reason}: {outcome.message}".replace("  ", " "),
                resource_id=self.resource_id,
                error_type=outcome.error_type or "CollectorError",
                operation=self.failed_operation,
                retry_count=max(0, outcome.attempts - 1),
            )
        )

    def not_found(self) -> Result[ResourceSpec, CollectorError]:
        operation = self.primary_operation
        message = f"{operation} returned no match for '{self.resource_id}'"
        self.collector._log(message)
        with self.collector._lock:
            for record in reversed(self.collector.operations):
                if record.resource_arn == self.arn and record.operation == operation:
                    record.status = CallStatus.FAILED
                    record.error_type = "NotFound"
                    record.detail = message
                    break
        return Result.err(
            CollectorError(
                message=message,
                resource_id=self.resource_id,
                error_type="NotFound",
                operation=operation,
            )
        )

    def build(
        self, resource_type: str, region: str, account_id: str, specifications: dict[str, Any]
    ) -> Result[ResourceSpec, CollectorError]:
        spec = ResourceSpec(
            resource_type=resource_type,
            arn=self.arn,
            region=region,
            account_id=account_id,
            specifications=jsonable(strip_metadata(specifications)),
            metadata=SpecMetadata(
                collected_at=_utc_now(),
                collector_version=__version__,
                api_version=self.collector._api_version(),
                checksum="",
            ),
            raw_response=self.raw,
        )
        return Result.ok(spec)
