"""
Tests for the aws-inventory CLI (src/cli.py), using Click's CliRunner and moto.

Validates: Requirements 8.3, 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.5, 12.4, 12.5
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from unittest.mock import patch

import pytest
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from click.testing import CliRunner

from src import cli as cli_module
from src.aws_session import SessionError
from src.cli import SanitizingFilter, cli

pytestmark = pytest.mark.unit

FAKE_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
FAKE_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
FAKE_SESSION_TOKEN = "FwoGZXIvYXdzEXAMPLEsessiontokenvalue0123456789"
READ_ONLY_PREFIXES = ("Describe", "List", "Get")


@pytest.fixture(autouse=True)
def _reset_cli_logging():
    yield
    root = logging.getLogger()
    for handler in list(root.handlers):
        if isinstance(handler, cli_module.CliLogHandler):
            root.removeHandler(handler)
    root.setLevel(logging.WARNING)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def api_calls():
    """Record (operation, params) of every botocore call while the patch is active."""
    calls: list[tuple[str, dict]] = []
    original = BaseClient._make_api_call

    def record(self, operation_name, api_params):
        calls.append((operation_name, dict(api_params)))
        return original(self, operation_name, api_params)

    with patch.object(BaseClient, "_make_api_call", record):
        yield calls


def _collect(runner: CliRunner, out: Path, *extra: str):
    return runner.invoke(
        cli,
        ["--no-color", "collect", "--region", "us-east-1", "--output-dir", str(out), *extra],
    )


def _all_output_text(result, out: Path) -> str:
    texts = [result.stdout, result.stderr]
    for path in out.rglob("*"):
        if path.is_file():
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(texts)


# ============================================================================
# Credentials (Requirement 9)
# ============================================================================


def test_cli_uses_aws_credential_chain_req_9_1(runner, tmp_path):
    help_text = runner.invoke(cli, ["collect", "--help"]).stdout
    assert "--profile" in help_text
    for forbidden in ("--access-key", "--secret", "--session-token", "--aws-access-key-id"):
        assert forbidden not in help_text

    with patch.object(cli_module, "create_session", side_effect=SessionError("nope")) as create:
        result = runner.invoke(
            cli, ["collect", "--profile", "dev", "--output-dir", str(tmp_path / "out")]
        )
    assert result.exit_code == 2
    create.assert_called_once_with(profile="dev", role_arn=None, external_id=None)


def test_cli_supports_assume_role_req_9_3(runner, tmp_path, sample_account, api_calls):
    role_arn = "arn:aws:iam::123456789012:role/inventory-reader"
    result = _collect(runner, tmp_path / "out", "--role-arn", role_arn, "--external-id", "ext-1")
    assert result.exit_code == 0, result.output

    assume = [params for op, params in api_calls if op == "AssumeRole"]
    assert assume == [
        {"RoleArn": role_arn, "RoleSessionName": "aws-resource-inventory", "ExternalId": "ext-1"}
    ]


def test_cli_exits_2_when_assume_role_fails_req_12_5(runner, tmp_path):
    with patch.object(cli_module, "create_session", side_effect=SessionError("AssumeRole failed")):
        result = runner.invoke(
            cli, ["collect", "--role-arn", "arn:aws:iam::1:role/x", "--output-dir", str(tmp_path)]
        )
    assert result.exit_code == 2
    assert "AssumeRole failed" in result.stderr


def test_cli_exits_2_without_credentials_req_12_5(runner, tmp_path, monkeypatch):
    import os

    for name in list(os.environ):
        if name.startswith("AWS_"):
            monkeypatch.delenv(name)
    missing = str(tmp_path / "missing")
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", missing)
    monkeypatch.setenv("AWS_CONFIG_FILE", missing)
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")

    result = runner.invoke(
        cli, ["collect", "--region", "us-east-1", "--output-dir", str(tmp_path / "out")]
    )
    assert result.exit_code == 2
    assert "credentials" in result.stderr.lower()
    assert not (tmp_path / "out" / "collection_report.json").exists()


def test_cli_never_logs_credentials_req_9_2(runner, tmp_path, monkeypatch, sample_account):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", FAKE_ACCESS_KEY)
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", FAKE_SECRET_KEY)
    monkeypatch.setenv("AWS_SESSION_TOKEN", FAKE_SESSION_TOKEN)
    # botocore prefers AWS_SECURITY_TOKEN (set by conftest) over AWS_SESSION_TOKEN.
    monkeypatch.delenv("AWS_SECURITY_TOKEN", raising=False)
    out = tmp_path / "out"

    leak = logging.getLogger("src.discovery")
    original_init = cli_module.ResourceDiscovery.__init__

    def leaky_init(self, *args, **kwargs):
        # A careless log call must still be scrubbed by the CLI's handler.
        leak.warning("leak %s %s %s", FAKE_ACCESS_KEY, FAKE_SECRET_KEY, FAKE_SESSION_TOKEN)
        original_init(self, *args, **kwargs)

    with patch.object(cli_module.ResourceDiscovery, "__init__", leaky_init):
        result = runner.invoke(
            cli,
            [
                "--log-level",
                "DEBUG",
                "collect",
                "--region",
                "us-east-1",
                "--output-dir",
                str(out),
            ],
        )
    assert result.exit_code == 0, result.output
    assert "leak" in result.stderr
    text = _all_output_text(result, out)
    for secret in (FAKE_ACCESS_KEY, FAKE_SECRET_KEY, FAKE_SESSION_TOKEN):
        assert secret not in text


def test_cli_sanitizing_filter_scrubs_session_secrets_req_9_2():
    record = logging.LogRecord(
        "x", logging.ERROR, __file__, 1, "token=%s key=%s", ("tok-value-123", FAKE_ACCESS_KEY), None
    )
    log_filter = SanitizingFilter()
    log_filter.add_secrets(["tok-value-123"])
    assert log_filter.filter(record) is True
    message = record.getMessage()
    assert "tok-value-123" not in message
    assert FAKE_ACCESS_KEY not in message
    assert "[REDACTED" in message


def test_cli_only_read_only_api_calls_req_9_4(runner, tmp_path, sample_account, api_calls):
    result = _collect(runner, tmp_path / "out", "--role-arn", "arn:aws:iam::123456789012:role/r")
    assert result.exit_code == 0, result.output
    operations = {op for op, _ in api_calls}
    assert operations, "no API calls recorded"
    allowed_sts = {"AssumeRole", "GetCallerIdentity"}
    offending = sorted(
        op for op in operations if not op.startswith(READ_ONLY_PREFIXES) and op not in allowed_sts
    )
    assert offending == []


# ============================================================================
# Collection, metrics and reports (Requirements 10, 12)
# ============================================================================


def test_cli_collect_prints_time_savings_req_10_5(runner, tmp_path, sample_account):
    out = tmp_path / "out"
    result = _collect(runner, out)
    assert result.exit_code == 0, result.output
    assert re.search(r"Time saved: \d+\.\d+ hours \(\d+\.\d+%\)", result.stdout)
    assert "\033[" not in result.output  # --no-color

    summary = (out / "summary_report.md").read_text(encoding="utf-8")
    assert "5 minutes" in summary
    for name in ("manifest.json", "resources.json", "resources.md", "discovery.json"):
        assert (out / name).is_file(), name
    assert (out / "checksums.sha256").is_file()


def test_cli_collection_report_lists_operations_req_12_4(runner, tmp_path, sample_account):
    out = tmp_path / "out"
    result = _collect(runner, out)
    assert result.exit_code == 0, result.output

    report = json.loads((out / "collection_report.json").read_text(encoding="utf-8"))
    assert report["operations"], "operations must be listed"
    for op in report["operations"]:
        assert op["status"] in ("success", "failed")
        assert {"resource_arn", "operation", "attempts"} <= set(op)
    assert report["collection_errors"] == []
    assert report["discovery_errors"] == []
    assert [p["name"] for p in report["phases"]] == ["discovery", "collection", "output"]

    metrics = report["metrics"]
    assert metrics["resources_discovered"] == metrics["specs_collected"] > 0
    assert metrics["specs_failed"] == 0
    assert metrics["api_calls"] >= metrics["resources_discovered"]
    assert metrics["data_volume_bytes"] > 0
    assert set(report["time_savings"]) == {
        "manual_hours",
        "automated_hours",
        "hours_saved",
        "percent_saved",
    }


def test_cli_exits_nonzero_on_errors_req_12_5(runner, tmp_path, sample_account):
    original = BaseClient._make_api_call

    def deny_get_function(self, operation_name, api_params):
        if operation_name == "GetFunction":
            raise ClientError(
                {
                    "Error": {"Code": "AccessDeniedException", "Message": "no"},
                    "ResponseMetadata": {"HTTPStatusCode": 403},
                },
                operation_name,
            )
        return original(self, operation_name, api_params)

    out = tmp_path / "out"
    with patch.object(BaseClient, "_make_api_call", deny_get_function):
        result = _collect(runner, out)

    assert result.exit_code == 1, result.output
    assert "GetFunction" in result.stderr
    report = json.loads((out / "collection_report.json").read_text(encoding="utf-8"))
    (error,) = report["collection_errors"]
    assert error["operation"] == "GetFunction"
    assert report["metrics"]["specs_failed"] == 1
    assert any(
        op["operation"] == "GetFunction" and op["status"] == "failed" for op in report["operations"]
    )
    assert list((out / "aws_s3_bucket").glob("*/*.json")), "other resources are still written"


def test_cli_rejects_invalid_arguments_with_exit_2_req_12_5(runner):
    assert runner.invoke(cli, ["collect", "--max-workers", "zero"]).exit_code == 2
    assert runner.invoke(cli, ["no-such-command"]).exit_code == 2


# ============================================================================
# Offline commands (Requirements 8.3, 12.5)
# ============================================================================


@pytest.mark.parametrize("command", ["analyze", "generate-iac", "generate-docs"])
def test_cli_offline_command_without_specs_exits_2_req_12_5(runner, tmp_path, command):
    result = runner.invoke(cli, [command, "--output-dir", str(tmp_path)])
    assert result.exit_code == 2
    assert "aws-inventory collect" in result.stderr


def test_cli_offline_pipeline_after_collect_req_8_3(runner, tmp_path, sample_account):
    out = tmp_path / "out"
    assert _collect(runner, out).exit_code == 0

    for args in (
        ["analyze", "--output-dir", str(out)],
        ["generate-iac", "--output-dir", str(out)],
        ["generate-docs", "--output-dir", str(out)],
    ):
        result = runner.invoke(cli, ["--no-color", *args])
        assert result.exit_code == 0, (args, result.output)

    assert (out / "analysis" / "analysis.json").is_file()
    assert (out / "analysis" / "analysis.md").is_file()
    assert (out / "diagrams" / "architecture.drawio").is_file()
    assert (out / "terraform" / "import.sh").is_file()
    assert "[cite:" in (out / "docs" / "infrastructure.md").read_text(encoding="utf-8")

    result = runner.invoke(cli, ["verify", "--output-dir", str(out)])
    assert result.exit_code == 0, result.output
    assert result.stdout.startswith("OK:")


def test_cli_verify_reports_discrepancies_with_exit_1_req_8_4(runner, tmp_path, sample_account):
    out = tmp_path / "out"
    assert _collect(runner, out).exit_code == 0
    spec_file = next((out / "aws_s3_bucket").glob("*/*.json"))
    spec_file.write_text(spec_file.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    result = runner.invoke(cli, ["verify", "--output-dir", str(out)])
    assert result.exit_code == 1
    rel = spec_file.relative_to(out).as_posix()
    assert f"{rel}:0: checksum mismatch" in result.stdout


def test_cli_verify_missing_dir_exits_2_req_12_5(runner, tmp_path):
    result = runner.invoke(cli, ["verify", "--output-dir", str(tmp_path / "nope")])
    assert result.exit_code == 2


def test_cli_mcp_serve_runs_stdio_server_req_9_7(runner, tmp_path):
    with patch("src.mcp_stdio.serve") as serve:
        result = runner.invoke(cli, ["mcp-serve", "--cache-dir", str(tmp_path)])
    assert result.exit_code == 0, result.output
    serve.assert_called_once_with(str(tmp_path))


def test_cli_help_lists_commands_with_examples(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for command in (
        "discover",
        "collect",
        "analyze",
        "generate-iac",
        "generate-docs",
        "verify",
        "mcp-serve",
    ):
        assert command in result.stdout
    assert "Example" in runner.invoke(cli, ["collect", "--help"]).stdout


def test_cli_discover_writes_discovery_json_req_1_1(runner, tmp_path, sample_account):
    out = tmp_path / "out"
    result = runner.invoke(cli, ["discover", "--region", "us-east-1", "--output-dir", str(out)])
    assert result.exit_code == 0, result.output
    data = json.loads((out / "discovery.json").read_text(encoding="utf-8"))
    assert data["account_id"] == "123456789012"
    assert data["resources"] and data["errors"] == []
    assert {"resource_type", "resource_id", "arn", "region"} <= set(data["resources"][0])


# IAM action names that differ from the API operation name.
IAM_ACTION_OVERRIDES = {
    "s3:GetBucketCors": "s3:GetBucketCORS",
    "s3:GetBucketEncryption": "s3:GetEncryptionConfiguration",
    "s3:GetBucketLifecycleConfiguration": "s3:GetLifecycleConfiguration",
    "s3:ListBuckets": "s3:ListAllMyBuckets",
    "tagging:GetResources": "tag:GetResources",
}


def test_cli_api_calls_covered_by_iam_policy_req_9_4(runner, tmp_path, sample_account):
    calls: set[str] = set()
    original = BaseClient._make_api_call

    def record(self, operation_name, api_params):
        action = f"{self.meta.service_model.endpoint_prefix}:{operation_name}"
        calls.add(IAM_ACTION_OVERRIDES.get(action, action))
        return original(self, operation_name, api_params)

    with patch.object(BaseClient, "_make_api_call", record):
        result = _collect(runner, tmp_path / "out", "--role-arn", "arn:aws:iam::1:role/r")
        assert result.exit_code == 0, result.output
        result = _collect(runner, tmp_path / "scoped", "--project-tag", "team=orders")
        assert result.exit_code == 0, result.output
    assert "tag:GetResources" in calls

    policy_path = Path(__file__).resolve().parents[2] / "docs" / "iam-policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    allowed = {a for s in policy["Statement"] for a in s["Action"]}
    assert sorted(calls - allowed) == []


def test_cli_collect_project_tag_option_req_13_1(runner, tmp_path, sample_account):
    for bad in ("team", "=orders"):
        result = runner.invoke(
            cli, ["collect", "--project-tag", bad, "--output-dir", str(tmp_path)]
        )
        assert result.exit_code == 2
        assert "KEY=VALUE" in result.output

    out = tmp_path / "out"
    result = _collect(runner, out, "--project-tag", "team=orders", "--include-defaults")
    assert result.exit_code == 0, result.output
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["scope"]["project_tags"] == {"team": "orders"}
    assert manifest["scope"]["include_defaults"] is True
    # team=orders is on S3, logs, RDS, Lambda (moto's tagging API); closure adds the
    # Lambda role and the RDS security group with its VPC. The untagged instance stays out.
    counts = manifest["resource_counts"]
    assert "aws_instance" not in counts
    assert counts["aws_iam_role"] == 1
    assert counts["aws_security_group"] == 1 and counts["aws_vpc"] == 1

    result = runner.invoke(
        cli,
        [
            "discover",
            "--region",
            "us-east-1",
            "--project-tag",
            "team=orders",
            "--output-dir",
            str(tmp_path / "disc"),
        ],
    )
    assert result.exit_code == 0, result.output
    data = json.loads((tmp_path / "disc" / "discovery.json").read_text(encoding="utf-8"))
    assert data["scope"]["mode"] == "project_tag"
    assert {r["resource_type"] for r in data["resources"]} == {
        "aws_s3_bucket",
        "aws_cloudwatch_log_group",
        "aws_db_instance",
        "aws_lambda_function",
    }
