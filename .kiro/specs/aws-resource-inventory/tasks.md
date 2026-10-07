# Implementation Plan: AWS Resource Inventory

## Overview

This implementation plan follows Test-Driven Development (TDD) methodology with the Red-Green-Refactor cycle. Every implementation task is preceded by writing tests first. The system will be built using Python 3.11+ with comprehensive test coverage including property-based tests, unit tests, integration tests, and end-to-end tests.

## Tasks

- [x] 1. Project Setup and Infrastructure
  - [x] 1.1 Create project structure and initialize Python package
    - Create directory structure: `src/`, `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/fixtures/`
    - Initialize Python package with `__init__.py` files
    - Create `setup.py` or `pyproject.toml` for package configuration
    - _Requirements: All_

  - [x] 1.2 Install testing frameworks and dependencies
    - Install pytest, pytest-cov, hypothesis, moto, freezegun, responses
    - Install boto3, AWS SDK dependencies
    - Create `requirements.txt` and `requirements-dev.txt`
    - _Requirements: All_

  - [x] 1.3 Configure test infrastructure and fixtures
    - Set up `tests/conftest.py` with shared fixtures
    - Create sample AWS response fixtures in `tests/fixtures/sample_aws_responses/`
    - Create sample spec fixtures in `tests/fixtures/sample_specs/`
    - Set up test configuration for pytest
    - _Requirements: 2.6, 3.1_

  - [x] 1.4 Set up CI/CD pipeline with test gates
    - Create `.github/workflows/tdd-pipeline.yml`
    - Configure unit test job with 80% coverage gate
    - Configure property test job with 100 iterations minimum
    - Configure integration and E2E test jobs
    - Add type checking (mypy) and linting (ruff, black) jobs
    - _Requirements: All_

- [x] 2. Checkpoint - Verify project setup
  - Ensure all tests pass (even if empty), ask the user if questions arise.

- [x] 3. Resource Parser - TDD Implementation
  - [x] 3.1 Write property tests for parser (RED phase)
    - Write test: `test_property_parse_print_roundtrip_req_4_4` using Hypothesis
    - Write test: `test_property_print_parse_roundtrip_req_4_4` for JSON preservation
    - Write test: `test_parser_malformed_json_returns_descriptive_error_req_4_2`
    - Verify all tests fail with NotImplementedError
    - _Requirements: 4.4, 4.2_

  - [x] 3.2 Property test for parser - round-trip consistency
    - **Property 1: Parse-Print Round-Trip**
    - **Validates: Requirements 4.4**

  - [x] 3.3 Implement ResourceSpec data model and ResourceParser (GREEN phase)
    - Create `src/parser.py` with `ResourceSpec` dataclass
    - Implement `ResourceParser.parse_spec()` method
    - Implement `ResourceParser.print_spec()` method
    - Run tests until all property tests pass
    - _Requirements: 4.1, 4.3, 4.4_

  - [x] 3.4 Refactor parser for error handling and validation (REFACTOR phase)
    - Add comprehensive error handling with descriptive messages
    - Improve type annotations
    - Extract helper functions for JSON normalization
    - Ensure all tests still pass
    - _Requirements: 4.2, 4.5_

- [x] 4. Checkpoint - Parser tests passing
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Data Sanitizer - TDD Implementation
  - [x] 5.1 Write property tests for sanitizer (RED phase)
    - Write test: `test_property_sanitizer_preserves_structure_req_9_5` using Hypothesis
    - Write test: `test_sanitizer_removes_aws_credentials_req_9_5`
    - Write test: `test_sanitizer_logs_redactions_req_9_6`
    - Verify all tests fail
    - _Requirements: 9.5, 9.6_

  - [x] 5.2 Property test for sanitizer - structure preservation
    - **Property 2: Sanitization Preserves Structure**
    - **Validates: Requirements 9.5**

  - [x] 5.3 Implement DataSanitizer class (GREEN phase)
    - Create `src/sanitizer.py` with `DataSanitizer` class
    - Implement `sanitize()` method with pattern matching
    - Implement credential detection regex patterns
    - Implement redaction logging
    - Run tests until all pass
    - _Requirements: 9.5, 9.6_

  - [x] 5.4 Refactor sanitizer with additional patterns (REFACTOR phase)
    - Add patterns for passwords, private keys, secrets
    - Improve performance for large nested structures
    - Ensure all tests still pass
    - _Requirements: 9.5_

- [x] 6. Spec Collector - TDD Implementation
  - [x] 6.1 Write unit tests for collector resilience (RED phase)
    - Write test: `test_collector_retry_exponential_backoff_req_12_1`
    - Write test: `test_collector_continues_after_permission_error_req_2_5`
    - Write test: `test_collector_waits_on_rate_limit_req_12_3`
    - Write test: `test_collector_preserves_raw_response_req_2_6`
    - Verify all tests fail
    - _Requirements: 12.1, 2.5, 12.3, 2.6_

  - [x] 6.2 Unit tests for collector - retry and error handling
    - Test exponential backoff on failures
    - Test permission error handling
    - Test rate limit handling
    - _Requirements: 12.1, 2.5, 12.3_

  - [x] 6.3 Implement SpecCollector base class (GREEN phase)
    - Create `src/collector.py` with `SpecCollector` class
    - Implement retry logic with exponential backoff
    - Implement rate limit handling
    - Implement error logging and continuation
    - _Requirements: 2.1, 12.1, 12.2, 12.3_

  - [x] 6.4 Write integration tests for S3 spec collection (RED phase)
    - Write test: `test_integration_collector_s3_all_specs_req_2_2` using moto
    - Mock S3 bucket with all specification types
    - Verify test fails before implementation
    - _Requirements: 2.2_

  - [x] 6.5 Integration test for S3 collector
    - Test collection of all S3 bucket specifications
    - Test with mocked AWS S3 service
    - _Requirements: 2.2_

  - [x] 6.6 Implement S3 spec collection (GREEN phase)
    - Implement `collect_s3_specs()` method
    - Collect: bucket-acl, bucket-cors, bucket-encryption, bucket-lifecycle-configuration
    - Collect: bucket-policy, bucket-tagging, bucket-versioning, bucket-website
    - Run integration tests until passing
    - _Requirements: 2.2_

  - [x] 6.7 Write integration tests for EC2 and Lambda (RED phase)
    - Write test: `test_integration_collector_ec2_all_specs_req_2_3` using moto
    - Write test: `test_integration_collector_lambda_all_specs_req_2_4` using moto
    - _Requirements: 2.3, 2.4_

  - [x] 6.8 Integration tests for EC2 and Lambda collectors
    - Test EC2 instance specification collection
    - Test Lambda function specification collection
    - _Requirements: 2.3, 2.4_

  - [x] 6.9 Implement EC2 and Lambda spec collection (GREEN phase)
    - Implement `collect_ec2_spec()` method
    - Implement `collect_lambda_spec()` method
    - Collect all specifications per requirements
    - _Requirements: 2.3, 2.4_

  - [x] 6.10 Refactor collector with common patterns (REFACTOR phase)
    - Extract common retry logic into decorator
    - Extract common error handling patterns
    - Improve logging and error messages
    - _Requirements: 2.1, 12.1, 12.2_

- [x] 7. Checkpoint - Collector tests passing
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Resource Discovery - TDD Implementation
  - [x] 8.1 Write unit tests for resource discovery (RED phase)
    - Write test: `test_discovery_lists_all_regions_req_1_1`
    - Write test: `test_discovery_handles_inaccessible_region_req_1_4`
    - Write test: `test_discovery_completes_under_5_minutes_req_1_5`
    - _Requirements: 1.1, 1.4, 1.5_

  - [x] 8.2 Unit tests for resource discovery
    - Test discovery across all AWS regions
    - Test error handling for inaccessible regions
    - Test performance requirements
    - _Requirements: 1.1, 1.4, 1.5_

  - [x] 8.3 Implement ResourceDiscovery class (GREEN phase)
    - Create `src/discovery.py` with `ResourceDiscovery` class
    - Implement `discover_all_resources()` method
    - Support EC2, S3, Lambda, RDS, VPC, Security Groups, IAM, CloudWatch, Step Functions, DynamoDB
    - Implement region enumeration and parallel discovery
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 8.4 Refactor discovery for performance (REFACTOR phase)
    - Optimize parallel region discovery
    - Add progress reporting
    - Ensure 5-minute completion for 1000 resources
    - _Requirements: 1.5_

- [x] 9. Output Generator - TDD Implementation
  - [x] 9.1 Write unit tests for output generation (RED phase)
    - Write test: `test_output_generator_creates_json_and_markdown_req_3_1`
    - Write test: `test_output_generator_includes_checksums_req_3_5`
    - Write test: `test_output_generator_organizes_by_type_and_region_req_3_2`
    - _Requirements: 3.1, 3.5, 3.2_

  - [x] 9.2 Unit tests for output generator
    - Test JSON and Markdown output generation
    - Test checksum calculation
    - Test file organization structure
    - _Requirements: 3.1, 3.5, 3.2_

  - [x] 9.3 Implement OutputGenerator class (GREEN phase)
    - Create `src/output_generator.py` with `OutputGenerator` class
    - Implement `generate_json()` method with metadata
    - Implement `generate_markdown()` method with formatting
    - Implement checksum calculation
    - Implement directory organization
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 9.4 Refactor output generator for readability (REFACTOR phase)
    - Improve Markdown formatting with tables
    - Add color coding for terminal output
    - Ensure all tests still pass
    - _Requirements: 3.4_

- [x] 10. IaC Generator - TDD Implementation
  - [x] 10.1 Write property tests for IaC generator (RED phase)
    - Write test: `test_property_iac_generator_includes_all_specs_req_7_3` using Hypothesis
    - Write test: `test_iac_generator_includes_import_commands_req_7_4`
    - _Requirements: 7.3, 7.4_

  - [x] 10.2 Property test for IaC generator - completeness
    - **Property 3: IaC Generation Completeness**
    - **Validates: Requirements 7.3**

  - [x] 10.3 Write E2E test for Terraform validation (RED phase)
    - Write test: `test_iac_generator_terraform_plan_zero_changes_req_7_5`
    - Set up Terraform workspace in test environment
    - Verify test fails before implementation
    - _Requirements: 7.5_

  - [x] 10.4 E2E test for Terraform plan validation
    - Test that generated Terraform shows zero changes
    - Validate against actual AWS state
    - _Requirements: 7.5_

  - [x] 10.5 Implement IaCGenerator class (GREEN phase)
    - Create `src/iac_generator.py` with `IaCGenerator` class
    - Implement `generate_terraform()` method
    - Implement `generate_resource_block()` for each resource type
    - Implement `generate_import_script()` method
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 10.6 Implement Terraform verification (GREEN phase)
    - Implement `generate_verification_script()` method
    - Add validation that terraform plan shows zero changes
    - Add traceability comments linking to spec files
    - _Requirements: 7.5, 7.6, 7.7_

  - [x] 10.7 Refactor IaC generator for maintainability (REFACTOR phase)
    - Extract resource-specific generators into separate modules
    - Improve Terraform formatting
    - Ensure all tests still pass
    - _Requirements: 7.2_

- [x] 11. Checkpoint - IaC generator tests passing
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Diagram Generator - TDD Implementation
  - [x] 12.1 Write property tests for diagram generator (RED phase)
    - Write test: `test_property_diagram_includes_all_resources_req_6_4` using Hypothesis
    - Write test: `test_diagram_generator_creates_valid_drawio_xml_req_6_4`
    - Write test: `test_diagram_generator_shows_relationships_req_6_1`
    - _Requirements: 6.4, 6.1_

  - [x] 12.2 Property test for diagram generator - resource inclusion
    - **Property 4: Diagram Includes All Resources**
    - **Validates: Requirements 6.4**

  - [x] 12.3 Unit tests for diagram generator
    - Test valid drawio XML generation
    - Test relationship visualization
    - _Requirements: 6.4, 6.1_

  - [x] 12.4 Implement DiagramGenerator class (GREEN phase)
    - Create `src/diagram_generator.py` with `DiagramGenerator` class
    - Integrate drawio-ai-kit library
    - Implement `generate_diagram()` method
    - Implement `identify_relationships()` method
    - _Requirements: 6.1, 6.4_

  - [x] 12.5 Refactor diagram generator with pattern detection (REFACTOR phase)
    - Add common pattern detection (API Gateway + Lambda + DynamoDB, etc.)
    - Improve layout algorithm
    - _Requirements: 6.2_

- [x] 13. Analysis Engine - TDD Implementation
  - [x] 13.1 Write unit tests for analysis engine (RED phase)
    - Write test: `test_analysis_engine_identifies_relationships_req_6_1`
    - Write test: `test_analysis_engine_detects_patterns_req_6_2`
    - Write test: `test_analysis_engine_flags_suspicious_patterns_req_6_6`
    - _Requirements: 6.1, 6.2, 6.6_

  - [x] 13.2 Unit tests for analysis engine
    - Test relationship identification
    - Test common pattern detection
    - Test security issue flagging
    - _Requirements: 6.1, 6.2, 6.6_

  - [x] 13.3 Implement AnalysisEngine class (GREEN phase)
    - Create `src/analysis_engine.py` with `AnalysisEngine` class
    - Implement relationship detection algorithms
    - Implement pattern matching logic
    - Implement security pattern detection
    - _Requirements: 6.1, 6.2, 6.6_

  - [x] 13.4 Implement citation and confidence scoring (GREEN phase)
    - Add citation generation linking to source specs
    - Add confidence scoring for detected patterns
    - Add evidence collection
    - _Requirements: 6.5, 8.1, 8.2_

  - [x] 13.5 Refactor analysis engine (REFACTOR phase)
    - Extract pattern definitions into configuration
    - Improve confidence score algorithms
    - _Requirements: 6.5_

- [ ] 14. MCP Server - TDD Implementation
  - [x] 14.1 Write integration tests for MCP server (RED phase)
    - Write test: `test_mcp_server_list_resources_returns_cached_data_req_5_3`
    - Write test: `test_mcp_server_blocks_unauthorized_operations_req_5_6`
    - Write test: `test_mcp_server_enforces_rate_limit_req_5_7`
    - Write test: `test_mcp_server_no_aws_credentials_in_responses_req_5_2`
    - _Requirements: 5.3, 5.6, 5.7, 5.2_

  - [ ] 14.2 Integration tests for MCP server
    - Test cached data retrieval without AWS calls
    - Test operation authorization
    - Test rate limiting
    - Test credential sanitization
    - _Requirements: 5.3, 5.6, 5.7, 5.2_

  - [ ] 14.3 Implement MCPServer class (GREEN phase)
    - Create `src/mcp_server.py` with `MCPServer` class
    - Implement `handle_request()` method with authorization
    - Implement rate limiting middleware
    - Implement whitelisted operations: list-resources, get-resource-spec, analyze-activity-flow, generate-documentation
    - _Requirements: 5.1, 5.5, 5.6, 5.7_

  - [ ] 14.4 Implement MCP server operations (GREEN phase)
    - Implement `list_resources()` using cached data
    - Implement `get_resource_spec()` from cache
    - Ensure no AWS API calls are made
    - Ensure no credentials in responses
    - _Requirements: 5.2, 5.3, 5.4_

  - [ ] 14.5 Refactor MCP server for security (REFACTOR phase)
    - Add comprehensive security logging
    - Add request validation
    - Ensure sandboxing from AWS credentials
    - _Requirements: 5.2, 5.6, 9.7_

- [ ] 15. Checkpoint - MCP server tests passing
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. CLI Tool - TDD Implementation
  - [ ] 16.1 Write unit tests for CLI (RED phase)
    - Write test: `test_cli_never_logs_credentials_req_9_2`
    - Write test: `test_cli_uses_aws_credential_chain_req_9_1`
    - Write test: `test_cli_supports_assume_role_req_9_3`
    - Write test: `test_cli_exits_nonzero_on_errors_req_12_5`
    - _Requirements: 9.2, 9.1, 9.3, 12.5_

  - [ ] 16.2 Unit tests for CLI tool
    - Test credential handling security
    - Test AWS credential chain integration
    - Test assume-role support
    - Test error exit codes
    - _Requirements: 9.1, 9.2, 9.3, 12.5_

  - [ ] 16.3 Implement CLI interface (GREEN phase)
    - Create `src/cli.py` with CLI application using argparse or Click
    - Implement commands: discover, collect, analyze, generate-iac, generate-docs
    - Implement AWS credential chain integration
    - Implement logging without credential exposure
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ] 16.4 Implement performance metrics collection (GREEN phase)
    - Add timing instrumentation
    - Implement metrics collection: resources discovered, API calls made, data volume
    - Calculate time savings vs manual effort
    - Generate summary report
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 16.5 Implement collection report generation (GREEN phase)
    - Generate report of successful/failed operations
    - List all errors with details
    - Display time savings metrics
    - _Requirements: 12.4_

  - [ ] 16.6 Refactor CLI for usability (REFACTOR phase)
    - Add progress bars for long operations
    - Improve help messages and examples
    - Add colored output for better readability
    - _Requirements: All_

- [ ] 17. End-to-End Testing
  - [ ] 17.1 Write E2E test for complete discovery workflow
    - Write test: `test_e2e_discovery_collection_output_workflow`
    - Test: CLI discovery → collection → output generation
    - Verify all output files created correctly
    - _Requirements: 1.1, 2.1, 3.1_

  - [ ] 17.2 E2E test - complete workflow
    - Test full discovery and collection pipeline
    - Validate output file generation
    - _Requirements: 1.1, 2.1, 3.1_

  - [ ] 17.3 Write E2E test for IaC generation workflow
    - Write test: `test_e2e_iac_generation_terraform_plan_zero_req_7_5`
    - Test: Collection → IaC generation → Terraform validation
    - _Requirements: 7.5_

  - [ ] 17.4 E2E test - IaC generation
    - Test complete IaC generation pipeline
    - Validate Terraform plan output
    - _Requirements: 7.5_

  - [ ] 17.5 Write E2E test for MCP server analysis workflow
    - Write test: `test_e2e_mcp_server_analysis_workflow`
    - Test: Collection → MCP server → AI Agent → Documentation
    - _Requirements: 5.1, 6.1, 8.1_

  - [ ] 17.6 E2E test - MCP server analysis
    - Test MCP server with AI Agent integration
    - Validate generated documentation
    - _Requirements: 5.1, 6.1, 8.1_

  - [ ] 17.7 Implement AI Agent integration for analysis
    - Integrate LLM for activity flow analysis
    - Implement citation generation
    - Implement hallucination prevention checks
    - _Requirements: 6.3, 8.1, 8.2, 8.5_

  - [ ] 17.8 Implement verification command
    - Create verification command that validates citations
    - Check checksums against source files
    - Report discrepancies
    - _Requirements: 8.3, 8.4, 8.6_

- [ ] 18. Checkpoint - All E2E tests passing
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 19. Documentation and Demo
  - [ ] 19.1 Create README.md with installation and usage
    - Document prerequisites and dependencies
    - Provide installation instructions
    - Include usage examples for all CLI commands
    - Add troubleshooting section
    - _Requirements: 11.1_

  - [ ] 19.2 Create architecture documentation
    - Create architecture diagrams showing component interaction
    - Document CLI, MCP Server, and AI Agent flow
    - Document data flow from AWS to output
    - _Requirements: 11.2_

  - [ ] 19.3 Create TESTING.md documentation
    - Document TDD workflow and methodology
    - Explain how to write new tests
    - Document test fixture structure
    - Provide examples of property tests, unit tests, integration tests
    - _Requirements: 11.1_

  - [ ] 19.4 Create demo script and sample AWS account setup
    - Create demo script that runs against sample AWS environment
    - Set up sample AWS resources using moto or real test account
    - Create demo video or walkthrough
    - _Requirements: 11.3_

  - [ ] 19.5 Create example output files
    - Generate example JSON output
    - Generate example Markdown reports
    - Generate example Terraform IaC
    - Generate example diagrams
    - Generate example analysis reports
    - _Requirements: 11.5_

  - [ ] 19.6 Document accuracy methodology and security measures
    - Document citation methodology
    - Document hallucination prevention approach
    - Document security measures and credential handling
    - Document performance benchmarks
    - _Requirements: 11.4_

- [ ] 20. Final Integration and Polish
  - [ ] 20.1 Run complete test suite and validate coverage
    - Run all unit tests with coverage report
    - Verify 80% minimum coverage achieved
    - Verify 100% coverage for parser and sanitizer
    - Run all property tests with 100+ iterations
    - Run all integration and E2E tests
    - _Requirements: All_

  - [ ] 20.2 Final test suite validation
    - Run complete test suite
    - Validate coverage requirements met
    - _Requirements: All_

  - [ ] 20.3 Security audit and vulnerability scanning
    - Run bandit security scanner
    - Review all credential handling code
    - Verify no secrets in logs or outputs
    - Test MCP server sandboxing
    - _Requirements: 9.1, 9.2, 9.5, 9.6, 9.7_

  - [ ] 20.4 Performance optimization and benchmarking
    - Profile performance bottlenecks
    - Optimize slow operations
    - Validate 5-minute discovery requirement
    - Generate performance benchmark report
    - _Requirements: 1.5, 10.1, 10.2_

  - [ ] 20.5 Code quality checks
    - Run mypy type checking
    - Run ruff linting
    - Run black formatting
    - Fix all type errors and linting issues
    - _Requirements: All_

- [ ] 21. Final Checkpoint - Production Ready
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test-related sub-tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- TDD methodology requires writing tests BEFORE implementation code
- RED-GREEN-REFACTOR cycle must be followed strictly
- Property tests must run minimum 100 iterations
- Minimum 80% code coverage required; 100% for parser and sanitizer
- Integration tests use moto for AWS service mocking
- E2E tests validate complete workflows end-to-end
- Checkpoints ensure incremental validation before proceeding
- All security-sensitive code must have dedicated security tests
- Performance tests validate time and resource constraints
- Documentation must include test examples and TDD workflow explanation

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3", "1.4"] },
    { "id": 2, "tasks": ["3.1"] },
    { "id": 3, "tasks": ["3.2", "3.3"] },
    { "id": 4, "tasks": ["3.4", "5.1"] },
    { "id": 5, "tasks": ["5.2", "5.3"] },
    { "id": 6, "tasks": ["5.4", "6.1"] },
    { "id": 7, "tasks": ["6.2", "6.3"] },
    { "id": 8, "tasks": ["6.4"] },
    { "id": 9, "tasks": ["6.5", "6.6"] },
    { "id": 10, "tasks": ["6.7"] },
    { "id": 11, "tasks": ["6.8", "6.9"] },
    { "id": 12, "tasks": ["6.10", "8.1"] },
    { "id": 13, "tasks": ["8.2", "8.3"] },
    { "id": 14, "tasks": ["8.4", "9.1"] },
    { "id": 15, "tasks": ["9.2", "9.3"] },
    { "id": 16, "tasks": ["9.4", "10.1"] },
    { "id": 17, "tasks": ["10.2", "10.3"] },
    { "id": 18, "tasks": ["10.4", "10.5"] },
    { "id": 19, "tasks": ["10.6"] },
    { "id": 20, "tasks": ["10.7", "12.1"] },
    { "id": 21, "tasks": ["12.2", "12.3", "12.4"] },
    { "id": 22, "tasks": ["12.5", "13.1"] },
    { "id": 23, "tasks": ["13.2", "13.3"] },
    { "id": 24, "tasks": ["13.4"] },
    { "id": 25, "tasks": ["13.5", "14.1"] },
    { "id": 26, "tasks": ["14.2", "14.3"] },
    { "id": 27, "tasks": ["14.4"] },
    { "id": 28, "tasks": ["14.5", "16.1"] },
    { "id": 29, "tasks": ["16.2", "16.3"] },
    { "id": 30, "tasks": ["16.4", "16.5"] },
    { "id": 31, "tasks": ["16.6", "17.1"] },
    { "id": 32, "tasks": ["17.2", "17.3"] },
    { "id": 33, "tasks": ["17.4", "17.5"] },
    { "id": 34, "tasks": ["17.6", "17.7"] },
    { "id": 35, "tasks": ["17.8", "19.1", "19.2"] },
    { "id": 36, "tasks": ["19.3", "19.4", "19.5"] },
    { "id": 37, "tasks": ["19.6", "20.1"] },
    { "id": 38, "tasks": ["20.2", "20.3", "20.4"] },
    { "id": 39, "tasks": ["20.5"] }
  ]
}
```
