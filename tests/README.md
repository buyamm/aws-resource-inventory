# Test Infrastructure Documentation

This document describes the test infrastructure setup for the AWS Resource Inventory project, following Test-Driven Development (TDD) principles.

## Overview

The test infrastructure supports:
- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete workflows
- **Property-Based Tests**: Use Hypothesis to verify universal properties

## Directory Structure

```
tests/
├── conftest.py              # Shared pytest fixtures and configuration
├── pytest.ini               # Pytest configuration (in project root)
├── test_fixtures.py         # Tests to verify fixture infrastructure
├── README.md                # This file
├── fixtures/                # Test data fixtures
│   ├── README.md           # Fixture documentation
│   ├── sample_aws_responses/  # Mock AWS API responses
│   │   ├── s3_responses.json
│   │   ├── ec2_responses.json
│   │   └── lambda_responses.json
│   └── sample_specs/       # Sample ResourceSpec structures
│       ├── s3_bucket_spec.json
│       ├── ec2_instance_spec.json
│       └── lambda_function_spec.json
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── e2e/                     # End-to-end tests
└── logs/                    # Test execution logs
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# End-to-end tests only
pytest -m e2e

# Property-based tests only
pytest -m property
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Open HTML report
open htmlcov/index.html
```

### Run Specific Test File
```bash
pytest tests/unit/test_parser.py -v
```

### Run Tests Matching Pattern
```bash
pytest -k "test_parser" -v
```

## Available Fixtures

### Path Fixtures
- `fixtures_dir`: Path to the fixtures directory
- `sample_aws_responses_dir`: Path to AWS response fixtures
- `sample_specs_dir`: Path to spec fixtures

### AWS Mock Fixtures
- `aws_credentials`: Sets up mock AWS credentials in environment
- `mock_s3_client`: Mocked boto3 S3 client using moto
- `mock_ec2_client`: Mocked boto3 EC2 client
- `mock_lambda_client`: Mocked boto3 Lambda client
- `mock_iam_client`: Mocked boto3 IAM client
- `mock_dynamodb_client`: Mocked boto3 DynamoDB client

### Sample Data Fixtures
- `sample_s3_bucket_response`: Sample S3 bucket API response
- `sample_s3_bucket_acl_response`: Sample S3 ACL response
- `sample_ec2_instance_response`: Sample EC2 instance response
- `sample_lambda_function_response`: Sample Lambda function response
- `sample_resource_spec`: Sample ResourceSpec structure
- `sample_ec2_resource_spec`: Sample EC2 ResourceSpec
- `sample_lambda_resource_spec`: Sample Lambda ResourceSpec
- `sample_collection_report`: Sample collection report structure

### Helper Fixtures
- `load_fixture_json`: Function to load JSON fixtures from files
- `load_fixture_text`: Function to load text fixtures from files

## Using Fixtures in Tests

### Example: Basic Fixture Usage
```python
def test_s3_parser(sample_s3_bucket_response):
    """Test S3 bucket response parsing."""
    parser = ResourceParser()
    result = parser.parse_s3_bucket(sample_s3_bucket_response)
    
    assert result.is_ok()
    assert result.value.resource_type == "aws_s3_bucket"
```

### Example: Mock AWS Client
```python
def test_s3_collector(mock_s3_client):
    """Test S3 spec collection with mocked client."""
    # Create test bucket
    mock_s3_client.create_bucket(Bucket="test-bucket")
    
    # Test collection
    collector = SpecCollector(s3_client=mock_s3_client)
    specs = collector.collect_s3_specs("test-bucket")
    
    assert len(specs) > 0
```

### Example: Loading JSON Fixtures
```python
def test_with_fixture_file(load_fixture_json, sample_aws_responses_dir):
    """Test using fixture file data."""
    data = load_fixture_json(sample_aws_responses_dir / "s3_responses.json")
    bucket_acl = data["get_bucket_acl"]
    
    # Use the fixture data
    assert "Owner" in bucket_acl
```

### Example: Property-Based Test
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_property_parser_handles_all_strings(input_text):
    """Property: Parser handles any non-empty string gracefully."""
    parser = ResourceParser()
    result = parser.parse_spec(input_text)
    
    # Should either succeed or return a descriptive error
    assert result.is_ok() or result.error_message() != ""
```

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_parser_unit():
    """Unit test example."""
    pass

@pytest.mark.integration
def test_collector_integration():
    """Integration test example."""
    pass

@pytest.mark.e2e
def test_full_workflow():
    """End-to-end test example."""
    pass

@pytest.mark.property
@given(st.integers())
def test_property_example(n):
    """Property-based test example."""
    pass

@pytest.mark.slow
def test_long_running_operation():
    """Slow test example."""
    pass
```

## TDD Workflow

### Red-Green-Refactor Cycle

1. **RED**: Write a failing test
```python
def test_parser_malformed_json_returns_descriptive_error():
    """Test that parser handles malformed JSON gracefully."""
    malformed = '{"key": invalid}'
    parser = ResourceParser()
    result = parser.parse_spec(malformed)
    
    # This will fail because parse_spec doesn't exist yet
    assert result.is_err()
    assert "invalid" in result.error_message()
```

2. **GREEN**: Write minimal code to pass
```python
class ResourceParser:
    def parse_spec(self, json_data: str) -> Result:
        try:
            data = json.loads(json_data)
            return Ok(data)
        except json.JSONDecodeError as e:
            return Err(f"JSON parse error: {str(e)}")
```

3. **REFACTOR**: Improve code quality
```python
class ResourceParser:
    def parse_spec(self, json_data: str) -> Result[ResourceSpec, ParseError]:
        """Parse JSON into ResourceSpec with detailed error handling."""
        try:
            data = json.loads(json_data)
            return Ok(self._build_resource_spec(data))
        except json.JSONDecodeError as e:
            excerpt = self._get_error_excerpt(json_data, e.pos)
            return Err(ParseError(
                message=f"Invalid JSON: {str(e)}",
                excerpt=excerpt,
                position=e.pos
            ))
```

## Coverage Requirements

- **Minimum**: 80% code coverage across all components
- **Critical paths**: 100% coverage for:
  - Parsing logic
  - Credential handling
  - Data sanitization
  - Security-sensitive code

Check coverage with:
```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

## Property-Based Testing Guidelines

### Minimum Iterations
- Run at least 100 iterations per property test
- Configure in test or pytest.ini

### Example Configuration
```python
from hypothesis import settings

@settings(max_examples=100)
@given(st.from_type(ResourceSpec))
def test_property_parse_print_roundtrip(spec):
    """Property: parse(print(spec)) == spec"""
    json_output = print_spec(spec)
    parsed = parse_spec(json_output)
    assert parsed == spec
```

## Adding New Tests

### For New AWS Services

1. **Create AWS Response Fixtures**
```bash
# Add to tests/fixtures/sample_aws_responses/
touch tests/fixtures/sample_aws_responses/rds_responses.json
```

2. **Create Spec Fixtures**
```bash
# Add to tests/fixtures/sample_specs/
touch tests/fixtures/sample_specs/rds_instance_spec.json
```

3. **Add Fixtures to conftest.py**
```python
@pytest.fixture
def sample_rds_instance_response() -> Dict[str, Any]:
    """Sample RDS instance response."""
    return {
        "DBInstanceIdentifier": "test-db",
        "DBInstanceClass": "db.t3.micro",
        # ... more fields
    }
```

4. **Write Tests (TDD)**
```python
def test_rds_parser(sample_rds_instance_response):
    """Test RDS instance parsing - WRITE THIS FIRST."""
    parser = ResourceParser()
    result = parser.parse_rds_instance(sample_rds_instance_response)
    
    assert result.is_ok()
    # More assertions...
```

## Continuous Integration

Tests run automatically in CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Unit Tests
  run: pytest tests/unit/ -v --cov=src --cov-fail-under=80

- name: Run Property Tests
  run: pytest -m property --hypothesis-show-statistics

- name: Run Integration Tests
  run: pytest tests/integration/ -v

- name: Run E2E Tests
  run: pytest tests/e2e/ -v
```

## Troubleshooting

### Tests Not Discovered
```bash
# Check test discovery
pytest --collect-only

# Verify pytest configuration
pytest --version
cat pytest.ini
```

### Fixture Not Found
```bash
# List available fixtures
pytest --fixtures

# Check if conftest.py is being loaded
pytest --setup-show tests/test_file.py
```

### Moto AWS Mocking Issues
```bash
# Ensure moto is installed with all services
pip install "moto[all]"

# Check moto version
pip show moto
```

### Coverage Issues
```bash
# Generate detailed coverage report
pytest --cov=src --cov-report=html

# View uncovered lines
coverage report --show-missing
```

## Best Practices

1. **Test First**: Always write tests before implementation code
2. **One Assertion Focus**: Each test should verify one specific behavior
3. **Descriptive Names**: Test names should describe what is being tested
4. **Arrange-Act-Assert**: Structure tests clearly with AAA pattern
5. **Independent Tests**: Tests should not depend on each other
6. **Fast Tests**: Keep unit tests fast (<100ms each)
7. **Property Tests**: Use Hypothesis for universal properties
8. **Mock External Calls**: Always mock AWS API calls in unit tests
9. **Use Fixtures**: Leverage shared fixtures to reduce duplication
10. **Document Complex Tests**: Add docstrings explaining test purpose

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Moto Documentation](http://docs.getmoto.org/)
- [TDD Best Practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
