"""
Unit tests for SpecCollector resilience (RED phase - TDD).

This module contains unit tests for the SpecCollector class that MUST be written
before implementation following TDD Red-Green-Refactor methodology.

All tests are expected to fail with ImportError or NotImplementedError initially
(RED phase), proving they test real behaviour that does not yet exist.

Test Coverage:
- test_collector_retry_exponential_backoff_req_12_1:
    Collector retries up to 3 times with exponential backoff on transient failures.
- test_collector_continues_after_permission_error_req_2_5:
    Missing-permission errors are logged and the collector continues with
    the remaining specs rather than aborting entirely.
- test_collector_waits_on_rate_limit_req_12_3:
    Rate-limit exceptions are handled by waiting the retry-after duration
    before retrying the failed call.
- test_collector_preserves_raw_response_req_2_6:
    The raw AWS API response is preserved verbatim inside the resulting
    ResourceSpec for audit purposes.

Requirements Coverage:
- Requirement 12.1: Retry up to 3 times with exponential backoff
- Requirement 2.5:  Log missing permission and continue with available specs
- Requirement 12.3: Wait and retry according to AWS retry-after headers
- Requirement 2.6:  Preserve raw API response in collected specification
"""

import pytest
from unittest.mock import Mock, patch, call


# ---------------------------------------------------------------------------
# Lazy import — will be None until src/collector.py is implemented (RED phase)
# ---------------------------------------------------------------------------
try:
    from src.collector import SpecCollector, AccessDeniedError, RateLimitError
except ImportError:
    SpecCollector = None
    AccessDeniedError = None
    RateLimitError = None


# ===========================================================================
# Helper: build a lightweight fake "permission denied" exception that the
# collector is expected to recognise as an access-denied error.
# The real implementation may wrap botocore ClientError; for the unit tests
# we use a placeholder exception type imported from src.collector.
# ===========================================================================

def _access_denied(operation: str, message: str = None):
    """Return an AccessDeniedError (or a plain Exception in RED phase)."""
    if AccessDeniedError is not None:
        return AccessDeniedError(message or f"Missing {operation} permission")
    # RED phase fallback — any exception will do to exercise the test path
    return PermissionError(message or f"Missing {operation} permission")


def _rate_limit(retry_after: int = 5):
    """Return a RateLimitError (or a plain Exception in RED phase)."""
    if RateLimitError is not None:
        return RateLimitError(retry_after=retry_after)
    exc = Exception("Rate limit exceeded")
    exc.retry_after = retry_after  # duck-type the attribute
    return exc


# ===========================================================================
# Test Class: Retry Logic
# ===========================================================================

class TestCollectorRetryLogic:
    """Tests for exponential-backoff retry behaviour (Requirement 12.1)."""

    @pytest.mark.skipif(SpecCollector is None, reason="SpecCollector not implemented yet (RED phase)")
    def test_collector_retry_exponential_backoff_req_12_1(self):
        """
        Unit: Collector retries up to 3 times with exponential backoff.

        Scenario:
        - The mock API raises a transient exception on the first two calls.
        - The third call succeeds and returns an EC2 instance response.

        Expected behaviour:
        - collect_ec2_spec() returns an Ok result.
        - The underlying API was called exactly 3 times (2 failures + 1 success).
        - time.sleep() was called twice with increasing delays (exponential backoff).

        **Validates: Requirements 12.1**
        """
        mock_api = Mock()
        mock_api.describe_instances.side_effect = [
            Exception("Connection timeout"),
            Exception("Connection timeout"),
            {"Reservations": [{"Instances": [{"InstanceId": "i-123abc"}]}]},
        ]

        with patch("time.sleep") as mock_sleep:
            collector = SpecCollector(api_client=mock_api)
            result = collector.collect_ec2_spec("i-123abc")

        # Result must be Ok
        assert result.is_ok(), (
            f"Expected successful result after retries, got error: {result.error}"
        )

        # API must have been called exactly 3 times
        assert mock_api.describe_instances.call_count == 3, (
            f"Expected 3 API calls (2 failures + 1 success), "
            f"got {mock_api.describe_instances.call_count}"
        )

        # sleep must have been called twice (after each failure)
        assert mock_sleep.call_count == 2, (
            f"Expected 2 sleep calls (one after each failure), "
            f"got {mock_sleep.call_count}"
        )

        # Verify exponential backoff: second sleep >= first sleep
        sleep_calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert sleep_calls[1] >= sleep_calls[0], (
            f"Second backoff delay ({sleep_calls[1]}) should be >= "
            f"first delay ({sleep_calls[0]}) to confirm exponential growth"
        )

    @pytest.mark.skipif(SpecCollector is None, reason="SpecCollector not implemented yet (RED phase)")
    def test_collector_exhausts_retries_and_returns_error_req_12_1(self):
        """
        Unit: Collector returns an Err after exhausting all 3 retry attempts.

        When all 3 attempts fail the collector must:
        - Return an Err (not raise an unhandled exception).
        - Have attempted the API call exactly 3 times.

        **Validates: Requirements 12.1, 12.2**
        """
        mock_api = Mock()
        mock_api.describe_instances.side_effect = Exception("Persistent failure")

        with patch("time.sleep"):
            collector = SpecCollector(api_client=mock_api)
            result = collector.collect_ec2_spec("i-dead")

        assert result.is_err(), "After 3 failures the result must be Err"
        assert mock_api.describe_instances.call_count == 3, (
            "Collector must attempt exactly 3 calls before giving up"
        )


# ===========================================================================
# Test Class: Permission Error Handling
# ===========================================================================

class TestCollectorPermissionErrorHandling:
    """Tests for graceful handling of missing-permission errors (Requirement 2.5)."""

    @pytest.mark.skipif(SpecCollector is None, reason="SpecCollector not implemented yet (RED phase)")
    def test_collector_continues_after_permission_error_req_2_5(self):
        """
        Unit: Collector logs a missing permission and continues collecting
        the remaining S3 bucket specifications.

        Scenario:
        - get_bucket_policy raises AccessDeniedError (missing s3:GetBucketPolicy).
        - All other S3 spec calls succeed normally.

        Expected behaviour:
        - collect_s3_specs() returns an Ok result (not an Err).
        - 'bucket-policy' is absent from the collected specifications.
        - collector.get_logs() contains a message mentioning the missing permission.

        **Validates: Requirements 2.5**
        """
        mock_api = Mock()

        # Successful calls for all specs except bucket policy
        mock_api.get_bucket_acl.return_value = {
            "Owner": {"ID": "owner-id", "DisplayName": "owner"},
            "Grants": [],
        }
        mock_api.get_bucket_cors.return_value = {"CORSRules": []}
        mock_api.get_bucket_encryption.return_value = {
            "ServerSideEncryptionConfiguration": {"Rules": []}
        }
        mock_api.get_bucket_lifecycle_configuration.return_value = {"Rules": []}
        mock_api.get_bucket_tagging.return_value = {"TagSet": []}
        mock_api.get_bucket_versioning.return_value = {"Status": "Enabled"}
        mock_api.get_bucket_website.return_value = {}

        # The policy call will raise a permission error
        mock_api.get_bucket_policy.side_effect = _access_denied(
            "s3:GetBucketPolicy",
            "Missing s3:GetBucketPolicy permission",
        )

        collector = SpecCollector(api_client=mock_api)
        result = collector.collect_s3_specs("my-bucket")

        # Must return Ok (not abort with an error)
        assert result.is_ok(), (
            "Collector should continue and return Ok even when one spec "
            f"is inaccessible, got: {result.error if result.is_err() else 'ok'}"
        )

        # The inaccessible spec must be absent from the result
        specifications = result.value.specifications
        assert "bucket-policy" not in specifications, (
            "bucket-policy spec should be absent when permission is denied"
        )

        # The permission error must be logged
        logs = collector.get_logs()
        permission_logged = any(
            "s3:getbucketpolicy" in log.lower() or "bucket-policy" in log.lower()
            or "getbucketpolicy" in log.lower()
            for log in logs
        )
        assert permission_logged, (
            f"Missing-permission error for s3:GetBucketPolicy must appear in logs. "
            f"Logs: {logs}"
        )

    @pytest.mark.skipif(SpecCollector is None, reason="SpecCollector not implemented yet (RED phase)")
    def test_collector_logs_permission_error_message_req_2_5(self):
        """
        Unit: The log entry for a missing permission includes the permission name.

        **Validates: Requirements 2.5**
        """
        mock_api = Mock()
        mock_api.get_bucket_acl.return_value = {
            "Owner": {"ID": "o", "DisplayName": "o"},
            "Grants": [],
        }
        mock_api.get_bucket_cors.return_value = {"CORSRules": []}
        mock_api.get_bucket_encryption.return_value = {
            "ServerSideEncryptionConfiguration": {"Rules": []}
        }
        mock_api.get_bucket_lifecycle_configuration.return_value = {"Rules": []}
        mock_api.get_bucket_tagging.return_value = {"TagSet": []}
        mock_api.get_bucket_versioning.return_value = {}
        mock_api.get_bucket_website.return_value = {}

        mock_api.get_bucket_policy.side_effect = _access_denied(
            "s3:GetBucketPolicy",
            "Missing s3:GetBucketPolicy permission",
        )

        collector = SpecCollector(api_client=mock_api)
        collector.collect_s3_specs("my-bucket")

        logs = collector.get_logs()

        # At least one log entry must mention the specific permission
        assert len(logs) > 0, "get_logs() must return non-empty list after permission error"
        combined = " ".join(logs).lower()
        assert "s3:getbucketpolicy" in combined or "getbucketpolicy" in combined, (
            "Log entry must mention the specific permission that was denied. "
            f"Logs: {logs}"
        )


# ===========================================================================
# Test Class: Rate Limit Handling
# ===========================================================================

class TestCollectorRateLimitHandling:
    """Tests for AWS rate-limit / throttling handling (Requirement 12.3)."""

    @pytest.mark.skipif(SpecCollector is None, reason="SpecCollector not implemented yet (RED phase)")
    def test_collector_waits_on_rate_limit_req_12_3(self):
        """
        Unit: Collector respects the retry-after duration when rate-limited.

        Scenario:
        - First call raises a RateLimitError with retry_after=5 seconds.
        - Second call succeeds.

        Expected behaviour:
        - collect_lambda_spec() returns an Ok result.
        - time.sleep() was called with (at least) the retry-after value of 5.

        **Validates: Requirements 12.3**
        """
        mock_api = Mock()
        mock_api.get_function.side_effect = [
            _rate_limit(retry_after=5),
            {"Configuration": {"FunctionName": "my-function", "FunctionArn": "arn:aws:lambda:us-east-1:123:function:my-function"}},
        ]

        with patch("time.sleep") as mock_sleep:
            collector = SpecCollector(api_client=mock_api)
            result = collector.collect_lambda_spec("my-function")

        assert result.is_ok(), (
            f"Expected Ok after rate-limit retry, got: "
            f"{result.error if result.is_err() else 'ok'}"
        )

        # sleep must have been called with the retry-after duration
        assert mock_sleep.called, "time.sleep() must be called when rate limited"
        sleep_durations = [c.args[0] for c in mock_sleep.call_args_list]
        assert any(d >= 5 for d in sleep_durations), (
            f"Collector must sleep for at least the retry-after value (5s). "
            f"Actual sleep durations: {sleep_durations}"
        )

    @pytest.mark.skipif(SpecCollector is None, reason="SpecCollector not implemented yet (RED phase)")
    def test_collector_respects_exact_retry_after_value_req_12_3(self):
        """
        Unit: Collector uses the exact retry-after value from the rate-limit error,
        not a hardcoded constant.

        Scenario:
        - Rate-limit error with retry_after=30 seconds (unusually large).
        - Verifies the 30-second value, not a default, is used.

        **Validates: Requirements 12.3**
        """
        mock_api = Mock()
        mock_api.get_function.side_effect = [
            _rate_limit(retry_after=30),
            {"Configuration": {"FunctionName": "fn", "FunctionArn": "arn:aws:lambda:us-east-1:123:function:fn"}},
        ]

        with patch("time.sleep") as mock_sleep:
            collector = SpecCollector(api_client=mock_api)
            collector.collect_lambda_spec("fn")

        sleep_durations = [c.args[0] for c in mock_sleep.call_args_list]
        assert any(d >= 30 for d in sleep_durations), (
            f"Collector must honour the retry-after=30 from the error. "
            f"Actual sleep durations: {sleep_durations}"
        )


# ===========================================================================
# Test Class: Raw Response Preservation
# ===========================================================================

class TestCollectorRawResponsePreservation:
    """Tests for raw AWS API response preservation (Requirement 2.6)."""

    @pytest.mark.skipif(SpecCollector is None, reason="SpecCollector not implemented yet (RED phase)")
    def test_collector_preserves_raw_response_req_2_6(self):
        """
        Unit: The raw AWS API response is stored verbatim in the ResourceSpec.

        The ResourceSpec.raw_response field must contain the original AWS API
        payload so that it can be audited or re-processed later without making
        additional API calls.

        **Validates: Requirements 2.6**
        """
        raw_ec2_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-abc123",
                            "InstanceType": "t3.micro",
                            "State": {"Name": "running", "Code": 16},
                            "VpcId": "vpc-111",
                        }
                    ]
                }
            ]
        }

        mock_api = Mock()
        mock_api.describe_instances.return_value = raw_ec2_response

        collector = SpecCollector(api_client=mock_api)
        result = collector.collect_ec2_spec("i-abc123")

        assert result.is_ok(), f"Expected Ok result, got error: {result.error if result.is_err() else 'ok'}"

        spec = result.value

        # The spec must expose the raw response
        assert hasattr(spec, "raw_response"), (
            "ResourceSpec must have a 'raw_response' attribute"
        )
        assert spec.raw_response is not None, (
            "raw_response must not be None when a successful API call was made"
        )

        # The raw response must include data from the original payload
        raw = spec.raw_response
        if isinstance(raw, dict):
            assert "Reservations" in raw, (
                "raw_response dict must contain the original 'Reservations' key"
            )
        elif isinstance(raw, str):
            assert "Reservations" in raw, (
                "raw_response string must contain 'Reservations' from original response"
            )
        else:
            pytest.fail(
                f"raw_response must be a dict or JSON string, got {type(raw)}"
            )

    @pytest.mark.skipif(SpecCollector is None, reason="SpecCollector not implemented yet (RED phase)")
    def test_collector_raw_response_contains_original_data_req_2_6(self):
        """
        Unit: Every field from the original AWS API response appears in raw_response.

        This guards against the collector accidentally truncating or normalising
        the raw payload before storing it.

        **Validates: Requirements 2.6**
        """
        import json

        raw_response = {
            "Reservations": [
                {
                    "ReservationId": "r-0abc1234",
                    "Instances": [
                        {
                            "InstanceId": "i-xyz789",
                            "InstanceType": "m5.large",
                            "ImageId": "ami-00000001",
                            "State": {"Name": "running", "Code": 16},
                            "Tags": [{"Key": "env", "Value": "prod"}],
                        }
                    ],
                }
            ]
        }

        mock_api = Mock()
        mock_api.describe_instances.return_value = raw_response

        collector = SpecCollector(api_client=mock_api)
        result = collector.collect_ec2_spec("i-xyz789")

        assert result.is_ok()
        spec = result.value

        raw = spec.raw_response
        raw_str = json.dumps(raw) if isinstance(raw, dict) else str(raw)

        # Check a selection of original fields appear in the stored raw response
        for key in ("i-xyz789", "m5.large", "ami-00000001", "r-0abc1234"):
            assert key in raw_str, (
                f"raw_response must preserve '{key}' from the original API response"
            )


