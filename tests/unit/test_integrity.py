"""
Unit tests for src/integrity.py: checksums, sealing, property paths and
Output_Dir verification.

Validates: Requirements 3.5, 8.2, 8.3, 8.4
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.integrity import (
    canonical_json,
    find_property_line,
    pretty_json,
    resolve_property_path,
    seal_specs,
    spec_checksum,
    verify_output_dir,
)
from src.output_generator import OutputGenerator
from src.parser import ResourceSpec, SpecMetadata
from src.sanitizer import DataSanitizer


def _sg_spec() -> ResourceSpec:
    return ResourceSpec(
        resource_type="aws_security_group",
        arn="arn:aws:ec2:us-east-1:123456789012:security-group/sg-1",
        region="us-east-1",
        account_id="123456789012",
        specifications={
            "GroupId": "sg-1",
            "VpcId": "vpc-1",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }
            ],
        },
        metadata=SpecMetadata("2026-01-01T00:00:00Z", "0.1.0", "2016-11-15", ""),
        raw_response={"DescribeSecurityGroups": {"SecurityGroups": [{"GroupId": "sg-1"}]}},
    )


def _lambda_spec() -> ResourceSpec:
    return ResourceSpec(
        resource_type="aws_lambda_function",
        arn="arn:aws:lambda:us-east-1:123456789012:function:fn",
        region="us-east-1",
        account_id="123456789012",
        specifications={
            "FunctionName": "fn",
            "Environment": {"Variables": {"DB_PASSWORD": "hunter2", "TABLE": "orders"}},
        },
        metadata=SpecMetadata("2026-01-01T00:00:00Z", "0.1.0", "2015-03-31", ""),
        raw_response={
            "GetFunction": {
                "Configuration": {"Environment": {"Variables": {"DB_PASSWORD": "hunter2"}}}
            }
        },
    )


# ---------------------------------------------------------------------------
# Checksums and sealing (Req 3.5)
# ---------------------------------------------------------------------------


def test_spec_checksum_is_canonical_req_3_5():
    a = {"b": 1, "a": {"y": [1, 2], "x": "é"}}
    b = {"a": {"x": "é", "y": [1, 2]}, "b": 1}
    expected = hashlib.sha256(
        json.dumps(a, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    assert canonical_json(a) == canonical_json(b)
    assert spec_checksum(a) == spec_checksum(b) == expected


def test_seal_specs_sanitizes_and_sets_checksum_req_3_5():
    original = _lambda_spec()
    before = copy.deepcopy(original)
    (sealed,) = seal_specs([original], DataSanitizer())

    assert sealed.specifications["Environment"]["Variables"]["DB_PASSWORD"] == "[REDACTED]"
    assert sealed.specifications["Environment"]["Variables"]["TABLE"] == "orders"
    assert "hunter2" not in json.dumps(sealed.raw_response)
    assert sealed.metadata.checksum == spec_checksum(sealed.specifications)
    assert original == before, "seal_specs must not mutate its input"


def test_seal_specs_is_idempotent_req_3_5():
    once = seal_specs([_lambda_spec()], DataSanitizer())
    twice = seal_specs(once, DataSanitizer())
    assert once == twice


# ---------------------------------------------------------------------------
# Property paths and line numbers (Req 8.3, 8.4)
# ---------------------------------------------------------------------------


def test_resolve_property_path():
    doc = _sg_spec().to_dict()
    assert (
        resolve_property_path(doc, "specifications.IpPermissions[0].IpRanges[0].CidrIp")
        == "0.0.0.0/0"
    )
    assert resolve_property_path(doc, "specifications.VpcId") == "vpc-1"
    assert resolve_property_path(doc, "arn") == doc["arn"]
    for bad in (
        "specifications.Nope",
        "specifications.IpPermissions[3]",
        "specifications.VpcId[0]",
        "",
    ):
        with pytest.raises(KeyError):
            resolve_property_path(doc, bad)


def test_find_property_line_req_8_4():
    doc = _sg_spec().to_dict()
    text = pretty_json(doc)
    lines = text.splitlines()
    line = find_property_line(text, "specifications.IpPermissions[0].IpRanges[0].CidrIp")
    assert lines[line - 1].strip() == '"CidrIp": "0.0.0.0/0"'
    line = find_property_line(text, "specifications.VpcId")
    assert lines[line - 1].strip() == '"VpcId": "vpc-1"'
    line = find_property_line(text, "specifications.IpPermissions[0]")
    assert lines[line - 1].strip() == "{"
    assert find_property_line(text, "specifications.Missing") == 0


_JSON = st.recursive(
    st.one_of(st.none(), st.booleans(), st.integers(), st.text(max_size=8)),
    lambda children: st.one_of(
        st.lists(children, max_size=3),
        st.dictionaries(st.text(min_size=1, max_size=6), children, max_size=3),
    ),
    max_leaves=12,
)


@given(st.dictionaries(st.text(min_size=1, max_size=6), _JSON, max_size=4))
def test_property_pretty_json_matches_json_dumps_req_8_4(doc):
    assert pretty_json(doc) == json.dumps(doc, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# verify_output_dir (Req 8.3, 8.4)
# ---------------------------------------------------------------------------


def _write_output(tmp_path: Path) -> tuple[Path, ResourceSpec]:
    generator = OutputGenerator(output_dir=tmp_path)
    generator.generate_json([_sg_spec()])
    sealed = OutputGenerator.load_specs(tmp_path)[0]
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()
    citation = {
        "resource_arn": sealed.arn,
        "spec_file": "aws_security_group/us-east-1/sg-1.json",
        "property_path": "specifications.IpPermissions[0].IpRanges[0]",
        "source_checksum": sealed.metadata.checksum,
        "evidence_value": {"CidrIp": "0.0.0.0/0"},
    }
    (analysis_dir / "analysis.json").write_text(
        json.dumps(
            {"security_findings": [{"citation": citation}], "patterns": [{"citations": [citation]}]}
        ),
        encoding="utf-8",
    )
    generator.generate_checksums()
    return tmp_path, sealed


def test_verify_output_dir_ok_req_8_3(tmp_path):
    out, _ = _write_output(tmp_path)
    report = verify_output_dir(out)
    assert report.ok, report.discrepancies
    assert report.citations_checked == 2
    assert report.files_checked >= 3


def test_verify_output_dir_detects_tampered_file_req_8_4(tmp_path):
    out, _ = _write_output(tmp_path)
    spec_file = out / "aws_security_group/us-east-1/sg-1.json"
    doc = json.loads(spec_file.read_text())
    doc["specifications"]["IpPermissions"][0]["IpRanges"][0]["CidrIp"] = "10.0.0.0/8"
    spec_file.write_text(json.dumps(doc, indent=2, sort_keys=True))

    report = verify_output_dir(out)
    assert not report.ok
    reasons = [(d.path, d.reason) for d in report.discrepancies]
    assert ("aws_security_group/us-east-1/sg-1.json", "checksum mismatch") in reasons
    citation_issue = [d for d in report.discrepancies if "source_checksum" in d.reason]
    assert citation_issue and citation_issue[0].line > 0
    text = spec_file.read_text().splitlines()
    assert '"specifications"' in text[citation_issue[0].line - 1]


def test_verify_output_dir_detects_wrong_evidence_req_8_3(tmp_path):
    out, sealed = _write_output(tmp_path)
    analysis = out / "analysis/analysis.json"
    data = json.loads(analysis.read_text())
    data["patterns"][0]["citations"][0]["evidence_value"] = {"CidrIp": "1.2.3.4/32"}
    analysis.write_text(json.dumps(data))
    OutputGenerator(out).generate_checksums()

    report = verify_output_dir(out)
    assert not report.ok
    (issue,) = report.discrepancies
    assert issue.path == "aws_security_group/us-east-1/sg-1.json"
    assert "evidence" in issue.reason
    lines = (out / issue.path).read_text().splitlines()
    assert lines[issue.line - 1].strip() == "{"
    assert str(issue) == f"{issue.path}:{issue.line}: {issue.reason}"


def test_verify_output_dir_detects_unresolvable_path_and_missing_file_req_8_4(tmp_path):
    out, _ = _write_output(tmp_path)
    analysis = out / "analysis/analysis.json"
    data = json.loads(analysis.read_text())
    data["patterns"][0]["citations"][0]["property_path"] = "specifications.Gone"
    data["security_findings"][0]["citation"]["spec_file"] = "aws_vpc/us-east-1/nope.json"
    analysis.write_text(json.dumps(data))
    OutputGenerator(out).generate_checksums()

    report = verify_output_dir(out)
    reasons = {(d.path, d.line, d.reason.split(":")[0]) for d in report.discrepancies}
    assert ("aws_security_group/us-east-1/sg-1.json", 0, "property_path not found") in reasons
    assert ("aws_vpc/us-east-1/nope.json", 0, "spec file not found") in reasons


def test_verify_output_dir_missing_checksums_req_8_3(tmp_path):
    report = verify_output_dir(tmp_path)
    assert not report.ok
    assert report.discrepancies[0].path == "checksums.sha256"
