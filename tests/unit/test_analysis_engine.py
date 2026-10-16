"""
Unit tests for AnalysisEngine (AWS-field-name Specifications schema).

Requirements Coverage:
- Requirement 6.1: Relationships (vpc_connection, iam_role_usage, security_group,
  dynamodb_access, log_group)
- Requirement 6.2: Patterns and explicitly undetectable patterns
- Requirement 6.5: Rule-defined confidence scores and citations
- Requirement 6.6: Suspicious configuration findings
- Requirement 8.1 / 8.2 / 8.5: Every statement cited; citations resolve against specs
- Requirement 14.2: Network and load-balancing relationships
- Requirement 14.3: Edge relationships (CloudFront origins, WAF, ACM, Route 53 aliases)
- Requirement 14.4: Compute and data relationships (ECS, Auto Scaling, ElastiCache,
  messaging and event targets) and the web-app / static-site patterns
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
        # S3 + CloudFront is detected since Task 29 ("Static site: S3 + CloudFront").
        assert names == {"API Gateway + Lambda + DynamoDB", "EC2 + Load Balancer"}
        reasons = {u["pattern"]: u["reason"] for u in report.undetectable_patterns}
        assert (
            "API Gateway is not a Supported_Resource_Type"
            in reasons["API Gateway + Lambda + DynamoDB"]
        )
        # CloudFront and ELB are supported now: the reasons must not claim otherwise.
        assert "DescribeTargetHealth" in reasons["EC2 + Load Balancer"]
        assert "lb_target" in reasons["EC2 + Load Balancer"]
        assert not any(
            "CloudFront is not" in r or "Load Balancing is not" in r for r in reasons.values()
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


# ----------------------------------------------------------------------------
# Network, load-balancing and edge relationships (Req 14.2, 14.3)
# ----------------------------------------------------------------------------

EC2 = f"arn:aws:ec2:us-east-1:{ACCOUNT}"
ELB = f"arn:aws:elasticloadbalancing:us-east-1:{ACCOUNT}"
LB_ARN = f"{ELB}:loadbalancer/app/web-alb/abc"
LISTENER_ARN = f"{ELB}:listener/app/web-alb/abc/def"
TG_ARN = f"{ELB}:targetgroup/web-tg/123"
CERT_ARN = f"arn:aws:acm:us-east-1:{ACCOUNT}:certificate/uuid-1"
WAF_ARN = f"arn:aws:wafv2:us-east-1:{ACCOUNT}:global/webacl/web-acl/uuid-2"
CF_ARN = f"arn:aws:cloudfront::{ACCOUNT}:distribution/E1"
ZONE_ARN = "arn:aws:route53:::hostedzone/Z1"
BUCKET_ARN = "arn:aws:s3:::static-site"
LB_DNS = "web-alb-1.us-east-1.elb.amazonaws.com"
CF_DNS = "d111111abcdef8.cloudfront.net"


@pytest.fixture
def web_stack_specs() -> list[ResourceSpec]:
    return [
        _spec("aws_vpc", f"{EC2}:vpc/vpc-1", {"VpcId": "vpc-1"}),
        _spec("aws_subnet", f"{EC2}:subnet/subnet-a", {"SubnetId": "subnet-a", "VpcId": "vpc-1"}),
        _spec("aws_subnet", f"{EC2}:subnet/subnet-b", {"SubnetId": "subnet-b", "VpcId": "vpc-1"}),
        _spec(
            "aws_route_table",
            f"{EC2}:route-table/rtb-public",
            {
                "RouteTableId": "rtb-public",
                "VpcId": "vpc-1",
                "Routes": [
                    {"DestinationCidrBlock": "10.0.0.0/16", "GatewayId": "local"},
                    {"DestinationCidrBlock": "0.0.0.0/0", "GatewayId": "igw-1"},
                ],
                "Associations": [{"Main": True}, {"Main": False, "SubnetId": "subnet-a"}],
            },
        ),
        _spec(
            "aws_route_table",
            f"{EC2}:route-table/rtb-private",
            {
                "RouteTableId": "rtb-private",
                "VpcId": "vpc-1",
                "Routes": [
                    {"DestinationCidrBlock": "0.0.0.0/0", "NatGatewayId": "nat-1"},
                    {"DestinationPrefixListId": "pl-1", "GatewayId": "vpce-1"},
                ],
                "Associations": [],
            },
        ),
        _spec(
            "aws_internet_gateway",
            f"{EC2}:internet-gateway/igw-1",
            {"InternetGatewayId": "igw-1", "Attachments": [{"VpcId": "vpc-1"}]},
        ),
        _spec(
            "aws_nat_gateway",
            f"{EC2}:natgateway/nat-1",
            {"NatGatewayId": "nat-1", "SubnetId": "subnet-a", "VpcId": "vpc-1"},
        ),
        _spec(
            "aws_vpc_endpoint",
            f"{EC2}:vpc-endpoint/vpce-1",
            {"VpcEndpointId": "vpce-1", "VpcId": "vpc-1"},
        ),
        _spec("aws_security_group", f"{EC2}:security-group/sg-alb", {"GroupId": "sg-alb"}),
        _spec(
            "aws_instance",
            f"{EC2}:instance/i-1",
            {"InstanceId": "i-1", "SubnetId": "subnet-b"},
        ),
        _spec(
            "aws_lb",
            LB_ARN,
            {
                "LoadBalancerArn": LB_ARN,
                "DNSName": LB_DNS,
                "VpcId": "vpc-1",
                "AvailabilityZones": [{"SubnetId": "subnet-a"}, {"SubnetId": "subnet-b"}],
                "SecurityGroups": ["sg-alb"],
            },
        ),
        _spec(
            "aws_lb_listener",
            LISTENER_ARN,
            {
                "ListenerArn": LISTENER_ARN,
                "LoadBalancerArn": LB_ARN,
                "Certificates": [{"CertificateArn": CERT_ARN}],
                "DefaultActions": [{"Type": "forward", "TargetGroupArn": TG_ARN}],
            },
        ),
        _spec(
            "aws_lb_target_group",
            TG_ARN,
            {"TargetGroupArn": TG_ARN, "VpcId": "vpc-1", "LoadBalancerArns": [LB_ARN]},
        ),
        _spec("aws_acm_certificate", CERT_ARN, {"CertificateArn": CERT_ARN}),
        _spec("aws_wafv2_web_acl", WAF_ARN, {"ARN": WAF_ARN, "Name": "web-acl"}, region="global"),
        _spec("aws_s3_bucket", BUCKET_ARN, {"Name": "static-site"}, region="global"),
        _spec(
            "aws_cloudfront_distribution",
            CF_ARN,
            {
                "Id": "E1",
                "DomainName": CF_DNS,
                "DistributionConfig": {
                    "Origins": {
                        "Items": [
                            {"Id": "s3", "DomainName": "static-site.s3.us-east-1.amazonaws.com"},
                            {"Id": "alb", "DomainName": LB_DNS},
                            {"Id": "other", "DomainName": "api.example.com"},
                        ]
                    },
                    "WebACLId": WAF_ARN,
                    "ViewerCertificate": {"ACMCertificateArn": CERT_ARN},
                },
            },
            region="global",
        ),
        _spec(
            "aws_route53_zone",
            ZONE_ARN,
            {
                "Id": "/hostedzone/Z1",
                "Name": "example.com.",
                "ResourceRecordSets": [
                    {"Name": "example.com.", "Type": "NS", "ResourceRecords": []},
                    {
                        "Name": "shop.example.com.",
                        "Type": "A",
                        "AliasTarget": {"DNSName": CF_DNS.upper() + "."},
                    },
                    {
                        "Name": "api.example.com.",
                        "Type": "A",
                        "AliasTarget": {"DNSName": f"dualstack.{LB_DNS}."},
                    },
                ],
            },
            region="global",
        ),
    ]


class TestAnalysisEngineNetworkEdge:
    def test_analysis_engine_network_relationships_req_14_2(self, web_stack_specs):
        rels = AnalysisEngine().identify_relationships(web_stack_specs)
        found = {(r.from_arn, r.to_arn, r.relationship_type) for r in rels}
        vpc = f"{EC2}:vpc/vpc-1"
        subnet_a, subnet_b = f"{EC2}:subnet/subnet-a", f"{EC2}:subnet/subnet-b"
        expected = {
            (subnet_a, vpc, "vpc_connection"),
            (f"{EC2}:route-table/rtb-public", vpc, "vpc_connection"),
            (f"{EC2}:route-table/rtb-public", subnet_a, "route_table_association"),
            (f"{EC2}:route-table/rtb-public", f"{EC2}:internet-gateway/igw-1", "route_target"),
            (f"{EC2}:route-table/rtb-private", f"{EC2}:natgateway/nat-1", "route_target"),
            (f"{EC2}:route-table/rtb-private", f"{EC2}:vpc-endpoint/vpce-1", "route_target"),
            (f"{EC2}:internet-gateway/igw-1", vpc, "vpc_connection"),
            (f"{EC2}:natgateway/nat-1", subnet_a, "subnet_placement"),
            (f"{EC2}:vpc-endpoint/vpce-1", vpc, "vpc_connection"),
            (f"{EC2}:instance/i-1", subnet_b, "subnet_placement"),
            (LB_ARN, subnet_a, "subnet_placement"),
            (LB_ARN, subnet_b, "subnet_placement"),
            (LB_ARN, f"{EC2}:security-group/sg-alb", "security_group"),
            (LB_ARN, vpc, "vpc_connection"),
            (LISTENER_ARN, LB_ARN, "lb_listener"),
            (LISTENER_ARN, TG_ARN, "forwards_to"),
            (LISTENER_ARN, CERT_ARN, "certificate"),
            (TG_ARN, vpc, "vpc_connection"),
        }
        assert expected <= found
        by_key = {(r.from_arn, r.to_arn, r.relationship_type): r for r in rels}
        association = by_key[(f"{EC2}:route-table/rtb-public", subnet_a, "route_table_association")]
        assert association.citations[0].property_path == ("specifications.Associations[1].SubnetId")
        forward = by_key[(LISTENER_ARN, TG_ARN, "forwards_to")]
        assert forward.citations[0].property_path == (
            "specifications.DefaultActions[0].TargetGroupArn"
        )
        assert all(r.confidence == 1.0 for r in rels if r.relationship_type != "security_group")

    def test_analysis_engine_edge_relationships_req_14_3(self, web_stack_specs):
        rels = AnalysisEngine().identify_relationships(web_stack_specs)
        by_key = {(r.from_arn, r.to_arn, r.relationship_type): r for r in rels}
        edge = {k for k in by_key if k[0] in (CF_ARN, ZONE_ARN)}
        assert edge == {
            (CF_ARN, BUCKET_ARN, "cdn_origin"),
            (CF_ARN, LB_ARN, "cdn_origin"),
            (CF_ARN, WAF_ARN, "waf_protection"),
            (CF_ARN, CERT_ARN, "certificate"),
            (ZONE_ARN, CF_ARN, "dns_alias"),
            (ZONE_ARN, LB_ARN, "dns_alias"),
        }
        origin = by_key[(CF_ARN, LB_ARN, "cdn_origin")]
        assert [c.property_path for c in origin.citations] == [
            "specifications.DistributionConfig.Origins.Items[1].DomainName",
            "specifications.DNSName",
        ]
        alias = by_key[(ZONE_ARN, CF_ARN, "dns_alias")]
        assert [c.property_path for c in alias.citations] == [
            "specifications.ResourceRecordSets[1].AliasTarget.DNSName",
            "specifications.DomainName",
        ]
        assert by_key[(CF_ARN, BUCKET_ARN, "cdn_origin")].citations[0].evidence_value == (
            "static-site.s3.us-east-1.amazonaws.com"
        )

    def test_analysis_engine_network_edge_citations_resolve_req_8_5(self, web_stack_specs):
        sealed = seal_specs(web_stack_specs, DataSanitizer())
        documents = {spec_relpath(s): {"specifications": s.specifications} for s in sealed}
        checksums = {spec_relpath(s): s.metadata.checksum for s in sealed}
        rels = AnalysisEngine().identify_relationships(sealed)
        assert rels
        for rel in rels:
            for citation in rel.citations:
                assert citation.source_checksum == checksums[citation.spec_file]
                assert (
                    resolve_property_path(documents[citation.spec_file], citation.property_path)
                    == citation.evidence_value
                )


# ----------------------------------------------------------------------------
# Compute and data relationships and patterns (Req 14.4, 6.2)
# ----------------------------------------------------------------------------

ECS = f"arn:aws:ecs:us-east-1:{ACCOUNT}"
CLUSTER_ARN = f"{ECS}:cluster/web"
SERVICE_ARN = f"{ECS}:service/web/api"
TASK_ARN = f"{ECS}:task-definition/api:7"
REPO_ARN = f"arn:aws:ecr:us-east-1:{ACCOUNT}:repository/api"
REPO_URI = f"{ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/api"
ASG_ARN = (
    f"arn:aws:autoscaling:us-east-1:{ACCOUNT}:autoScalingGroup:uuid:autoScalingGroupName/workers"
)
LT_ARN = f"{EC2}:launch-template/lt-1"
CACHE_ARN = f"arn:aws:elasticache:us-east-1:{ACCOUNT}:replicationgroup:cache"
QUEUE_ARN = f"arn:aws:sqs:us-east-1:{ACCOUNT}:jobs"
TOPIC_ARN = f"arn:aws:sns:us-east-1:{ACCOUNT}:events"
RULE_ARN = f"arn:aws:events:us-east-1:{ACCOUNT}:rule/nightly"
SCHEDULE_ARN = f"arn:aws:scheduler:us-east-1:{ACCOUNT}:schedule/default/report"
FUNCTION_ARN = f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:worker"
TASK_ROLE = f"arn:aws:iam::{ACCOUNT}:role/api-task"
EVENTS_ROLE = f"arn:aws:iam::{ACCOUNT}:role/events"


@pytest.fixture
def compute_stack_specs(web_stack_specs) -> list[ResourceSpec]:
    return [
        *web_stack_specs,
        _spec("aws_security_group", f"{EC2}:security-group/sg-app", {"GroupId": "sg-app"}),
        _spec("aws_iam_role", TASK_ROLE, {"RoleName": "api-task", "Arn": TASK_ROLE}, "global"),
        _spec("aws_iam_role", EVENTS_ROLE, {"RoleName": "events", "Arn": EVENTS_ROLE}, "global"),
        _spec(
            "aws_cloudwatch_log_group",
            f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/ecs/api",
            {"logGroupName": "/ecs/api"},
        ),
        _spec("aws_ecs_cluster", CLUSTER_ARN, {"clusterArn": CLUSTER_ARN, "clusterName": "web"}),
        _spec(
            "aws_ecs_service",
            SERVICE_ARN,
            {
                "serviceArn": SERVICE_ARN,
                "clusterArn": CLUSTER_ARN,
                "taskDefinition": TASK_ARN,
                "loadBalancers": [{"targetGroupArn": TG_ARN, "containerName": "api"}],
                "networkConfiguration": {
                    "awsvpcConfiguration": {"subnets": ["subnet-b"], "securityGroups": ["sg-app"]}
                },
            },
        ),
        _spec(
            "aws_ecs_task_definition",
            TASK_ARN,
            {
                "taskDefinitionArn": TASK_ARN,
                "taskRoleArn": TASK_ROLE,
                "containerDefinitions": [
                    {
                        "name": "api",
                        "image": f"{REPO_URI}:1.2.3",
                        "logConfiguration": {"options": {"awslogs-group": "/ecs/api"}},
                    }
                ],
            },
        ),
        _spec(
            "aws_ecr_repository",
            REPO_ARN,
            {"repositoryName": "api", "repositoryArn": REPO_ARN, "repositoryUri": REPO_URI},
        ),
        _spec(
            "aws_autoscaling_group",
            ASG_ARN,
            {
                "AutoScalingGroupName": "workers",
                "LaunchTemplate": {"LaunchTemplateId": "lt-1"},
                "VPCZoneIdentifier": "subnet-a,subnet-b",
                "TargetGroupARNs": [TG_ARN],
            },
        ),
        _spec(
            "aws_launch_template",
            LT_ARN,
            {
                "LaunchTemplateId": "lt-1",
                "LaunchTemplateData": {
                    "SecurityGroupIds": ["sg-app"],
                    "IamInstanceProfile": {"Name": "api-task"},
                },
            },
        ),
        _spec(
            "aws_elasticache_replication_group",
            CACHE_ARN,
            {
                "ReplicationGroupId": "cache",
                "CacheCluster": {"SecurityGroups": [{"SecurityGroupId": "sg-app"}]},
                "CacheSubnetGroup": {
                    "VpcId": "vpc-1",
                    "Subnets": [{"SubnetIdentifier": "subnet-a"}],
                },
            },
        ),
        _spec("aws_sqs_queue", QUEUE_ARN, {"Attributes": {"QueueArn": QUEUE_ARN}}),
        _spec("aws_lambda_function", FUNCTION_ARN, {"FunctionName": "worker"}),
        _spec(
            "aws_sns_topic",
            TOPIC_ARN,
            {
                "Attributes": {"TopicArn": TOPIC_ARN},
                "Subscriptions": [{"Protocol": "sqs", "Endpoint": QUEUE_ARN}],
            },
        ),
        _spec(
            "aws_cloudwatch_event_rule",
            RULE_ARN,
            {
                "Name": "nightly",
                "Targets": [
                    {"Id": "1", "Arn": f"{FUNCTION_ARN}:live"},
                    {"Id": "2", "Arn": CLUSTER_ARN, "RoleArn": EVENTS_ROLE},
                ],
            },
        ),
        _spec(
            "aws_scheduler_schedule",
            SCHEDULE_ARN,
            {"Name": "report", "Target": {"Arn": QUEUE_ARN, "RoleArn": EVENTS_ROLE}},
        ),
    ]


class TestAnalysisEngineComputeData:
    def test_analysis_engine_compute_relationships_req_14_4(self, compute_stack_specs):
        rels = AnalysisEngine().identify_relationships(compute_stack_specs)
        by_key = {(r.from_arn, r.to_arn, r.relationship_type): r for r in rels}
        sg_app, vpc = f"{EC2}:security-group/sg-app", f"{EC2}:vpc/vpc-1"
        subnet_a, subnet_b = f"{EC2}:subnet/subnet-a", f"{EC2}:subnet/subnet-b"
        log_group = f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/ecs/api"
        expected = {
            (SERVICE_ARN, CLUSTER_ARN, "ecs_cluster"),
            (SERVICE_ARN, TASK_ARN, "task_definition"),
            (SERVICE_ARN, subnet_b, "subnet_placement"),
            (SERVICE_ARN, sg_app, "security_group"),
            (TG_ARN, SERVICE_ARN, "lb_target"),
            (TG_ARN, ASG_ARN, "lb_target"),
            (TASK_ARN, TASK_ROLE, "iam_role_usage"),
            (TASK_ARN, log_group, "log_group"),
            (TASK_ARN, REPO_ARN, "container_image"),
            (ASG_ARN, LT_ARN, "launch_template"),
            (ASG_ARN, subnet_a, "subnet_placement"),
            (ASG_ARN, subnet_b, "subnet_placement"),
            (LT_ARN, sg_app, "security_group"),
            (LT_ARN, TASK_ROLE, "iam_role_usage"),
            (CACHE_ARN, sg_app, "security_group"),
            (CACHE_ARN, subnet_a, "subnet_placement"),
            (CACHE_ARN, vpc, "vpc_connection"),
            (TOPIC_ARN, QUEUE_ARN, "subscription"),
            (RULE_ARN, FUNCTION_ARN, "event_target"),
            (RULE_ARN, CLUSTER_ARN, "event_target"),
            (RULE_ARN, EVENTS_ROLE, "iam_role_usage"),
            (SCHEDULE_ARN, QUEUE_ARN, "event_target"),
            (SCHEDULE_ARN, EVENTS_ROLE, "iam_role_usage"),
        }
        assert expected <= set(by_key)

        # The target group -> service edge is cited at the service's own reference.
        lb_target = by_key[(TG_ARN, SERVICE_ARN, "lb_target")]
        assert [(c.resource_arn, c.property_path) for c in lb_target.citations] == [
            (SERVICE_ARN, "specifications.loadBalancers[0].targetGroupArn")
        ]
        image = by_key[(TASK_ARN, REPO_ARN, "container_image")]
        assert [c.property_path for c in image.citations] == [
            "specifications.containerDefinitions[0].image",
            "specifications.repositoryUri",
        ]
        subnet = by_key[(ASG_ARN, subnet_b, "subnet_placement")]
        assert subnet.citations[0].evidence_value == "subnet-a,subnet-b"
        target = by_key[(RULE_ARN, FUNCTION_ARN, "event_target")]
        assert target.citations[0].property_path == "specifications.Targets[0].Arn"
        assert by_key[(LT_ARN, TASK_ROLE, "iam_role_usage")].confidence == 0.95
        assert by_key[(SERVICE_ARN, sg_app, "security_group")].confidence == 0.9
        assert by_key[(TG_ARN, ASG_ARN, "lb_target")].confidence == 1.0

    def test_analysis_engine_web_app_pattern_req_6_2(self, compute_stack_specs):
        patterns = AnalysisEngine().detect_patterns(compute_stack_specs)
        (web,) = [p for p in patterns if p.pattern_name == "Web app: CloudFront + ALB + ECS"]
        assert web.participating_resources == [CF_ARN, LB_ARN, LISTENER_ARN, TG_ARN, SERVICE_ARN]
        assert web.confidence == 1.0
        assert "web-alb" in web.description and "web/api" in web.description
        assert {c.resource_arn for c in web.citations} == {
            CF_ARN,
            LB_ARN,
            LISTENER_ARN,
            SERVICE_ARN,
        }

    def test_analysis_engine_static_site_pattern_req_6_2(self, web_stack_specs):
        patterns = AnalysisEngine().detect_patterns(web_stack_specs)
        (site,) = [p for p in patterns if p.pattern_name == "Static site: S3 + CloudFront"]
        assert site.participating_resources == [CF_ARN, BUCKET_ARN]
        assert site.confidence == 1.0
        assert "static-site" in site.description
        # Without an ECS service behind the load balancer there is no web-app pattern.
        assert not [p for p in patterns if p.pattern_name.startswith("Web app")]

    def test_analysis_engine_compute_citations_resolve_req_8_5(self, compute_stack_specs):
        sealed = seal_specs(compute_stack_specs, DataSanitizer())
        documents = {spec_relpath(s): {"specifications": s.specifications} for s in sealed}
        report = AnalysisEngine().analyze(sealed)
        citations = [c for r in report.relationships for c in r.citations]
        citations += [c for p in report.patterns for c in p.citations]
        assert citations
        for citation in citations:
            assert (
                resolve_property_path(documents[citation.spec_file], citation.property_path)
                == citation.evidence_value
            )


# ----------------------------------------------------------------------------
# Network access through security group rules (Req 15.2)
# ----------------------------------------------------------------------------

DB_ARN = f"arn:aws:rds:us-east-1:{ACCOUNT}:db:orders"


@pytest.fixture
def network_access_specs(compute_stack_specs) -> list[ResourceSpec]:
    """sg-app admits Redis from itself; sg-db admits PostgreSQL from sg-app."""
    specs = [s for s in compute_stack_specs if s.arn != f"{EC2}:security-group/sg-app"]
    return [
        *specs,
        _spec(
            "aws_security_group",
            f"{EC2}:security-group/sg-app",
            {
                "GroupId": "sg-app",
                "IpPermissions": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 80,
                        "ToPort": 80,
                        "UserIdGroupPairs": [{"GroupId": "sg-alb"}],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 6379,
                        "ToPort": 6379,
                        "UserIdGroupPairs": [{"GroupId": "sg-app"}],
                    },
                ],
            },
        ),
        _spec(
            "aws_security_group",
            f"{EC2}:security-group/sg-db",
            {
                "GroupId": "sg-db",
                "IpPermissions": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 5432,
                        "ToPort": 5432,
                        "UserIdGroupPairs": [{"GroupId": "sg-app"}],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [{"CidrIp": "10.0.0.0/8"}],
                    },
                ],
            },
        ),
        _spec(
            "aws_db_instance",
            DB_ARN,
            {
                "DBInstanceIdentifier": "orders",
                "VpcSecurityGroups": [{"VpcSecurityGroupId": "sg-db", "Status": "active"}],
            },
        ),
    ]


class TestAnalysisEngineNetworkAccess:
    def test_analysis_engine_network_access_from_security_group_rules_req_15_2(
        self, network_access_specs
    ):
        rels = AnalysisEngine().identify_relationships(network_access_specs)
        access = {
            (r.from_arn, r.to_arn): r for r in rels if r.relationship_type == "network_access"
        }
        # Compute -> data stores only: no cache -> service, no ALB -> service edge here.
        assert set(access) == {
            (SERVICE_ARN, DB_ARN),
            (SERVICE_ARN, CACHE_ARN),
            (ASG_ARN, DB_ARN),
            (ASG_ARN, CACHE_ARN),
        }
        to_db = access[(SERVICE_ARN, DB_ARN)]
        assert to_db.confidence == 0.9
        assert [(c.resource_arn, c.property_path, c.evidence_value) for c in to_db.citations] == [
            (
                f"{EC2}:security-group/sg-db",
                "specifications.IpPermissions[0].UserIdGroupPairs[0].GroupId",
                "sg-app",
            ),
            (
                SERVICE_ARN,
                "specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0]",
                "sg-app",
            ),
        ]
        # Auto Scaling groups reach their security groups through the launch template.
        assert access[(ASG_ARN, CACHE_ARN)].citations[1].resource_arn == LT_ARN

    def test_analysis_engine_network_access_citations_resolve_req_8_5(self, network_access_specs):
        sealed = seal_specs(network_access_specs, DataSanitizer())
        documents = {spec_relpath(s): {"specifications": s.specifications} for s in sealed}
        rels = [
            r
            for r in AnalysisEngine().identify_relationships(sealed)
            if r.relationship_type == "network_access"
        ]
        assert rels
        for citation in (c for r in rels for c in r.citations):
            assert (
                resolve_property_path(documents[citation.spec_file], citation.property_path)
                == citation.evidence_value
            )
