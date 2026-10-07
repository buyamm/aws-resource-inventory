"""
Test to verify fixture infrastructure is working correctly.

This test file validates that all fixtures defined in conftest.py
are accessible and working as expected.
"""

import pytest
import json
from pathlib import Path


class TestFixtureInfrastructure:
    """Test fixture setup and configuration."""

    def test_fixtures_directory_exists(self, fixtures_dir):
        """Verify fixtures directory is accessible."""
        assert fixtures_dir.exists()
        assert fixtures_dir.is_dir()

    def test_sample_aws_responses_directory(self, sample_aws_responses_dir):
        """Verify sample AWS responses directory exists."""
        assert sample_aws_responses_dir.exists()
        assert sample_aws_responses_dir.is_dir()

    def test_sample_specs_directory(self, sample_specs_dir):
        """Verify sample specs directory exists."""
        assert sample_specs_dir.exists()
        assert sample_specs_dir.is_dir()

    def test_load_fixture_json_helper(self, load_fixture_json, sample_specs_dir):
        """Test JSON fixture loading helper."""
        spec_file = sample_specs_dir / "s3_bucket_spec.json"
        data = load_fixture_json(spec_file)
        
        assert isinstance(data, dict)
        assert "resource_type" in data
        assert data["resource_type"] == "aws_s3_bucket"

    def test_sample_s3_bucket_response_fixture(self, sample_s3_bucket_response):
        """Test S3 bucket response fixture."""
        assert "Name" in sample_s3_bucket_response
        assert sample_s3_bucket_response["Name"] == "test-bucket"

    def test_sample_ec2_instance_response_fixture(self, sample_ec2_instance_response):
        """Test EC2 instance response fixture."""
        assert "InstanceId" in sample_ec2_instance_response
        assert sample_ec2_instance_response["InstanceType"] == "t2.micro"

    def test_sample_lambda_function_response_fixture(self, sample_lambda_function_response):
        """Test Lambda function response fixture."""
        assert "FunctionName" in sample_lambda_function_response
        assert sample_lambda_function_response["Runtime"] == "python3.9"

    def test_sample_resource_spec_fixture(self, sample_resource_spec):
        """Test ResourceSpec fixture structure."""
        assert "resource_type" in sample_resource_spec
        assert "arn" in sample_resource_spec
        assert "region" in sample_resource_spec
        assert "specifications" in sample_resource_spec
        assert "metadata" in sample_resource_spec

    def test_mock_s3_client_fixture(self, mock_s3_client):
        """Test mocked S3 client is functional."""
        # Create a test bucket
        mock_s3_client.create_bucket(Bucket="test-fixture-bucket")
        
        # List buckets
        response = mock_s3_client.list_buckets()
        
        assert "Buckets" in response
        assert len(response["Buckets"]) == 1
        assert response["Buckets"][0]["Name"] == "test-fixture-bucket"

    def test_mock_ec2_client_fixture(self, mock_ec2_client):
        """Test mocked EC2 client is functional."""
        # Describe instances (should be empty initially)
        response = mock_ec2_client.describe_instances()
        
        assert "Reservations" in response
        assert isinstance(response["Reservations"], list)

    def test_mock_lambda_client_fixture(self, mock_lambda_client):
        """Test mocked Lambda client is functional."""
        # List functions (should be empty initially)
        response = mock_lambda_client.list_functions()
        
        assert "Functions" in response
        assert isinstance(response["Functions"], list)

    def test_aws_response_fixtures_are_valid_json(self, sample_aws_responses_dir):
        """Verify all AWS response fixtures are valid JSON."""
        json_files = [
            "s3_responses.json",
            "ec2_responses.json",
            "lambda_responses.json",
        ]
        
        for filename in json_files:
            filepath = sample_aws_responses_dir / filename
            assert filepath.exists(), f"Missing fixture: {filename}"
            
            with open(filepath, "r") as f:
                data = json.load(f)
                assert isinstance(data, dict), f"{filename} should contain a dict"

    def test_spec_fixtures_are_valid_json(self, sample_specs_dir):
        """Verify all spec fixtures are valid JSON."""
        json_files = [
            "s3_bucket_spec.json",
            "ec2_instance_spec.json",
            "lambda_function_spec.json",
        ]
        
        for filename in json_files:
            filepath = sample_specs_dir / filename
            assert filepath.exists(), f"Missing spec fixture: {filename}"
            
            with open(filepath, "r") as f:
                data = json.load(f)
                assert isinstance(data, dict), f"{filename} should contain a dict"
                assert "resource_type" in data
                assert "arn" in data
                assert "specifications" in data
