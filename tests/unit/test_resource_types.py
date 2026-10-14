"""
Unit tests for the resource type registry (src/resource_types.py).

Validates:
- Req 1.3: the ten Supported_Resource_Types and their scope
- Req 3.2: resource ids, file ids and per-resource spec paths
"""

from __future__ import annotations

import pytest

from src.parser import ResourceSpec, SpecMetadata
from src.resource_types import (
    REGISTRY,
    canonical_type,
    file_id,
    resource_id,
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


def test_registry_has_ten_supported_types_req_1_3() -> None:
    assert set(REGISTRY) == {
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
    assert global_types == {"aws_s3_bucket", "aws_iam_role"}
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
