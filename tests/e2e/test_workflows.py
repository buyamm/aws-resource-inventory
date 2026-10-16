"""
End-to-end workflows: the aws-inventory CLI (Click's CliRunner) against a moto
account holding every Supported_Resource_Type (``sample_account`` fixture).

Validates: Requirements 1.1, 2.1, 3.1-3.6, 5.1, 6.1, 7.1-7.4, 8.1, 8.3, 8.4,
12.2, 12.4, 12.5
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from unittest.mock import patch

import hcl2
import pytest
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from click.testing import CliRunner

from src import cli as cli_module
from src.cli import cli
from src.integrity import (
    ANALYSIS_FILE,
    find_property_line,
    iter_citations,
    pretty_json,
    resolve_property_path,
    verify_output_dir,
)
from src.mcp_server import MCPServer
from src.output_generator import OutputGenerator
from src.resource_types import REGISTRY, file_id, resource_id, spec_relpath

pytestmark = [pytest.mark.e2e, pytest.mark.slow]

REGION = "us-east-1"


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


def _run(runner: CliRunner, *args: str):
    return runner.invoke(cli, ["--no-color", *args])


def _collect(runner: CliRunner, out: Path):
    return _run(runner, "collect", "--region", REGION, "--output-dir", str(out))


@pytest.fixture
def collected(runner, tmp_path, sample_account) -> Path:
    """Output_Dir after a successful `collect` of the sample account."""
    out = tmp_path / "out"
    result = _collect(runner, out)
    assert result.exit_code == 0, result.output
    return out


# ============================================================================
# 22.1 discovery -> collection -> output
# ============================================================================


def test_e2e_discovery_collection_output_workflow(collected, sample_account):
    out = collected
    _, ids = sample_account

    for name in (
        "manifest.json",
        "resources.json",
        "resources.md",
        "discovery.json",
        "collection_report.json",
        "summary_report.md",
        "checksums.sha256",
        "checksums.json",
    ):
        assert (out / name).is_file(), name

    specs = OutputGenerator.load_specs(out)
    assert {spec.resource_type for spec in specs} == set(REGISTRY), "all types collected"

    discovered = json.loads((out / "discovery.json").read_text(encoding="utf-8"))["resources"]
    assert sorted(r["arn"] for r in discovered) == sorted(spec.arn for spec in specs)

    for spec in specs:
        rel = spec_relpath(spec)
        cloudfront_acl = ":global/webacl/" in spec.arn  # CloudFront-scope WAF (Req 14.1)
        is_global = REGISTRY[spec.resource_type].scope == "global" or cloudfront_acl
        expected_region = "global" if is_global else REGION
        assert rel.split("/")[1] == expected_region, rel
        document = json.loads((out / rel).read_text(encoding="utf-8"))
        assert document["arn"] == spec.arn
        assert "raw_response" not in document
        assert (out / rel).with_suffix(".md").is_file(), rel
        raw = (
            out
            / "raw_responses"
            / spec.resource_type
            / expected_region
            / f"{file_id(resource_id(spec))}_raw.json"
        )
        assert raw.is_file(), raw

    sample_ids = {
        ids.instance_id,
        ids.vpc_id,
        ids.security_group_id,
        ids.function_name,
        ids.db_instance_id,
        ids.log_group_name,
        "order-flow",
        ids.table_name,
        ids.bucket_name,
        "order-lambda-role",
        "orders-app-role",
    }
    assert sample_ids <= {resource_id(spec) for spec in specs}

    aggregate = json.loads((out / "resources.json").read_text(encoding="utf-8"))
    assert aggregate["total_resources"] == len(aggregate["resources"]) == len(specs)

    # Secrets set in the sample account never reach the disk (Req 3.6, 9.2).
    for path in out.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            assert "hunter2-demo" not in text, path

    report = verify_output_dir(out)
    assert report.ok, [str(d) for d in report.discrepancies]
    assert report.files_checked > len(specs)


# ============================================================================
# 22.2 collect -> generate-iac
# ============================================================================


def _resource_addresses(terraform_dir: Path) -> list[str]:
    """`module.<module>.<type>.<name>` of every resource block, parsed with python-hcl2."""
    addresses = []
    for tf_file in sorted(terraform_dir.glob("modules/*/main.tf")):
        module = tf_file.parent.name
        parsed = hcl2.loads(tf_file.read_text(encoding="utf-8"))
        for item in parsed.get("resource", []):
            for tf_type, named in item.items():
                for name in named:
                    addresses.append(".".join(["module", module, tf_type, name]).replace('"', ""))
    return addresses


def test_e2e_iac_generation_workflow(runner, collected):
    out = collected
    result = _run(runner, "generate-iac", "--output-dir", str(out))
    assert result.exit_code == 0, result.output

    terraform_dir = out / "terraform"
    env_dirs = sorted(p for p in (terraform_dir / "envs").iterdir() if p.is_dir())
    assert len(env_dirs) == 1, env_dirs
    env_dir = env_dirs[0]
    for name in ("providers.tf", "main.tf", "variables.tf", "outputs.tf", "versions.tf"):
        hcl2.loads((env_dir / name).read_text(encoding="utf-8"))

    addresses = _resource_addresses(terraform_dir)
    assert len(addresses) == len(set(addresses)), "resource addresses are unique"

    specs = OutputGenerator.load_specs(out)
    primary = [a for a in addresses if a.split(".")[2] in REGISTRY]
    assert len(primary) == len(specs), "one primary block per collected resource"
    assert {a.split(".")[2] for a in primary} == set(REGISTRY)

    imports = hcl2.loads((env_dir / "imports.tf").read_text(encoding="utf-8"))["import"]
    imported = [block["to"].strip('"${}') for block in imports]
    assert sorted(imported) == sorted(addresses), "exactly one import block per resource block"

    assert verify_output_dir(out).ok, "generate-iac refreshes checksums"


# ============================================================================
# 22.3 collect -> MCP server
# ============================================================================


def test_e2e_mcp_server_analysis_workflow(collected):
    out = collected
    server = MCPServer(str(out), clock=iter(range(0, 1000, 2)).__next__)

    listed = server.handle_request("list-resources")
    assert listed["status"] == "ok"
    resources = listed["data"]
    assert {r["resource_type"] for r in resources} == set(REGISTRY)

    lambdas = server.handle_request("list-resources", {"resource_type": "lambda"})["data"]
    assert [r["resource_id"] for r in lambdas] == ["order-processor"]

    spec = server.handle_request("get-resource-spec", {"arn": lambdas[0]["arn"]})
    assert spec["status"] == "ok"
    assert spec["data"]["spec_file"] == lambdas[0]["spec_file"]
    assert spec["data"]["metadata"]["checksum"] == lambdas[0]["checksum"]
    assert "hunter2-demo" not in json.dumps(spec)

    analysis = server.handle_request("analyze-activity-flow")
    assert analysis["status"] == "ok"
    data = analysis["data"]
    assert data["relationships"] and data["security_findings"]
    severities = {f["severity"] for f in data["security_findings"]}
    assert {"CRITICAL", "HIGH"} <= severities

    docs = server.handle_request("generate-documentation")
    assert docs["status"] == "ok"
    assert "[cite:" in docs["data"]["markdown"]

    citations = list(iter_citations(data)) + list(docs["data"]["citations"])
    assert citations
    for citation in citations:
        document = json.loads((out / citation["spec_file"]).read_text(encoding="utf-8"))
        assert document["metadata"]["checksum"] == citation["source_checksum"]
        assert resolve_property_path(document, citation["property_path"]) == (
            citation["evidence_value"]
        )

    unknown = server.handle_request("get-resource-spec", {"arn": "arn:aws:s3:::not-collected"})
    assert unknown["status"] == "error"
    assert server.get_security_logs() == []


# ============================================================================
# 22.4 collect -> analyze -> tamper -> verify
# ============================================================================


def test_e2e_verify_detects_tampering(runner, collected):
    out = collected
    result = _run(runner, "analyze", "--output-dir", str(out))
    assert result.exit_code == 0, result.output
    clean = _run(runner, "verify", "--output-dir", str(out))
    assert clean.exit_code == 0, clean.output
    assert re.match(r"OK: \d+ files, [1-9]\d* citations verified", clean.stdout)

    analysis = json.loads((out / ANALYSIS_FILE).read_text(encoding="utf-8"))
    citation = next(
        c for c in iter_citations(analysis) if isinstance(c["evidence_value"], str | int)
    )
    spec_path = out / citation["spec_file"]
    document = json.loads(spec_path.read_text(encoding="utf-8"))
    path = citation["property_path"]
    parent_path, _, key = path.rpartition(".")
    parent = resolve_property_path(document, parent_path)
    parent[key] = f"tampered-{parent[key]}"
    text = pretty_json(document) + "\n"
    spec_path.write_text(text, encoding="utf-8")
    line = find_property_line(text, path)
    assert line > 0

    result = _run(runner, "verify", "--output-dir", str(out))
    assert result.exit_code == 1
    spec_file = citation["spec_file"]
    assert f"{spec_file}:0: checksum mismatch" in result.stdout
    assert f"{spec_file}:{line}: evidence_value differs at {path}" in result.stdout
    assert re.search(rf"{re.escape(spec_file)}:\d+: source_checksum mismatch", result.stdout)
    for reported in result.stdout.splitlines():
        assert re.match(r"^[^:\s]+:\d+: \S", reported), reported
    assert "FAILED:" in result.stderr


# ============================================================================
# 22.5 partial failure
# ============================================================================


def test_e2e_partial_failure_exit_code(runner, tmp_path, sample_account):
    original = BaseClient._make_api_call

    def deny_describe_table(self, operation_name, api_params):
        if operation_name == "DescribeTable":
            raise ClientError(
                {
                    "Error": {"Code": "AccessDeniedException", "Message": "denied"},
                    "ResponseMetadata": {"HTTPStatusCode": 403},
                },
                operation_name,
            )
        return original(self, operation_name, api_params)

    out = tmp_path / "out"
    with patch.object(BaseClient, "_make_api_call", deny_describe_table):
        result = _collect(runner, out)

    assert result.exit_code == 1, result.output
    assert "DescribeTable" in result.stderr

    report = json.loads((out / "collection_report.json").read_text(encoding="utf-8"))
    (error,) = report["collection_errors"]
    assert error["operation"] == "DescribeTable"
    assert error["resource_arn"].endswith(":table/orders")
    assert report["metrics"]["specs_failed"] == 1
    failed_ops = [op for op in report["operations"] if op["status"] == "failed"]
    assert [op["operation"] for op in failed_ops] == ["DescribeTable"]

    specs = OutputGenerator.load_specs(out)
    collected_types = {spec.resource_type for spec in specs}
    assert collected_types == set(REGISTRY) - {"aws_dynamodb_table"}
    assert not (out / "aws_dynamodb_table").exists()
    assert verify_output_dir(out).ok, "partial output is still sealed"
