"""
Unit tests for the resource type registry (src/resource_types.py).

Validates:
- Req 1.3: the Supported_Resource_Types and their scope
- Req 14.1: network, edge and load-balancing types (ids, ARNs, aliases)
- Req 3.2: resource ids, file ids and per-resource spec paths
"""

from __future__ import annotations

import pytest

from src.parser import ResourceSpec, SpecMetadata
from src.resource_types import (
    REGISTRY,
    build_arn,
    canonical_type,
    file_id,
    parse_arn,
    resource_id,
    s3_bucket_from_domain,
    spec_relpath,
)


def _spec(
    resource_type: str, arn: str, specifications: dict, region: str = "us-east-1"
) -> ResourceSpec:
    return ResourceSpec(
        resource_type=resource_type,
        arn=arn,
        region=region,
        account_id="123456789012",
        specifications=specifications,
        metadata=SpecMetadata("2026-01-01T00:00:00Z", "0.1.0", "", ""),
    )


NETWORK_EDGE_TYPES = {
    "aws_subnet",
    "aws_route_table",
    "aws_internet_gateway",
    "aws_nat_gateway",
    "aws_vpc_endpoint",
    "aws_cloudfront_distribution",
    "aws_lb",
    "aws_lb_listener",
    "aws_lb_target_group",
    "aws_route53_zone",
    "aws_acm_certificate",
    "aws_wafv2_web_acl",
}


def test_registry_has_supported_types_req_1_3() -> None:
    assert set(REGISTRY) == NETWORK_EDGE_TYPES | {
        "aws_instance",
        "aws_vpc",
        "aws_security_group",
        "aws_lambda_function",
        "aws_db_instance",
        "aws_cloudwatch_log_group",
        "aws_sfn_state_machine",
        "aws_dynamodb_table",
        "aws_s3_bucket",
        "aws_iam_role",
    }
    global_types = {t for t, info in REGISTRY.items() if info.scope == "global"}
    assert global_types == {
        "aws_s3_bucket",
        "aws_iam_role",
        "aws_cloudfront_distribution",
        "aws_route53_zone",
    }
    for type_id, info in REGISTRY.items():
        assert info.type_id == type_id
        assert info.terraform_type == type_id


@pytest.mark.parametrize(
    ("alias", "expected"),
    [
        ("aws_instance", "aws_instance"),
        ("AWS_EC2_INSTANCE", "aws_instance"),
        ("ec2", "aws_instance"),
        ("ec2_instance", "aws_instance"),
        ("aws_rds_instance", "aws_db_instance"),
        ("rds", "aws_db_instance"),
        ("aws_step_function", "aws_sfn_state_machine"),
        ("stepfunctions", "aws_sfn_state_machine"),
        ("lambda", "aws_lambda_function"),
        ("lambda_function", "aws_lambda_function"),
        ("s3", "aws_s3_bucket"),
        ("s3_bucket", "aws_s3_bucket"),
        ("iam_role", "aws_iam_role"),
        ("dynamodb", "aws_dynamodb_table"),
        ("vpc", "aws_vpc"),
        ("security_group", "aws_security_group"),
        ("log_group", "aws_cloudwatch_log_group"),
        ("subnet", "aws_subnet"),
        ("route_table", "aws_route_table"),
        ("internet_gateway", "aws_internet_gateway"),
        ("nat_gateway", "aws_nat_gateway"),
        ("vpc_endpoint", "aws_vpc_endpoint"),
        ("cloudfront", "aws_cloudfront_distribution"),
        ("aws_alb", "aws_lb"),
        ("alb", "aws_lb"),
        ("aws_alb_listener", "aws_lb_listener"),
        ("aws_alb_target_group", "aws_lb_target_group"),
        ("target_group", "aws_lb_target_group"),
        ("route53", "aws_route53_zone"),
        ("hosted_zone", "aws_route53_zone"),
        ("acm", "aws_acm_certificate"),
        ("waf", "aws_wafv2_web_acl"),
        ("not_a_type", None),
        ("", None),
    ],
)
def test_canonical_type_resolves_aliases(alias: str, expected: str | None) -> None:
    assert canonical_type(alias) == expected


@pytest.mark.parametrize(
    ("resource_type", "arn", "specifications", "expected"),
    [
        (
            "aws_instance",
            "arn:aws:ec2:us-east-1:123456789012:instance/i-0abc",
            {"InstanceId": "i-0abc"},
            "i-0abc",
        ),
        ("aws_vpc", "arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1", {"VpcId": "vpc-1"}, "vpc-1"),
        (
            "aws_security_group",
            "arn:aws:ec2:us-east-1:123456789012:security-group/sg-1",
            {"GroupId": "sg-1"},
            "sg-1",
        ),
        (
            "aws_lambda_function",
            "arn:aws:lambda:us-east-1:123456789012:function:fn",
            {"FunctionName": "fn"},
            "fn",
        ),
        (
            "aws_db_instance",
            "arn:aws:rds:us-east-1:123456789012:db:db1",
            {"DBInstanceIdentifier": "db1"},
            "db1",
        ),
        (
            "aws_cloudwatch_log_group",
            "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/fn",
            {"logGroupName": "/aws/lambda/fn"},
            "/aws/lambda/fn",
        ),
        (
            "aws_sfn_state_machine",
            "arn:aws:states:us-east-1:123456789012:stateMachine:flow",
            {"name": "flow"},
            "flow",
        ),
        (
            "aws_dynamodb_table",
            "arn:aws:dynamodb:us-east-1:123456789012:table/orders",
            {"TableName": "orders"},
            "orders",
        ),
        ("aws_s3_bucket", "arn:aws:s3:::my-bucket", {"Name": "my-bucket"}, "my-bucket"),
        (
            "aws_iam_role",
            "arn:aws:iam::123456789012:role/app-role",
            {"RoleName": "app-role"},
            "app-role",
        ),
    ],
)
def test_resource_id_per_type_req_3_2(
    resource_type: str, arn: str, specifications: dict, expected: str
) -> None:
    assert resource_id(_spec(resource_type, arn, specifications)) == expected


def test_resource_id_falls_back_to_arn_segment_req_3_2() -> None:
    assert (
        resource_id(_spec("aws_s3_bucket", "arn:aws:s3:::fallback-bucket", {})) == "fallback-bucket"
    )
    assert resource_id(_spec("aws_iam_role", "arn:aws:iam::1:role/path/r1", {})) == "r1"
    assert (
        resource_id(_spec("aws_lambda_function", "arn:aws:lambda:us-east-1:1:function:f1", {}))
        == "f1"
    )
    assert resource_id(_spec("unknown_type", "arn:aws:x:us-east-1:1:thing/t1", {})) == "t1"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("i-0abc", "i-0abc"),
        ("/aws/lambda/fn", "aws_lambda_fn"),
        ("my bucket:name", "my_bucket_name"),
        ("a.b-c_d", "a.b-c_d"),
        ("///", "resource"),
        ("", "resource"),
    ],
)
def test_file_id_replaces_unsafe_characters_req_3_2(raw: str, expected: str) -> None:
    assert file_id(raw) == expected


def test_spec_relpath_layout_req_3_2() -> None:
    spec = _spec(
        "aws_cloudwatch_log_group",
        "arn:aws:logs:eu-west-1:123456789012:log-group:/aws/lambda/fn",
        {"logGroupName": "/aws/lambda/fn"},
        region="eu-west-1",
    )
    assert spec_relpath(spec) == "aws_cloudwatch_log_group/eu-west-1/aws_lambda_fn.json"

    global_spec = _spec("aws_s3_bucket", "arn:aws:s3:::b1", {"Name": "b1"}, region="global")
    assert spec_relpath(global_spec) == "aws_s3_bucket/global/b1.json"


def test_spec_relpath_defaults_missing_region_to_global_req_3_2() -> None:
    spec = _spec("aws_iam_role", "arn:aws:iam::1:role/r", {"RoleName": "r"}, region="")
    assert spec_relpath(spec) == "aws_iam_role/global/r.json"


def test_registry_drawio_styles_use_aws4_stencils_req_6_4() -> None:
    for info in REGISTRY.values():
        assert "mxgraph.aws4." in info.drawio_style


# ============================================================================
# Network, edge and load-balancing types (Requirement 14.1)
# ============================================================================

LB_ARN = (
    "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/web-alb/50dc6c495c0c9188"
)
LISTENER_ARN = (
    "arn:aws:elasticloadbalancing:us-east-1:123456789012:"
    "listener/app/web-alb/50dc6c495c0c9188/f2f7dc8efc522ab2"
)
TG_ARN = "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/web-tg/73e2d6bc24d8a067"
CERT_ARN = "arn:aws:acm:us-east-1:123456789012:certificate/8ce467c2-0f73-4f59-9932-6b8ca0a23ab0"
WAF_CF_ARN = "arn:aws:wafv2:us-east-1:123456789012:global/webacl/web-acl/25f96b32-2dac-4734"
WAF_REGIONAL_ARN = "arn:aws:wafv2:eu-west-1:123456789012:regional/webacl/api-acl/0270052e-779d"


@pytest.mark.parametrize(
    ("arn", "expected"),
    [
        (
            "arn:aws:ec2:us-east-1:123456789012:subnet/subnet-1",
            ("aws_subnet", "subnet-1", "us-east-1"),
        ),
        (
            "arn:aws:ec2:us-east-1:123456789012:route-table/rtb-1",
            ("aws_route_table", "rtb-1", "us-east-1"),
        ),
        (
            "arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-1",
            ("aws_internet_gateway", "igw-1", "us-east-1"),
        ),
        (
            "arn:aws:ec2:us-east-1:123456789012:natgateway/nat-1",
            ("aws_nat_gateway", "nat-1", "us-east-1"),
        ),
        (
            "arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-1",
            ("aws_vpc_endpoint", "vpce-1", "us-east-1"),
        ),
        (
            "arn:aws:cloudfront::123456789012:distribution/E1ABC",
            ("aws_cloudfront_distribution", "E1ABC", "global"),
        ),
        (LB_ARN, ("aws_lb", "app/web-alb/50dc6c495c0c9188", "us-east-1")),
        (
            LISTENER_ARN,
            ("aws_lb_listener", "app/web-alb/50dc6c495c0c9188/f2f7dc8efc522ab2", "us-east-1"),
        ),
        (TG_ARN, ("aws_lb_target_group", "web-tg/73e2d6bc24d8a067", "us-east-1")),
        ("arn:aws:route53:::hostedzone/Z123", ("aws_route53_zone", "Z123", "global")),
        (CERT_ARN, ("aws_acm_certificate", "8ce467c2-0f73-4f59-9932-6b8ca0a23ab0", "us-east-1")),
        # CloudFront-scope web ACLs are global (API endpoint us-east-1); moto writes "global".
        (WAF_CF_ARN, ("aws_wafv2_web_acl", "web-acl/25f96b32-2dac-4734", "global")),
        (
            "arn:aws:wafv2:global:123456789012:global/webacl/web-acl/25f96b32-2dac-4734",
            ("aws_wafv2_web_acl", "web-acl/25f96b32-2dac-4734", "global"),
        ),
        (
            WAF_REGIONAL_ARN,
            ("aws_wafv2_web_acl", "api-acl/0270052e-779d", "eu-west-1"),
        ),
        # Classic load balancers, listener rules and WAF IP sets are not supported.
        ("arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/classic-lb", None),
        (
            "arn:aws:elasticloadbalancing:us-east-1:123456789012:"
            "listener-rule/app/web-alb/50dc/f2f7/9683",
            None,
        ),
        ("arn:aws:wafv2:us-east-1:123456789012:regional/ipset/ips/1234", None),
        ("arn:aws:route53:::healthcheck/abc", None),
    ],
)
def test_parse_arn_network_edge_types_req_14_1(arn: str, expected: tuple | None) -> None:
    assert parse_arn(arn) == expected


def test_build_arn_network_edge_types_req_14_1() -> None:
    assert build_arn("aws_subnet", "subnet-1", "us-east-1", "123456789012") == (
        "arn:aws:ec2:us-east-1:123456789012:subnet/subnet-1"
    )
    assert build_arn("aws_cloudfront_distribution", "E1ABC", "global", "123456789012") == (
        "arn:aws:cloudfront::123456789012:distribution/E1ABC"
    )
    # Route 53 ARNs carry neither region nor account.
    assert build_arn("aws_route53_zone", "Z123", "global", "123456789012") == (
        "arn:aws:route53:::hostedzone/Z123"
    )
    for arn in (LB_ARN, LISTENER_ARN, TG_ARN, CERT_ARN, WAF_CF_ARN, WAF_REGIONAL_ARN):
        type_id, raw_id, region = parse_arn(arn)  # type: ignore[misc]
        assert build_arn(type_id, raw_id, region, "123456789012") == arn


@pytest.mark.parametrize(
    ("resource_type", "arn", "specifications", "expected"),
    [
        (
            "aws_subnet",
            "arn:aws:ec2:us-east-1:1:subnet/subnet-1",
            {"SubnetId": "subnet-1"},
            "subnet-1",
        ),
        ("aws_lb", LB_ARN, {"LoadBalancerArn": LB_ARN}, "app/web-alb/50dc6c495c0c9188"),
        ("aws_lb_target_group", TG_ARN, {}, "web-tg/73e2d6bc24d8a067"),
        ("aws_acm_certificate", CERT_ARN, {}, "8ce467c2-0f73-4f59-9932-6b8ca0a23ab0"),
        (
            "aws_route53_zone",
            "arn:aws:route53:::hostedzone/Z123",
            {"Id": "/hostedzone/Z123"},
            "Z123",
        ),
        (
            "aws_cloudfront_distribution",
            "arn:aws:cloudfront::1:distribution/E1ABC",
            {"Id": "E1ABC"},
            "E1ABC",
        ),
    ],
)
def test_resource_id_network_edge_types_req_14_1(
    resource_type: str, arn: str, specifications: dict, expected: str
) -> None:
    spec = _spec(resource_type, arn, specifications)
    assert resource_id(spec) == expected
    assert "/" not in spec_relpath(spec).split("/", 2)[2]


@pytest.mark.parametrize(
    ("domain", "expected"),
    [
        ("assets.s3.amazonaws.com", "assets"),
        ("assets.s3.us-east-1.amazonaws.com", "assets"),
        ("my.assets.s3.eu-west-1.amazonaws.com", "my.assets"),
        ("assets.s3-website-us-east-1.amazonaws.com", "assets"),
        ("assets.s3-website.eu-west-1.amazonaws.com", "assets"),
        ("assets.s3.dualstack.us-east-1.amazonaws.com", "assets"),
        ("web-alb-1.us-east-1.elb.amazonaws.com", None),
        ("api.example.com", None),
    ],
)
def test_s3_bucket_from_origin_domain_req_14_3(domain: str, expected: str | None) -> None:
    assert s3_bucket_from_domain(domain) == expected
