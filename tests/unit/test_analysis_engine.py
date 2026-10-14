"""
Unit tests for AnalysisEngine (AWS-field-name Specifications schema).

Requirements Coverage:
- Requirement 6.1: Relationships (vpc_connection, iam_role_usage, security_group,
  dynamodb_access, log_group)
- Requirement 6.2: Patterns and explicitly undetectable patterns
- Requirement 6.5: Rule-defined confidence scores and citations
- Requirement 6.6: Suspicious configuration findings
- Requirement 8.1 / 8.2 / 8.5: Every statement cited; citations resolve against specs
"""

from __future__ import annotations

import json

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.analysis_engine import AnalysisEngine
from src.integrity import resolve_property_path, seal_specs, spec_checksum
from src.parser import ResourceSpec, SpecMetadata
from src.resource_types import spec_relpath
from src.sanitizer import DataSanitizer

ACCOUNT = "123456789012"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT}:role/OrderServiceRole"


def _spec(
    resource_type: str, arn: str, specifications: dict, region: str = "us-east-1"
) -> ResourceSpec:
    return ResourceSpec(
        resource_type=resource_type,
        arn=arn,
        region=region,
        account_id=ACCOUNT,
        specifications=specifications,
        metadata=SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "2026-01-01", "chk-hash-999"),
    )


@pytest.fixture
def serverless_pattern_specs() -> list[ResourceSpec]:
    role = _spec(
        "aws_iam_role",
        ROLE_ARN,
        {
            "RoleName": "OrderServiceRole",
            "Arn": ROLE_ARN,
            "InlinePolicies": {},
            "AttachedPolicies": [],
        },
        region="global",
    )
    table = _spec(
        "aws_dynamodb_table",
        f"arn:aws:dynamodb:us-east-1:{ACCOUNT}:table/OrdersTable",
        {
            "TableName": "OrdersTable",
            "TableArn": f"arn:aws:dynamodb:us-east-1:{ACCOUNT}:table/OrdersTable",
        },
    )
    function = _spec(
        "aws_lambda_function",
        f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:OrderHandler",
        {
            "FunctionName": "OrderHandler",
            "Runtime": "python3.11",
            "Role": ROLE_ARN,
            "Environment": {"Variables": {"TABLE_NAME": "OrdersTable", "LOG_LEVEL": "INFO"}},
            "VpcConfig": {
                "VpcId": "vpc-1",
                "SubnetIds": ["subnet-1"],
                "SecurityGroupIds": ["sg-1"],
            },
        },
    )
    log_group = _spec(
        "aws_cloudwatch_log_group",
        f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/aws/lambda/OrderHandler",
        {"logGroupName": "/aws/lambda/OrderHandler", "retentionInDays": 14},
    )
    vpc = _spec("aws_vpc", f"arn:aws:ec2:us-east-1:{ACCOUNT}:vpc/vpc-1", {"VpcId": "vpc-1"})
    sg = _spec(
        "aws_security_group",
        f"arn:aws:ec2:us-east-1:{ACCOUNT}:security-group/sg-1",
        {"GroupId": "sg-1", "VpcId": "vpc-1", "IpPermissions": []},
    )
    return [role, table, function, log_group, vpc, sg]


@pytest.fixture
def compute_specs() -> list[ResourceSpec]:
    vpc = _spec("aws_vpc", f"arn:aws:ec2:us-east-1:{ACCOUNT}:vpc/vpc-9", {"VpcId": "vpc-9"})
    sg = _spec(
        "aws_security_group",
        f"arn:aws:ec2:us-east-1:{ACCOUNT}:security-group/sg-9",
        {"GroupId": "sg-9", "VpcId": "vpc-9", "IpPermissions": []},
    )
    role = _spec(
        "aws_iam_role",
        f"arn:aws:iam::{ACCOUNT}:role/web-role",
        {"RoleName": "web-role", "Arn": f"arn:aws:iam::{ACCOUNT}:role/web-role"},
        region="global",
    )
    instance = _spec(
        "aws_instance",
        f"arn:aws:ec2:us-east-1:{ACCOUNT}:instance/i-9",
        {
            "InstanceId": "i-9",
            "VpcId": "vpc-9",
            "SecurityGroups": [{"GroupId": "sg-9", "GroupName": "web"}],
            "IamInstanceProfile": {"Arn": f"arn:aws:iam::{ACCOUNT}:instance-profile/web-role"},
        },
    )
    db = _spec(
        "aws_db_instance",
        f"arn:aws:rds:us-east-1:{ACCOUNT}:db:orders-db",
        {
            "DBInstanceIdentifier": "orders-db",
            "DBSubnetGroup": {"VpcId": "vpc-9"},
            "VpcSecurityGroups": [{"VpcSecurityGroupId": "sg-9", "Status": "active"}],
        },
    )
    machine = _spec(
        "aws_sfn_state_machine",
        f"arn:aws:states:us-east-1:{ACCOUNT}:stateMachine:flow",
        {"name": "flow", "roleArn": f"arn:aws:iam::{ACCOUNT}:role/web-role"},
    )
    return [vpc, sg, role, instance, db, machine]


@pytest.fixture
def suspicious_security_specs() -> list[ResourceSpec]:
    admin_role = _spec(
        "aws_iam_role",
        f"arn:aws:iam::{ACCOUNT}:role/SuperAdminRole",
        {
            "RoleName": "SuperAdminRole",
            "InlinePolicies": {
                "admin": {"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}
            },
            "AttachedPolicies": [],
        },
        region="global",
    )
    public_bucket = _spec(
        "aws_s3_bucket",
        "arn:aws:s3:::leaky-bucket",
        {
            "Name": "leaky-bucket",
            "bucket-acl": {
                "Grants": [
                    {
                        "Grantee": {"Type": "CanonicalUser", "ID": "abc"},
                        "Permission": "FULL_CONTROL",
                    },
                    {
                        "Grantee": {
                            "Type": "Group",
                            "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                        },
                        "Permission": "READ",
                    },
                ]
            },
        },
        region="global",
    )
    open_sg = _spec(
        "aws_security_group",
        f"arn:aws:ec2:us-east-1:{ACCOUNT}:security-group/sg-01234567",
        {
            "GroupId": "sg-01234567",
            "GroupName": "open-ssh-sg",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "10.0.0.0/8"}, {"CidrIp": "0.0.0.0/0"}],
                }
            ],
        },
    )
    return [admin_role, public_bucket, open_sg]


def _rels(specs):
    return {
        (r.from_arn, r.to_arn, r.relationship_type): r
        for r in AnalysisEngine().identify_relationships(specs)
    }


# ----------------------------------------------------------------------------
# Relationships (Req 6.1)
# ----------------------------------------------------------------------------


class TestAnalysisEngineRelationships:
    def test_analysis_engine_identifies_relationships_req_6_1(self, serverless_pattern_specs):
        role, table, function, log_group, vpc, sg = serverless_pattern_specs
        rels = _rels(serverless_pattern_specs)
        assert rels[(function.arn, role.arn, "iam_role_usage")].confidence == 0.95
        assert rels[(function.arn, table.arn, "dynamodb_access")].confidence == 1.0
        assert rels[(function.arn, vpc.arn, "vpc_connection")].confidence == 1.0
        assert rels[(function.arn, sg.arn, "security_group")].confidence == 0.9
        assert rels[(sg.arn, vpc.arn, "vpc_connection")].confidence == 1.0

    def test_analysis_engine_log_group_relationship_req_6_1(self, serverless_pattern_specs):
        _role, _table, function, log_group, _vpc, _sg = serverless_pattern_specs
        rel = _rels(serverless_pattern_specs)[(function.arn, log_group.arn, "log_group")]
        assert rel.confidence == 1.0
        paths = {c.property_path for c in rel.citations}
        assert "specifications.FunctionName" in paths

    def test_analysis_engine_compute_relationships_req_6_1(self, compute_specs):
        vpc, sg, role, instance, db, machine = compute_specs
        rels = _rels(compute_specs)
        assert (instance.arn, vpc.arn, "vpc_connection") in rels
        assert (instance.arn, sg.arn, "security_group") in rels
        assert (instance.arn, role.arn, "iam_role_usage") in rels
        assert (db.arn, vpc.arn, "vpc_connection") in rels
        assert (db.arn, sg.arn, "security_group") in rels
        assert (machine.arn, role.arn, "iam_role_usage") in rels

    def test_analysis_engine_dynamodb_substring_match_confidence_req_6_5(
        self, serverless_pattern_specs
    ):
        function = serverless_pattern_specs[2]
        function.specifications["Environment"]["Variables"] = {
            "TABLE_URL": "https://example/OrdersTable/items"
        }
        rel = _rels(serverless_pattern_specs)[
            (function.arn, serverless_pattern_specs[1].arn, "dynamodb_access")
        ]
        assert rel.confidence == 0.85
        assert rel.citations[0].property_path == "specifications.Environment.Variables.TABLE_URL"

    def test_analysis_engine_ignores_references_to_uncollected_resources_req_8_5(self):
        lonely = _spec(
            "aws_lambda_function",
            f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:alone",
            {
                "FunctionName": "alone",
                "Role": f"arn:aws:iam::{ACCOUNT}:role/not-collected",
                "VpcConfig": {"VpcId": "vpc-x", "SecurityGroupIds": ["sg-x"]},
            },
        )
        assert AnalysisEngine().identify_relationships([lonely]) == []


# ----------------------------------------------------------------------------
# Patterns (Req 6.2, 6.5)
# ----------------------------------------------------------------------------


class TestAnalysisEnginePatterns:
    def test_analysis_engine_detects_patterns_req_6_2(self, serverless_pattern_specs):
        patterns = AnalysisEngine().detect_patterns(serverless_pattern_specs)
        serverless = next(p for p in patterns if p.pattern_name == "Serverless Application")
        function = serverless_pattern_specs[2]
        assert serverless.participating_resources[0] == function.arn
        assert set(serverless.participating_resources) >= {
            serverless_pattern_specs[0].arn,
            serverless_pattern_specs[1].arn,
        }
        # confidence = min of supporting relationships (0.95 role, 1.0 table)
        assert serverless.confidence == 0.95
        assert serverless.citations

    def test_analysis_engine_detects_compute_in_vpc_req_6_2(self, compute_specs):
        patterns = AnalysisEngine().detect_patterns(compute_specs)
        compute = next(p for p in patterns if p.pattern_name == "Compute in VPC")
        assert compute.participating_resources == [compute_specs[3].arn, compute_specs[0].arn]
        assert compute.confidence == 1.0

    def test_analysis_engine_reports_undetectable_patterns_req_6_2(self, serverless_pattern_specs):
        report = AnalysisEngine().analyze(serverless_pattern_specs)
        names = {u["pattern"] for u in report.undetectable_patterns}
        assert names == {
            "API Gateway + Lambda + DynamoDB",
            "S3 + CloudFront",
            "EC2 + Load Balancer",
        }
        assert all(
            "not a Supported_Resource_Type" in u["reason"] for u in report.undetectable_patterns
        )


# ----------------------------------------------------------------------------
# Security findings (Req 6.6)
# ----------------------------------------------------------------------------


class TestAnalysisEngineSecurity:
    def test_analysis_engine_flags_suspicious_patterns_req_6_6(self, suspicious_security_specs):
        findings = AnalysisEngine().flag_suspicious_patterns(suspicious_security_specs)
        by_type = {f.finding_type: f for f in findings}
        assert set(by_type) == {
            "OVERLY_PERMISSIVE_IAM_POLICY",
            "PUBLIC_S3_BUCKET",
            "UNRESTRICTED_SECURITY_GROUP_ACCESS",
        }
        assert by_type["OVERLY_PERMISSIVE_IAM_POLICY"].severity == "CRITICAL"
        assert by_type["PUBLIC_S3_BUCKET"].severity == "HIGH"
        assert by_type["UNRESTRICTED_SECURITY_GROUP_ACCESS"].severity == "HIGH"
        assert by_type["OVERLY_PERMISSIVE_IAM_POLICY"].citation.property_path == (
            "specifications.InlinePolicies.admin.Statement[0]"
        )
        assert (
            by_type["PUBLIC_S3_BUCKET"].citation.property_path
            == "specifications.bucket-acl.Grants[1]"
        )
        assert by_type["UNRESTRICTED_SECURITY_GROUP_ACCESS"].citation.property_path == (
            "specifications.IpPermissions[0].IpRanges[1]"
        )
        for finding in findings:
            assert finding.description and finding.evidence

    def test_analysis_engine_flags_admin_managed_policy_req_6_6(self):
        role = _spec(
            "aws_iam_role",
            f"arn:aws:iam::{ACCOUNT}:role/ops",
            {
                "RoleName": "ops",
                "AttachedPolicies": [
                    {
                        "PolicyName": "ReadOnlyAccess",
                        "PolicyArn": "arn:aws:iam::aws:policy/ReadOnlyAccess",
                    },
                    {
                        "PolicyName": "AdministratorAccess",
                        "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess",
                    },
                ],
            },
            region="global",
        )
        (finding,) = AnalysisEngine().flag_suspicious_patterns([role])
        assert finding.finding_type == "OVERLY_PERMISSIVE_IAM_POLICY"
        assert finding.citation.property_path == "specifications.AttachedPolicies[1]"

    def test_analysis_engine_does_not_flag_scoped_policies_req_6_6(self):
        role = _spec(
            "aws_iam_role",
            f"arn:aws:iam::{ACCOUNT}:role/app",
            {
                "RoleName": "app",
                "InlinePolicies": {
                    "scoped": {
                        "Statement": [
                            {"Effect": "Allow", "Action": ["s3:GetObject"], "Resource": "*"},
                            {"Effect": "Deny", "Action": "*", "Resource": "*"},
                        ]
                    }
                },
            },
            region="global",
        )
        assert AnalysisEngine().flag_suspicious_patterns([role]) == []

    def test_analysis_engine_flags_public_bucket_policy_req_6_6(self):
        policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::web/*",
                }
            ]
        }
        bucket = _spec(
            "aws_s3_bucket",
            "arn:aws:s3:::web",
            {"Name": "web", "bucket-policy": {"Policy": json.dumps(policy)}},
            region="global",
        )
        (finding,) = AnalysisEngine().flag_suspicious_patterns([bucket])
        assert finding.finding_type == "PUBLIC_S3_BUCKET"
        assert finding.citation.property_path == "specifications.bucket-policy.Policy"

    def test_analysis_engine_flags_ipv6_open_ingress_req_6_6(self):
        sg = _spec(
            "aws_security_group",
            f"arn:aws:ec2:us-east-1:{ACCOUNT}:security-group/sg-6",
            {
                "GroupId": "sg-6",
                "IpPermissions": [
                    {"IpProtocol": "-1", "IpRanges": [], "Ipv6Ranges": [{"CidrIpv6": "::/0"}]}
                ],
            },
        )
        (finding,) = AnalysisEngine().flag_suspicious_patterns([sg])
        assert finding.citation.property_path == "specifications.IpPermissions[0].Ipv6Ranges[0]"
        assert "all traffic" in finding.description


# ----------------------------------------------------------------------------
# Citations and report (Req 6.5, 8.1, 8.2, 8.5)
# ----------------------------------------------------------------------------


class TestAnalysisEngineCitations:
    def test_analysis_engine_includes_citations_and_evidence(self, serverless_pattern_specs):
        report = AnalysisEngine().analyze(serverless_pattern_specs)
        assert report.patterns
        for pattern in report.patterns:
            assert 0.0 <= pattern.confidence <= 1.0
            assert pattern.citations
            for citation in pattern.citations:
                assert citation.resource_arn.startswith("arn:aws:")
                assert citation.property_path.startswith("specifications.")
                assert citation.source_checksum == "chk-hash-999"
        assert "# Activity Flow & Architecture Analysis" in report.summary_markdown
        assert "Evidence Citations" in report.summary_markdown

    def test_analysis_engine_citations_include_spec_file_req_8_2(self, serverless_pattern_specs):
        report = AnalysisEngine().analyze(serverless_pattern_specs)
        by_arn = {s.arn: s for s in serverless_pattern_specs}
        for rel in report.relationships:
            assert rel.citations
            for citation in rel.citations:
                assert citation.spec_file == spec_relpath(by_arn[citation.resource_arn])

    def test_analysis_engine_unsealed_specs_use_computed_checksum_req_8_2(
        self, serverless_pattern_specs
    ):
        for spec in serverless_pattern_specs:
            spec.metadata.checksum = ""
        report = AnalysisEngine().analyze(serverless_pattern_specs)
        by_arn = {s.arn: s for s in serverless_pattern_specs}
        for rel in report.relationships:
            for citation in rel.citations:
                assert citation.source_checksum == spec_checksum(
                    by_arn[citation.resource_arn].specifications
                )

    def test_analysis_report_to_dict_is_json_serializable(
        self, serverless_pattern_specs, suspicious_security_specs
    ):
        data = (
            AnalysisEngine().analyze(serverless_pattern_specs + suspicious_security_specs).to_dict()
        )
        text = json.dumps(data)
        assert set(data) == {
            "generated_at",
            "resource_count",
            "relationships",
            "patterns",
            "security_findings",
            "undetectable_patterns",
        }
        assert data["resource_count"] == 9
        assert '"spec_file"' in text


_VARIABLE_VALUES = st.sampled_from(["OrdersTable", "x-OrdersTable-y", "INFO", "orders", ""])


@given(
    env=st.dictionaries(
        st.from_regex(r"[A-Z_]{1,8}", fullmatch=True), _VARIABLE_VALUES, max_size=4
    ),
    open_port=st.integers(min_value=0, max_value=65535),
    include_role=st.booleans(),
)
def test_property_citations_resolve_req_8_5(env, open_port, include_role):
    """Every citation's property_path resolves to evidence_value in the sealed spec."""
    specs = [
        _spec(
            "aws_dynamodb_table",
            f"arn:aws:dynamodb:us-east-1:{ACCOUNT}:table/OrdersTable",
            {"TableName": "OrdersTable"},
        ),
        _spec(
            "aws_lambda_function",
            f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:fn",
            {"FunctionName": "fn", "Role": ROLE_ARN, "Environment": {"Variables": env}},
        ),
        _spec(
            "aws_security_group",
            f"arn:aws:ec2:us-east-1:{ACCOUNT}:security-group/sg-p",
            {
                "GroupId": "sg-p",
                "IpPermissions": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": open_port,
                        "ToPort": open_port,
                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    }
                ],
            },
        ),
    ]
    if include_role:
        specs.append(
            _spec(
                "aws_iam_role",
                ROLE_ARN,
                {"RoleName": "OrderServiceRole", "Arn": ROLE_ARN},
                region="global",
            )
        )
    sealed = {s.arn: s for s in seal_specs(specs, DataSanitizer())}
    report = AnalysisEngine().analyze(list(sealed.values()))
    citations = [c for r in report.relationships for c in r.citations]
    citations += [c for p in report.patterns for c in p.citations]
    citations += [f.citation for f in report.security_findings]
    assert citations
    for citation in citations:
        spec = sealed[citation.resource_arn]
        document = spec.to_dict()
        assert resolve_property_path(document, citation.property_path) == citation.evidence_value
        assert citation.source_checksum == spec.metadata.checksum
        assert citation.spec_file == spec_relpath(spec)
