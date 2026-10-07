# Test Fixtures

This directory contains sample data fixtures used across unit, integration, and E2E tests.

## Directory Structure

```
fixtures/
├── sample_aws_responses/    # Mock AWS API response data
│   ├── s3_responses.json    # S3 bucket operations
│   ├── ec2_responses.json   # EC2 instance operations
│   └── lambda_responses.json # Lambda function operations
└── sample_specs/            # Sample ResourceSpec structures
    ├── s3_bucket_spec.json
    ├── ec2_instance_spec.json
    └── lambda_function_spec.json
```

## Sample AWS Responses

Contains JSON files with realistic AWS API responses for various services. These fixtures are used to mock boto3 calls in tests.

### S3 Responses (`s3_responses.json`)
- `list_buckets`: List all S3 buckets
- `get_bucket_acl`: Bucket access control list
- `get_bucket_versioning`: Bucket versioning configuration
- `get_bucket_encryption`: Bucket encryption settings
- `get_bucket_lifecycle_configuration`: Lifecycle rules
- `get_bucket_policy`: Bucket policy JSON
- `get_bucket_tagging`: Bucket tags
- `get_bucket_cors`: CORS configuration
- `get_bucket_website`: Website configuration

### EC2 Responses (`ec2_responses.json`)
- `describe_instances`: EC2 instance details
- `describe_instance_attribute`: Instance-specific attributes
- `describe_security_groups`: Security group configurations

### Lambda Responses (`lambda_responses.json`)
- `list_functions`: List all Lambda functions
- `get_function`: Complete function configuration
- `get_function_configuration`: Function settings only
- `get_policy`: Function resource policy

## Sample Resource Specifications

Contains complete `ResourceSpec` structures showing how collected AWS data is formatted after parsing and transformation.

### S3 Bucket Spec
A fully-populated S3 bucket specification including:
- ACL configuration
- Versioning settings
- Encryption configuration
- Lifecycle rules
- Tags and CORS

### EC2 Instance Spec
A complete EC2 instance specification including:
- Instance type and state
- Network configuration (VPC, subnet, IPs)
- Security groups
- Block device mappings
- Tags and metadata

### Lambda Function Spec
A comprehensive Lambda function specification including:
- Runtime and handler configuration
- Environment variables
- VPC configuration
- Layers
- Tags and execution role

## Usage in Tests

### Loading JSON Fixtures

```python
def test_parser_with_fixture(load_fixture_json, sample_aws_responses_dir):
    # Load S3 response fixture
    s3_data = load_fixture_json(sample_aws_responses_dir / "s3_responses.json")
    bucket_acl = s3_data["get_bucket_acl"]
    
    # Use in test
    parser = ResourceParser()
    result = parser.parse_s3_acl(bucket_acl)
    assert result.is_ok()
```

### Using Pre-defined Fixtures

```python
def test_with_predefined_fixture(sample_s3_bucket_response):
    # sample_s3_bucket_response is automatically available from conftest.py
    assert sample_s3_bucket_response["Name"] == "test-bucket"
```

### Using Mock AWS Clients

```python
def test_with_mock_s3(mock_s3_client):
    # mock_s3_client is a mocked boto3 S3 client
    mock_s3_client.create_bucket(Bucket="test-bucket")
    response = mock_s3_client.list_buckets()
    assert len(response["Buckets"]) == 1
```

## Adding New Fixtures

When adding new AWS service support:

1. **Create AWS response fixture**: Add a new JSON file in `sample_aws_responses/` with common API responses
2. **Create spec fixture**: Add a corresponding ResourceSpec JSON in `sample_specs/`
3. **Add fixture functions**: Update `conftest.py` with any new fixture functions needed
4. **Document here**: Update this README with the new fixture details

## Test Data Principles

- **Realistic**: Fixtures should match actual AWS API response formats
- **Minimal**: Include only necessary data for testing, avoid excessive detail
- **Documented**: Complex or non-obvious test data should be explained
- **Versioned**: Update fixtures when AWS API versions change
- **Safe**: Never include real credentials, secrets, or production data
