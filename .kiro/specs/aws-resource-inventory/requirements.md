# Requirements Document

## Introduction

AWS Resource Inventory là hệ thống tự động thu thập và phân tích AWS infrastructure resources. Hệ thống giải quyết bài toán inventory resources khi infrastructure engineer tiếp nhận hệ thống mà không có Infrastructure as Code (IaC), tài liệu hoặc diagram. Hệ thống bao gồm một CLI tool, MCP server để AI Agent tương tác an toàn với dữ liệu đã thu thập, và khả năng phân tích tự động (deterministic, có trích dẫn nguồn) để tạo tài liệu hiểu được về infrastructure.

### Scope decisions (binding)

- Runtime: Python 3.11+. Package import root is `src` (e.g. `from src.parser import ResourceSpec`).
- The system does **not** embed or call an LLM. All analysis statements are produced by the rule-based Analysis_Engine and carry citations. An external AI_Agent (e.g. Claude Desktop / Claude Code) consumes the data through the MCP_Server.
- The MCP_Server speaks the Model Context Protocol over stdio using the official `mcp` Python SDK.
- Diagrams are draw.io (`.drawio`, mxGraph XML) files using native `mxgraph.aws4.*` stencil styles (the same stencil catalog used by drawio-ai-kit). Validation with the drawio-ai-kit CLI (`drawio-ai validate`) is optional and only runs when that CLI is installed.
- Tests never touch a real AWS account, except tests marked `@pytest.mark.aws`, which are skipped unless `AWS_INVENTORY_LIVE_TESTS=1`.

## Glossary

- **Resource_Inventory_System**: The complete system: CLI_Tool, MCP_Server, and all components below.
- **CLI_Tool**: The `aws-inventory` command-line program (`src/cli.py`).
- **MCP_Server**: Model Context Protocol server (`src/mcp_server.py` core + `src/mcp_stdio.py` transport) that serves cached data to AI agents.
- **AI_Agent**: An external LLM-based client connected to the MCP_Server. It is outside the system boundary.
- **Supported_Resource_Type**: One of the ten resource types in the table below, identified by its canonical type id (the Terraform AWS provider resource type name).
- **Resource_Spec**: A `ResourceSpec` record: `resource_type`, `arn`, `region`, `account_id`, `specifications`, `metadata`, `raw_response`.
- **Specifications**: The `specifications` field of a Resource_Spec. Its exact shape per type is defined in design.md §"Specification schema" (AWS API field names, `ResponseMetadata` removed).
- **Spec_Checksum**: SHA-256 hex digest of the canonical JSON (sorted keys, `separators=(",", ":")`, UTF-8) of the sanitized Specifications. Stored in `metadata.checksum`.
- **Output_Dir**: The directory a collection run writes to (default `./output`). Its layout is defined in design.md §"Output directory layout".
- **Citation**: A reference `{resource_arn, spec_file, property_path, source_checksum, evidence_value}` linking an analysis statement to a value inside a spec file.
- **Activity_Flow**: Relationships and interactions between resources (e.g. Lambda → DynamoDB, EC2 → VPC).
- **Resource_Parser / Resource_Spec_Printer**: `ResourceParser.parse_spec()` / `ResourceParser.print_spec()` in `src/parser.py`.
- **Spec_Collector**: `src/collector.py`, collects Specifications for discovered resources.
- **Analysis_Engine**: `src/analysis_engine.py`, rule-based relationship, pattern and security analysis.
- **Diagram_Generator**: `src/diagram_generator.py`, produces `.drawio` diagrams.
- **IaC_Generator**: `src/iac_generator.py`, produces Terraform code.
- **Output_Generator**: `src/output_generator.py`, writes JSON/Markdown/raw/checksum files.
- **Data_Sanitizer**: `src/sanitizer.py`, redacts sensitive values.

### Supported resource types

| Canonical type id | AWS service | Scope | Discovered by | Resource id |
|---|---|---|---|---|
| `aws_instance` | EC2 | regional | `ec2:DescribeInstances` | InstanceId |
| `aws_vpc` | EC2 | regional | `ec2:DescribeVpcs` | VpcId |
| `aws_security_group` | EC2 | regional | `ec2:DescribeSecurityGroups` | GroupId |
| `aws_lambda_function` | Lambda | regional | `lambda:ListFunctions` | FunctionName |
| `aws_db_instance` | RDS | regional | `rds:DescribeDBInstances` | DBInstanceIdentifier |
| `aws_cloudwatch_log_group` | CloudWatch Logs | regional | `logs:DescribeLogGroups` | logGroupName |
| `aws_sfn_state_machine` | Step Functions | regional | `states:ListStateMachines` | state machine name |
| `aws_dynamodb_table` | DynamoDB | regional | `dynamodb:ListTables` | TableName |
| `aws_s3_bucket` | S3 | global (`region = "global"`) | `s3:ListBuckets` | bucket name |
| `aws_iam_role` | IAM | global (`region = "global"`) | `iam:ListRoles` | RoleName |

Aliases accepted on input (CLI filters, MCP parameters) and normalized to the canonical id: `aws_ec2_instance`, `ec2`, `ec2_instance` → `aws_instance`; `aws_rds_instance`, `rds` → `aws_db_instance`; `aws_step_function`, `stepfunctions` → `aws_sfn_state_machine`; `lambda`, `lambda_function` → `aws_lambda_function`; `s3`, `s3_bucket` → `aws_s3_bucket`; `iam_role` → `aws_iam_role`; `dynamodb` → `aws_dynamodb_table`; `vpc` → `aws_vpc`; `security_group` → `aws_security_group`; `log_group` → `aws_cloudwatch_log_group`.

## Requirements

### Requirement 1: AWS Resource Discovery

**User Story:** As an infrastructure engineer, I want to automatically discover all AWS resources in an account, so that I can inventory the infrastructure without manual effort.

#### Acceptance Criteria

1. WHEN the CLI_Tool runs discovery without `--region`, THE Resource_Inventory_System SHALL scan every region returned by `ec2:DescribeRegions(AllRegions=False)` (regions enabled for the account). WHEN one or more `--region` options are given, it SHALL scan exactly those regions.
2. FOR ALL discovered resources, THE Resource_Inventory_System SHALL record `resource_type` (canonical id), `resource_id`, `arn`, `region` (`"global"` for S3 and IAM), and `tags` when the list API returns them.
3. THE Resource_Inventory_System SHALL discover all ten Supported_Resource_Types. Regional types are discovered once per scanned region; global types are discovered exactly once per run using the `us-east-1` endpoint.
4. WHEN a list/describe call for a region or resource type fails, THE Resource_Inventory_System SHALL record a discovery error `{region, resource_type, message}`, continue with the remaining types and regions, and include the error in the collection report.
5. WHEN AWS API latency is ≤ 100 ms per call, discovery of an account with up to 1000 resources across up to 17 regions SHALL complete in under 5 minutes (regions are scanned concurrently, default 10 workers). List calls SHALL follow pagination so no resources are dropped.

### Requirement 2: Resource Specification Collection

**User Story:** As an infrastructure engineer, I want to collect detailed specifications for each discovered resource, so that I have complete configuration information for analysis.

#### Acceptance Criteria

1. FOR ALL discovered resources, THE Spec_Collector SHALL produce one Resource_Spec whose Specifications follow the per-type schema in design.md, using only read-only API calls (`Describe*`, `List*`, `Get*`).
2. WHEN collecting `aws_s3_bucket`, THE Spec_Collector SHALL call GetBucketAcl, GetBucketCors, GetBucketEncryption, GetBucketLifecycleConfiguration, GetBucketPolicy, GetBucketTagging, GetBucketVersioning and GetBucketWebsite and store each response under the keys `bucket-acl`, `bucket-cors`, `bucket-encryption`, `bucket-lifecycle-configuration`, `bucket-policy`, `bucket-tagging`, `bucket-versioning`, `bucket-website`. WHEN AWS reports that a sub-configuration does not exist (e.g. `NoSuchCORSConfiguration`, `NoSuchBucketPolicy`, `NoSuchTagSet`, `NoSuchWebsiteConfiguration`, `NoSuchLifecycleConfiguration`, `ServerSideEncryptionConfigurationNotFoundError`), the key SHALL be omitted and this SHALL NOT count as an error.
3. WHEN collecting `aws_instance`, THE Spec_Collector SHALL store the instance object from DescribeInstances, which includes instance attributes, `SecurityGroups`, `NetworkInterfaces`, `BlockDeviceMappings` (attached volumes) and `Tags`.
4. WHEN collecting `aws_lambda_function`, THE Spec_Collector SHALL store the `Configuration` object from GetFunction (function configuration, `Environment.Variables`, `Layers`, `VpcConfig`, `Role`) plus the function `Tags`.
5. IF an API call fails with an access-denied error (`AccessDenied`, `AccessDeniedException`, `UnauthorizedOperation`, `AuthorizationError`), THE Spec_Collector SHALL NOT retry it, SHALL log a message naming the missing IAM permission in `service:Action` form (e.g. `s3:GetBucketPolicy`), and SHALL continue with the remaining calls for that resource.
6. FOR ALL successful API calls, THE Spec_Collector SHALL keep the complete API response (including `ResponseMetadata`) in `raw_response`, keyed by API operation name when a resource needs more than one call.

### Requirement 3: Specification Persistence

**User Story:** As an infrastructure engineer, I want resource specifications saved to local files, so that I can verify accuracy and perform offline analysis.

#### Acceptance Criteria

1. FOR ALL collected Resource_Specs, THE Output_Generator SHALL write one JSON file and one Markdown file, plus the aggregate files `resources.json` and `resources.md`.
2. THE Output_Generator SHALL write per-resource files to `<Output_Dir>/<canonical_type>/<region>/<file_id>.{json,md}`, where `file_id` is the resource id with every character outside `[A-Za-z0-9_.-]` replaced by `_` and leading/trailing `_` stripped.
3. WHEN saving JSON output, THE Output_Generator SHALL include `generated_at` (UTC ISO-8601), `account_id`, `region`, `arn`, `resource_type`, and `metadata` (`collected_at`, `collector_version`, `api_version`, `checksum`).
4. WHEN saving Markdown output, THE Output_Generator SHALL render an "Overview" table (type, ARN, region, account, collection time), a table of scalar configuration values, a tags table when tags exist, and one section per nested configuration value.
5. THE Output_Generator SHALL write `checksums.sha256` (format `<sha256>  <relative/path>`, compatible with `shasum -a 256 -c`) and `checksums.json` covering every file in Output_Dir except the two checksum files, and SHALL set `metadata.checksum` of every Resource_Spec to its Spec_Checksum.
6. THE Output_Generator SHALL write raw API responses to `<Output_Dir>/raw_responses/<canonical_type>/<region>/<file_id>_raw.json`, sanitized with the same Data_Sanitizer rules as other outputs (structure preserved, sensitive values replaced).

### Requirement 4: AWS API Response Parsing

**User Story:** As a developer, I want to parse AWS API responses into structured data, so that specifications can be analyzed programmatically.

#### Acceptance Criteria

1. WHEN the Resource_Parser receives a JSON document, THE Resource_Parser SHALL return `Result.ok(ResourceSpec)` if the document contains the required fields `resource_type`, `arn`, `region`, `account_id` (strings), `specifications` (object) and `metadata` (object).
2. WHEN parsing fails (invalid JSON, missing field, wrong type), THE Resource_Parser SHALL return `Result.err(ParseError)` whose message names the problem and includes an excerpt of up to 40 characters on each side of the error position.
3. THE Resource_Spec_Printer SHALL serialize a ResourceSpec to JSON containing exactly the fields listed in 4.1 plus `raw_response` when it is not null.
4. FOR ALL valid ResourceSpecs, `parse(print(spec))` SHALL equal `spec` (round-trip property, ≥100 generated examples).
5. FOR ALL parsing errors, THE ParseError SHALL keep the complete original input in `original_response`.

### Requirement 5: MCP Server for Safe AI Integration

**User Story:** As a system designer, I want an MCP server that provides controlled access to collected data, so that AI Agents can analyze infrastructure safely without AWS credential access.

#### Acceptance Criteria

1. THE MCP_Server SHALL expose exactly four MCP tools: `list-resources`, `get-resource-spec`, `analyze-activity-flow`, `generate-documentation`, with the parameters defined in design.md §"MCP Server". It SHALL be started with `aws-inventory mcp-serve --cache-dir <Output_Dir>` and communicate over stdio.
2. THE MCP_Server SHALL NOT return AWS credentials: every response SHALL pass through the Data_Sanitizer before it is returned, and the MCP_Server code SHALL NOT import `boto3` or `botocore`.
3. THE MCP_Server SHALL answer every request only from files in the cache directory; it SHALL NOT make AWS API calls.
4. IF the cache directory has no spec files, or a requested ARN is not in the cache, THE MCP_Server SHALL return `{"status": "error", "message": ...}` where the message says the resource is not in the collected data and that `aws-inventory collect` must be run.
5. THE MCP_Server SHALL reject any operation not in the four-tool whitelist, and any request whose parameters are not in that tool's parameter list or have the wrong type.
6. WHEN the MCP_Server rejects a request under 5.5, THE MCP_Server SHALL append a security log entry `{timestamp, operation, reason}` (available via `get_security_logs()` and Python logging at WARNING level) and return `{"status": "error", "message": "Unauthorized ..."}` for unknown operations or `{"status": "error", "message": "Invalid parameters ..."}` for bad parameters.
7. THE MCP_Server SHALL accept at most 10 requests in any sliding 1-second window. Further requests within that window SHALL return `{"status": "rate_limited", "message": "Rate limit exceeded: max 10 requests per second"}`; rejected requests do not count toward the limit.

### Requirement 6: Activity Flow Analysis

**User Story:** As an infrastructure engineer, I want automated analysis of resource relationships and activity flows, so that I can quickly understand how the infrastructure works.

#### Acceptance Criteria

1. WHEN the Analysis_Engine processes Resource_Specs, THE Analysis_Engine SHALL identify these relationships when both endpoints are present in the collected data: `vpc_connection` (resource → VPC by VpcId), `iam_role_usage` (Lambda `Role`, EC2 `IamInstanceProfile`, Step Functions `roleArn` → IAM role), `security_group` (EC2/Lambda/RDS → security group by GroupId), `dynamodb_access` (Lambda environment variable value equal to, or containing, a collected table name or ARN), `log_group` (Lambda → `/aws/lambda/<FunctionName>` log group).
2. THE Analysis_Engine SHALL detect the patterns "Serverless Application" (Lambda with an `iam_role_usage` and/or `dynamodb_access` relationship) and "Compute in VPC" (EC2 instance with a `vpc_connection`). The patterns "API Gateway + Lambda + DynamoDB", "EC2 + Load Balancer" and "S3 + CloudFront" involve services that are not Supported_Resource_Types; THE Analysis_Engine SHALL list them in `undetectable_patterns` with that reason and SHALL NOT make statements about them.
3. WHEN `aws-inventory generate-docs` runs, THE Output_Generator SHALL write `<Output_Dir>/docs/infrastructure.md` that, for each detected pattern and each relationship, states which resources interact and how, and attaches the Citations that support the statement.
4. THE Diagram_Generator SHALL write `<Output_Dir>/diagrams/architecture.drawio`: valid mxGraph XML with root `<mxfile>`, one vertex per Resource_Spec (a `UserObject` whose `arn` and `tooltip` attributes are the ARN), one edge per identified relationship, and AWS stencil styles `mxgraph.aws4.*` for each Supported_Resource_Type.
5. FOR ALL patterns and findings, THE Analysis_Engine SHALL include a confidence score in [0.0, 1.0] and at least one Citation. Confidence is rule-defined: 1.0 for direct ID references, 0.95 for ARN/name matches of roles, 0.9 for security group attachments, 0.85 for environment-variable substring matches; a pattern's confidence is the minimum of its supporting relationships' confidences.
6. THE Analysis_Engine SHALL flag: `OVERLY_PERMISSIVE_IAM_POLICY` (CRITICAL) when an IAM role's inline policy has a statement with `Effect: Allow`, `Action` containing `*`, and `Resource` containing `*`, or the role has the managed policy `arn:aws:iam::aws:policy/AdministratorAccess` attached; `PUBLIC_S3_BUCKET` (HIGH) when a bucket ACL grants to the `AllUsers` or `AuthenticatedUsers` group, or the bucket policy has an `Allow` statement with `Principal` `"*"` or `{"AWS": "*"}`; `UNRESTRICTED_SECURITY_GROUP_ACCESS` (HIGH) when an ingress rule allows `0.0.0.0/0` or `::/0`.

### Requirement 7: Terraform IaC Generation

**User Story:** As an infrastructure engineer who received a project without IaC code, I want to generate Terraform configurations from collected specifications, so that I can manage the infrastructure as code going forward.

#### Acceptance Criteria

1. THE CLI_Tool SHALL provide the command `aws-inventory generate-iac --output-dir <Output_Dir> [--terraform-dir <dir>]` that reads only the cached spec files (default target `<Output_Dir>/terraform`).
2. THE IaC_Generator SHALL write `<terraform-dir>/<region>/<canonical_type>.tf` for each (region, type) pair present (`global` for S3 and IAM), a `versions.tf` in each region directory, and in the root `providers.tf` (default `us-east-1` provider plus one aliased provider per region), `main.tf` (one `module "<region with - replaced by _>"` per region directory, passing that region's provider), `import.sh` and `verify_state.sh`. Running `terraform validate` in the root SHALL succeed.
3. FOR ALL Resource_Specs, THE IaC_Generator SHALL emit a resource block (plus companion resources for S3 and IAM) whose arguments are mapped from the Specifications (mapping table in design.md). Above the block it SHALL list the consumed top-level keys in one `# mapped: <k1>, <k2>, ...` comment and each remaining key in its own `# unmapped: <key>` comment, so every collected key appears in the generated file.
4. THE IaC_Generator SHALL write `import.sh` containing one `terraform import module.<region module>.<type>.<name> <import-id>` command per generated resource block (including S3/IAM companion resources), skipped when the address is already in state, using the import ID format documented by the Terraform AWS provider for that type.
5. WHEN `verify_state.sh` (or `IaCGenerator.verify_terraform_plan()`) runs after the imports, it SHALL run `terraform plan -detailed-exitcode` and report success only for exit code 0 (no changes). Exit code 2 SHALL be reported as "changes detected" with the plan output; any other code as an error. The zero-change outcome is verified by the live test `test_live_iac_terraform_plan_zero_changes_req_7_5` (`@pytest.mark.aws`); known unavoidable differences (values redacted by the sanitizer, Lambda code packages, RDS master password) are covered by `lifecycle { ignore_changes = [...] }` and listed in design.md.
6. THE IaC_Generator SHALL write `verify_state.sh`, which initializes Terraform if needed, runs the plan in 7.5, and exits 0 / 2 / 1 for no changes / changes / error.
7. FOR ALL generated resource blocks, THE IaC_Generator SHALL precede the block with comments giving the source spec file path (relative to Output_Dir), the ARN and the region.

### Requirement 8: Accuracy and Hallucination Prevention

**User Story:** As a system architect, I want to prove the system's accuracy and prevent unsupported statements, so that engineers can trust the generated documentation.

#### Acceptance Criteria

1. FOR ALL statements in `analysis/analysis.json`, `analysis/analysis.md` and `docs/infrastructure.md`, THE Output_Generator SHALL include at least one Citation.
2. EACH Citation SHALL contain the Spec_Checksum of the cited spec file (`source_checksum`) and the file path relative to Output_Dir (`spec_file`).
3. THE CLI_Tool SHALL provide `aws-inventory verify --output-dir <Output_Dir>` that (a) recomputes every file hash listed in `checksums.sha256` and (b) for every Citation in `analysis/analysis.json` checks that `spec_file` exists, its Spec_Checksum equals `source_checksum`, `property_path` resolves inside the file, and the resolved value equals `evidence_value`.
4. WHEN verification finds a mismatch, THE CLI_Tool SHALL print one line per discrepancy containing the file path, the 1-based line number in the pretty-printed JSON file where the cited property starts (or `0` if the property no longer exists), and the reason, and SHALL exit with code 1.
5. THE Analysis_Engine SHALL only produce statements derived from values present in the collected Specifications; every relationship, pattern and finding SHALL be traceable to a Citation that `verify` can resolve.
6. THE MCP_Server SHALL reject `get-resource-spec` and `analyze-activity-flow` requests that reference an ARN not present in the cache (see 5.4), so that an AI_Agent cannot obtain answers about resources outside the collected data.

### Requirement 9: Security and Credential Management

**User Story:** As a security engineer, I want to ensure AWS credentials are handled securely, so that the system doesn't introduce security vulnerabilities.

#### Acceptance Criteria

1. THE CLI_Tool SHALL obtain credentials only through the boto3 default credential chain (environment variables, shared config/credentials files, SSO, container/instance roles), optionally selecting a profile with `--profile`.
2. THE CLI_Tool SHALL NOT write credentials to any file or log. All log handlers installed by the CLI_Tool SHALL pass messages through the Data_Sanitizer, and no credential value from the active session SHALL appear in stdout, stderr, log files or Output_Dir.
3. WHEN `--role-arn` is given (with optional `--external-id`), THE CLI_Tool SHALL call `sts:AssumeRole` with session name `aws-resource-inventory` and use the temporary credentials for all subsequent calls.
4. THE CLI_Tool SHALL only invoke AWS API operations whose names start with `Describe`, `List` or `Get`, plus `sts:AssumeRole` and `sts:GetCallerIdentity`. The minimal IAM policy SHALL be published in `docs/iam-policy.json`.
5. THE Data_Sanitizer SHALL redact (a) any string value containing an AWS access key ID (`AKIA` or `ASIA` followed by 16 uppercase letters/digits), (b) any string value containing a PEM private key header (`-----BEGIN ... PRIVATE KEY-----`), and (c) the string value of any key whose name contains, case-insensitively, `password`, `passwd`, `secret`, `private_key`, `token`, `api_key`, `access_key_id` or `credential` (keys containing `public` are exempt). Key-name redaction applies only to string values; dicts and lists are traversed, so keys, list lengths and nesting are always preserved. Key names such as `KeyName`, `KmsKeyId` or `KeyType` SHALL NOT be redacted.
6. THE Data_Sanitizer SHALL replace each redacted value with one of the placeholders `[REDACTED_AWS_KEY]` (key IDs and keys containing `access_key_id`), `[REDACTED_AWS_SECRET]` (keys containing `secret_access_key`), `[REDACTED_PRIVATE_KEY]`, or `[REDACTED]` (all other cases), and record a log entry containing the JSON path and placeholder but never the original value. Sanitizing already-sanitized data SHALL return identical data (idempotence).
7. THE `mcp-serve` command SHALL remove all `AWS_*` environment variables and set `AWS_SHARED_CREDENTIALS_FILE` and `AWS_CONFIG_FILE` to a non-existent path before serving, so the MCP_Server process has no AWS credential access.

### Requirement 10: Performance Measurement

**User Story:** As a project stakeholder, I want to measure time savings compared to manual inventory, so that I can demonstrate ROI.

#### Acceptance Criteria

1. THE CLI_Tool SHALL record start time, end time and duration (seconds) for the phases `discovery`, `collection` and `output`.
2. THE CLI_Tool SHALL report `resources_discovered`, `specs_collected`, `specs_failed`, `api_calls` (every AWS API call attempted, including retries) and `data_volume_bytes` (total size of files written to Output_Dir).
3. THE Output_Generator SHALL write `summary_report.md` comparing estimated manual effort with automated collection time.
4. THE Resource_Inventory_System SHALL compute `manual_hours = resources_discovered × 5 / 60`, `automated_hours = total_duration_seconds / 3600`, `hours_saved = max(0, manual_hours − automated_hours)` and `percent_saved = hours_saved / manual_hours × 100` (0 when no resources).
5. WHEN `aws-inventory collect` completes, THE CLI_Tool SHALL print `percent_saved` and `hours_saved`.

### Requirement 11: Documentation and Demo

**User Story:** As a project reviewer, I want complete documentation and a working demo, so that I can evaluate the system's capabilities.

#### Acceptance Criteria

1. THE repository SHALL include `README.md` with prerequisites, installation, every CLI command with an example, MCP client configuration, and troubleshooting.
2. THE repository SHALL include `docs/ARCHITECTURE.md` with a diagram of CLI, MCP_Server and AI_Agent interaction and the data flow from AWS to Output_Dir.
3. THE repository SHALL include `scripts/demo.py`, which by default creates sample resources in a moto-mocked AWS account and runs collect → analyze → generate-iac → generate-docs → verify; with `--live` it runs against the account of the current credential chain.
4. THE repository SHALL include `docs/ACCURACY_AND_SECURITY.md` describing the citation/verification method, the security measures in Requirement 9, and a performance benchmark (measured discovery+collection time for a mocked 1000-resource account).
5. THE repository SHALL include `examples/output/`, the Output_Dir produced by `scripts/demo.py`, containing JSON, Markdown, analysis, diagram and Terraform files.

### Requirement 12: Error Handling and Resilience

**User Story:** As a developer, I want robust error handling, so that partial AWS API failures don't stop the entire collection process.

#### Acceptance Criteria

1. WHEN an AWS API call fails with a transient error (throttling, 5xx, connection/timeout), THE CLI_Tool SHALL make at most 3 attempts in total (1 initial + up to 2 retries), waiting 1 s then 2 s (base 1 s, multiplier 2). botocore's own retries SHALL be disabled (`total_max_attempts=1`) so this is the only retry layer.
2. IF all attempts fail, THE CLI_Tool SHALL record a collection error `{resource_arn, operation, error_type, error_message, timestamp, retry_count}` and continue with the next resource.
3. WHEN a throttling error carries a `Retry-After` HTTP header, THE CLI_Tool SHALL wait that many seconds before the next attempt instead of the backoff delay.
4. THE CLI_Tool SHALL write `<Output_Dir>/collection_report.json` listing every attempted operation with status `success` or `failed`, the discovery and collection errors, the phase timings and metrics of Requirement 10.
5. WHEN a run completes with at least one discovery or collection error, THE CLI_Tool SHALL print a failure summary and exit with code 1. Exit code 0 means no errors; exit code 2 means the run could not start (invalid arguments, no credentials, assume-role failure).
