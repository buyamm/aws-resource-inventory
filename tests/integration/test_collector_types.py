"""
Integration tests (moto): SpecCollector produces the per-type Specifications
schema defined in design.md for every Supported_Resource_Type.

Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.6, 3.3
"""

from __future__ import annotations

import pytest

from src.collector import SpecCollector

pytestmark = pytest.mark.integration

ACCOUNT = "123456789012"
REGION = "us-east-1"


def _collect(session, service, resource_type, resource_id, arn, region=REGION):
    client = session.client(service, region_name="us-east-1" if region == "global" else region)
    collector = SpecCollector(api_client=client)
    result = collector.collect_resource(resource_type, resource_id, arn, region, ACCOUNT)
    assert result.is_ok(), result.error if result.is_err() else ""
    spec = result.value
    assert spec.resource_type == resource_type
    assert spec.region == region
    assert spec.account_id == ACCOUNT
    assert spec.arn == arn
    assert "ResponseMetadata" not in spec.specifications
    assert spec.raw_response, "raw_response must keep the full API responses (Req 2.6)"
    for response in spec.raw_response.values():
        assert "ResponseMetadata" in response
    return spec, collector


def test_integration_collector_instance_spec_req_2_3(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:instance/{ids.instance_id}"
    spec, _ = _collect(session, "ec2", "aws_instance", ids.instance_id, arn)
    specs = spec.specifications
    assert specs["InstanceId"] == ids.instance_id
    assert specs["SecurityGroups"][0]["GroupId"] == ids.security_group_id
    assert "NetworkInterfaces" in specs and "BlockDeviceMappings" in specs
    assert {"Key": "Name", "Value": "orders-web-1"} in specs["Tags"]
    assert isinstance(specs["LaunchTime"], str), "datetimes must be ISO strings"


def test_integration_collector_vpc_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:vpc/{ids.vpc_id}"
    spec, _ = _collect(session, "ec2", "aws_vpc", ids.vpc_id, arn)
    assert spec.specifications["VpcId"] == ids.vpc_id
    assert spec.specifications["CidrBlock"] == "10.0.0.0/16"
    assert spec.specifications["EnableDnsSupport"] is True
    assert isinstance(spec.specifications["EnableDnsHostnames"], bool)
    assert set(spec.raw_response) == {
        "DescribeVpcs",
        "DescribeVpcAttribute:enableDnsSupport",
        "DescribeVpcAttribute:enableDnsHostnames",
    }


def test_integration_collector_security_group_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:security-group/{ids.security_group_id}"
    spec, _ = _collect(session, "ec2", "aws_security_group", ids.security_group_id, arn)
    perms = spec.specifications["IpPermissions"]
    assert any(r["CidrIp"] == "0.0.0.0/0" for p in perms for r in p.get("IpRanges", []))
    assert spec.specifications["VpcId"] == ids.vpc_id


def test_integration_collector_lambda_spec_with_tags_req_2_4(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:lambda:{REGION}:{ACCOUNT}:function:{ids.function_name}"
    spec, _ = _collect(session, "lambda", "aws_lambda_function", ids.function_name, arn)
    specs = spec.specifications
    assert specs["FunctionName"] == ids.function_name
    assert specs["Role"] == ids.lambda_role_arn
    assert specs["Environment"]["Variables"]["TABLE_NAME"] == "orders"
    assert specs["Tags"] == {"team": "orders"}


def test_integration_collector_db_instance_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:rds:{REGION}:{ACCOUNT}:db:{ids.db_instance_id}"
    spec, _ = _collect(session, "rds", "aws_db_instance", ids.db_instance_id, arn)
    specs = spec.specifications
    assert specs["DBInstanceIdentifier"] == ids.db_instance_id
    assert specs["Engine"] == "postgres"
    assert specs["VpcSecurityGroups"][0]["VpcSecurityGroupId"] == ids.security_group_id


def test_integration_collector_log_group_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:logs:{REGION}:{ACCOUNT}:log-group:{ids.log_group_name}"
    spec, _ = _collect(session, "logs", "aws_cloudwatch_log_group", ids.log_group_name, arn)
    assert spec.specifications["logGroupName"] == ids.log_group_name
    assert spec.specifications["retentionInDays"] == 14
    assert spec.specifications["tags"] == {"team": "orders"}


def test_integration_collector_state_machine_spec_req_2_1(sample_account):
    session, ids = sample_account
    spec, _ = _collect(
        session, "stepfunctions", "aws_sfn_state_machine", "order-flow", ids.state_machine_arn
    )
    assert spec.specifications["name"] == "order-flow"
    assert spec.specifications["roleArn"] == ids.lambda_role_arn
    assert '"StartAt"' in spec.specifications["definition"]
    assert spec.specifications["tags"] == [{"key": "team", "value": "orders"}]


def test_integration_collector_dynamodb_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:dynamodb:{REGION}:{ACCOUNT}:table/{ids.table_name}"
    spec, _ = _collect(session, "dynamodb", "aws_dynamodb_table", ids.table_name, arn)
    specs = spec.specifications
    assert specs["TableName"] == ids.table_name
    assert specs["KeySchema"] == [{"AttributeName": "order_id", "KeyType": "HASH"}]
    assert specs["Tags"] == [{"Key": "team", "Value": "orders"}]


def test_integration_collector_s3_spec_req_2_2(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:s3:::{ids.bucket_name}"
    spec, collector = _collect(
        session, "s3", "aws_s3_bucket", ids.bucket_name, arn, region="global"
    )
    specs = spec.specifications
    assert specs["Name"] == ids.bucket_name
    assert specs["bucket-versioning"]["Status"] == "Enabled"
    assert any(
        g["Grantee"].get("URI", "").endswith("AllUsers") for g in specs["bucket-acl"]["Grants"]
    )
    # Not configured in the sample account → omitted and not counted as failures (Req 2.2)
    for absent in (
        "bucket-cors",
        "bucket-website",
        "bucket-policy",
        "bucket-lifecycle-configuration",
    ):
        assert absent not in specs
    assert not collector.get_errors()


def test_integration_collector_iam_role_spec_req_2_1(sample_account):
    session, ids = sample_account
    spec, _ = _collect(
        session, "iam", "aws_iam_role", "order-lambda-role", ids.lambda_role_arn, region="global"
    )
    specs = spec.specifications
    assert specs["RoleName"] == "order-lambda-role"
    assert specs["AssumeRolePolicyDocument"]["Statement"][0]["Principal"] == {
        "Service": "lambda.amazonaws.com"
    }
    assert specs["AttachedPolicies"] == []
    assert specs["InlinePolicies"]["too-broad"]["Statement"][0]["Action"] == "*"
