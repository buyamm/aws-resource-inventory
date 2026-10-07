"""
Shared test fixtures and configuration for pytest.

This module provides reusable fixtures for AWS mocking, sample data,
and test configuration used across unit, integration, and E2E tests.
"""

import os

# Clean up AWS_PROFILE and set test AWS credentials before moto/boto3 initialization
os.environ.pop("AWS_PROFILE", None)
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SECURITY_TOKEN", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

import json
import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock
import boto3
from moto import mock_s3, mock_ec2, mock_lambda, mock_iam, mock_dynamodb


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_aws_responses_dir(fixtures_dir) -> Path:
    """Return path to sample AWS response fixtures."""
    return fixtures_dir / "sample_aws_responses"


@pytest.fixture
def sample_specs_dir(fixtures_dir) -> Path:
    """Return path to sample spec fixtures."""
    return fixtures_dir / "sample_specs"


# ============================================================================
# AWS Mock Fixtures
# ============================================================================

@pytest.fixture
def aws_credentials():
    """Provide mock AWS credentials for testing."""
    import os
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def mock_s3_client(aws_credentials):
    """Provide a mocked S3 client."""
    with mock_s3():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture
def mock_ec2_client(aws_credentials):
    """Provide a mocked EC2 client."""
    with mock_ec2():
        yield boto3.client("ec2", region_name="us-east-1")


@pytest.fixture
def mock_lambda_client(aws_credentials):
    """Provide a mocked Lambda client."""
    with mock_lambda():
        yield boto3.client("lambda", region_name="us-east-1")


@pytest.fixture
def mock_iam_client(aws_credentials):
    """Provide a mocked IAM client."""
    with mock_iam():
        yield boto3.client("iam", region_name="us-east-1")


@pytest.fixture
def mock_dynamodb_client(aws_credentials):
    """Provide a mocked DynamoDB client."""
    with mock_dynamodb():
        yield boto3.client("dynamodb", region_name="us-east-1")


# ============================================================================
# Sample Resource Fixtures
# ============================================================================

@pytest.fixture
def sample_s3_bucket_response() -> Dict[str, Any]:
    """Sample S3 bucket response from AWS API."""
    return {
        "Name": "test-bucket",
        "CreationDate": datetime(2023, 1, 1, 0, 0, 0),
    }


@pytest.fixture
def sample_s3_bucket_acl_response() -> Dict[str, Any]:
    """Sample S3 bucket ACL response."""
    return {
        "Owner": {
            "DisplayName": "owner",
            "ID": "owner-id-123",
        },
        "Grants": [
            {
                "Grantee": {
                    "Type": "CanonicalUser",
                    "DisplayName": "owner",
                    "ID": "owner-id-123",
                },
                "Permission": "FULL_CONTROL",
            }
        ],
    }


@pytest.fixture
def sample_ec2_instance_response() -> Dict[str, Any]:
    """Sample EC2 instance response from AWS API."""
    return {
        "InstanceId": "i-1234567890abcdef0",
        "InstanceType": "t2.micro",
        "State": {"Code": 16, "Name": "running"},
        "ImageId": "ami-12345678",
        "LaunchTime": datetime(2023, 1, 1, 0, 0, 0),
        "Placement": {
            "AvailabilityZone": "us-east-1a",
        },
        "VpcId": "vpc-12345678",
        "SubnetId": "subnet-12345678",
        "PrivateIpAddress": "10.0.1.100",
        "SecurityGroups": [
            {"GroupId": "sg-12345678", "GroupName": "default"}
        ],
        "Tags": [
            {"Key": "Name", "Value": "test-instance"},
            {"Key": "Environment", "Value": "test"},
        ],
    }


@pytest.fixture
def sample_lambda_function_response() -> Dict[str, Any]:
    """Sample Lambda function response from AWS API."""
    return {
        "FunctionName": "test-function",
        "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:test-function",
        "Runtime": "python3.9",
        "Role": "arn:aws:iam::123456789012:role/test-role",
        "Handler": "index.handler",
        "CodeSize": 1024,
        "Description": "Test function",
        "Timeout": 30,
        "MemorySize": 128,
        "LastModified": "2023-01-01T00:00:00.000+0000",
        "Environment": {
            "Variables": {
                "ENV": "test",
                "LOG_LEVEL": "INFO",
            }
        },
        "VpcConfig": {},
        "Layers": [],
        "State": "Active",
        "PackageType": "Zip",
    }


# ============================================================================
# ResourceSpec Fixtures
# ============================================================================

@pytest.fixture
def sample_resource_spec() -> Dict[str, Any]:
    """Sample ResourceSpec structure."""
    return {
        "resource_type": "aws_s3_bucket",
        "arn": "arn:aws:s3:::test-bucket",
        "region": "us-east-1",
        "account_id": "123456789012",
        "specifications": {
            "bucket-acl": {
                "Owner": {"DisplayName": "owner", "ID": "owner-id-123"},
                "Grants": [
                    {
                        "Grantee": {
                            "Type": "CanonicalUser",
                            "DisplayName": "owner",
                            "ID": "owner-id-123",
                        },
                        "Permission": "FULL_CONTROL",
                    }
                ],
            },
            "bucket-versioning": {"Status": "Enabled"},
            "bucket-encryption": {
                "ServerSideEncryptionConfiguration": {
                    "Rules": [
                        {
                            "ApplyServerSideEncryptionByDefault": {
                                "SSEAlgorithm": "AES256"
                            }
                        }
                    ]
                }
            },
        },
        "metadata": {
            "collected_at": "2023-01-01T00:00:00Z",
            "collector_version": "1.0.0",
            "api_version": "2023-01-01",
            "checksum": "abc123def456",
        },
        "raw_response": None,
    }


@pytest.fixture
def sample_ec2_resource_spec() -> Dict[str, Any]:
    """Sample EC2 ResourceSpec structure."""
    return {
        "resource_type": "aws_ec2_instance",
        "arn": "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0",
        "region": "us-east-1",
        "account_id": "123456789012",
        "specifications": {
            "instance_type": "t2.micro",
            "state": "running",
            "vpc_id": "vpc-12345678",
            "subnet_id": "subnet-12345678",
            "security_groups": ["sg-12345678"],
            "tags": {"Name": "test-instance", "Environment": "test"},
        },
        "metadata": {
            "collected_at": "2023-01-01T00:00:00Z",
            "collector_version": "1.0.0",
            "api_version": "2023-01-01",
            "checksum": "xyz789abc123",
        },
        "raw_response": None,
    }


@pytest.fixture
def sample_lambda_resource_spec() -> Dict[str, Any]:
    """Sample Lambda ResourceSpec structure."""
    return {
        "resource_type": "aws_lambda_function",
        "arn": "arn:aws:lambda:us-east-1:123456789012:function:test-function",
        "region": "us-east-1",
        "account_id": "123456789012",
        "specifications": {
            "runtime": "python3.9",
            "handler": "index.handler",
            "timeout": 30,
            "memory_size": 128,
            "environment": {"ENV": "test", "LOG_LEVEL": "INFO"},
            "role": "arn:aws:iam::123456789012:role/test-role",
        },
        "metadata": {
            "collected_at": "2023-01-01T00:00:00Z",
            "collector_version": "1.0.0",
            "api_version": "2023-01-01",
            "checksum": "def456ghi789",
        },
        "raw_response": None,
    }


# ============================================================================
# Collection Report Fixtures
# ============================================================================

@pytest.fixture
def sample_collection_report() -> Dict[str, Any]:
    """Sample collection report."""
    return {
        "start_time": "2023-01-01T00:00:00Z",
        "end_time": "2023-01-01T00:05:00Z",
        "total_resources": 10,
        "successful_collections": 8,
        "failed_collections": 2,
        "errors": [
            {
                "resource_arn": "arn:aws:s3:::private-bucket",
                "operation": "get-bucket-policy",
                "error_type": "AccessDenied",
                "error_message": "Missing s3:GetBucketPolicy permission",
                "timestamp": "2023-01-01T00:02:00Z",
                "retry_count": 3,
            }
        ],
        "regions_scanned": ["us-east-1", "us-west-2"],
        "time_saved_hours": 0.75,
    }


# ============================================================================
# File Loading Helpers
# ============================================================================

@pytest.fixture
def load_fixture_json():
    """Factory fixture to load JSON fixture files."""
    def _load(fixture_path: Path) -> Dict[str, Any]:
        """Load a JSON fixture file."""
        with open(fixture_path, "r") as f:
            return json.load(f)
    return _load


@pytest.fixture
def load_fixture_text():
    """Factory fixture to load text fixture files."""
    def _load(fixture_path: Path) -> str:
        """Load a text fixture file."""
        with open(fixture_path, "r") as f:
            return f.read()
    return _load


# ============================================================================
# Test Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "property: mark test as a property-based test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
