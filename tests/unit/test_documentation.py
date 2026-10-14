"""
Unit tests for the infrastructure documentation generator.

Requirements Coverage:
- Requirement 6.3: Documentation of what interacts with what
- Requirement 8.1: Every statement carries at least one citation
"""

from __future__ import annotations

import re

from src.analysis_engine import AnalysisEngine
from src.documentation import document_citations, generate_infrastructure_doc
from src.integrity import resolve_property_path, seal_specs
from src.parser import ResourceSpec, SpecMetadata
from src.sanitizer import DataSanitizer

ACCOUNT = "123456789012"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT}:role/AppRole"
FUNCTION_ARN = f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:app"
SG_ARN = f"arn:aws:ec2:us-east-1:{ACCOUNT}:security-group/sg-1"

_CITE = re.compile(r"\[cite: [^#\s]+#\S+ sha256:[0-9a-f]{12}\]")


def _spec(resource_type: str, arn: str, specifications: dict, region: str = "us-east-1"):
    return ResourceSpec(
        resource_type=resource_type,
        arn=arn,
        region=region,
        account_id=ACCOUNT,
        specifications=specifications,
        metadata=SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "2026-01-01", ""),
    )


def _specs() -> list[ResourceSpec]:
    return seal_specs(
        [
            _spec(
                "aws_lambda_function",
                FUNCTION_ARN,
                {"FunctionName": "app", "Role": ROLE_ARN},
            ),
            _spec(
                "aws_iam_role",
                ROLE_ARN,
                {
                    "RoleName": "AppRole",
                    "Arn": ROLE_ARN,
                    "AttachedPolicies": [
                        {
                            "PolicyName": "AdministratorAccess",
                            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess",
                        }
                    ],
                    "InlinePolicies": {},
                },
                region="global",
            ),
            _spec(
                "aws_security_group",
                SG_ARN,
                {
                    "GroupId": "sg-1",
                    "GroupName": "open",
                    "IpPermissions": [
                        {
                            "IpProtocol": "tcp",
                            "FromPort": 22,
                            "ToPort": 22,
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                        }
                    ],
                },
            ),
            # No id field: still counted, never stated without a citation.
            _spec("aws_dynamodb_table", f"arn:aws:dynamodb:us-east-1:{ACCOUNT}:table/t", {}),
        ],
        DataSanitizer(),
    )


def _statement_lines(markdown: str) -> list[str]:
    lines = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            continue  # headings and the counts table derived from the inventory
        lines.append(stripped)
    return lines


def test_documentation_every_statement_cited_req_8_1():
    specs = _specs()
    report = AnalysisEngine().analyze(specs)
    markdown = generate_infrastructure_doc(report, specs)

    assert markdown.startswith("# Infrastructure Documentation")
    statements = _statement_lines(markdown)
    assert statements
    for line in statements:
        assert _CITE.search(line), f"uncited statement: {line!r}"


def test_documentation_sections_req_6_3():
    specs = _specs()
    markdown = generate_infrastructure_doc(AnalysisEngine().analyze(specs), specs)

    assert "| aws_lambda_function | us-east-1 | 1 |" in markdown
    assert "| aws_dynamodb_table | us-east-1 | 1 |" in markdown
    assert "## Architecture Patterns" in markdown
    assert "### Serverless Application" in markdown
    assert "iam_role_usage" in markdown
    assert "[CRITICAL]" in markdown or "[HIGH]" in markdown
    assert "aws_iam_role/global/AppRole.json#specifications.RoleName" in markdown


def test_documentation_citations_resolve_req_8_1():
    specs = _specs()
    report = AnalysisEngine().analyze(specs)
    citations = document_citations(report, specs)
    assert citations
    keys = [(c["spec_file"], c["property_path"]) for c in citations]
    assert len(keys) == len(set(keys))
    for citation in citations:
        spec = next(s for s in specs if s.arn == citation["resource_arn"])
        assert citation["source_checksum"] == spec.metadata.checksum
        value = resolve_property_path(spec.to_dict(), citation["property_path"])
        assert value == citation["evidence_value"]
