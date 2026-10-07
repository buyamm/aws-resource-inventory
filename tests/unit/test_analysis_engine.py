"""
Unit tests for AnalysisEngine (TDD RED and GREEN phases).

Requirements Coverage:
- Requirement 6.1: Identify relationships between resources (VPC connections, Lambda triggers, IAM roles)
- Requirement 6.2: Detect common patterns (API Gateway + Lambda + DynamoDB, EC2 in VPC, etc.)
- Requirement 6.5: Include confidence scores and cite specific resource specifications as evidence
- Requirement 6.6: Flag suspicious patterns (overly permissive IAM, public S3 buckets, unrestricted security groups)
- Requirement 8.1: Direct citations to specific resource specifications
- Requirement 8.2: Checksum references linking analysis statements to source data files
"""

import pytest

from src.analysis_engine import (
    AnalysisEngine,
)
from src.parser import ResourceSpec, SpecMetadata

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def metadata_fixture() -> SpecMetadata:
    """Standard SpecMetadata fixture."""
    return SpecMetadata(
        collected_at="2026-10-07T12:00:00Z",
        collector_version="1.0.0",
        api_version="2026-01-01",
        checksum="chk-hash-999",
    )


@pytest.fixture
def serverless_pattern_specs(metadata_fixture: SpecMetadata) -> list[ResourceSpec]:
    """Specs representing a serverless application pattern."""
    role = ResourceSpec(
        resource_type="aws_iam_role",
        arn="arn:aws:iam::123456789012:role/OrderServiceRole",
        region="global",
        account_id="123456789012",
        specifications={
            "role_name": "OrderServiceRole",
            "assume_role_policy_document": {"Statement": [{"Action": "sts:AssumeRole"}]},
        },
        metadata=metadata_fixture,
    )
    dynamo = ResourceSpec(
        resource_type="aws_dynamodb_table",
        arn="arn:aws:dynamodb:us-east-1:123456789012:table/OrdersTable",
        region="us-east-1",
        account_id="123456789012",
        specifications={"table_name": "OrdersTable", "billing_mode": "PAY_PER_REQUEST"},
        metadata=metadata_fixture,
    )
    lambda_fn = ResourceSpec(
        resource_type="aws_lambda_function",
        arn="arn:aws:lambda:us-east-1:123456789012:function:OrderHandler",
        region="us-east-1",
        account_id="123456789012",
        specifications={
            "function_name": "OrderHandler",
            "runtime": "python3.11",
            "role": "arn:aws:iam::123456789012:role/OrderServiceRole",
            "environment_variables": {"TABLE_NAME": "OrdersTable"},
        },
        metadata=metadata_fixture,
    )
    return [role, dynamo, lambda_fn]


@pytest.fixture
def suspicious_security_specs(metadata_fixture: SpecMetadata) -> list[ResourceSpec]:
    """Specs containing common security misconfigurations."""
    # 1. Overly permissive IAM role
    permissive_iam = ResourceSpec(
        resource_type="aws_iam_role",
        arn="arn:aws:iam::123456789012:role/SuperAdminRole",
        region="global",
        account_id="123456789012",
        specifications={
            "role_name": "SuperAdminRole",
            "policy": {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "*",
                        "Resource": "*",
                    }
                ]
            },
        },
        metadata=metadata_fixture,
    )

    # 2. Public S3 bucket
    public_s3 = ResourceSpec(
        resource_type="aws_s3_bucket",
        arn="arn:aws:s3:::leaky-bucket",
        region="us-east-1",
        account_id="123456789012",
        specifications={
            "bucket_name": "leaky-bucket",
            "acl": {
                "Grants": [
                    {
                        "Grantee": {"URI": "http://acs.amazonaws.com/groups/global/AllUsers"},
                        "Permission": "READ",
                    }
                ]
            },
        },
        metadata=metadata_fixture,
    )

    # 3. Unrestricted security group opening SSH 0.0.0.0/0
    open_sg = ResourceSpec(
        resource_type="aws_security_group",
        arn="arn:aws:ec2:us-east-1:123456789012:security-group/sg-01234567",
        region="us-east-1",
        account_id="123456789012",
        specifications={
            "group_id": "sg-01234567",
            "group_name": "open-ssh-sg",
            "ip_permissions": [
                {
                    "from_port": 22,
                    "to_port": 22,
                    "ip_protocol": "tcp",
                    "ip_ranges": [{"cidr_ip": "0.0.0.0/0"}],
                }
            ],
        },
        metadata=metadata_fixture,
    )

    return [permissive_iam, public_s3, open_sg]


# ============================================================================
# Unit Tests (Task 13.1 & 13.2)
# ============================================================================


class TestAnalysisEngineRelationships:
    """Tests for inter-resource relationship detection (Requirement 6.1)."""

    def test_analysis_engine_identifies_relationships_req_6_1(
        self, serverless_pattern_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 6.1: Identify relationships between resources."""
        engine = AnalysisEngine()
        relationships = engine.identify_relationships(serverless_pattern_specs)

        assert len(relationships) >= 2
        rel_types = [r.relationship_type for r in relationships]

        assert "iam_role_usage" in rel_types
        assert any("dynamodb" in t for t in rel_types)


class TestAnalysisEnginePatterns:
    """Tests for common architecture pattern detection (Requirement 6.2)."""

    def test_analysis_engine_detects_patterns_req_6_2(
        self, serverless_pattern_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 6.2: Detect common patterns (Lambda + DynamoDB + IAM)."""
        engine = AnalysisEngine()
        patterns = engine.detect_patterns(serverless_pattern_specs)

        assert len(patterns) >= 1
        serverless = patterns[0]
        assert (
            "serverless" in serverless.pattern_name.lower()
            or "lambda" in serverless.pattern_name.lower()
        )
        assert serverless.confidence >= 0.7
        assert len(serverless.participating_resources) >= 2


class TestAnalysisEngineSecurityFindings:
    """Tests for suspicious pattern and vulnerability flagging (Requirement 6.6)."""

    def test_analysis_engine_flags_suspicious_patterns_req_6_6(
        self, suspicious_security_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 6.6: Flag suspicious patterns (overly permissive IAM, public S3, unrestricted SG)."""
        engine = AnalysisEngine()
        findings = engine.flag_suspicious_patterns(suspicious_security_specs)

        assert len(findings) >= 3
        types = [f.finding_type for f in findings]

        assert any("IAM" in t or "PERMISSIVE" in t for t in types)
        assert any("S3" in t or "PUBLIC" in t for t in types)
        assert any("SECURITY_GROUP" in t or "UNRESTRICTED" in t or "PORT" in t for t in types)

        for finding in findings:
            assert finding.severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            assert len(finding.description) > 0
            assert len(finding.evidence) > 0


class TestAnalysisEngineCitationsAndConfidence:
    """Tests for confidence scoring and source citations (Requirements 6.5, 8.1, 8.2)."""

    def test_analysis_engine_includes_citations_and_evidence(
        self, serverless_pattern_specs: list[ResourceSpec]
    ) -> None:
        """Requirements 6.5, 8.1, 8.2: Cite specific resource specifications with source checksums."""
        engine = AnalysisEngine()
        report = engine.analyze(serverless_pattern_specs)

        assert len(report.patterns) >= 1
        for pattern in report.patterns:
            assert 0.0 <= pattern.confidence <= 1.0
            assert len(pattern.citations) > 0
            for citation in pattern.citations:
                assert citation.resource_arn.startswith("arn:aws:")
                assert len(citation.property_path) > 0
                assert citation.source_checksum == "chk-hash-999"

        # Check report summary markdown
        assert len(report.summary_markdown) > 0
        assert "# Activity Flow & Architecture Analysis" in report.summary_markdown
        assert (
            "Evidence Citations" in report.summary_markdown or "Citation" in report.summary_markdown
        )
