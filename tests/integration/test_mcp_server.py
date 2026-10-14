"""
Integration tests for the MCPServer core over an Output_Dir cache.

Requirements Coverage:
- Requirement 5.1: Four whitelisted tools with the parameters of design.md §"MCP Server"
- Requirement 5.2: No AWS credentials in responses; no boto3/botocore import
- Requirement 5.3 / 5.4: Answers only from cached spec files; cache misses are errors
- Requirement 5.5 / 5.6: Unknown operations and invalid parameters rejected and logged
- Requirement 5.7: Sliding 1-second window, max 10 accepted requests
- Requirement 8.1 / 8.6: Cited documentation; unknown ARNs rejected
"""

from __future__ import annotations

import json
import logging
import re
import string
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.integrity import resolve_property_path, spec_checksum
from src.mcp_server import MCPServer
from src.output_generator import OutputGenerator
from src.parser import ResourceSpec, SpecMetadata

ACCOUNT = "123456789012"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT}:role/OrderServiceRole"
FUNCTION_ARN = f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:my-func"
TABLE_ARN = f"arn:aws:dynamodb:us-east-1:{ACCOUNT}:table/OrdersTable"
LOG_GROUP_ARN = f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/aws/lambda/my-func"
UNKNOWN_ARN = f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:nonexistent"

# Matches AWS access key IDs and secret-access-key/session-token assignments.
_CREDENTIAL_PATTERN = re.compile(
    r"(?:AKIA|ASIA)[A-Z0-9]{16}" r"|(?:aws_secret_access_key|aws_session_token)\s*[=:]\s*\S+",
    re.IGNORECASE,
)


def _spec(resource_type: str, arn: str, specifications: dict, region: str = "us-east-1"):
    return ResourceSpec(
        resource_type=resource_type,
        arn=arn,
        region=region,
        account_id=ACCOUNT,
        specifications=specifications,
        metadata=SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "2026-01-01", ""),
    )


def _sample_specs() -> list[ResourceSpec]:
    return [
        _spec(
            "aws_lambda_function",
            FUNCTION_ARN,
            {
                "FunctionName": "my-func",
                "FunctionArn": FUNCTION_ARN,
                "Runtime": "python3.11",
                "Role": ROLE_ARN,
                "Environment": {"Variables": {"TABLE_NAME": "OrdersTable"}},
            },
        ),
        _spec(
            "aws_iam_role",
            ROLE_ARN,
            {
                "RoleName": "OrderServiceRole",
                "Arn": ROLE_ARN,
                "AttachedPolicies": [],
                "InlinePolicies": {},
            },
            region="global",
        ),
        _spec(
            "aws_dynamodb_table",
            TABLE_ARN,
            {"TableName": "OrdersTable", "TableArn": TABLE_ARN},
        ),
        _spec(
            "aws_cloudwatch_log_group",
            LOG_GROUP_ARN,
            {"logGroupName": "/aws/lambda/my-func", "arn": LOG_GROUP_ARN},
        ),
    ]


def _write_cache(root: Path, specs: list[ResourceSpec]) -> Path:
    OutputGenerator(output_dir=root).generate_json(specs)
    return root


class _FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def cache_dir(tmp_path):
    """Output_Dir populated by OutputGenerator (sealed specs, canonical layout)."""
    root = _write_cache(tmp_path / "out", _sample_specs())
    # Non-spec output must never be read as a spec.
    (root / "analysis").mkdir()
    (root / "analysis" / "analysis.json").write_text(json.dumps({"arn": "arn:aws:fake"}))
    return root


@pytest.fixture
def mcp(cache_dir):
    return MCPServer(cache_dir=str(cache_dir))


def _seed_raw(root: Path, rel: str, document: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document))


# ---------------------------------------------------------------------------
# Req 5.3 / 5.4 – cached data only
# ---------------------------------------------------------------------------


class TestMCPServerCachedData:
    def test_mcp_server_list_resources_returns_cached_data_req_5_3(self, mcp):
        with (
            mock.patch("boto3.client") as mock_client,
            mock.patch("boto3.resource") as mock_resource,
        ):
            response = mcp.handle_request(
                "list-resources",
                {"region": "us-east-1", "resource_type": "aws_lambda_function"},
            )

        assert response["status"] == "ok"
        assert response["data"] == [
            {
                "arn": FUNCTION_ARN,
                "resource_type": "aws_lambda_function",
                "region": "us-east-1",
                "account_id": ACCOUNT,
                "resource_id": "my-func",
                "spec_file": "aws_lambda_function/us-east-1/my-func.json",
                "checksum": response["data"][0]["checksum"],
            }
        ]
        assert len(response["data"][0]["checksum"]) == 64
        mock_client.assert_not_called()
        mock_resource.assert_not_called()

    def test_mcp_server_list_resources_all_sorted_by_spec_file_req_5_3(self, mcp):
        response = mcp.handle_request("list-resources")
        assert response["status"] == "ok"
        files = [item["spec_file"] for item in response["data"]]
        assert files == sorted(files)
        assert len(files) == 4
        assert "arn:aws:fake" not in [item["arn"] for item in response["data"]]

    def test_mcp_server_list_resources_filters_by_alias_req_5_1(self, mcp):
        for alias in ("lambda", "lambda_function", "LAMBDA"):
            response = mcp.handle_request("list-resources", {"resource_type": alias})
            assert response["status"] == "ok"
            assert [item["arn"] for item in response["data"]] == [FUNCTION_ARN]

        response = mcp.handle_request("list-resources", {"region": "global"})
        assert [item["arn"] for item in response["data"]] == [ROLE_ARN]

    def test_mcp_server_get_resource_spec_from_cache_req_5_3(self, mcp, cache_dir):
        with mock.patch("boto3.client") as mock_client:
            response = mcp.handle_request("get-resource-spec", {"arn": FUNCTION_ARN})

        assert response["status"] == "ok"
        data = response["data"]
        assert data["arn"] == FUNCTION_ARN
        assert data["spec_file"] == "aws_lambda_function/us-east-1/my-func.json"
        assert data["specifications"]["FunctionName"] == "my-func"
        on_disk = json.loads((cache_dir / data["spec_file"]).read_text())
        assert data["metadata"]["checksum"] == on_disk["metadata"]["checksum"]
        mock_client.assert_not_called()

    @pytest.mark.parametrize(
        "operation,params",
        [
            ("list-resources", {}),
            ("get-resource-spec", {"arn": FUNCTION_ARN}),
            ("analyze-activity-flow", {}),
            ("generate-documentation", {}),
        ],
    )
    def test_mcp_server_returns_error_when_cache_empty_req_5_4(self, tmp_path, operation, params):
        (tmp_path / "analysis").mkdir()
        (tmp_path / "analysis" / "analysis.json").write_text("{}")
        response = MCPServer(cache_dir=str(tmp_path)).handle_request(operation, params)
        assert response["status"] == "error"
        assert "not in the collected data" in response["message"]
        assert "aws-inventory collect" in response["message"]

    def test_mcp_server_get_spec_cache_miss_returns_error_req_5_4(self, mcp):
        response = mcp.handle_request("get-resource-spec", {"arn": UNKNOWN_ARN})
        assert response["status"] == "error"
        assert UNKNOWN_ARN in response["message"]
        assert "aws-inventory collect" in response["message"]

    def test_mcp_server_unknown_arn_rejected_req_8_6(self, mcp):
        for operation in ("get-resource-spec", "analyze-activity-flow"):
            response = mcp.handle_request(operation, {"arn": UNKNOWN_ARN})
            assert response["status"] == "error", operation
            assert "not in the collected data" in response["message"]
            assert "data" not in response


# ---------------------------------------------------------------------------
# Req 5.5 / 5.6 – whitelist, parameter validation, security log
# ---------------------------------------------------------------------------


class TestMCPServerAuthorization:
    WHITELISTED = [
        "list-resources",
        "get-resource-spec",
        "analyze-activity-flow",
        "generate-documentation",
    ]
    UNAUTHORIZED = ["delete-resource", "create-resource", "update-resource", "modify-policy"]

    def test_mcp_server_blocks_unauthorized_operations_req_5_6(self, mcp):
        response = mcp.handle_request("delete-resource", {"arn": "arn:aws:s3:::my-bucket"})
        assert response == {
            "status": "error",
            "message": "Unauthorized operation: 'delete-resource'",
        }

    def test_mcp_server_blocks_all_non_whitelisted_operations_req_5_6(self, mcp):
        for op in self.UNAUTHORIZED:
            response = mcp.handle_request(op, {})
            assert response["status"] == "error"
            assert response["message"].startswith("Unauthorized")

    def test_mcp_server_logs_unauthorized_attempt_req_5_6(self, mcp, caplog):
        with caplog.at_level(logging.WARNING, logger="src.mcp_server"):
            mcp.handle_request("destroy-everything", {})
        messages = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
        assert any("destroy-everything" in m and "Unauthorized" in m for m in messages)

    def test_mcp_server_whitelisted_operations_not_blocked_req_5_6(self, mcp):
        for op in self.WHITELISTED:
            response = mcp.handle_request(op, {"arn": FUNCTION_ARN} if "spec" in op else {})
            assert response["status"] == "ok", (op, response)

    @pytest.mark.parametrize(
        "operation,params",
        [
            ("list-resources", {"foo": "bar"}),
            ("list-resources", {"region": 5}),
            ("list-resources", {"resource_type": "aws_api_gateway_rest_api"}),
            ("get-resource-spec", {}),
            ("get-resource-spec", {"arn": 123}),
            ("get-resource-spec", {"arn": FUNCTION_ARN, "extra": True}),
            ("analyze-activity-flow", {"region": "us-east-1"}),
            ("generate-documentation", {"arn": FUNCTION_ARN}),
            ("list-resources", ["not", "a", "dict"]),
        ],
    )
    def test_mcp_server_rejects_unknown_params_req_5_5(self, mcp, operation, params):
        response = mcp.handle_request(operation, params)
        assert response["status"] == "error"
        assert response["message"].startswith("Invalid parameters")

    def test_mcp_server_security_log_entries_req_5_6(self, mcp):
        assert mcp.get_security_logs() == []
        mcp.handle_request("delete-resource", {})
        mcp.handle_request("list-resources", {"foo": "bar"})
        mcp.handle_request("list-resources", {})  # accepted: not logged

        logs = mcp.get_security_logs()
        assert [entry["operation"] for entry in logs] == ["delete-resource", "list-resources"]
        for entry in logs:
            assert set(entry) == {"timestamp", "operation", "reason"}
            assert re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z$", entry["timestamp"])
        assert "Unauthorized" in logs[0]["reason"]
        assert "foo" in logs[1]["reason"]


# ---------------------------------------------------------------------------
# Req 5.7 – rate limiting
# ---------------------------------------------------------------------------


class TestMCPServerRateLimit:
    def _burst(self, server: MCPServer, count: int) -> list[dict]:
        return [server.handle_request("list-resources") for _ in range(count)]

    def test_mcp_server_enforces_rate_limit_req_5_7(self, cache_dir):
        server = MCPServer(str(cache_dir), clock=_FakeClock())
        responses = self._burst(server, 15)
        assert [r["status"] for r in responses] == ["ok"] * 10 + ["rate_limited"] * 5
        assert responses[-1] == {
            "status": "rate_limited",
            "message": "Rate limit exceeded: max 10 requests per second",
        }

    def test_mcp_server_rate_limit_resets_after_window_req_5_7(self, cache_dir):
        clock = _FakeClock()
        server = MCPServer(str(cache_dir), clock=clock)
        self._burst(server, 10)
        clock.now = 1.0
        assert server.handle_request("list-resources")["status"] == "ok"

    def test_mcp_server_rate_limit_is_sliding_window_req_5_7(self, cache_dir):
        clock = _FakeClock()
        server = MCPServer(str(cache_dir), clock=clock)
        self._burst(server, 5)
        clock.now = 0.6
        self._burst(server, 5)
        clock.now = 1.2  # the first five left the window, the last five did not
        statuses = [r["status"] for r in self._burst(server, 6)]
        assert statuses == ["ok"] * 5 + ["rate_limited"]

    def test_mcp_server_rate_limited_requests_not_counted_req_5_7(self, cache_dir):
        clock = _FakeClock()
        server = MCPServer(str(cache_dir), clock=clock)
        self._burst(server, 10)
        clock.now = 0.5
        assert all(r["status"] == "rate_limited" for r in self._burst(server, 5))
        clock.now = 1.01
        assert all(r["status"] == "ok" for r in self._burst(server, 10))

    def test_mcp_server_rejected_requests_not_counted_req_5_7(self, cache_dir):
        server = MCPServer(str(cache_dir), clock=_FakeClock())
        for _ in range(20):
            server.handle_request("delete-resource", {})
            server.handle_request("list-resources", {"bad": 1})
        assert all(r["status"] == "ok" for r in self._burst(server, 10))


# ---------------------------------------------------------------------------
# Analysis and documentation over the cache (Req 5.1, 8.1)
# ---------------------------------------------------------------------------


def _assert_citation_resolves(cache: Path, citation: dict) -> None:
    document = json.loads((cache / citation["spec_file"]).read_text())
    assert spec_checksum(document["specifications"]) == citation["source_checksum"]
    assert resolve_property_path(document, citation["property_path"]) == citation["evidence_value"]


class TestMCPServerAnalysis:
    def test_mcp_server_analyze_activity_flow_uses_cache_req_5_1(self, mcp, cache_dir):
        response = mcp.handle_request("analyze-activity-flow")
        assert response["status"] == "ok"
        data = response["data"]
        assert data["resource_count"] == 4
        types = {r["relationship_type"] for r in data["relationships"]}
        assert {"iam_role_usage", "dynamodb_access", "log_group"} <= types
        assert "Serverless Application" in [p["pattern_name"] for p in data["patterns"]]
        for rel in data["relationships"]:
            for citation in rel["citations"]:
                _assert_citation_resolves(cache_dir, citation)

    def test_mcp_server_analyze_activity_flow_filters_by_arn_req_5_1(self, mcp):
        data = mcp.handle_request("analyze-activity-flow", {"arn": TABLE_ARN})["data"]
        assert data["relationships"]
        for rel in data["relationships"]:
            assert TABLE_ARN in (rel["from_arn"], rel["to_arn"])
        for pattern in data["patterns"]:
            assert TABLE_ARN in pattern["participating_resources"]
        for finding in data["security_findings"]:
            assert finding["resource_arn"] == TABLE_ARN

    def test_mcp_server_generate_documentation_cited_req_8_1(self, mcp, cache_dir):
        before = sorted(p.relative_to(cache_dir) for p in cache_dir.rglob("*"))
        response = mcp.handle_request("generate-documentation")
        assert response["status"] == "ok"
        markdown = response["data"]["markdown"]
        citations = response["data"]["citations"]
        assert markdown.startswith("# ")
        assert "[cite: aws_lambda_function/us-east-1/my-func.json#" in markdown
        assert citations
        for citation in citations:
            _assert_citation_resolves(cache_dir, citation)
        # Generated in memory: nothing written to the cache.
        assert sorted(p.relative_to(cache_dir) for p in cache_dir.rglob("*")) == before

    def test_mcp_server_handler_exception_becomes_error_req_5_1(self, mcp):
        with mock.patch("src.mcp_server.AnalysisEngine.analyze", side_effect=RuntimeError("boom")):
            response = mcp.handle_request("analyze-activity-flow")
        assert response == {"status": "error", "message": "RuntimeError: boom"}


# ---------------------------------------------------------------------------
# Req 5.2 – no credentials, no boto3
# ---------------------------------------------------------------------------


class TestMCPServerCredentialSafety:
    def test_mcp_server_no_credentials_in_responses_req_5_2(self, mcp):
        for operation, params in [
            ("list-resources", {}),
            ("get-resource-spec", {"arn": FUNCTION_ARN}),
            ("analyze-activity-flow", {}),
            ("generate-documentation", {}),
        ]:
            raw = json.dumps(mcp.handle_request(operation, params))
            assert not _CREDENTIAL_PATTERN.search(raw), operation

    def test_mcp_server_spec_with_credential_env_vars_is_sanitized_req_5_2(self, tmp_path):
        arn = f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:sensitive-func"
        # Written directly (not through the sealing OutputGenerator).
        _seed_raw(
            tmp_path,
            "aws_lambda_function/us-east-1/sensitive-func.json",
            {
                "arn": arn,
                "resource_type": "aws_lambda_function",
                "region": "us-east-1",
                "account_id": ACCOUNT,
                "specifications": {
                    "FunctionName": "sensitive-func",
                    "Environment": {
                        "Variables": {
                            "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
                            "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                            "CONFIG": "key=AKIAIOSFODNN7EXAMPLF",
                        }
                    },
                },
                "metadata": {},
            },
        )
        server = MCPServer(cache_dir=str(tmp_path))
        for operation, params in [
            ("list-resources", {}),
            ("get-resource-spec", {"arn": arn}),
            ("analyze-activity-flow", {"arn": arn}),
            ("generate-documentation", {}),
        ]:
            raw = json.dumps(server.handle_request(operation, params))
            assert "AKIAIOSFODNN7EXAMPL" not in raw, operation
            assert "wJalrXUtnFEMI" not in raw, operation

    def test_mcp_server_module_does_not_import_boto3_req_5_2(self):
        code = (
            "import sys, src.mcp_server, src.mcp_stdio; "
            "print(sorted(m for m in sys.modules if m.split('.')[0] in ('boto3', 'botocore')))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).resolve().parents[2],
        )
        assert result.stdout.strip() == "[]"


_SECRET_SUFFIX = st.text(alphabet=string.ascii_uppercase + string.digits, min_size=16, max_size=16)
_PASSWORD = st.text(alphabet=string.ascii_letters + string.digits, min_size=24, max_size=32)


@given(
    access_key=_SECRET_SUFFIX,
    password=_PASSWORD,
    env_name=st.from_regex(r"[A-Z][A-Z0-9_]{2,12}", fullmatch=True),
    tag_value_prefix=st.text(alphabet=string.ascii_lowercase + " =:", max_size=8),
)
def test_property_mcp_server_no_credentials_req_5_2(
    access_key, password, env_name, tag_value_prefix
):
    key_id = "AKIA" + access_key
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        arn = f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:fn"
        _seed_raw(
            root,
            "aws_lambda_function/us-east-1/fn.json",
            {
                "arn": arn,
                "resource_type": "aws_lambda_function",
                "region": "us-east-1",
                "account_id": ACCOUNT,
                "specifications": {
                    "FunctionName": "fn",
                    "Role": ROLE_ARN,
                    "Environment": {"Variables": {env_name: key_id, "DB_PASSWORD": password}},
                    "Tags": {"note": tag_value_prefix + key_id},
                },
                "metadata": {},
            },
        )
        server = MCPServer(cache_dir=str(root))
        for operation, params in [
            ("list-resources", {}),
            ("get-resource-spec", {"arn": arn}),
            ("analyze-activity-flow", {}),
            ("generate-documentation", {}),
        ]:
            raw = json.dumps(server.handle_request(operation, params))
            assert key_id not in raw
            assert password not in raw
