"""
Integration Tests for MCPServer - TDD RED phase

Tests validate:
- Req 5.2: Never exposes AWS credentials in responses
- Req 5.3: Returns cached local data, no AWS API calls
- Req 5.4: Returns error when cached data is not available
- Req 5.6: Blocks unauthorized operations and logs them
- Req 5.7: Rate-limits requests to max 10 per second
"""

from __future__ import annotations

import json
import re
import time
from unittest import mock

import pytest

from src.mcp_server import MCPServer

# ---------------------------------------------------------------------------
# Credential detection helper used across multiple test classes
# ---------------------------------------------------------------------------

# Matches AWS access key IDs (all prefixes), secret-access-key values, and
# session-token values embedded in JSON text.
_CREDENTIAL_PATTERN = re.compile(
    r"(?:AKIA|ASIA|AROA|AIPA|ANPA|ANVA)[A-Z0-9]{16}"  # key ID formats
    r"|(?:aws_secret_access_key|aws_session_token)\s*[=:]\s*\S+",  # env-var style
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def cache_dir(tmp_path):
    """Create a temporary cache directory with sample spec files."""
    resource_dir = tmp_path / "us-east-1" / "lambda"
    resource_dir.mkdir(parents=True)

    spec = {
        "arn": "arn:aws:lambda:us-east-1:123456789012:function:my-func",
        "resource_type": "lambda_function",
        "region": "us-east-1",
        "specifications": {
            "FunctionName": "my-func",
            "Runtime": "python3.11",
        },
    }
    (resource_dir / "my-func.json").write_text(json.dumps(spec))
    return tmp_path


@pytest.fixture
def mcp(cache_dir):
    """Create an MCPServer instance pointed at the temp cache dir."""
    return MCPServer(cache_dir=str(cache_dir))


# ---------------------------------------------------------------------------
# Req 5.3 – Cached data retrieval (no AWS API calls)
# ---------------------------------------------------------------------------


class TestMCPServerCachedData:
    def test_mcp_server_list_resources_returns_cached_data_req_5_3(self, mcp):
        """list-resources must return locally cached data without AWS API calls."""
        with mock.patch("boto3.client") as mock_boto_client, mock.patch(
            "boto3.resource"
        ) as mock_boto_resource:
            response = mcp.handle_request(
                operation="list-resources",
                params={"region": "us-east-1", "resource_type": "lambda_function"},
            )

        assert response["status"] == "ok"
        assert isinstance(response["data"], list)
        # The seeded spec must be present.
        arns = [r["arn"] for r in response["data"]]
        assert "arn:aws:lambda:us-east-1:123456789012:function:my-func" in arns
        # Critical: zero AWS API calls.
        mock_boto_client.assert_not_called()
        mock_boto_resource.assert_not_called()

    def test_mcp_server_get_resource_spec_from_cache_req_5_3(self, mcp):
        """get-resource-spec must load spec from local cache, not AWS."""
        with mock.patch("boto3.client") as mock_boto_client, mock.patch(
            "boto3.resource"
        ) as mock_boto_resource:
            response = mcp.handle_request(
                operation="get-resource-spec",
                params={"arn": "arn:aws:lambda:us-east-1:123456789012:function:my-func"},
            )

        assert response["status"] == "ok"
        spec = response["data"]
        assert spec["arn"] == "arn:aws:lambda:us-east-1:123456789012:function:my-func"
        assert spec["specifications"]["FunctionName"] == "my-func"
        mock_boto_client.assert_not_called()
        mock_boto_resource.assert_not_called()

    def test_mcp_server_returns_error_when_cache_empty_req_5_3(self, tmp_path):
        """If cache dir has no matching files, server must return error not make AWS calls."""
        empty_mcp = MCPServer(cache_dir=str(tmp_path))
        with mock.patch("boto3.client") as mock_boto_client:
            response = empty_mcp.handle_request(
                operation="list-resources",
                params={"region": "us-east-1", "resource_type": "lambda_function"},
            )
        assert response["status"] == "error"
        assert "collection" in response["message"].lower()
        mock_boto_client.assert_not_called()

    # Req 5.4 – Error when cached spec for a specific ARN is not available
    def test_mcp_server_get_spec_cache_miss_returns_error_req_5_4(self, mcp):
        """get-resource-spec must return error (not make AWS call) for unknown ARN."""
        with mock.patch("boto3.client") as mock_boto_client:
            response = mcp.handle_request(
                operation="get-resource-spec",
                params={"arn": "arn:aws:lambda:us-east-1:123456789012:function:nonexistent"},
            )
        assert response["status"] == "error"
        # Message should guide user to run collection first.
        assert "collection" in response["message"].lower() or "not found" in response["message"].lower()
        mock_boto_client.assert_not_called()


# ---------------------------------------------------------------------------
# Req 5.6 – Authorization / whitelist enforcement
# ---------------------------------------------------------------------------


class TestMCPServerAuthorization:
    WHITELISTED_OPERATIONS = [
        "list-resources",
        "get-resource-spec",
        "analyze-activity-flow",
        "generate-documentation",
    ]
    UNAUTHORIZED_OPERATIONS = [
        "delete-resource",
        "create-resource",
        "update-resource",
        "modify-policy",
    ]

    def test_mcp_server_blocks_unauthorized_operations_req_5_6(self, mcp):
        """Unauthorized operations must be rejected with an error response."""
        response = mcp.handle_request(
            operation="delete-resource",
            params={"arn": "arn:aws:s3:::my-bucket"},
        )
        assert response["status"] == "error"
        assert "unauthorized" in response["message"].lower()

    def test_mcp_server_blocks_all_non_whitelisted_operations_req_5_6(self, mcp):
        """Every operation not in the whitelist must be blocked."""
        for op in self.UNAUTHORIZED_OPERATIONS:
            response = mcp.handle_request(operation=op, params={})
            assert response["status"] == "error", (
                f"Operation '{op}' should be blocked but returned status '{response['status']}'"
            )
            assert "unauthorized" in response["message"].lower(), (
                f"Operation '{op}' error message should contain 'unauthorized'"
            )

    def test_mcp_server_logs_unauthorized_attempt_req_5_6(self, mcp, caplog):
        """Every rejected request must produce a WARNING-level log entry."""
        import logging

        with caplog.at_level(logging.WARNING):
            mcp.handle_request(operation="create-resource", params={})

        assert any("unauthorized" in r.message.lower() for r in caplog.records), (
            "Unauthorized attempt was not logged at WARNING level"
        )

    def test_mcp_server_logs_operation_name_for_unauthorized_req_5_6(self, mcp, caplog):
        """The log entry for a rejected request must include the operation name."""
        import logging

        operation = "destroy-everything"
        with caplog.at_level(logging.WARNING):
            mcp.handle_request(operation=operation, params={})

        assert any(operation in r.message for r in caplog.records), (
            "The unauthorized operation name was not included in the log"
        )

    def test_mcp_server_whitelisted_operations_not_blocked_req_5_6(self, mcp):
        """Whitelisted operations must pass authorization check (any status except 'unauthorized error')."""
        for op in self.WHITELISTED_OPERATIONS:
            response = mcp.handle_request(operation=op, params={})
            # Must NOT be blocked as unauthorized.
            is_unauthorized = (
                response.get("status") == "error"
                and "unauthorized" in response.get("message", "").lower()
            )
            assert not is_unauthorized, (
                f"Whitelisted operation '{op}' was incorrectly blocked as unauthorized"
            )


# ---------------------------------------------------------------------------
# Req 5.7 – Rate limiting (max 10 req/s)
# ---------------------------------------------------------------------------


class TestMCPServerRateLimit:
    def test_mcp_server_enforces_rate_limit_req_5_7(self, mcp):
        """Sending 15 requests burst must result in some being rate-limited."""
        responses = []
        for _ in range(15):
            responses.append(
                mcp.handle_request(
                    operation="list-resources",
                    params={"region": "us-east-1", "resource_type": "lambda_function"},
                )
            )

        rate_limited = [r for r in responses if r.get("status") == "rate_limited"]
        assert len(rate_limited) >= 5, (
            f"Expected at least 5 rate-limited responses out of 15 burst requests, "
            f"got {len(rate_limited)}"
        )

    def test_mcp_server_rate_limit_error_message_req_5_7(self, mcp):
        """Rate-limited responses must contain a 'rate limit' message."""
        responses = []
        for _ in range(15):
            responses.append(
                mcp.handle_request(
                    operation="list-resources",
                    params={"region": "us-east-1", "resource_type": "lambda_function"},
                )
            )

        rate_limited = [r for r in responses if r.get("status") == "rate_limited"]
        if rate_limited:
            assert "rate limit" in rate_limited[0].get("message", "").lower(), (
                "Rate-limited response message should mention 'rate limit'"
            )

    def test_mcp_server_first_ten_requests_succeed_req_5_7(self, mcp):
        """The first 10 burst requests must not be rate-limited."""
        responses = []
        for _ in range(10):
            responses.append(
                mcp.handle_request(
                    operation="list-resources",
                    params={"region": "us-east-1", "resource_type": "lambda_function"},
                )
            )

        rate_limited = [r for r in responses if r.get("status") == "rate_limited"]
        assert len(rate_limited) == 0, (
            f"First 10 requests should not be rate-limited, but {len(rate_limited)} were"
        )

    def test_mcp_server_rate_limit_resets_after_window_req_5_7(self, mcp):
        """After 1 second, the rate limit window should reset."""
        # Exhaust the rate limit.
        for _ in range(10):
            mcp.handle_request(
                operation="list-resources",
                params={"region": "us-east-1", "resource_type": "lambda_function"},
            )

        # Wait for the rate limit window to reset.
        time.sleep(1.1)

        # Next request after reset should succeed.
        response = mcp.handle_request(
            operation="list-resources",
            params={"region": "us-east-1", "resource_type": "lambda_function"},
        )
        assert response.get("status") != "rate_limited", (
            "Request after rate limit window reset should not be rate-limited"
        )


# ---------------------------------------------------------------------------
# Req 5.2 – No AWS credentials in responses
# ---------------------------------------------------------------------------


class TestMCPServerCredentialSafety:
    def test_mcp_server_no_credentials_in_list_resources_response_req_5_2(self, mcp):
        """list-resources response must never contain AWS credential-like strings."""
        response = mcp.handle_request(
            operation="list-resources",
            params={"region": "us-east-1", "resource_type": "lambda_function"},
        )
        raw = json.dumps(response)
        assert not _CREDENTIAL_PATTERN.search(raw), (
            "list-resources response contained credential-like string"
        )

    def test_mcp_server_no_credentials_in_get_spec_response_req_5_2(self, mcp):
        """get-resource-spec response must never expose AWS credentials."""
        response = mcp.handle_request(
            operation="get-resource-spec",
            params={"arn": "arn:aws:lambda:us-east-1:123456789012:function:my-func"},
        )
        raw = json.dumps(response)
        assert not _CREDENTIAL_PATTERN.search(raw), (
            "get-resource-spec response contained credential-like string"
        )

    def test_mcp_server_no_access_key_id_field_in_responses_req_5_2(self, mcp):
        """Response JSON must not contain the 'aws_access_key_id' key or value."""
        response = mcp.handle_request(
            operation="list-resources",
            params={"region": "us-east-1", "resource_type": "lambda_function"},
        )
        raw = json.dumps(response).lower()
        assert "aws_access_key_id" not in raw, (
            "Response contained 'aws_access_key_id'"
        )
        assert "aws_secret_access_key" not in raw, (
            "Response contained 'aws_secret_access_key'"
        )
        assert "aws_session_token" not in raw, (
            "Response contained 'aws_session_token'"
        )

    def test_mcp_server_spec_with_credential_env_vars_is_sanitized_req_5_2(
        self, tmp_path
    ):
        """If a cached spec contains credential-like env vars, they must be redacted in response."""
        resource_dir = tmp_path / "us-east-1" / "lambda"
        resource_dir.mkdir(parents=True)

        # Seed a spec that includes a credential-like environment variable.
        spec_with_creds = {
            "arn": "arn:aws:lambda:us-east-1:123456789012:function:sensitive-func",
            "resource_type": "lambda_function",
            "region": "us-east-1",
            "specifications": {
                "FunctionName": "sensitive-func",
                "Environment": {
                    "Variables": {
                        "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
                        "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    }
                },
            },
        }
        (resource_dir / "sensitive-func.json").write_text(json.dumps(spec_with_creds))

        secure_mcp = MCPServer(cache_dir=str(tmp_path))
        response = secure_mcp.handle_request(
            operation="get-resource-spec",
            params={"arn": "arn:aws:lambda:us-east-1:123456789012:function:sensitive-func"},
        )

        raw = json.dumps(response)
        # Real key value must not appear in the response.
        assert "AKIAIOSFODNN7EXAMPLE" not in raw, (
            "AWS Access Key ID leaked into get-resource-spec response"
        )
        assert "wJalrXUtnFEMI" not in raw, (
            "AWS Secret Access Key leaked into get-resource-spec response"
        )

