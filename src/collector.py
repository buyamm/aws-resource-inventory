"""
Spec Collector Module

This module provides the SpecCollector class for collecting AWS resource specifications
with resilience features: exponential backoff retry, rate limit handling, and graceful
permission error continuation.

Requirements Coverage:
- Requirement 2.1: Collect all available configuration specifications
- Requirement 2.5: Log missing permissions and continue with available specs
- Requirement 2.6: Preserve raw API response in collected specification
- Requirement 12.1: Retry up to 3 times with exponential backoff
- Requirement 12.2: Log error and continue with next resource after retry exhaustion
- Requirement 12.3: Wait and retry according to AWS retry-after headers
"""

import time
import logging
import functools
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.parser import ResourceSpec, SpecMetadata, Result


# ============================================================================
# Custom Exception Types
# ============================================================================

class AccessDeniedError(Exception):
    """
    Raised when an AWS API call is denied due to missing IAM permissions.

    The collector catches this to log the missing permission and continue
    collecting other available specifications (Requirement 2.5).
    """
    pass


class RateLimitError(Exception):
    """
    Raised when AWS throttles an API call.

    Contains a ``retry_after`` attribute (seconds) that the collector must
    honour before retrying (Requirement 12.3).
    """

    def __init__(self, retry_after: int = 1, message: str = "Rate limit exceeded") -> None:
        super().__init__(message)
        self.retry_after = retry_after


# ============================================================================
# Collector Error (used as the Err payload in Result returns)
# ============================================================================

@dataclass
class CollectorError:
    """Structured error returned when collection ultimately fails."""
    message: str
    resource_id: str
    error_type: str = "CollectorError"

    def error_message(self) -> str:
        return self.message

    def __str__(self) -> str:
        return f"{self.error_type}[{self.resource_id}]: {self.message}"


# ============================================================================
# Retry configuration
# ============================================================================

@dataclass
class RetryConfig:
    """Exponential-backoff retry configuration."""
    max_attempts: int = 3
    base_delay: float = 1.0        # seconds
    backoff_multiplier: float = 2.0


def with_retry(call_fn: Callable[[], Dict[str, Any]], collector: "SpecCollector", resource_id: str) -> Optional[Dict[str, Any]]:
    """
    Shared retry decorator logic (Req 12.1, 12.2, 12.3).

    Executes ``call_fn()`` with exponential-backoff retry, honouring
    :class:`RateLimitError.retry_after` and logging via ``collector._log``.
    Used by every ``collect_*`` method so the retry/backoff behaviour lives
    in a single place instead of being duplicated per resource type.

    Returns the successful response dict, or ``None`` if all attempts fail.
    """
    cfg = collector.retry_config
    delay = cfg.base_delay

    for attempt in range(1, cfg.max_attempts + 1):
        try:
            return call_fn()
        except RateLimitError as exc:
            wait = exc.retry_after
            collector._log(
                f"Rate limit hit for '{resource_id}' "
                f"(attempt {attempt}/{cfg.max_attempts}). "
                f"Waiting {wait}s (retry-after)."
            )
            time.sleep(wait)
            # Do NOT count the rate-limit wait against the backoff multiplier;
            # subsequent attempts still use exponential growth from the base.
        except Exception as exc:
            if attempt < cfg.max_attempts:
                collector._log(
                    f"Transient error for '{resource_id}' "
                    f"(attempt {attempt}/{cfg.max_attempts}): "
                    f"{type(exc).__name__}: {exc}. "
                    f"Retrying in {delay}s."
                )
                time.sleep(delay)
                delay *= cfg.backoff_multiplier
            else:
                collector._log(
                    f"All {cfg.max_attempts} attempts exhausted for "
                    f"'{resource_id}': {type(exc).__name__}: {exc}."
                )
    return None


def resilient_call(resource_id_arg: str = "resource_id"):
    """
    Decorator that wraps a ``collect_*`` method's AWS call with retry/backoff.

    The decorated method must accept ``self`` and the resource identifier as
    its first positional argument, and must return the raw AWS API response
    (or raise on failure). Wraps :func:`with_retry` so each ``collect_*``
    method no longer has to build its own retry closure.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self: "SpecCollector", resource_id: str, *args: Any, **kwargs: Any) -> Optional[Dict[str, Any]]:
            return with_retry(
                lambda: func(self, resource_id, *args, **kwargs),
                collector=self,
                resource_id=resource_id,
            )
        return wrapper
    return decorator


# ============================================================================
# SpecCollector
# ============================================================================

class SpecCollector:
    """
    Collects AWS resource specifications with resilience against transient failures.

    Features
    --------
    * Exponential-backoff retry on transient exceptions (Req 12.1, 12.2)
    * Respects ``retry_after`` on :class:`RateLimitError` (Req 12.3)
    * Logs :class:`AccessDeniedError` and continues collecting other specs (Req 2.5)
    * Stores the raw API response verbatim in the resulting :class:`ResourceSpec` (Req 2.6)

    Parameters
    ----------
    api_client:
        A boto3 client (or mock) that exposes the AWS API methods used by this
        collector.  The exact method names are documented on each ``collect_*``
        method.
    retry_config:
        Optional custom :class:`RetryConfig`.  Defaults to 3 attempts with a
        1-second base delay and a 2× multiplier.
    """

    def __init__(
        self,
        api_client: Any,
        retry_config: Optional[RetryConfig] = None,
    ) -> None:
        self.api_client = api_client
        self.retry_config = retry_config or RetryConfig()
        self._logs: List[str] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def collect_ec2_spec(self, instance_id: str) -> Result:
        """
        Collect EC2 instance specification.

        Calls ``api_client.describe_instances(InstanceIds=[instance_id])``.
        Retries up to ``retry_config.max_attempts`` times with exponential
        backoff on transient failures (Req 12.1).

        Returns
        -------
        Result
            Ok(:class:`ResourceSpec`) on success; Err(:class:`CollectorError`)
            after all retry attempts are exhausted (Req 12.2).
        """
        raw = self._fetch_ec2(instance_id)
        if raw is None:
            return Result.err(CollectorError(
                message=f"Failed to collect EC2 spec for {instance_id} after "
                        f"{self.retry_config.max_attempts} attempts",
                resource_id=instance_id,
                error_type="RetryExhaustedError",
            ))

        spec = self._build_spec(
            resource_type="aws_instance",
            arn=f"arn:aws:ec2:unknown:unknown:instance/{instance_id}",
            region="unknown",
            account_id="unknown",
            specifications={"instance_id": instance_id},
            raw_response=raw,
        )
        return Result.ok(spec)

    def collect_s3_specs(self, bucket_name: str) -> Result:
        """
        Collect all S3 bucket specifications (Req 2.2).

        For each sub-spec listed below the method calls the corresponding
        ``api_client`` method.  If a call raises :class:`AccessDeniedError` the
        sub-spec is skipped, the error is logged, and collection continues.

        Sub-specs collected
        -------------------
        bucket-acl, bucket-cors, bucket-encryption,
        bucket-lifecycle-configuration, bucket-policy, bucket-tagging,
        bucket-versioning, bucket-website
        """
        specs: Dict[str, Any] = {}
        raw_parts: Dict[str, Any] = {}

        sub_specs = [
            ("bucket-acl",                    "get_bucket_acl",                    {"Bucket": bucket_name}),
            ("bucket-cors",                   "get_bucket_cors",                   {"Bucket": bucket_name}),
            ("bucket-encryption",             "get_bucket_encryption",             {"Bucket": bucket_name}),
            ("bucket-lifecycle-configuration","get_bucket_lifecycle_configuration",{"Bucket": bucket_name}),
            ("bucket-policy",                 "get_bucket_policy",                 {"Bucket": bucket_name}),
            ("bucket-tagging",                "get_bucket_tagging",                {"Bucket": bucket_name}),
            ("bucket-versioning",             "get_bucket_versioning",             {"Bucket": bucket_name}),
            ("bucket-website",                "get_bucket_website",                {"Bucket": bucket_name}),
        ]

        for spec_name, method_name, kwargs in sub_specs:
            response = self._safe_collect(spec_name, method_name, kwargs, bucket_name)
            if response is not None:
                specs[spec_name] = response
                raw_parts[spec_name] = response

        spec = self._build_spec(
            resource_type="aws_s3_bucket",
            arn=f"arn:aws:s3:::{bucket_name}",
            region="global",
            account_id="unknown",
            specifications=specs,
            raw_response=raw_parts,
        )
        return Result.ok(spec)

    def collect_lambda_spec(self, function_name: str) -> Result:
        """
        Collect Lambda function specification.

        Calls ``api_client.get_function(FunctionName=function_name)``.
        Retries on transient errors and respects the ``retry_after`` value
        from :class:`RateLimitError` (Req 12.3).
        """
        raw = self._fetch_lambda(function_name)
        if raw is None:
            return Result.err(CollectorError(
                message=f"Failed to collect Lambda spec for {function_name} after "
                        f"{self.retry_config.max_attempts} attempts",
                resource_id=function_name,
                error_type="RetryExhaustedError",
            ))

        config = raw.get("Configuration", {})
        arn = config.get(
            "FunctionArn",
            f"arn:aws:lambda:unknown:unknown:function:{function_name}",
        )

        spec = self._build_spec(
            resource_type="aws_lambda_function",
            arn=arn,
            region="unknown",
            account_id="unknown",
            specifications=config,
            raw_response=raw,
        )
        return Result.ok(spec)

    def get_logs(self) -> List[str]:
        """Return all log messages emitted during collection."""
        return list(self._logs)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @resilient_call()
    def _fetch_ec2(self, instance_id: str) -> Dict[str, Any]:
        """Raw ``describe_instances`` call, wrapped with retry/backoff."""
        return self.api_client.describe_instances(InstanceIds=[instance_id])

    @resilient_call()
    def _fetch_lambda(self, function_name: str) -> Dict[str, Any]:
        """Raw ``get_function`` call, wrapped with retry/backoff."""
        return self.api_client.get_function(FunctionName=function_name)

    def _safe_collect(
        self,
        spec_name: str,
        method_name: str,
        kwargs: Dict[str, Any],
        resource_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Call ``api_client.<method_name>(**kwargs)`` and swallow errors.

        Shared error-handling pattern for "collect many independent sub-specs,
        skip and log whichever ones fail" (Req 2.5): on
        :class:`AccessDeniedError` the missing permission is logged; any other
        exception is logged as a generic collection error. In both cases
        ``None`` is returned so the caller can skip this sub-spec and continue.
        """
        try:
            method = getattr(self.api_client, method_name)
            return method(**kwargs)
        except AccessDeniedError as exc:
            self._log(
                f"Permission denied collecting {spec_name} for "
                f"'{resource_name}': {exc}. "
                f"Missing s3:{_to_permission_name(method_name)} permission."
            )
        except Exception as exc:
            self._log(
                f"Error collecting {spec_name} for '{resource_name}': "
                f"{type(exc).__name__}: {exc}"
            )
        return None

    @staticmethod
    def _build_spec(
        resource_type: str,
        arn: str,
        region: str,
        account_id: str,
        specifications: Dict[str, Any],
        raw_response: Any,
    ) -> ResourceSpec:
        """Construct a ResourceSpec with current timestamp metadata."""
        metadata = SpecMetadata(
            collected_at=datetime.utcnow().isoformat(),
            collector_version="1.0.0",
            api_version="2006-03-01",
            checksum="",
        )
        return ResourceSpec(
            resource_type=resource_type,
            arn=arn,
            region=region,
            account_id=account_id,
            specifications=specifications,
            metadata=metadata,
            raw_response=raw_response,
        )

    def _log(self, message: str) -> None:
        """Append a message to the internal log."""
        self._logs.append(message)


# ============================================================================
# Utility helpers
# ============================================================================

def _to_permission_name(method_name: str) -> str:
    """Convert a boto3 method name like 'get_bucket_policy' to 'GetBucketPolicy'."""
    return "".join(part.capitalize() for part in method_name.split("_"))
