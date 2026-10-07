# Requirements Document

## Introduction

AWS Resource Inventory là hệ thống tự động thu thập và phân tích AWS infrastructure resources. Hệ thống giải quyết bài toán inventory resources khi infrastructure engineer tiếp nhận hệ thống mà không có Infrastructure as Code (IaC), tài liệu hoặc diagram. Hệ thống bao gồm một CLI tool, MCP server để AI Agent tương tác an toàn với AWS, và khả năng phân tích tự động để tạo tài liệu hiểu được về infrastructure.

## Glossary

- **Resource_Inventory_System**: Hệ thống hoàn chỉnh bao gồm CLI tool, MCP server, và AI Agent integration
- **CLI_Tool**: Command-line interface tool để thu thập AWS resource specifications
- **MCP_Server**: Model Context Protocol server cung cấp interface an toàn cho AI Agent tương tác với AWS
- **AI_Agent**: LLM-based agent phân tích resource specifications và tạo tài liệu
- **Resource_Spec**: Thông tin cấu hình chi tiết của một AWS resource (EC2 instance type, S3 bucket policy, etc.)
- **Activity_Flow**: Luồng hoạt động và mối quan hệ giữa các resources trong infrastructure
- **IaC_Generator**: Component tạo Infrastructure as Code (Terraform) từ collected specifications
- **Diagram_Generator**: Component tạo visual diagrams sử dụng drawio-ai-kit
- **Resource_Parser**: Component parse và validate AWS API responses thành structured data
- **Spec_Collector**: Component thu thập tất cả specifications của một resource type
- **Analysis_Engine**: Component phân tích resource specs để hiểu activity flow
- **Output_Generator**: Component tạo tài liệu output (JSON, Markdown, diagram)

## Requirements

### Requirement 1: AWS Resource Discovery

**User Story:** As an infrastructure engineer, I want to automatically discover all AWS resources in an account, so that I can inventory the infrastructure without manual effort.

#### Acceptance Criteria

1. WHEN the CLI_Tool is invoked with AWS credentials, THE Resource_Inventory_System SHALL list all supported AWS resource types across all regions
2. FOR ALL discovered resources, THE Resource_Inventory_System SHALL collect the resource ARN, region, and basic metadata
3. THE Resource_Inventory_System SHALL support at minimum: EC2 instances, S3 buckets, Lambda functions, RDS instances, VPCs, Security Groups, IAM roles, CloudWatch log groups, Step Functions state machines, and DynamoDB tables
4. WHEN a region is inaccessible, THE Resource_Inventory_System SHALL log the error and continue with other regions
5. FOR ALL resource lists, the discovery SHALL complete within 5 minutes for accounts with up to 1000 resources

### Requirement 2: Resource Specification Collection

**User Story:** As an infrastructure engineer, I want to collect detailed specifications for each discovered resource, so that I have complete configuration information for analysis.

#### Acceptance Criteria

1. FOR ALL discovered resources, THE Spec_Collector SHALL retrieve all available configuration specifications using AWS CLI/SDK APIs
2. WHEN collecting S3 bucket specifications, THE Spec_Collector SHALL retrieve: bucket-acl, bucket-cors, bucket-encryption, bucket-lifecycle-configuration, bucket-policy, bucket-tagging, bucket-versioning, and bucket-website
3. WHEN collecting EC2 instance specifications, THE Spec_Collector SHALL retrieve: instance attributes, security groups, network interfaces, attached volumes, and tags
4. WHEN collecting Lambda function specifications, THE Spec_Collector SHALL retrieve: function configuration, environment variables, layers, VPC configuration, and execution role
5. IF an API call fails due to permissions, THE Spec_Collector SHALL log the missing permission and continue with available specs
6. FOR ALL collected specifications, THE Resource_Inventory_System SHALL preserve the raw API response for verification

### Requirement 3: Specification Persistence

**User Story:** As an infrastructure engineer, I want resource specifications saved to local files, so that I can verify accuracy and perform offline analysis.

#### Acceptance Criteria

1. FOR ALL collected specifications, THE Output_Generator SHALL save data in both JSON and Markdown formats
2. THE Output_Generator SHALL organize output files by resource type and region in a directory structure
3. WHEN saving JSON output, THE Output_Generator SHALL include timestamps, AWS account ID, region, and collection metadata
4. WHEN saving Markdown output, THE Output_Generator SHALL format specifications in human-readable tables and sections
5. FOR ALL output files, THE Output_Generator SHALL include checksums for data integrity verification
6. THE Resource_Inventory_System SHALL store all raw API responses in a separate directory for audit purposes

### Requirement 4: AWS API Response Parsing

**User Story:** As a developer, I want to parse AWS API responses into structured data, so that specifications can be analyzed programmatically.

#### Acceptance Criteria

1. WHEN an AWS API response is received, THE Resource_Parser SHALL parse it into a typed data structure
2. WHEN parsing fails due to malformed response, THE Resource_Parser SHALL return a descriptive error with the response excerpt
3. THE Resource_Spec_Printer SHALL format parsed specifications back into valid JSON matching AWS API format
4. FOR ALL valid parsed specifications, parsing then printing then parsing SHALL produce an equivalent data structure (round-trip property)
5. FOR ALL parsing errors, THE Resource_Parser SHALL preserve the original response for debugging

### Requirement 5: MCP Server for Safe AI Integration

**User Story:** As a system designer, I want an MCP server that provides controlled AWS access, so that AI Agents can analyze infrastructure safely without direct AWS credential access.

#### Acceptance Criteria

1. THE MCP_Server SHALL expose operations: list-resources, get-resource-spec, analyze-activity-flow, and generate-documentation
2. THE MCP_Server SHALL NOT expose AWS credentials or direct AWS API access to AI Agents
3. WHEN an AI_Agent requests resource specifications, THE MCP_Server SHALL retrieve cached local data instead of making new AWS API calls
4. IF cached data is not available, THE MCP_Server SHALL return an error indicating collection must be run first
5. THE MCP_Server SHALL validate all AI_Agent requests against a whitelist of permitted operations
6. WHEN the MCP_Server receives an unauthorized request, THE MCP_Server SHALL log the attempt and return an error
7. THE MCP_Server SHALL rate-limit AI_Agent requests to maximum 10 requests per second

### Requirement 6: Activity Flow Analysis

**User Story:** As an infrastructure engineer, I want AI-generated analysis of resource relationships and activity flows, so that I can quickly understand how the infrastructure works.

#### Acceptance Criteria

1. WHEN the Analysis_Engine processes collected specifications, THE Analysis_Engine SHALL identify relationships between resources (VPC connections, Lambda triggers, IAM role usage)
2. THE Analysis_Engine SHALL detect common patterns: API Gateway + Lambda + DynamoDB, EC2 + Load Balancer, S3 + CloudFront
3. WHEN generating activity flow documentation, THE Output_Generator SHALL describe the purpose and interaction of related resources
4. THE Diagram_Generator SHALL create visual diagrams showing resource relationships using drawio-ai-kit (https://github.com/sparklabx/drawio-ai-kit)
5. FOR ALL generated analysis, THE Output_Generator SHALL include confidence scores and cite specific resource specifications as evidence
6. THE Analysis_Engine SHALL flag suspicious patterns: overly permissive IAM policies, public S3 buckets, unrestricted security groups

### Requirement 7: Terraform IaC Generation

**User Story:** As an infrastructure engineer who received a project without IaC code, I want to generate Terraform configurations from collected specifications, so that I can manage the infrastructure as code going forward.

#### Acceptance Criteria

1. WHEN all resource specifications are collected, THE CLI_Tool SHALL provide an option to generate Terraform IaC code
2. WHEN generating Terraform code, THE IaC_Generator SHALL create .tf files organized by resource type and region
3. FOR ALL discovered resources, THE IaC_Generator SHALL generate corresponding Terraform resource blocks with all collected specifications
4. THE IaC_Generator SHALL generate terraform import commands for all existing resources
5. WHEN Terraform code generation completes, THE Resource_Inventory_System SHALL validate that running `terraform plan` shows zero changes (state matches AWS actual state)
6. THE IaC_Generator SHALL include a verification script that compares generated Terraform state with actual AWS resources
7. FOR ALL generated Terraform code, THE IaC_Generator SHALL include comments linking back to the original specification files for traceability

### Requirement 8: Accuracy and Hallucination Prevention

**User Story:** As a system architect, I want to prove the system's accuracy and prevent AI hallucinations, so that engineers can trust the generated documentation.

#### Acceptance Criteria

1. FOR ALL AI-generated statements about resources, THE Output_Generator SHALL include direct citations to specific resource specifications
2. THE Output_Generator SHALL include checksum references linking analysis statements to source data files
3. THE Resource_Inventory_System SHALL provide a verification command that validates all citations against actual specification files
4. WHEN verification detects mismatches, THE Resource_Inventory_System SHALL report the discrepancy with file paths and line numbers
5. THE AI_Agent SHALL NOT generate statements about resources that are not present in collected specifications
6. THE MCP_Server SHALL reject AI_Agent queries that would require assumptions or external knowledge beyond collected data

### Requirement 9: Security and Credential Management

**User Story:** As a security engineer, I want to ensure AWS credentials are handled securely, so that the system doesn't introduce security vulnerabilities.

#### Acceptance Criteria

1. THE CLI_Tool SHALL use standard AWS credential chain (environment variables, AWS CLI config, IAM roles)
2. THE CLI_Tool SHALL NOT log or persist AWS credentials to disk
3. THE CLI_Tool SHALL support AWS STS assume-role for cross-account access
4. WHEN collecting specifications, THE CLI_Tool SHALL use least-privilege read-only IAM permissions
5. THE Output_Generator SHALL sanitize sensitive data (secrets, passwords, private keys) from output files
6. THE Output_Generator SHALL replace detected sensitive values with placeholder text and log the sanitization
7. THE MCP_Server SHALL run in a sandboxed environment with no AWS credential access

### Requirement 10: Performance Measurement

**User Story:** As a project stakeholder, I want to measure time savings compared to manual inventory, so that I can demonstrate ROI.

#### Acceptance Criteria

1. THE CLI_Tool SHALL log start time, end time, and duration for each collection phase
2. THE CLI_Tool SHALL report metrics: total resources discovered, specifications collected, API calls made, and data volume
3. THE Output_Generator SHALL include a summary report comparing estimated manual effort versus automated collection time
4. THE Resource_Inventory_System SHALL calculate time savings using baseline: 5 minutes per resource for manual documentation
5. WHEN collection completes, THE CLI_Tool SHALL display percentage of time saved and total hours saved

### Requirement 11: Documentation and Demo

**User Story:** As a project reviewer, I want complete documentation and a working demo, so that I can evaluate the system's capabilities.

#### Acceptance Criteria

1. THE Resource_Inventory_System SHALL include a README with installation instructions, prerequisites, and usage examples
2. THE Resource_Inventory_System SHALL include architecture diagrams showing CLI, MCP Server, and AI Agent interaction
3. THE Resource_Inventory_System SHALL provide a demo script that runs against a sample AWS account
4. THE Resource_Inventory_System SHALL include documentation proving accuracy methodology, security measures, and performance benchmarks
5. THE Resource_Inventory_System SHALL provide example output files showing JSON, Markdown, and analysis reports

### Requirement 12: Error Handling and Resilience

**User Story:** As a developer, I want robust error handling, so that partial AWS API failures don't stop the entire collection process.

#### Acceptance Criteria

1. WHEN an AWS API call fails, THE CLI_Tool SHALL retry up to 3 times with exponential backoff
2. IF a retry fails, THE CLI_Tool SHALL log the error and continue with the next resource
3. WHEN rate limits are exceeded, THE CLI_Tool SHALL wait and retry according to AWS retry-after headers
4. THE CLI_Tool SHALL generate a collection report listing all successful and failed operations
5. WHEN collection completes with errors, THE CLI_Tool SHALL exit with a non-zero status code and summary of failures
