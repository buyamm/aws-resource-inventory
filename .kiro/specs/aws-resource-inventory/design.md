# Design Document: AWS Resource Inventory

## Overview

AWS Resource Inventory is a system that automatically discovers, collects, and analyzes AWS infrastructure resources. The system follows **Test-Driven Development (TDD)** methodology, where all tests are written before implementation code. This approach ensures correctness, maintainability, and verifiable behavior across all components.

### Core Design Principles

1. **Test-First Development**: Every feature begins with a failing test
2. **Red-Green-Refactor Cycle**: Rigorous adherence to TDD workflow
3. **Property-Based Testing**: Universal properties verified across generated inputs for parsers and transformations
4. **Integration Testing**: API contracts and MCP server behavior validated before implementation
5. **Verifiable Accuracy**: All AI-generated output traceable to source data

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Tool                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Resource   │  │     Spec     │  │    Output    │     │
│  │   Discovery  │─▶│  Collector   │─▶│  Generator   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │              │
│         ▼                  ▼                  ▼              │
│  ┌──────────────────────────────────────────────────┐      │
│  │           Local Spec Storage (JSON)              │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        MCP Server                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Safe Query  │  │   Analysis   │  │   Diagram    │     │
│  │  Interface   │─▶│    Engine    │─▶│  Generator   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │              │
│         ▼                  ▼                  ▼              │
│  ┌──────────────────────────────────────────────────┐      │
│  │              AI Agent (LLM)                      │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Generated Artifacts  │
                  │  - Documentation      │
                  │  - Diagrams           │
                  │  - Terraform IaC      │
                  └───────────────────────┘
```

## Development Methodology: Test-Driven Development

### TDD Workflow

All development follows the **Red-Green-Refactor** cycle:

1. **RED**: Write a failing test that defines desired behavior
   - Write property-based test for parsers/transformations
   - Write unit test for specific behavior
   - Write integration test for API contracts
   - Verify test fails (proves test is actually testing something)

2. **GREEN**: Write minimal code to make the test pass
   - Implement only what's needed to pass the test
   - No premature optimization
   - Keep implementation simple and focused

3. **REFACTOR**: Improve code quality while keeping tests green
   - Remove duplication
   - Improve naming and structure
   - Optimize performance if needed
   - Ensure all tests still pass

4. **REPEAT**: Move to next test/feature

### Test Coverage Requirements

- **Minimum 80% code coverage** across all components
- **100% coverage** for critical paths: parsing, credential handling, data sanitization
- **Property-based tests** must run minimum 100 iterations per property
- **Integration tests** must cover all MCP server operations
- **End-to-end tests** must validate complete workflows

### Test Organization

```
aws-resource-inventory/
├── src/
│   ├── parser/
│   ├── collector/
│   ├── generator/
│   └── mcp_server/
├── tests/
│   ├── unit/
│   │   ├── test_parser.py          # Property-based parser tests
│   │   ├── test_collector.py       # Retry/resilience tests
│   │   ├── test_generator.py       # Output validation tests
│   │   └── test_sanitizer.py       # Security tests
│   ├── integration/
│   │   ├── test_mcp_server.py      # API contract tests
│   │   ├── test_aws_api.py         # AWS SDK mock tests
│   │   └── test_iac_generator.py   # Terraform validation tests
│   ├── e2e/
│   │   └── test_full_workflow.py   # Complete collection workflow
│   ├── fixtures/
│   │   ├── sample_aws_responses/   # Mock AWS API responses
│   │   ├── sample_specs/           # Sample resource specifications
│   │   └── expected_outputs/       # Expected test outputs
│   └── conftest.py                 # Shared test configuration
```

### Test Naming Conventions

- Property tests: `test_property_<description>_<requirement_id>`
- Unit tests: `test_<function>_<scenario>_<expected>`
- Integration tests: `test_integration_<component>_<operation>`
- E2E tests: `test_e2e_<workflow>_<scenario>`

Example:
```python
def test_property_parse_print_roundtrip_req_4_4():
    """Property: For all valid parsed specs, parsing→printing→parsing produces equivalent structure"""
    pass

def test_collector_retry_on_rate_limit_success():
    """Unit: Collector retries with exponential backoff on rate limit"""
    pass

def test_integration_mcp_server_list_resources():
    """Integration: MCP server list-resources returns cached data"""
    pass
```

## Architecture

### Technology Stack

- **Language**: Python 3.11+ (for AWS SDK support, type hints, and property testing libraries)
- **AWS SDK**: boto3 (AWS API interactions)
- **MCP Framework**: Model Context Protocol SDK
- **Property Testing**: Hypothesis (property-based testing framework)
- **Unit Testing**: pytest (test framework)
- **IaC Generation**: Terraform (infrastructure as code)
- **Diagram Generation**: drawio-ai-kit (visual diagrams)
- **Output Formats**: JSON, Markdown
- **CI/CD**: GitHub Actions with test gates

### Test Tooling Stack

```python
# requirements-dev.txt
pytest>=7.4.0              # Test framework
pytest-cov>=4.1.0          # Coverage reporting
pytest-mock>=3.11.1        # Mocking utilities
hypothesis>=6.82.0         # Property-based testing
moto>=4.1.0                # AWS service mocking
freezegun>=1.2.2           # Time mocking
responses>=0.23.0          # HTTP mocking
black>=23.7.0              # Code formatting
mypy>=1.4.1                # Type checking
ruff>=0.0.280              # Fast linting
```

### TDD Pipeline

```yaml
# .github/workflows/tdd-pipeline.yml
name: TDD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run Unit Tests
        run: pytest tests/unit/ -v --cov=src --cov-report=term-missing
        # Must pass with >= 80% coverage
      
      - name: Run Property Tests
        run: pytest tests/unit/ -k property -v --hypothesis-show-statistics
        # Must run 100+ iterations per property
      
      - name: Run Integration Tests
        run: pytest tests/integration/ -v
      
      - name: Run E2E Tests
        run: pytest tests/e2e/ -v
      
      - name: Type Checking
        run: mypy src/
      
      - name: Coverage Gate
        run: |
          coverage report --fail-under=80
          coverage report --include="src/parser/*" --fail-under=100
```

## Components and Interfaces

### 1. Resource Parser (TDD Component)

**Purpose**: Parse AWS API responses into typed structures and format back to JSON

#### Test Specification (Write FIRST)

```python
from hypothesis import given, strategies as st

# Property Test 1: Round-trip (MUST WRITE FIRST)
@given(st.from_type(ResourceSpec))
def test_property_parse_print_roundtrip_req_4_4(spec):
    """
    Property: For all valid ResourceSpec objects,
    parse(print(spec)) produces equivalent structure
    
    Validates: Requirement 4.4
    """
    json_output = print_spec(spec)
    parsed = parse_spec(json_output)
    assert parsed == spec

# Property Test 2: Parse then Print Preserves JSON
@given(st.text().filter(is_valid_json))
def test_property_print_parse_roundtrip(json_text):
    """
    Property: For all valid JSON strings,
    print(parse(json)) produces equivalent JSON
    
    Validates: Requirement 4.4
    """
    parsed = parse_spec(json_text)
    output = print_spec(parsed)
    assert normalize_json(output) == normalize_json(json_text)

# Error Test (MUST WRITE FIRST)
def test_parser_malformed_json_returns_descriptive_error_req_4_2():
    """
    Unit: Parser returns descriptive error with excerpt for malformed JSON
    
    Validates: Requirement 4.2
    """
    malformed = '{"key": invalid}'
    result = parse_spec(malformed)
    assert result.is_err()
    assert "invalid" in result.error_message()
    assert "excerpt" in result.error_context()
```

#### Interface

```python
from typing import Dict, Any, Result
from dataclasses import dataclass

@dataclass
class ResourceSpec:
    """Typed AWS resource specification"""
    resource_type: str
    arn: str
    region: str
    specifications: Dict[str, Any]
    metadata: SpecMetadata
    
class ResourceParser:
    """TDD: Tests written before implementation"""
    
    def parse_spec(self, json_data: str) -> Result[ResourceSpec, ParseError]:
        """Parse AWS API response into ResourceSpec
        
        TDD: test_property_parse_print_roundtrip_req_4_4 MUST pass
        TDD: test_parser_malformed_json_returns_descriptive_error_req_4_2 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
    
    def print_spec(self, spec: ResourceSpec) -> str:
        """Format ResourceSpec back to valid AWS JSON
        
        TDD: test_property_print_parse_roundtrip MUST pass
        """
        raise NotImplementedError("RED: Write test first")
```

### 2. Spec Collector (TDD Component)

**Purpose**: Collect resource specifications with retry logic and resilience

#### Test Specification (Write FIRST)

```python
import pytest
from unittest.mock import Mock, patch

# Resilience Test 1 (MUST WRITE FIRST)
def test_collector_retry_exponential_backoff_req_12_1():
    """
    Unit: Collector retries up to 3 times with exponential backoff
    
    Validates: Requirement 12.1
    """
    mock_api = Mock()
    mock_api.side_effect = [
        Exception("Timeout"),
        Exception("Timeout"),
        {"InstanceId": "i-123"}  # Success on 3rd try
    ]
    
    collector = SpecCollector(api_client=mock_api)
    result = collector.collect_ec2_spec("i-123")
    
    assert result.is_ok()
    assert mock_api.call_count == 3
    # Assert exponential backoff delays

# Resilience Test 2 (MUST WRITE FIRST)
def test_collector_continues_after_permission_error_req_2_5():
    """
    Unit: Collector logs missing permission and continues
    
    Validates: Requirement 2.5
    """
    mock_api = Mock()
    mock_api.get_bucket_policy.side_effect = AccessDenied("Missing s3:GetBucketPolicy")
    
    collector = SpecCollector(api_client=mock_api)
    result = collector.collect_s3_specs("my-bucket")
    
    assert result.is_ok()
    assert "bucket-policy" not in result.value.specifications
    assert "Missing s3:GetBucketPolicy" in collector.get_logs()

# Rate Limit Test (MUST WRITE FIRST)
def test_collector_waits_on_rate_limit_req_12_3():
    """
    Unit: Collector respects AWS retry-after headers
    
    Validates: Requirement 12.3
    """
    mock_api = Mock()
    mock_api.side_effect = [
        RateLimitException(retry_after=5),
        {"FunctionName": "my-function"}
    ]
    
    with patch('time.sleep') as mock_sleep:
        collector = SpecCollector(api_client=mock_api)
        result = collector.collect_lambda_spec("my-function")
        
        assert result.is_ok()
        mock_sleep.assert_called_with(5)
```

#### Interface

```python
class SpecCollector:
    """TDD: Tests written before implementation"""
    
    def __init__(self, api_client: AWSClient):
        self.api_client = api_client
        self.retry_config = RetryConfig(max_attempts=3, backoff_multiplier=2)
    
    def collect_s3_specs(self, bucket_name: str) -> Result[ResourceSpec, CollectorError]:
        """Collect all S3 bucket specifications
        
        TDD: test_collector_continues_after_permission_error_req_2_5 MUST pass
        
        Specifications: bucket-acl, bucket-cors, bucket-encryption,
        bucket-lifecycle-configuration, bucket-policy, bucket-tagging,
        bucket-versioning, bucket-website
        """
        raise NotImplementedError("RED: Write test first")
    
    def collect_ec2_spec(self, instance_id: str) -> Result[ResourceSpec, CollectorError]:
        """Collect EC2 instance specifications with retry
        
        TDD: test_collector_retry_exponential_backoff_req_12_1 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
    
    def collect_lambda_spec(self, function_name: str) -> Result[ResourceSpec, CollectorError]:
        """Collect Lambda function specifications with rate limit handling
        
        TDD: test_collector_waits_on_rate_limit_req_12_3 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
```

### 3. IaC Generator (TDD Component)

**Purpose**: Generate Terraform code from collected specifications

#### Test Specification (Write FIRST)

```python
# Validation Test (MUST WRITE FIRST)
def test_iac_generator_terraform_plan_zero_changes_req_7_5():
    """
    E2E: Generated Terraform plan shows zero changes vs actual AWS
    
    Validates: Requirement 7.5
    """
    # Given: Collected specs from AWS
    specs = load_fixture("sample_specs/complete_infrastructure.json")
    
    # When: Generate Terraform code
    generator = IaCGenerator()
    tf_code = generator.generate_terraform(specs)
    
    # Then: terraform plan shows zero changes
    with terraform_workspace(tf_code):
        plan_output = run_terraform_plan()
        assert "No changes" in plan_output
        assert plan_output.changes_count == 0

# Property Test (MUST WRITE FIRST)
@given(st.from_type(ResourceSpec))
def test_property_iac_generator_includes_all_specs(spec):
    """
    Property: For all ResourceSpecs, generated Terraform includes all specifications
    
    Validates: Requirement 7.3
    """
    generator = IaCGenerator()
    tf_code = generator.generate_resource_block(spec)
    
    # All spec keys should appear in generated Terraform
    for key, value in spec.specifications.items():
        assert key_appears_in_tf(tf_code, key)

# Import Command Test (MUST WRITE FIRST)
def test_iac_generator_includes_import_commands_req_7_4():
    """
    Unit: Generator creates terraform import commands for all resources
    
    Validates: Requirement 7.4
    """
    specs = [
        ResourceSpec(resource_type="aws_s3_bucket", arn="arn:aws:s3:::my-bucket"),
        ResourceSpec(resource_type="aws_lambda_function", arn="arn:aws:lambda:us-east-1:123:function:my-func")
    ]
    
    generator = IaCGenerator()
    import_script = generator.generate_import_script(specs)
    
    assert "terraform import aws_s3_bucket.my_bucket my-bucket" in import_script
    assert "terraform import aws_lambda_function.my_func my-func" in import_script
```

#### Interface

```python
class IaCGenerator:
    """TDD: Tests written before implementation"""
    
    def generate_terraform(self, specs: List[ResourceSpec]) -> TerraformCode:
        """Generate complete Terraform configuration
        
        TDD: test_iac_generator_terraform_plan_zero_changes_req_7_5 MUST pass
        TDD: test_iac_generator_includes_import_commands_req_7_4 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
    
    def generate_resource_block(self, spec: ResourceSpec) -> str:
        """Generate single Terraform resource block
        
        TDD: test_property_iac_generator_includes_all_specs MUST pass
        """
        raise NotImplementedError("RED: Write test first")
    
    def generate_import_script(self, specs: List[ResourceSpec]) -> str:
        """Generate terraform import commands
        
        TDD: test_iac_generator_includes_import_commands_req_7_4 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
    
    def generate_verification_script(self, specs: List[ResourceSpec]) -> str:
        """Generate script to verify Terraform state matches AWS
        
        TDD: test_iac_generator_verification_script_req_7_6 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
```

### 4. MCP Server (TDD Component)

**Purpose**: Provide safe, controlled interface for AI Agent to query infrastructure

#### Test Specification (Write FIRST)

```python
# API Contract Tests (MUST WRITE FIRST)
def test_mcp_server_list_resources_returns_cached_data_req_5_3():
    """
    Integration: MCP server returns cached local data, not AWS API calls
    
    Validates: Requirement 5.3
    """
    # Given: Cached specs exist
    cached_specs = load_fixture("sample_specs/resources.json")
    server = MCPServer(cache_dir="/tmp/specs")
    
    # When: AI Agent requests resource list
    with mock.patch('boto3.client') as mock_boto:
        response = server.handle_request({
            "operation": "list-resources",
            "filters": {"region": "us-east-1"}
        })
        
        # Then: Returns cached data, no AWS API calls
        assert response.is_ok()
        assert len(response.value) > 0
        mock_boto.assert_not_called()

# Security Test (MUST WRITE FIRST)
def test_mcp_server_blocks_unauthorized_operations_req_5_6():
    """
    Integration: MCP server rejects non-whitelisted operations
    
    Validates: Requirement 5.6
    """
    server = MCPServer()
    
    # When: AI Agent requests unauthorized operation
    response = server.handle_request({
        "operation": "delete-resource",  # NOT in whitelist
        "resource_id": "i-123"
    })
    
    # Then: Returns error and logs attempt
    assert response.is_err()
    assert "unauthorized" in response.error_message().lower()
    assert server.get_security_logs()[0].operation == "delete-resource"

# Rate Limit Test (MUST WRITE FIRST)
def test_mcp_server_enforces_rate_limit_req_5_7():
    """
    Integration: MCP server limits AI Agent to 10 requests/second
    
    Validates: Requirement 5.7
    """
    server = MCPServer()
    
    # When: AI Agent sends 15 requests in 1 second
    responses = []
    for i in range(15):
        responses.append(server.handle_request({"operation": "list-resources"}))
    
    # Then: First 10 succeed, remaining 5 are rate limited
    assert sum(r.is_ok() for r in responses) == 10
    assert sum(r.is_err() for r in responses) == 5
    assert "rate limit" in responses[-1].error_message().lower()

# No Credential Exposure Test (MUST WRITE FIRST)
def test_mcp_server_no_aws_credentials_in_responses_req_5_2():
    """
    Security: MCP server never exposes AWS credentials
    
    Validates: Requirement 5.2
    """
    server = MCPServer()
    
    # When: AI Agent requests any operation
    response = server.handle_request({"operation": "get-resource-spec", "arn": "arn:aws:s3:::bucket"})
    
    # Then: Response contains no credential-like strings
    response_text = json.dumps(response.value)
    assert not contains_credential_pattern(response_text)
    assert "aws_access_key_id" not in response_text.lower()
    assert "aws_secret_access_key" not in response_text.lower()
```

#### Interface

```python
class MCPServer:
    """TDD: Tests written before implementation"""
    
    WHITELISTED_OPERATIONS = [
        "list-resources",
        "get-resource-spec",
        "analyze-activity-flow",
        "generate-documentation"
    ]
    
    def handle_request(self, request: Dict[str, Any]) -> Result[Dict, MCPError]:
        """Handle AI Agent request with security checks
        
        TDD: test_mcp_server_list_resources_returns_cached_data_req_5_3 MUST pass
        TDD: test_mcp_server_blocks_unauthorized_operations_req_5_6 MUST pass
        TDD: test_mcp_server_enforces_rate_limit_req_5_7 MUST pass
        TDD: test_mcp_server_no_aws_credentials_in_responses_req_5_2 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
    
    def list_resources(self, filters: Dict[str, Any]) -> List[ResourceSummary]:
        """List resources from cached data
        
        TDD: test_mcp_server_list_resources_returns_cached_data_req_5_3 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
    
    def get_resource_spec(self, arn: str) -> Result[ResourceSpec, MCPError]:
        """Get resource specification from cache
        
        TDD: test_mcp_server_get_spec_cache_miss_returns_error_req_5_4 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
```

### 5. Diagram Generator (TDD Component)

**Purpose**: Generate visual infrastructure diagrams using drawio-ai-kit

#### Test Specification (Write FIRST)

```python
# Output Validation Test (MUST WRITE FIRST)
def test_diagram_generator_creates_valid_drawio_xml_req_6_4():
    """
    Unit: Generator outputs valid drawio XML format
    
    Validates: Requirement 6.4
    """
    specs = load_fixture("sample_specs/vpc_with_ec2.json")
    generator = DiagramGenerator()
    
    # When: Generate diagram
    diagram_xml = generator.generate_diagram(specs)
    
    # Then: Output is valid drawio XML
    assert is_valid_xml(diagram_xml)
    assert diagram_xml.startswith('<mxfile')
    assert can_open_in_drawio(diagram_xml)

# Relationship Test (MUST WRITE FIRST)
def test_diagram_generator_shows_relationships_req_6_1():
    """
    Unit: Diagram includes resource relationships
    
    Validates: Requirement 6.1
    """
    specs = [
        ResourceSpec(resource_type="vpc", id="vpc-123"),
        ResourceSpec(resource_type="ec2", id="i-456", vpc_id="vpc-123"),
    ]
    
    generator = DiagramGenerator()
    diagram = generator.generate_diagram(specs)
    
    # Then: Diagram shows connection between VPC and EC2
    assert has_connection(diagram, from_id="vpc-123", to_id="i-456")

# Property Test (MUST WRITE FIRST)
@given(st.lists(st.from_type(ResourceSpec), min_size=1))
def test_property_diagram_includes_all_resources(specs):
    """
    Property: For all non-empty resource lists, diagram includes all resources
    
    Validates: Requirement 6.4
    """
    generator = DiagramGenerator()
    diagram = generator.generate_diagram(specs)
    
    for spec in specs:
        assert resource_appears_in_diagram(diagram, spec.arn)
```

#### Interface

```python
class DiagramGenerator:
    """TDD: Tests written before implementation"""
    
    def __init__(self, drawio_kit_path: str):
        self.drawio_kit = load_drawio_kit(drawio_kit_path)
    
    def generate_diagram(self, specs: List[ResourceSpec]) -> str:
        """Generate drawio XML diagram from resource specs
        
        TDD: test_diagram_generator_creates_valid_drawio_xml_req_6_4 MUST pass
        TDD: test_diagram_generator_shows_relationships_req_6_1 MUST pass
        TDD: test_property_diagram_includes_all_resources MUST pass
        """
        raise NotImplementedError("RED: Write test first")
    
    def identify_relationships(self, specs: List[ResourceSpec]) -> List[ResourceRelationship]:
        """Identify relationships between resources
        
        TDD: test_diagram_generator_shows_relationships_req_6_1 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
```

### 6. Data Sanitizer (TDD Component)

**Purpose**: Remove sensitive data from output files

#### Test Specification (Write FIRST)

```python
# Security Test (MUST WRITE FIRST)
def test_sanitizer_removes_aws_credentials_req_9_5():
    """
    Security: Sanitizer replaces AWS credentials with placeholders
    
    Validates: Requirement 9.5
    """
    data = {
        "environment_variables": {
            "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
            "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        }
    }
    
    sanitizer = DataSanitizer()
    sanitized = sanitizer.sanitize(data)
    
    assert sanitized["environment_variables"]["AWS_ACCESS_KEY_ID"] == "[REDACTED_AWS_KEY]"
    assert sanitized["environment_variables"]["AWS_SECRET_ACCESS_KEY"] == "[REDACTED_AWS_SECRET]"

# Property Test (MUST WRITE FIRST)
@given(st.dictionaries(keys=st.text(), values=st.text()))
def test_property_sanitizer_preserves_structure(data):
    """
    Property: For all dictionaries, sanitization preserves structure
    
    Validates: Requirement 9.5
    """
    sanitizer = DataSanitizer()
    sanitized = sanitizer.sanitize(data)
    
    assert sanitized.keys() == data.keys()

# Logging Test (MUST WRITE FIRST)
def test_sanitizer_logs_redactions_req_9_6():
    """
    Unit: Sanitizer logs what was redacted
    
    Validates: Requirement 9.6
    """
    data = {"password": "secret123"}
    
    sanitizer = DataSanitizer()
    sanitized = sanitizer.sanitize(data)
    
    logs = sanitizer.get_redaction_logs()
    assert any("password" in log for log in logs)
```

#### Interface

```python
class DataSanitizer:
    """TDD: Tests written before implementation"""
    
    SENSITIVE_PATTERNS = [
        r'AKIA[0-9A-Z]{16}',  # AWS Access Key
        r'aws_secret_access_key',
        r'password',
        r'private_key',
        r'secret',
    ]
    
    def sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from dictionary
        
        TDD: test_sanitizer_removes_aws_credentials_req_9_5 MUST pass
        TDD: test_property_sanitizer_preserves_structure MUST pass
        TDD: test_sanitizer_logs_redactions_req_9_6 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
    
    def get_redaction_logs(self) -> List[str]:
        """Get log of what was redacted
        
        TDD: test_sanitizer_logs_redactions_req_9_6 MUST pass
        """
        raise NotImplementedError("RED: Write test first")
```

## Data Models

### Core Data Structures

```python
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class ResourceSpec:
    """Complete specification of an AWS resource"""
    resource_type: str           # e.g., "aws_s3_bucket"
    arn: str                     # AWS ARN
    region: str                  # AWS region
    account_id: str              # AWS account ID
    specifications: Dict[str, Any]  # Resource-specific config
    metadata: 'SpecMetadata'
    raw_response: Optional[str]  # Original AWS API response (for audit)

@dataclass
class SpecMetadata:
    """Collection metadata"""
    collected_at: datetime
    collector_version: str
    api_version: str
    checksum: str

@dataclass
class ResourceRelationship:
    """Relationship between two resources"""
    from_arn: str
    to_arn: str
    relationship_type: str  # e.g., "vpc_connection", "iam_role_usage"
    confidence: float       # 0.0 to 1.0

@dataclass
class CollectionReport:
    """Report of collection process"""
    start_time: datetime
    end_time: datetime
    total_resources: int
    successful_collections: int
    failed_collections: int
    errors: List['CollectionError']
    regions_scanned: List[str]
    time_saved_hours: float

@dataclass
class CollectionError:
    """Error during collection"""
    resource_arn: str
    operation: str
    error_type: str
    error_message: str
    timestamp: datetime
    retry_count: int
```

## Data Flow

```
1. Discovery Phase (TDD: test_e2e_discovery_workflow)
   ┌─────────────┐
   │  AWS APIs   │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐     Tests FIRST:
   │  Discovery  │     - test_discovery_lists_all_regions
   │   Module    │     - test_discovery_handles_inaccessible_region
   └──────┬──────┘     - test_discovery_completes_under_5_minutes
          │
          ▼
   [ Resource ARN List ]

2. Collection Phase (TDD: test_e2e_collection_workflow)
   ┌─────────────────┐
   │  Resource ARN   │
   │      List       │
   └────────┬────────┘
            │
            ▼
   ┌────────────────┐  Tests FIRST:
   │ Spec Collector │  - test_collector_retry_exponential_backoff
   │  (with retry)  │  - test_collector_continues_after_permission_error
   └────────┬───────┘  - test_collector_waits_on_rate_limit
            │
            ▼
   ┌────────────────┐
   │ Resource Parser│  Tests FIRST:
   │                │  - test_property_parse_print_roundtrip
   └────────┬───────┘  - test_parser_malformed_json_returns_error
            │
            ▼
   [ Typed ResourceSpec Objects ]

3. Persistence Phase (TDD: test_e2e_persistence_workflow)
   ┌────────────────┐
   │  ResourceSpec  │
   │    Objects     │
   └────────┬───────┘
            │
            ▼
   ┌────────────────┐  Tests FIRST:
   │ Data Sanitizer │  - test_sanitizer_removes_aws_credentials
   │                │  - test_property_sanitizer_preserves_structure
   └────────┬───────┘
            │
            ▼
   ┌────────────────┐  Tests FIRST:
   │     Output     │  - test_output_generator_creates_json_and_markdown
   │   Generator    │  - test_output_generator_includes_checksums
   └────────┬───────┘
            │
            ▼
   [ JSON + Markdown Files in Local Storage ]

4. Analysis Phase (TDD: test_e2e_analysis_workflow)
   ┌────────────────┐
   │  Local Specs   │
   └────────┬───────┘
            │
            ▼
   ┌────────────────┐  Tests FIRST:
   │   MCP Server   │  - test_mcp_server_list_resources_returns_cached_data
   │                │  - test_mcp_server_blocks_unauthorized_operations
   └────────┬───────┘  - test_mcp_server_enforces_rate_limit
            │
            ▼
   ┌────────────────┐  Tests FIRST:
   │  AI Agent      │  - test_ai_agent_analysis_includes_citations
   │  (LLM)         │  - test_ai_agent_no_hallucination
   └────────┬───────┘
            │
            ▼
   [ Documentation + Diagrams ]

5. IaC Generation Phase (TDD: test_e2e_iac_generation_workflow)
   ┌────────────────┐
   │  Local Specs   │
   └────────┬───────┘
            │
            ▼
   ┌────────────────┐  Tests FIRST:
   │ IaC Generator  │  - test_iac_generator_terraform_plan_zero_changes
   │                │  - test_iac_generator_includes_import_commands
   └────────┬───────┘  - test_property_iac_generator_includes_all_specs
            │
            ▼
   [ Terraform .tf Files + Import Script ]
```

## Testing Strategy

### Test-First Development Process

**Every feature begins with tests:**

1. **Write Property Tests** (for parsers, transformations, generators)
   - Define universal properties that should hold
   - Use Hypothesis to generate test inputs
   - Minimum 100 iterations per property
   - Tag with requirement reference

2. **Write Unit Tests** (for specific behaviors)
   - Define expected behavior for edge cases
   - Test error handling explicitly
   - Test retry logic and resilience
   - Mock external dependencies

3. **Write Integration Tests** (for API contracts)
   - Test MCP server operations end-to-end
   - Test AWS SDK interactions with moto mocks
   - Test component interactions
   - Verify no AWS API calls where prohibited

4. **Write E2E Tests** (for complete workflows)
   - Test full discovery → collection → output workflow
   - Test IaC generation → terraform plan validation
   - Test MCP server → AI Agent → documentation generation
   - Use fixtures and sample AWS data

5. **Implement Code** (only after tests are written)
   - Write minimal code to pass tests
   - Run tests continuously
   - Refactor while keeping tests green

### Test Categories and Coverage

#### 1. Property-Based Tests (Hypothesis)

**Parser Tests** - 100% coverage required
```python
# Feature: aws-resource-inventory, Property 1: Parse-print round-trip
@given(st.from_type(ResourceSpec))
def test_property_parse_print_roundtrip_req_4_4(spec):
    """For all valid ResourceSpecs, parse(print(spec)) == spec"""
    json_output = print_spec(spec)
    parsed = parse_spec(json_output)
    assert parsed == spec

# Feature: aws-resource-inventory, Property 2: Print-parse round-trip
@given(st.text().filter(is_valid_json))
def test_property_print_parse_roundtrip_req_4_4(json_text):
    """For all valid JSON, print(parse(json)) preserves structure"""
    parsed = parse_spec(json_text)
    output = print_spec(parsed)
    assert normalize_json(output) == normalize_json(json_text)
```

**Sanitizer Tests** - 100% coverage required
```python
# Feature: aws-resource-inventory, Property 3: Sanitization preserves structure
@given(st.dictionaries(keys=st.text(), values=st.recursive(
    st.one_of(st.text(), st.integers(), st.booleans()),
    lambda children: st.dictionaries(st.text(), children)
)))
def test_property_sanitizer_preserves_structure_req_9_5(data):
    """For all nested dictionaries, sanitizer preserves structure"""
    sanitizer = DataSanitizer()
    sanitized = sanitizer.sanitize(data)
    assert sanitized.keys() == data.keys()
    assert get_structure(sanitized) == get_structure(data)
```

**IaC Generator Tests**
```python
# Feature: aws-resource-inventory, Property 4: IaC includes all specs
@given(st.from_type(ResourceSpec))
def test_property_iac_generator_includes_all_specs_req_7_3(spec):
    """For all ResourceSpecs, generated Terraform includes all config"""
    generator = IaCGenerator()
    tf_code = generator.generate_resource_block(spec)
    for key, value in spec.specifications.items():
        assert key_appears_in_tf(tf_code, key)
```

#### 2. Unit Tests (pytest)

**Retry Logic Tests**
```python
def test_collector_retry_exponential_backoff_req_12_1():
    """Collector retries up to 3 times with exponential backoff"""
    mock_api = Mock(side_effect=[
        Exception("Timeout"),
        Exception("Timeout"),
        {"InstanceId": "i-123"}
    ])
    collector = SpecCollector(api_client=mock_api)
    result = collector.collect_ec2_spec("i-123")
    assert result.is_ok()
    assert mock_api.call_count == 3
```

**Error Handling Tests**
```python
def test_parser_malformed_json_returns_descriptive_error_req_4_2():
    """Parser returns descriptive error for malformed JSON"""
    malformed = '{"key": invalid}'
    result = parse_spec(malformed)
    assert result.is_err()
    assert "invalid" in result.error_message()
```

**Security Tests**
```python
def test_sanitizer_removes_aws_credentials_req_9_5():
    """Sanitizer replaces AWS credentials with placeholders"""
    data = {
        "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
        "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCY"
    }
    sanitizer = DataSanitizer()
    sanitized = sanitizer.sanitize(data)
    assert sanitized["AWS_ACCESS_KEY_ID"] == "[REDACTED_AWS_KEY]"
```

#### 3. Integration Tests (pytest + moto)

**MCP Server Tests**
```python
def test_integration_mcp_server_list_resources_req_5_3():
    """MCP server returns cached data without AWS API calls"""
    with mock.patch('boto3.client') as mock_boto:
        server = MCPServer(cache_dir="tests/fixtures/sample_specs")
        response = server.handle_request({
            "operation": "list-resources",
            "filters": {"region": "us-east-1"}
        })
        assert response.is_ok()
        mock_boto.assert_not_called()

def test_integration_mcp_server_blocks_unauthorized_req_5_6():
    """MCP server rejects non-whitelisted operations"""
    server = MCPServer()
    response = server.handle_request({"operation": "delete-resource"})
    assert response.is_err()
    assert "unauthorized" in response.error_message().lower()
```

**AWS API Mock Tests**
```python
@moto.mock_s3
def test_integration_collector_s3_all_specs_req_2_2():
    """Collector retrieves all S3 bucket specifications"""
    # Setup mock S3 bucket
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')
    
    # Collect specs
    collector = SpecCollector(api_client=s3)
    result = collector.collect_s3_specs('test-bucket')
    
    # Verify all spec types collected
    assert result.is_ok()
    expected_specs = ['bucket-acl', 'bucket-cors', 'bucket-encryption', 
                      'bucket-lifecycle-configuration', 'bucket-policy',
                      'bucket-tagging', 'bucket-versioning', 'bucket-website']
    for spec_type in expected_specs:
        assert spec_type in result.value.specifications
```

#### 4. End-to-End Tests (pytest)

**Full Workflow Tests**
```python
def test_e2e_discovery_collection_output_workflow():
    """Complete workflow: discovery → collection → output"""
    # Discovery phase
    discoverer = ResourceDiscovery(aws_client=mock_aws_client())
    resources = discoverer.discover_all_resources()
    assert len(resources) > 0
    
    # Collection phase
    collector = SpecCollector(api_client=mock_aws_client())
    specs = [collector.collect_spec(r.arn) for r in resources]
    assert all(s.is_ok() for s in specs)
    
    # Output phase
    generator = OutputGenerator(output_dir="/tmp/test_output")
    generator.generate_json(specs)
    generator.generate_markdown(specs)
    
    # Verify outputs exist
    assert os.path.exists("/tmp/test_output/resources.json")
    assert os.path.exists("/tmp/test_output/resources.md")

def test_e2e_iac_generation_terraform_plan_zero_req_7_5():
    """Generated Terraform shows zero changes vs AWS"""
    # Given: Collected specs
    specs = load_fixture("tests/fixtures/sample_specs/complete_infra.json")
    
    # When: Generate Terraform
    generator = IaCGenerator()
    tf_code = generator.generate_terraform(specs)
    
    # Then: terraform plan shows zero changes
    with terraform_workspace(tf_code) as workspace:
        workspace.init()
        plan_output = workspace.plan()
        assert "No changes" in plan_output
        assert plan_output.changes_count == 0
```

### Test Fixtures

**Sample AWS Responses**
```
tests/fixtures/sample_aws_responses/
├── ec2/
│   ├── describe_instances.json
│   ├── describe_security_groups.json
│   └── describe_volumes.json
├── s3/
│   ├── list_buckets.json
│   ├── get_bucket_policy.json
│   ├── get_bucket_encryption.json
│   └── get_bucket_versioning.json
├── lambda/
│   ├── list_functions.json
│   └── get_function_configuration.json
└── iam/
    ├── list_roles.json
    └── get_role.json
```

**Sample Specifications**
```
tests/fixtures/sample_specs/
├── complete_infrastructure.json  # Full multi-service setup
├── vpc_with_ec2.json            # Simple VPC + EC2 scenario
├── api_gateway_lambda_dynamo.json  # Serverless pattern
└── malformed/
    ├── invalid_json.txt
    ├── missing_required_fields.json
    └── unknown_resource_type.json
```

### TDD Development Workflow Example

**Example: Implementing Resource Parser**

```bash
# Step 1: RED - Write failing test
$ cat > tests/unit/test_parser.py << EOF
from hypothesis import given, strategies as st

@given(st.from_type(ResourceSpec))
def test_property_parse_print_roundtrip_req_4_4(spec):
    json_output = print_spec(spec)
    parsed = parse_spec(json_output)
    assert parsed == spec
EOF

$ pytest tests/unit/test_parser.py
# FAILS: NotImplementedError

# Step 2: GREEN - Minimal implementation
$ cat > src/parser.py << EOF
def print_spec(spec: ResourceSpec) -> str:
    return json.dumps(spec.__dict__)

def parse_spec(json_text: str) -> ResourceSpec:
    data = json.loads(json_text)
    return ResourceSpec(**data)
EOF

$ pytest tests/unit/test_parser.py
# PASSES

# Step 3: REFACTOR - Improve while keeping tests green
$ cat > src/parser.py << EOF
class ResourceParser:
    def print_spec(self, spec: ResourceSpec) -> str:
        """Format spec to valid AWS JSON"""
        return json.dumps(
            spec.__dict__,
            indent=2,
            sort_keys=True,
            default=str
        )
    
    def parse_spec(self, json_text: str) -> Result[ResourceSpec, ParseError]:
        """Parse AWS JSON into typed structure"""
        try:
            data = json.loads(json_text)
            return Ok(ResourceSpec(**data))
        except json.JSONDecodeError as e:
            return Err(ParseError(f"Malformed JSON: {e}"))
EOF

$ pytest tests/unit/test_parser.py
# STILL PASSES - refactor successful

# Step 4: REPEAT - Add next test
$ cat >> tests/unit/test_parser.py << EOF
def test_parser_malformed_json_returns_descriptive_error_req_4_2():
    malformed = '{"key": invalid}'
    result = parse_spec(malformed)
    assert result.is_err()
    assert "invalid" in result.error_message()
EOF

# Continue RED-GREEN-REFACTOR cycle...
```

## Error Handling

### TDD Error Handling Strategy

**All error paths MUST have tests written first:**

1. **Expected Errors** (part of normal operation)
   - Permission denied → continue with warning
   - Rate limit → wait and retry
   - Resource not found → log and skip

2. **Unexpected Errors** (should not happen)
   - Malformed API response → fail with diagnostic
   - Network timeout → retry with backoff
   - Invalid credentials → fail immediately

### Error Types

```python
# TDD: Write tests for each error type FIRST

class CollectorError(Exception):
    """Base class for collection errors
    
    TDD: test_collector_error_includes_context
    """
    def __init__(self, message: str, resource_arn: str, context: Dict):
        self.message = message
        self.resource_arn = resource_arn
        self.context = context

class ParseError(CollectorError):
    """Parsing AWS response failed
    
    TDD: test_parser_malformed_json_returns_descriptive_error_req_4_2
    """
    pass

class PermissionError(CollectorError):
    """AWS permission denied
    
    TDD: test_collector_continues_after_permission_error_req_2_5
    """
    pass

class RateLimitError(CollectorError):
    """AWS rate limit exceeded
    
    TDD: test_collector_waits_on_rate_limit_req_12_3
    """
    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after
```

### Error Handling Tests (Write FIRST)

```python
# Resilience Tests
def test_collector_retry_on_network_timeout():
    """Collector retries on network timeout with exponential backoff"""
    pass

def test_collector_continues_after_permission_denied():
    """Collector logs permission error and continues with other specs"""
    pass

def test_collector_waits_on_rate_limit():
    """Collector respects retry-after header on rate limit"""
    pass

def test_collector_fails_fast_on_invalid_credentials():
    """Collector fails immediately on credential errors"""
    pass

# Error Reporting Tests
def test_collection_report_includes_all_errors():
    """Collection report lists all failed operations"""
    pass

def test_cli_exits_nonzero_on_errors():
    """CLI exits with non-zero status when errors occur"""
    pass
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Parse-Print Round-Trip (Parser)

**For any** valid `ResourceSpec` object, parsing then printing then parsing SHALL produce an equivalent data structure.

**Validates: Requirement 4.4**

**Test Implementation:**
```python
from hypothesis import given, strategies as st

# Feature: aws-resource-inventory, Property 1: Parse-print round-trip
@given(st.from_type(ResourceSpec))
@settings(max_examples=100)
def test_property_parse_print_roundtrip_req_4_4(spec):
    """For all valid ResourceSpecs, parse(print(spec)) == spec"""
    parser = ResourceParser()
    json_output = parser.print_spec(spec)
    parsed = parser.parse_spec(json_output)
    assert parsed.is_ok()
    assert parsed.value == spec
```

### Property 2: Sanitization Preserves Structure

**For any** nested dictionary structure, sanitization SHALL preserve the dictionary structure (keys and nesting) while replacing only sensitive values.

**Validates: Requirement 9.5**

**Test Implementation:**
```python
# Feature: aws-resource-inventory, Property 2: Sanitization preserves structure
@given(st.dictionaries(
    keys=st.text(),
    values=st.recursive(
        st.one_of(st.text(), st.integers(), st.booleans()),
        lambda children: st.dictionaries(st.text(), children)
    )
))
@settings(max_examples=100)
def test_property_sanitizer_preserves_structure_req_9_5(data):
    """For all nested dicts, sanitizer preserves structure"""
    sanitizer = DataSanitizer()
    sanitized = sanitizer.sanitize(data)
    assert get_structure(sanitized) == get_structure(data)
```

### Property 3: IaC Generation Completeness

**For any** valid `ResourceSpec`, the generated Terraform resource block SHALL include all specifications from the original spec.

**Validates: Requirement 7.3**

**Test Implementation:**
```python
# Feature: aws-resource-inventory, Property 3: IaC includes all specs
@given(st.from_type(ResourceSpec))
@settings(max_examples=100)
def test_property_iac_generator_includes_all_specs_req_7_3(spec):
    """For all ResourceSpecs, Terraform includes all config keys"""
    generator = IaCGenerator()
    tf_code = generator.generate_resource_block(spec)
    
    for key, value in spec.specifications.items():
        assert key_appears_in_tf(tf_code, key), f"Key {key} missing in Terraform"
```

### Property 4: Diagram Includes All Resources

**For any** non-empty list of `ResourceSpec` objects, the generated diagram SHALL include a visual representation of every resource.

**Validates: Requirement 6.4**

**Test Implementation:**
```python
# Feature: aws-resource-inventory, Property 4: Diagram includes all resources
@given(st.lists(st.from_type(ResourceSpec), min_size=1, max_size=20))
@settings(max_examples=100)
def test_property_diagram_includes_all_resources_req_6_4(specs):
    """For all resource lists, diagram includes all resources"""
    generator = DiagramGenerator()
    diagram = generator.generate_diagram(specs)
    
    for spec in specs:
        assert resource_appears_in_diagram(diagram, spec.arn), \
            f"Resource {spec.arn} missing in diagram"
```

### Property 5: Collection Preserves AWS Data

**For any** AWS API response that is successfully parsed, the raw response SHALL be preserved in the `ResourceSpec` for audit purposes.

**Validates: Requirement 2.6**

**Test Implementation:**
```python
# Feature: aws-resource-inventory, Property 5: Collection preserves raw data
@given(st.from_type(AWSAPIResponse))
@settings(max_examples=100)
def test_property_collector_preserves_raw_response_req_2_6(aws_response):
    """For all AWS responses, collector preserves raw response"""
    collector = SpecCollector()
    spec = collector.parse_aws_response(aws_response)
    
    if spec.is_ok():
        assert spec.value.raw_response == aws_response.raw_data
```

### Property 6: MCP Server Never Exposes Credentials

**For any** valid MCP server request, the response SHALL NOT contain AWS credentials or credential patterns.

**Validates: Requirement 5.2**

**Test Implementation:**
```python
# Feature: aws-resource-inventory, Property 6: MCP never exposes credentials
@given(st.dictionaries(
    keys=st.sampled_from(["list-resources", "get-resource-spec", "analyze-activity-flow"]),
    values=st.dictionaries(st.text(), st.text())
))
@settings(max_examples=100)
def test_property_mcp_server_no_credentials_req_5_2(request):
    """For all MCP requests, response contains no credentials"""
    server = MCPServer()
    response = server.handle_request(request)
    
    response_text = json.dumps(response.value if response.is_ok() else response.error)
    assert not contains_credential_pattern(response_text)
```

## Performance Requirements

### TDD Performance Testing

**Performance tests MUST be written before optimization:**

```python
# Performance Test (Write FIRST)
def test_discovery_completes_under_5_minutes_req_1_5():
    """
    Performance: Discovery completes within 5 minutes for 1000 resources
    
    Validates: Requirement 1.5
    """
    # Given: Mock AWS with 1000 resources
    mock_aws = create_mock_aws_with_resources(count=1000)
    
    # When: Run discovery
    start = time.time()
    discoverer = ResourceDiscovery(aws_client=mock_aws)
    resources = discoverer.discover_all_resources()
    elapsed = time.time() - start
    
    # Then: Completes under 5 minutes
    assert elapsed < 300, f"Discovery took {elapsed}s, expected < 300s"
    assert len(resources) == 1000
```

### Performance Targets

- **Discovery**: Complete in < 5 minutes for 1000 resources (Requirement 1.5)
- **Collection**: Process 10 resources/second with retry logic
- **Parsing**: Parse 100 specs/second
- **MCP Server**: Handle 10 requests/second (Requirement 5.7)
- **IaC Generation**: Generate Terraform for 1000 resources in < 2 minutes

## Security Considerations

### TDD Security Testing

**All security requirements MUST have tests written first:**

```python
# Security Test 1
def test_cli_never_logs_credentials_req_9_2():
    """Security: CLI never logs AWS credentials"""
    with captured_logs() as logs:
        cli = CLI(aws_access_key="AKIATEST", aws_secret="SECRET")
        cli.run_discovery()
        
        assert "AKIATEST" not in logs
        assert "SECRET" not in logs

# Security Test 2
def test_sanitizer_removes_all_sensitive_patterns_req_9_5():
    """Security: Sanitizer removes all known sensitive patterns"""
    sensitive_data = {
        "aws_key": "AKIAIOSFODNN7EXAMPLE",
        "password": "mypassword123",
        "private_key": "-----BEGIN RSA PRIVATE KEY-----"
    }
    
    sanitizer = DataSanitizer()
    sanitized = sanitizer.sanitize(sensitive_data)
    
    assert all(v == "[REDACTED]" for v in sanitized.values())

# Security Test 3
def test_mcp_server_sandboxed_no_aws_access_req_9_7():
    """Security: MCP server has no AWS credential access"""
    server = MCPServer()
    
    # Attempt to access AWS credentials should fail
    with pytest.raises(CredentialAccessError):
        server._get_aws_credentials()
```

### Security Checklist

- [ ] AWS credentials never logged (Req 9.2)
- [ ] Credentials not persisted to disk (Req 9.2)
- [ ] STS assume-role supported (Req 9.3)
- [ ] Least-privilege IAM permissions (Req 9.4)
- [ ] Sensitive data sanitized in outputs (Req 9.5)
- [ ] MCP server sandboxed (Req 9.7)
- [ ] Rate limiting enforced (Req 5.7)
- [ ] Unauthorized operations blocked (Req 5.6)

## Deployment and CI/CD

### TDD CI/CD Pipeline

**Test gates enforce TDD discipline:**

```yaml
# .github/workflows/tdd-pipeline.yml
name: TDD Pipeline

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run Unit Tests with Coverage
        run: |
          pytest tests/unit/ -v \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-report=html
      
      - name: Coverage Gate (80% minimum)
        run: coverage report --fail-under=80
      
      - name: Critical Path Coverage Gate (100%)
        run: |
          coverage report --include="src/parser/*" --fail-under=100
          coverage report --include="src/sanitizer/*" --fail-under=100
      
      - name: Upload Coverage Report
        uses: codecov/codecov-action@v3
  
  property-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run Property-Based Tests
        run: |
          pytest tests/unit/ -k property -v \
            --hypothesis-show-statistics \
            --hypothesis-seed=random
      
      - name: Verify Property Test Iterations
        run: |
          # Ensure each property test runs 100+ iterations
          pytest tests/unit/ -k property -v \
            --hypothesis-show-statistics \
            | grep "examples" \
            | awk '{if ($1 < 100) exit 1}'
  
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run Integration Tests
        run: pytest tests/integration/ -v
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run E2E Tests
        run: pytest tests/e2e/ -v --slow
  
  type-checking:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: pip install mypy
      
      - name: Type Check
        run: mypy src/ --strict
  
  linting:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: pip install ruff black
      
      - name: Lint with Ruff
        run: ruff check src/
      
      - name: Format Check with Black
        run: black --check src/
  
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Security Scan
        run: |
          pip install bandit
          bandit -r src/ -ll
  
  test-summary:
    needs: [unit-tests, property-tests, integration-tests, e2e-tests, type-checking, linting]
    runs-on: ubuntu-latest
    steps:
      - name: All Tests Passed
        run: echo "✅ All TDD gates passed"
```

### Test Execution Order

1. **Fast Unit Tests** (< 1 minute) - Run on every commit
2. **Property Tests** (1-5 minutes) - Run on every commit
3. **Integration Tests** (5-10 minutes) - Run on every PR
4. **E2E Tests** (10-20 minutes) - Run before merge
5. **Type Checking** (< 1 minute) - Run on every commit
6. **Linting** (< 1 minute) - Run on every commit

## Documentation Requirements

### TDD Documentation

**Documentation MUST include test examples:**

1. **README.md**
   - Installation with test setup
   - Running tests (unit, property, integration, e2e)
   - TDD workflow explanation
   - Coverage reports

2. **TESTING.md**
   - Complete testing strategy
   - How to write new tests
   - Test fixture documentation
   - Mock setup guides

3. **API_DOCS.md**
   - Every function includes test example
   - Property tests documented with examples
   - Error cases with test references

4. **CONTRIBUTING.md**
   - TDD workflow mandatory
   - No PR accepted without tests
   - Coverage requirements
   - Test naming conventions

## Summary

This design implements AWS Resource Inventory with **Test-Driven Development as a core principle**, not an afterthought. Every component has tests written before implementation, ensuring:

- **Correctness**: Property-based testing verifies universal properties
- **Reliability**: Comprehensive error handling with tests for every error path
- **Security**: All security requirements have test coverage
- **Maintainability**: High test coverage makes refactoring safe
- **Confidence**: Developers can trust the system because tests prove correctness

**Key TDD Requirements:**

1. ✅ **Minimum 80% code coverage** across all components
2. ✅ **100% coverage** for parser, sanitizer, credential handling
3. ✅ **Property tests run 100+ iterations** per property
4. ✅ **Tests written BEFORE implementation** (Red-Green-Refactor)
5. ✅ **CI/CD pipeline enforces** test gates
6. ✅ **Every PR requires tests** for new features
7. ✅ **Test fixtures** provide comprehensive mock data
8. ✅ **Integration tests** verify component interactions
9. ✅ **E2E tests** validate complete workflows
10. ✅ **Security tests** ensure no credential exposure

**Next Steps:**

1. Set up project structure with test directories
2. Install testing frameworks (pytest, hypothesis, moto)
3. Write first failing test for Resource Parser
4. Begin Red-Green-Refactor cycle
5. Build up test suite incrementally
6. Implement features only after tests are green
