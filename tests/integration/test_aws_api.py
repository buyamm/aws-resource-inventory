"""
Integration tests for AWS API interactions via SpecCollector.

This module tests the SpecCollector against mocked AWS services using moto,
verifying that real boto3 clients work end-to-end with the collector logic.

Test Coverage:
- test_integration_collector_s3_all_specs_req_2_2:
    SpecCollector collects all 8 S3 bucket specification types from a real
    (moto-mocked) S3 bucket.

Requirements Coverage:
- Requirement 2.2: Spec_Collector SHALL retrieve all 8 S3 bucket spec types
"""

import json
import os
import pytest
import boto3
from moto import mock_s3

from src.collector import SpecCollector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_aws_env():
    """Set dummy AWS credentials so boto3 / moto don't complain."""
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
    os.environ.setdefault("AWS_SECURITY_TOKEN", "testing")
    os.environ.setdefault("AWS_SESSION_TOKEN", "testing")
    os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")


# ---------------------------------------------------------------------------
# Integration Test: S3 Spec Collection
# ---------------------------------------------------------------------------


@mock_s3
def test_integration_collector_s3_all_specs_req_2_2():
    """
    Integration: SpecCollector collects all 8 S3 bucket specification types.

    Scenario:
    - A real boto3 S3 client is created inside moto's mock environment.
    - A bucket is created and all 8 sub-spec types are configured on it.
    - A SpecCollector using that same boto3 client collects the bucket.

    Expected behaviour:
    - collect_s3_specs() returns an Ok result.
    - All 8 spec types are present in result.value.specifications:
        bucket-acl, bucket-cors, bucket-encryption,
        bucket-lifecycle-configuration, bucket-policy,
        bucket-tagging, bucket-versioning, bucket-website

    **Validates: Requirement 2.2**
    """
    _setup_aws_env()

    bucket_name = "integration-test-bucket"
    region = "us-east-1"

    # --- Create the mock S3 bucket ---
    s3 = boto3.client("s3", region_name=region)
    s3.create_bucket(Bucket=bucket_name)

    # bucket-cors
    s3.put_bucket_cors(
        Bucket=bucket_name,
        CORSConfiguration={
            "CORSRules": [
                {
                    "AllowedHeaders": ["*"],
                    "AllowedMethods": ["GET", "PUT"],
                    "AllowedOrigins": ["https://example.com"],
                    "MaxAgeSeconds": 3000,
                }
            ]
        },
    )

    # bucket-encryption
    s3.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    },
                    "BucketKeyEnabled": False,
                }
            ]
        },
    )

    # bucket-lifecycle-configuration
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={
            "Rules": [
                {
                    "ID": "expire-old-objects",
                    "Status": "Enabled",
                    "Filter": {"Prefix": "logs/"},
                    "Expiration": {"Days": 90},
                }
            ]
        },
    )

    # bucket-policy
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "arn:aws:iam::123456789012:root"},
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    }
                ],
            }
        ),
    )

    # bucket-tagging
    s3.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={
            "TagSet": [
                {"Key": "Environment", "Value": "integration-test"},
                {"Key": "Owner", "Value": "team-infra"},
            ]
        },
    )

    # bucket-versioning
    s3.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={"Status": "Enabled"},
    )

    # bucket-website
    s3.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            "IndexDocument": {"Suffix": "index.html"},
            "ErrorDocument": {"Key": "error.html"},
        },
    )

    # --- Run the collector with the same boto3 client ---
    collector = SpecCollector(api_client=s3)
    result = collector.collect_s3_specs(bucket_name)

    # --- Assertions ---
    assert result.is_ok(), (
        f"collect_s3_specs() should return Ok, got error: "
        f"{result.error if result.is_err() else 'ok'}"
    )

    specifications = result.value.specifications

    expected_spec_types = [
        "bucket-acl",
        "bucket-cors",
        "bucket-encryption",
        "bucket-lifecycle-configuration",
        "bucket-policy",
        "bucket-tagging",
        "bucket-versioning",
        "bucket-website",
    ]

    missing = [s for s in expected_spec_types if s not in specifications]
    assert not missing, (
        f"The following spec types were not collected: {missing}. "
        f"Collected specs: {list(specifications.keys())}"
    )

    # Spot-check a few values to confirm real data was collected
    assert "CORSRules" in specifications["bucket-cors"], (
        "bucket-cors should contain CORSRules"
    )
    assert specifications["bucket-versioning"].get("Status") == "Enabled", (
        "bucket-versioning should show Status=Enabled"
    )
    assert "ServerSideEncryptionConfiguration" in specifications["bucket-encryption"], (
        "bucket-encryption should contain ServerSideEncryptionConfiguration"
    )
    assert "TagSet" in specifications["bucket-tagging"], (
        "bucket-tagging should contain TagSet"
    )
    assert "Rules" in specifications["bucket-lifecycle-configuration"], (
        "bucket-lifecycle-configuration should contain Rules"
    )


# ---------------------------------------------------------------------------
# Integration Test: EC2 Spec Collection
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=False)
def aws_credentials_env():
    """Ensure dummy AWS credentials are set for all moto tests."""
    _setup_aws_env()


from moto import mock_ec2, mock_lambda, mock_iam  # noqa: E402 – imported here to keep grouping clear
import io
import zipfile


@mock_ec2
def test_integration_collector_ec2_all_specs_req_2_3():
    """
    Integration: SpecCollector collects EC2 instance specifications.

    Scenario:
    - A real boto3 EC2 client is created inside moto's mock environment.
    - An EC2 instance is launched (moto intercepts the API calls).
    - A SpecCollector using that same boto3 client collects the instance.

    Expected behaviour:
    - collect_ec2_spec() returns an Ok result.
    - result.value.raw_response preserves the original API response from
      describe_instances(), satisfying the raw-response preservation requirement.
    - The spec contains the instance_id used for collection.

    **Validates: Requirement 2.3**
    """
    _setup_aws_env()

    region = "us-east-1"
    ec2 = boto3.client("ec2", region_name=region)

    # Launch a minimal EC2 instance (moto intercepts this).
    # Use an AMI ID that moto knows about (from ec2.describe_images(Owners=["amazon"])).
    response = ec2.run_instances(
        ImageId="ami-12c6146b",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "integration-test-instance"},
                    {"Key": "Environment", "Value": "test"},
                ],
            }
        ],
    )
    instance_id = response["Instances"][0]["InstanceId"]

    # --- Run the collector with the same boto3 EC2 client ---
    collector = SpecCollector(api_client=ec2)
    result = collector.collect_ec2_spec(instance_id)

    # --- Assertions ---
    assert result.is_ok(), (
        f"collect_ec2_spec() should return Ok, got error: "
        f"{result.error if result.is_err() else 'ok'}"
    )

    spec = result.value

    # The raw_response must preserve the original describe_instances response
    assert spec.raw_response is not None, (
        "raw_response must not be None – Requirement 2.6 requires raw preservation"
    )

    # The raw response should be the describe_instances dict with Reservations key
    assert "Reservations" in spec.raw_response, (
        "raw_response should contain the Reservations key from describe_instances()"
    )

    # Spot-check: the returned instance ID is present in the raw response
    reservations = spec.raw_response["Reservations"]
    all_instance_ids = [
        inst["InstanceId"]
        for reservation in reservations
        for inst in reservation["Instances"]
    ]
    assert instance_id in all_instance_ids, (
        f"Instance {instance_id} not found in raw_response. "
        f"Found: {all_instance_ids}"
    )

    # The spec should record the correct resource type
    assert spec.resource_type == "aws_instance", (
        f"Expected resource_type='aws_instance', got '{spec.resource_type}'"
    )


# ---------------------------------------------------------------------------
# Integration Test: Lambda Spec Collection
# ---------------------------------------------------------------------------


def _make_lambda_zip() -> bytes:
    """Create a minimal in-memory ZIP archive containing a stub handler."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "handler.py",
            "def handler(event, context):\n    return {'statusCode': 200}\n",
        )
    return buf.getvalue()


@mock_iam
@mock_lambda
def test_integration_collector_lambda_all_specs_req_2_4():
    """
    Integration: SpecCollector collects Lambda function specifications.

    Scenario:
    - Real boto3 IAM and Lambda clients are created inside moto's mock environment.
    - An IAM execution role is created first (moto requires a real assumable role).
    - A Lambda function is created with a minimal ZIP archive (moto intercepts).
    - A SpecCollector using that same boto3 Lambda client collects the function.

    Expected behaviour:
    - collect_lambda_spec() returns an Ok result.
    - The resulting spec contains function configuration, including FunctionName,
      FunctionArn, Runtime, Role, and Handler – satisfying Requirement 2.4.
    - The spec's raw_response preserves the original get_function() response.

    **Validates: Requirement 2.4**
    """
    _setup_aws_env()

    region = "us-east-1"
    function_name = "integration-test-function"

    # Create an IAM role that Lambda can assume (moto requires this)
    iam = boto3.client("iam", region_name=region)
    role = iam.create_role(
        RoleName="lambda-execution-role",
        AssumeRolePolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }),
    )
    execution_role_arn = role["Role"]["Arn"]

    lambda_client = boto3.client("lambda", region_name=region)

    # Create a Lambda function (moto intercepts this)
    lambda_client.create_function(
        FunctionName=function_name,
        Runtime="python3.11",
        Role=execution_role_arn,
        Handler="handler.handler",
        Code={"ZipFile": _make_lambda_zip()},
        Description="Integration test Lambda function",
        Timeout=30,
        MemorySize=128,
        Environment={
            "Variables": {
                "APP_ENV": "test",
                "LOG_LEVEL": "INFO",
            }
        },
        Tags={
            "Environment": "integration-test",
            "Owner": "team-infra",
        },
    )

    # --- Run the collector with the same boto3 Lambda client ---
    collector = SpecCollector(api_client=lambda_client)
    result = collector.collect_lambda_spec(function_name)

    # --- Assertions ---
    assert result.is_ok(), (
        f"collect_lambda_spec() should return Ok, got error: "
        f"{result.error if result.is_err() else 'ok'}"
    )

    spec = result.value

    # The raw_response must preserve the original get_function() response
    assert spec.raw_response is not None, (
        "raw_response must not be None – Requirement 2.6 requires raw preservation"
    )

    # get_function() returns a dict with a 'Configuration' key
    assert "Configuration" in spec.raw_response, (
        "raw_response should contain the 'Configuration' key from get_function()"
    )

    # The spec's specifications should be the function Configuration dict
    config = spec.specifications
    assert config.get("FunctionName") == function_name, (
        f"Expected FunctionName='{function_name}', got '{config.get('FunctionName')}'"
    )
    assert "FunctionArn" in config, "spec.specifications must include FunctionArn"
    assert config.get("Runtime") == "python3.11", (
        f"Expected Runtime='python3.11', got '{config.get('Runtime')}'"
    )
    assert config.get("Role") == execution_role_arn, (
        f"Expected Role='{execution_role_arn}', got '{config.get('Role')}'"
    )
    assert config.get("Handler") == "handler.handler", (
        f"Expected Handler='handler.handler', got '{config.get('Handler')}'"
    )

    # Environment variables should be present (Requirement 2.4)
    env_vars = config.get("Environment", {}).get("Variables", {})
    assert env_vars.get("APP_ENV") == "test", (
        f"Expected environment variable APP_ENV='test', got '{env_vars.get('APP_ENV')}'"
    )

    # The spec should record the correct resource type
    assert spec.resource_type == "aws_lambda_function", (
        f"Expected resource_type='aws_lambda_function', got '{spec.resource_type}'"
    )
