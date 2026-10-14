# Implementation Plan: AWS Resource Inventory

## Overview

This implementation plan follows Test-Driven Development (TDD) methodology with the Red-Green-Refactor cycle. Every implementation task is preceded by writing tests first. The system is built with Python 3.11+ with property-based, unit, integration (moto) and end-to-end tests.

Tasks 1–13 were implemented against the first draft of the design. Tasks 14–18 align that code with the revised requirements/design (canonical resource types, AWS-field-name spec schema, checksums and citations, Terraform mapping). Each top-level task ends with a commit that is pushed. Tests are always run with `venv/bin/python -m pytest`.

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

- [ ] 14. Foundations alignment: resource registry and sanitizer
  - [ ] 14.1 Write tests for the resource type registry (RED)
    - `tests/unit/test_resource_types.py`: `test_registry_has_ten_supported_types_req_1_3`, `test_canonical_type_resolves_aliases`, `test_resource_id_per_type_req_3_2`, `test_file_id_replaces_unsafe_characters_req_3_2`, `test_spec_relpath_layout_req_3_2`
    - _Requirements: 1.3, 3.2_
  - [ ] 14.2 Implement `src/resource_types.py` (GREEN)
    - `ResourceTypeInfo`, `REGISTRY`, `canonical_type()`, `resource_id()`, `file_id()`, `spec_relpath()`, draw.io style per type
    - _Requirements: 1.3, 3.2_
  - [ ] 14.3 Write sanitizer tests for the revised rules (RED)
    - `test_sanitizer_does_not_redact_keyname_kmskeyid_keytype_req_9_5`, `test_sanitizer_redacts_pem_private_key_req_9_5`, `test_sanitizer_does_not_redact_role_unique_ids_req_9_5`, `test_property_sanitizer_idempotent_req_9_6`
    - _Requirements: 9.5, 9.6_
  - [ ] 14.4 Update `src/sanitizer.py` (GREEN): remove the generic `key` rule and non-credential ID prefixes, add the PEM rule and `[REDACTED_PRIVATE_KEY]`
    - _Requirements: 9.5, 9.6_
  - [ ] 14.5 Use the registry everywhere a type name, id or file name is derived (`output_generator`, `iac_generator`, `diagram_generator`, `analysis_engine`, `discovery`) (REFACTOR)
    - _Requirements: 3.2, 7.7_
  - Commit: `feat(core): add resource type registry and align sanitizer rules (Task 14)`

- [ ] 15. Collection alignment: all resource types, error classification, sessions
  - [ ] 15.1 Write tests (RED)
    - `tests/unit/test_collector.py`: `test_collector_maps_client_error_access_denied_no_retry_req_2_5`, `test_collector_uses_retry_after_header_req_12_3`, `test_collector_counts_api_calls_req_10_2`, `test_collector_s3_missing_subconfig_not_error_req_2_2`
    - `tests/integration/test_aws_api.py` (moto): one `test_integration_collector_<type>_spec_req_2_1` per type not yet covered (vpc, security group, rds, log group, state machine, dynamodb, iam role), each asserting the schema in design.md and `ResponseMetadata` absence
    - `tests/integration/test_inventory.py`: `test_integration_inventory_collects_all_discovered_types_req_2_1`, `test_inventory_sets_region_and_account_req_3_3`, `test_inventory_records_failed_operations_req_12_2`
    - `tests/unit/test_aws_session.py`: `test_session_uses_default_chain_req_9_1`, `test_session_assume_role_req_9_3`, `test_session_disables_botocore_retries_req_12_1`
    - `tests/unit/test_discovery.py`: `test_discovery_follows_pagination_req_1_5`
    - _Requirements: 1.5, 2.1–2.6, 9.1, 9.3, 12.1–12.3_
  - [ ] 15.2 Implement (GREEN): `SpecCollector` per-type `collect_*` methods + `collect_resource()` dispatcher, `ClientError` classification, `src/inventory.py`, `src/aws_session.py`, discovery pagination and API-call counting
    - _Requirements: 1.5, 2.1–2.6, 9.1, 9.3, 12.1–12.3_
  - [ ] 15.3 Refactor shared retry/classification code; remove `"unknown"` region/account placeholders
  - Commit: `feat(collector): collect all supported resource types with classified retries (Task 15)`

- [ ] 16. Integrity and persistence alignment
  - [ ] 16.1 Write tests (RED)
    - `tests/unit/test_integrity.py`: `test_spec_checksum_is_canonical_req_3_5`, `test_seal_specs_sanitizes_and_sets_checksum_req_3_5`, `test_resolve_property_path`, `test_find_property_line_req_8_4`, `test_verify_output_dir_detects_tampered_file_req_8_4`, `test_verify_output_dir_detects_wrong_evidence_req_8_3`
    - `tests/unit/test_output_generator.py`: `test_output_generator_sanitizes_raw_responses_req_3_6`, `test_output_generator_load_specs_reads_only_spec_files_req_5_3`, `test_output_generator_writes_manifest_req_3_3`
    - _Requirements: 3.3, 3.5, 3.6, 8.3, 8.4_
  - [ ] 16.2 Implement `src/integrity.py` and update `src/output_generator.py` (GREEN)
  - Commit: `feat(integrity): add spec checksums, sealing and output verification (Task 16)`

- [ ] 17. Analysis and diagram alignment
  - [ ] 17.1 Rewrite analysis/diagram test fixtures to the AWS-field-name schema; add `test_analysis_engine_citations_include_spec_file_req_8_2`, `test_analysis_engine_log_group_relationship_req_6_1`, `test_analysis_engine_flags_admin_managed_policy_req_6_6`, `test_analysis_engine_flags_public_bucket_policy_req_6_6`, `test_analysis_engine_flags_ipv6_open_ingress_req_6_6`, `test_analysis_engine_reports_undetectable_patterns_req_6_2`, `test_property_citations_resolve_req_8_5`, `test_diagram_uses_aws4_stencils_req_6_4` (RED)
    - _Requirements: 6.1, 6.2, 6.4, 6.5, 6.6, 8.1, 8.2, 8.5_
  - [ ] 17.2 Implement rules, citations, `AnalysisReport.to_dict()`, stencil styles and region layout (GREEN)
  - Commit: `feat(analysis): align relationship rules, citations and diagram styles with design (Task 17)`

- [ ] 18. Terraform mapping alignment
  - [ ] 18.1 Write tests (RED): per-type mapping tests `test_iac_<type>_maps_arguments_req_7_3` (10 types), `test_iac_generated_files_parse_as_hcl_req_7_2` (python-hcl2), `test_iac_import_ids_per_type_req_7_4`, `test_iac_companion_resources_s3_iam_req_7_4`, `test_iac_redacted_values_ignored_req_7_5`, `test_iac_verify_plan_uses_exit_code_only_req_7_5`, `test_iac_provider_alias_per_region_req_7_2`; keep Property 3
    - _Requirements: 7.2–7.7_
  - [ ] 18.2 Implement the mapping table, companion resources, provider aliases and exit-code-only plan verification (GREEN)
  - [ ] 18.3 Add live test `test_live_iac_terraform_plan_zero_changes_req_7_5` (`@pytest.mark.aws`, skipped by default)
  - Commit: `feat(iac): map specifications to Terraform arguments per resource type (Task 18)`

- [ ] 19. MCP Server - TDD Implementation
  - [x] 19.1 Write integration tests for MCP server core (RED) — formerly 14.1, done
    - `test_mcp_server_list_resources_returns_cached_data_req_5_3`, `test_mcp_server_blocks_unauthorized_operations_req_5_6`, `test_mcp_server_enforces_rate_limit_req_5_7`, `test_mcp_server_no_aws_credentials_in_responses_req_5_2`
  - [ ] 19.2 Extend tests to the revised contract (RED)
    - Cache fixtures use the Output_Dir layout and canonical types
    - `test_mcp_server_list_resources_filters_by_alias_req_5_1`, `test_mcp_server_rejects_unknown_params_req_5_5`, `test_mcp_server_security_log_entries_req_5_6`, `test_mcp_server_rate_limited_requests_not_counted_req_5_7`, `test_mcp_server_analyze_activity_flow_uses_cache_req_5_1`, `test_mcp_server_generate_documentation_cited_req_8_1`, `test_mcp_server_unknown_arn_rejected_req_8_6`, `test_mcp_server_module_does_not_import_boto3_req_5_2`, `test_property_mcp_server_no_credentials_req_5_2`
    - `tests/integration/test_mcp_stdio.py`: `test_mcp_stdio_lists_four_tools_req_5_1`, `test_mcp_stdio_tool_call_roundtrip_req_5_1`, `test_sandbox_environment_removes_aws_vars_req_9_7`
    - _Requirements: 5.1–5.7, 8.6, 9.7_
  - [ ] 19.3 Implement `MCPServer` revisions: parameter schemas, security log, registry-based cache loading, analysis/documentation operations (GREEN)
  - [ ] 19.4 Implement `src/mcp_stdio.py` (FastMCP tools + `sandbox_environment`) (GREEN)
  - [ ] 19.5 Refactor for security: sanitize every response at a single exit point, no boto3 import (REFACTOR)
  - Commit: `feat(mcp): MCP stdio server over cached specs with whitelist, validation and rate limit (Task 19)`

- [ ] 20. Checkpoint - Foundations, collector, analysis, IaC and MCP tests passing
  - Run the full suite; fix regressions before continuing.

- [ ] 21. CLI Tool - TDD Implementation
  - [ ] 21.1 Write tests (RED) in `tests/unit/test_cli.py` and `tests/unit/test_metrics.py`
    - `test_cli_never_logs_credentials_req_9_2`, `test_cli_uses_aws_credential_chain_req_9_1`, `test_cli_supports_assume_role_req_9_3`, `test_cli_exits_nonzero_on_errors_req_12_5`, `test_cli_exits_2_without_credentials_req_12_5`, `test_cli_collect_prints_time_savings_req_10_5`, `test_cli_collection_report_lists_operations_req_12_4`, `test_metrics_time_savings_formula_req_10_4`, `test_metrics_phase_timings_req_10_1`, `test_cli_only_read_only_api_calls_req_9_4`
    - _Requirements: 9.1–9.4, 10.1–10.5, 12.4, 12.5_
  - [ ] 21.2 Implement `src/cli.py` commands `discover`, `collect`, `analyze`, `generate-iac`, `generate-docs`, `verify`, `mcp-serve` with exit codes and `SanitizingFilter` (GREEN)
  - [ ] 21.3 Implement `src/metrics.py` and `collection_report.json` / `summary_report.md` (GREEN)
  - [ ] 21.4 Implement `src/documentation.py` (`docs/infrastructure.md`, every statement cited) (GREEN)
    - _Requirements: 6.3, 8.1_
  - [ ] 21.5 Refactor: progress output on stderr, `--no-color`, help texts with examples (REFACTOR)
  - Commit: `feat(cli): add aws-inventory CLI with metrics, reports and verification (Task 21)`

- [ ] 22. End-to-End Testing (CliRunner + moto)
  - [ ] 22.1 `test_e2e_discovery_collection_output_workflow`: collect on a moto account with all 10 types → every expected file exists, checksums verify, exit 0
    - _Requirements: 1.1, 2.1, 3.1–3.6_
  - [ ] 22.2 `test_e2e_iac_generation_workflow`: collect → generate-iac → HCL parses, one block per resource, `import.sh` has one import per block
    - _Requirements: 7.1–7.4_
  - [ ] 22.3 `test_e2e_mcp_server_analysis_workflow`: collect → MCPServer over Output_Dir → list/get/analyze/generate-documentation; all citations verify
    - _Requirements: 5.1, 6.1, 8.1_
  - [ ] 22.4 `test_e2e_verify_detects_tampering`: collect → analyze → edit a spec value → verify exits 1 and prints `path:line: reason`
    - _Requirements: 8.3, 8.4_
  - [ ] 22.5 `test_e2e_partial_failure_exit_code`: one resource's primary call denied → exit 1, report lists the failure, other resources written
    - _Requirements: 12.2, 12.4, 12.5_
  - Commit: `test(e2e): end-to-end workflows for collect, IaC, MCP and verify (Task 22)`

- [ ] 23. Documentation and Demo
  - [ ] 23.1 `README.md`: prerequisites, install, every command with an example, MCP client config, troubleshooting, known limitations — _Req 11.1_
  - [ ] 23.2 `docs/ARCHITECTURE.md`: component + data-flow diagrams (Mermaid) — _Req 11.2_
  - [ ] 23.3 `docs/TESTING.md`: TDD workflow, markers, fixtures, how to add a resource type — _Req 11.1_
  - [ ] 23.4 `scripts/demo.py` (moto by default, `--live` optional) — _Req 11.3_
  - [ ] 23.5 `examples/output/` generated by the demo — _Req 11.5_
  - [ ] 23.6 `docs/ACCURACY_AND_SECURITY.md` (citation method, security measures, measured benchmark) and `docs/iam-policy.json` — _Req 9.4, 11.4_
  - [ ] 23.7 Rewrite `instruction.md` (Vietnamese user guide) to match the real CLI; remove obsolete `TASK_*_COMPLETED.md` notes
  - Commit: `docs: README, architecture, testing, accuracy/security docs and demo (Task 23)`

- [ ] 24. Final Integration and Polish
  - [ ] 24.1 Coverage: ≥ 80 % overall, 100 % for `src/parser.py` and `src/sanitizer.py`
  - [ ] 24.2 `bandit -r src -ll` clean; review credential handling
  - [ ] 24.3 Benchmark: mocked 1000-resource discovery+collection timing recorded in `docs/ACCURACY_AND_SECURITY.md` — _Req 1.5, 10.1, 10.2_
  - [ ] 24.4 `ruff check`, `black --check`, `mypy src` clean; CI workflow gates point at the real module files
  - Commit: `chore: final quality gates (Task 24)`

- [ ] 25. Final Checkpoint - Production Ready
  - Full suite green, CI configuration consistent, ask the user if questions arise.

## Notes

- TDD is mandatory: every sub-task marked (RED) is committed together with its (GREEN) implementation in the same top-level task commit, but the test must have been run and seen failing first.
- Property tests run ≥ 100 examples (hypothesis profile in `tests/conftest.py`).
- Integration tests use moto 4.x (`mock_s3`, `mock_ec2`, ...). No test may reach a real AWS account unless marked `@pytest.mark.aws` and run with `AWS_INVENTORY_LIVE_TESTS=1`.
- Every top-level task is committed and pushed when its tests pass.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["14"] },
    { "id": 1, "tasks": ["15", "16"] },
    { "id": 2, "tasks": ["17", "18"] },
    { "id": 3, "tasks": ["19"] },
    { "id": 4, "tasks": ["20"] },
    { "id": 5, "tasks": ["21"] },
    { "id": 6, "tasks": ["22"] },
    { "id": 7, "tasks": ["23"] },
    { "id": 8, "tasks": ["24", "25"] }
  ]
}
```
