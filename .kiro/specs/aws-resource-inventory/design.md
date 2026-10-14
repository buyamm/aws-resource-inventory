# Design Document: AWS Resource Inventory

## Overview

AWS Resource Inventory discovers, collects, persists and analyzes AWS resources of an account that has no IaC or documentation. A CLI collects data with read-only AWS calls into a local **Output_Dir**. All later steps (analysis, diagram, Terraform, documentation, verification, MCP serving) are **offline** and read only from Output_Dir.

Binding scope decisions are listed in requirements.md §"Scope decisions". In short: Python 3.11+, no embedded LLM, MCP over stdio with the official `mcp` SDK, draw.io output with `mxgraph.aws4.*` stencils, moto-mocked tests only (live tests opt-in).

### Core Design Principles

1. **Test-first development**: every behavior is introduced by a failing test (Red → Green → Refactor).
2. **Online/offline split**: only `discover` and `collect` talk to AWS. Everything else consumes Output_Dir, which makes results reproducible and auditable.
3. **Single source of truth per concept**: resource types (`src/resource_types.py`), checksums and citations (`src/integrity.py`), sanitization (`src/sanitizer.py`).
4. **Verifiable accuracy**: every analysis statement carries a Citation that `aws-inventory verify` can check mechanically.
5. **Defense in depth for secrets**: sanitize before writing anything, sanitize every MCP response, sanitize every log record.

### System Components

```
                      ONLINE (AWS credentials)                         OFFLINE (Output_Dir only)
┌──────────────────────────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│ CLI: aws-inventory collect                                │   │ CLI: analyze / generate-iac /            │
│                                                           │   │      generate-docs / verify              │
│  ResourceDiscovery ──▶ InventoryCollector ──▶ seal_specs ─┼──▶│  AnalysisEngine ─▶ DiagramGenerator      │
│  (src/discovery.py)    (src/inventory.py)    (integrity)  │   │  IaCGenerator   ─▶ terraform/            │
│                         └─ SpecCollector                  │   │  DocumentationGenerator ─▶ docs/         │
│                            (src/collector.py)             │   │  verify_output_dir (integrity)           │
│                                    │                      │   └──────────────────────────────────────────┘
│                                    ▼                      │   ┌──────────────────────────────────────────┐
│                           OutputGenerator ───────────────┼──▶│ MCP: aws-inventory mcp-serve (stdio)     │
│                           (src/output_generator.py)       │   │  mcp_stdio (FastMCP tools)               │
└──────────────────────────────────────────────────────────┘   │   └─▶ MCPServer core (whitelist, params,  │
                                                                │       rate limit, sanitize, cache only)  │
                                                                └───────────────────▲──────────────────────┘
                                                                                    │ MCP tool calls
                                                                         External AI_Agent (Claude, ...)
```

### Module map

| Module | Responsibility |
|---|---|
| `src/resource_types.py` | Registry of the 10 Supported_Resource_Types: canonical id, aliases, service, scope, id extraction, file id, Terraform type, import id, draw.io style. |
| `src/parser.py` | `ResourceSpec`, `SpecMetadata`, `Result`, `ParseError`, `ResourceParser` (parse/print JSON). |
| `src/sanitizer.py` | `DataSanitizer`: structure-preserving redaction with a redaction log. |
| `src/discovery.py` | `ResourceDiscovery`: concurrent per-region listing with pagination; `DiscoveredResource`, `DiscoveryError`. |
| `src/collector.py` | `SpecCollector`: per-type spec collection for one boto3 client, retry/backoff, error classification, API call counting. |
| `src/inventory.py` | `InventoryCollector`: turns `DiscoveredResource`s into `ResourceSpec`s (one SpecCollector per service+region), `CollectionError`, `CollectionResult`. |
| `src/integrity.py` | Canonical JSON, Spec_Checksum, `seal_specs()`, citation path resolution, `verify_output_dir()`. |
| `src/output_generator.py` | JSON/Markdown/raw/checksum/summary files, `load_specs()` from Output_Dir. |
| `src/analysis_engine.py` | Relationship rules (single source), patterns, security findings, citations, `AnalysisReport` (+ JSON serialization, `analysis.md`). |
| `src/diagram_generator.py` | `.drawio` generation from specs + relationships; optional `drawio-ai validate`. |
| `src/iac_generator.py` | Terraform generation per type mapping, `import.sh`, `verify_state.sh`, `verify_terraform_plan()`. |
| `src/documentation.py` | `docs/infrastructure.md` from an `AnalysisReport` (every statement cited). |
| `src/metrics.py` | Phase timer, run metrics, time-savings computation, `collection_report.json`. |
| `src/aws_session.py` | boto3 session creation (profile, assume-role, botocore retry config), account id lookup. |
| `src/mcp_server.py` | `MCPServer` core (no boto3 import). |
| `src/mcp_stdio.py` | FastMCP stdio adapter + environment sandboxing. |
| `src/cli.py` | Click CLI `aws-inventory`, logging setup with sanitizing filter, exit codes. |

## Development Methodology: Test-Driven Development

1. **RED**: write a failing test that encodes one acceptance criterion; run it and see it fail.
2. **GREEN**: write the minimal code that makes it pass.
3. **REFACTOR**: improve structure with all tests green.
4. **REPEAT**.

### Test organization and naming

```
tests/
├── conftest.py            # fake AWS creds, hypothesis profile (100 examples), live-test skipping
├── unit/                  # one file per src module, no AWS (mocks only)
├── integration/           # moto-backed AWS tests, MCP server tests
├── e2e/                   # full CLI workflows via click.testing.CliRunner + moto
└── fixtures/              # sample AWS responses and sample specs
```

- Property tests: `test_property_<description>_req_<X>_<Y>`
- Unit tests: `test_<component>_<scenario>_req_<X>_<Y>` (requirement suffix whenever a criterion is covered)
- Integration tests: `test_integration_<component>_<operation>_req_<X>_<Y>` or `test_<component>_..._req_<X>_<Y>`
- E2E tests: `test_e2e_<workflow>_<scenario>`
- Live tests: `test_live_<...>`, marked `@pytest.mark.aws`

Markers (pytest.ini, `--strict-markers`): `unit`, `integration`, `e2e`, `property`, `slow`, `aws`.

### Coverage and quality gates (CI: `.github/workflows/tdd-pipeline.yml`)

- Line coverage ≥ 80 % for `src/` across unit+integration+e2e.
- 100 % line coverage for `src/parser.py` and `src/sanitizer.py`.
- Property tests run ≥ 100 examples (hypothesis profile `default` registered in `tests/conftest.py`).
- `ruff check src tests`, `black --check src tests`, `mypy src` and `bandit -r src -ll` pass.

## Data Models

Implemented in `src/parser.py` (unchanged contract):

```python
@dataclass
class SpecMetadata:
    collected_at: str        # UTC ISO-8601, e.g. "2026-10-14T08:00:00Z"
    collector_version: str   # src.__version__
    api_version: str         # botocore service API version of the primary call, "" if unknown
    checksum: str            # Spec_Checksum, "" until sealed

@dataclass
class ResourceSpec:
    resource_type: str       # canonical type id (see registry)
    arn: str
    region: str              # AWS region or "global"
    account_id: str          # 12-digit account id
    specifications: dict     # per-type schema below
    metadata: SpecMetadata
    raw_response: Any = None # dict of full API responses (incl. ResponseMetadata)

class Result(Generic[T, E]):  # Result.ok(v) / Result.err(e), .is_ok(), .is_err(), .value, .error
```

Other models:

```python
@dataclass
class DiscoveredResource:            # src/discovery.py
    resource_type: str; resource_id: str; arn: str; region: str; tags: dict[str, str]

@dataclass
class DiscoveryError:                # src/discovery.py
    region: str; resource_type: str; message: str

@dataclass
class CollectionError:               # src/inventory.py (Req 12.2); one per DENIED or FAILED operation
    resource_arn: str; operation: str; error_type: str; error_message: str
    timestamp: str; retry_count: int

class CallStatus(str, Enum):         # src/collector.py
    SUCCESS = "success"; NOT_CONFIGURED = "not_configured"; DENIED = "denied"; FAILED = "failed"

@dataclass
class OperationRecord:               # src/collector.py (Req 12.4)
    resource_arn: str; operation: str; status: CallStatus; attempts: int
    error_type: str = ""; detail: str = ""; timestamp: str = ""

@dataclass
class CollectionResult:
    specs: list[ResourceSpec]; errors: list[CollectionError]
    operations: list[OperationRecord]; api_calls: int

@dataclass
class ResourceRelationship:          # src/analysis_engine.py (re-exported by diagram_generator)
    from_arn: str; to_arn: str; relationship_type: str; confidence: float
    citations: list[Citation]

@dataclass
class Citation:                      # src/analysis_engine.py (Req 8.2)
    resource_arn: str; spec_file: str; property_path: str
    source_checksum: str; evidence_value: Any
```

## Resource type registry (`src/resource_types.py`)

`ResourceTypeInfo(type_id, service, scope, terraform_type, aliases, drawio_style)` for each Supported_Resource_Type. Functions:

- `canonical_type(name: str) -> str | None`: case-insensitive lookup of canonical ids and aliases (alias list in requirements.md).
- `resource_id(spec: ResourceSpec) -> str`: the id from the "Resource id" column of requirements.md, read from Specifications, falling back to the last ARN segment (after the last `/` or `:`).
- `file_id(resource_id: str) -> str`: `re.sub(r"[^A-Za-z0-9_.-]", "_", id).strip("_") or "resource"`.
- `spec_relpath(spec) -> str`: `f"{resource_type}/{region}/{file_id}.json"` (posix, relative to Output_Dir).

Every module that needs a type name, file name or id uses these functions; no module hard-codes alternative type names.

## Specification schema (per type)

`specifications` holds the AWS API object(s) **with AWS field names unchanged** and `ResponseMetadata` removed. `raw_response` holds `{<OperationName>: <full response>}` for every successful call.

| Type | API calls (client region) | `specifications` content |
|---|---|---|
| `aws_instance` | `ec2.describe_instances(InstanceIds=[id])` | the `Instances[0]` object |
| `aws_vpc` | `ec2.describe_vpcs(VpcIds=[id])`, `ec2.describe_vpc_attribute(Attribute=enableDnsSupport / enableDnsHostnames)` | `Vpcs[0]` + `EnableDnsSupport: bool`, `EnableDnsHostnames: bool` |
| `aws_security_group` | `ec2.describe_security_groups(GroupIds=[id])` | `SecurityGroups[0]` |
| `aws_lambda_function` | `lambda.get_function(FunctionName=id)` | `Configuration` object + `Tags` (dict, from the same response) |
| `aws_db_instance` | `rds.describe_db_instances(DBInstanceIdentifier=id)` | `DBInstances[0]` |
| `aws_cloudwatch_log_group` | `logs.describe_log_groups(logGroupNamePrefix=id)`, `logs.list_tags_log_group(logGroupName=id)` | the log group whose `logGroupName == id` + `tags` |
| `aws_sfn_state_machine` | `stepfunctions.describe_state_machine(stateMachineArn=arn)`, `stepfunctions.list_tags_for_resource(resourceArn=arn)` | describe response + `tags` (list of `{key, value}`) |
| `aws_dynamodb_table` | `dynamodb.describe_table(TableName=id)`, `dynamodb.list_tags_of_resource(ResourceArn=arn)` | `Table` + `Tags` |
| `aws_s3_bucket` | 8 `s3.get_bucket_*` calls (Req 2.2), client `us-east-1` | `{"Name": bucket, "bucket-acl": {...}, ...}` (missing sub-configs omitted) |
| `aws_iam_role` | `iam.get_role`, `iam.list_attached_role_policies`, `iam.list_role_policies`, `iam.get_role_policy` per inline policy | `Role` + `AttachedPolicies: [{PolicyName, PolicyArn}]` + `InlinePolicies: {name: policy document dict}` |

Secondary calls (tags, attributes, policies) are best-effort: an access-denied secondary call omits that key and is logged (Req 2.5); a failure of the **primary** call (first call in the row) makes the resource fail (Req 12.2). `datetime` values are converted to ISO-8601 strings so Specifications are JSON-serializable.

## Collection (`src/collector.py`, `src/inventory.py`, `src/aws_session.py`)

### Error classification (Req 2.5, 12.1, 12.3)

`botocore.exceptions.ClientError` codes are mapped:

| Codes | Class | Behavior |
|---|---|---|
| `AccessDenied`, `AccessDeniedException`, `UnauthorizedOperation`, `AuthorizationError`, `AuthorizationErrorException` | `AccessDeniedError` | no retry; log `Missing <service>:<Action> permission` |
| `Throttling`, `ThrottlingException`, `RequestLimitExceeded`, `TooManyRequestsException`, `SlowDown`, `ProvisionedThroughputExceededException` | `RateLimitError(retry_after)` | retry; wait `Retry-After` header seconds if present, else backoff delay |
| `NoSuch*Configuration`, `NoSuchBucketPolicy`, `NoSuchTagSet`, `NoSuchWebsiteConfiguration`, `ServerSideEncryptionConfigurationNotFoundError`, `NoSuchEntity` (secondary IAM calls only) | `NotConfigured` | no retry, not an error; key omitted |
| other `ClientError` with HTTP status ≥ 500, `EndpointConnectionError`, `ConnectTimeoutError`, `ReadTimeoutError` | transient | retry with backoff |
| other `ClientError` (4xx) | permanent | no retry; operation failed |

`RetryConfig(max_attempts=3, base_delay=1.0, backoff_multiplier=2.0)`: attempts at t=0, +1 s, +2 s. A rate-limit wait replaces the backoff delay for that attempt. `SpecCollector.api_calls` counts every attempt. Operations with status `denied` or `failed` (primary or secondary) are collection errors and make the run exit with code 1; `not_configured` is not an error. `raw_response` keys are the API operation names, with `:<attribute>` / `:<policy name>` suffixes for repeated operations (e.g. `DescribeVpcAttribute:enableDnsSupport`).

`ResourceDiscovery(session, regions, max_workers, progress_callback, account_id)` uses `account_id` for ARNs that list APIs do not return (EC2, DynamoDB) and strips the `:*` suffix from log group ARNs.

`src/aws_session.py` builds the session: `boto3.Session(profile_name=profile)`; with `role_arn`, calls `sts.assume_role(RoleArn, RoleSessionName="aws-resource-inventory", ExternalId?)` and builds a new session from the temporary credentials. All clients are created with `botocore.config.Config(retries={"total_max_attempts": 1, "mode": "standard"}, user_agent_extra="aws-resource-inventory")` (`total_max_attempts` counts the initial call, so 1 disables botocore retries; the legacy `max_attempts` key counts retries only). `get_account_id(session)` calls `sts.get_caller_identity()`.

### InventoryCollector

```python
class InventoryCollector:
    def __init__(self, session, account_id: str, retry_config: RetryConfig | None = None,
                 max_workers: int = 10, progress_callback=None): ...
    def collect_all(self, resources: list[DiscoveredResource]) -> CollectionResult: ...
```

Groups resources by (service, client region), creates one client + `SpecCollector` per group, and collects resources concurrently (`max_workers`). Each result gets `region` and `account_id` from discovery/STS — never `"unknown"`.

### Discovery pagination

`ResourceDiscovery` uses `client.get_paginator(method)` when `client.can_paginate(method)` is true, else a single call. `get_api_calls()` reports the number of list calls made.

## Integrity (`src/integrity.py`)

```python
def canonical_json(value) -> str            # json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
def spec_checksum(specifications: dict) -> str   # sha256(canonical_json(specifications).encode()).hexdigest()
def seal_specs(specs, sanitizer) -> list[ResourceSpec]
    # returns NEW specs: specifications and raw_response sanitized; metadata.checksum = spec_checksum(sanitized specifications)
def resolve_property_path(document: dict, path: str) -> Any   # raises KeyError if not resolvable
def find_property_line(json_text: str, path: str) -> int      # 1-based line of the last path key in pretty JSON; 0 if absent
def verify_output_dir(output_dir) -> VerificationReport       # Req 8.3 / 8.4
```

**Property path grammar**: `segment ("." segment)*`, `segment = key ("[" index "]")*`. The first segment is a top-level field of the spec file (normally `specifications`). Keys containing `.`, `[` or `]` are not addressable; citations then point to the closest addressable parent.

**Verification algorithm** (`aws-inventory verify`):
1. For each line of `checksums.sha256`: file must exist and hash must match → else `"<path>:0: checksum mismatch"` / `"missing file"`.
2. Load `analysis/analysis.json`; for each Citation (in relationships, patterns, findings):
   - `spec_file` exists, else discrepancy line 0.
   - `spec_checksum(file["specifications"]) == source_checksum`, else discrepancy at the line of `"specifications"`.
   - `resolve_property_path(file, property_path)` succeeds, else discrepancy line 0.
   - resolved value `== evidence_value`, else discrepancy at `find_property_line`.
3. Output: `OK: <n> files, <m> citations verified` (exit 0) or one `path:line: reason` line per discrepancy (exit 1).

## Output directory layout

```
<Output_Dir>/
├── manifest.json                     # account_id, regions, started_at, finished_at, tool version, resource counts
├── resources.json  resources.md      # aggregates (Req 3.1)
├── <canonical_type>/<region>/<file_id>.json|.md   # per-resource (Req 3.2) — the MCP cache
├── raw_responses/<canonical_type>/<region>/<file_id>_raw.json   # sanitized raw responses (Req 3.6)
├── discovery.json                    # DiscoveredResource list + discovery errors
├── collection_report.json            # operations, errors, phases, metrics (Req 10, 12.4)
├── summary_report.md                 # manual vs automated (Req 10.3)
├── analysis/analysis.json  analysis/analysis.md   # `analyze`
├── diagrams/architecture.drawio      # `analyze`
├── docs/infrastructure.md            # `generate-docs`
├── terraform/...                     # `generate-iac`
└── checksums.sha256  checksums.json  # regenerated after every command that writes files
```

Per-resource JSON files contain the sealed spec without `raw_response` (that lives under `raw_responses/`) plus `generated_at`. Every OutputGenerator writer seals its input first, so `metadata.checksum` always equals the Spec_Checksum of the written `specifications`.

`OutputGenerator.load_specs(output_dir, errors=None) -> list[ResourceSpec]` reads exactly the files matching `<canonical_type>/<region>/*.json` (directory names validated against the registry), so other directories are never mistaken for specs.

## Analysis Engine (`src/analysis_engine.py`)

Rules operate on the AWS-field-name schema. Every rule records Citations whose `spec_file = spec_relpath(spec)` and `source_checksum = spec.metadata.checksum`.

| Relationship | Source field(s) | Target match | Confidence |
|---|---|---|---|
| `vpc_connection` | `VpcId` (EC2, SG), `VpcConfig.VpcId` (Lambda), `DBSubnetGroup.VpcId` (RDS) | VPC `VpcId` | 1.0 |
| `iam_role_usage` | Lambda `Role`, Step Functions `roleArn`, EC2 `IamInstanceProfile.Arn` (profile name == role name) | role `Arn` or `RoleName` | 0.95 |
| `security_group` | EC2 `SecurityGroups[].GroupId`, Lambda `VpcConfig.SecurityGroupIds[]`, RDS `VpcSecurityGroups[].VpcSecurityGroupId` | SG `GroupId` | 0.9 |
| `dynamodb_access` | Lambda `Environment.Variables.<K>` | value equals a `TableName`/`TableArn`, or contains a table name of length > 3 | 1.0 if equal, else 0.85 |
| `log_group` | Lambda `FunctionName` | log group `/aws/lambda/<FunctionName>` | 1.0 |

Patterns (confidence = min of supporting relationship confidences):
- **Serverless Application**: Lambda with ≥1 `iam_role_usage` or `dynamodb_access`.
- **Compute in VPC**: EC2 instance with a `vpc_connection`.
- **API Gateway + Lambda + DynamoDB**, **EC2 + Load Balancer**, **S3 + CloudFront**: reported in `undetectable_patterns` with reason "<service> is not a Supported_Resource_Type ..." (no statement is made about them).

Citations are built by `cite(spec, property_path)`, which resolves `evidence_value` from the spec itself, so every citation resolves by construction (Property 5). `source_checksum` is `metadata.checksum`, or the computed Spec_Checksum when the spec is not sealed. Environment variable or policy names containing `.`, `[` or `]` are cited at their parent object.

Security findings: exactly the three rules of Req 6.6 (citation to the offending statement/grant/permission). `AnalysisReport.to_dict()` is what `analysis/analysis.json` stores: `{generated_at, resource_count, relationships, patterns, security_findings, undetectable_patterns}`; `summary_markdown` goes to `analysis/analysis.md`.

## Diagram Generator (`src/diagram_generator.py`)

- Output: uncompressed mxGraph XML, root `<mxfile host="aws-resource-inventory">` → `<diagram>` → `<mxGraphModel>` → `<root>` with cells `0` and `1`.
- One vertex per spec (duplicates by ARN dropped): `<UserObject id="res-<sha1(arn)[:12]>" label="<type><br/><resource id>" tooltip=ARN arn=ARN>` wrapping an `mxCell vertex="1"`, style = registry `drawio_style` (`shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.<service>` with the official category fill color) — unknown types get a plain rounded rectangle.
- One edge per relationship, `value` = relationship type.
- Layout: one column per region (`global` first), resources grouped by type in rows; deterministic for identical input.
- `aws-inventory analyze --validate-diagram` runs `drawio-ai validate <file>` when the `drawio-ai` CLI is on PATH; otherwise prints that validation was skipped. XML well-formedness is always checked with `xml.etree.ElementTree`.

## IaC Generator (`src/iac_generator.py`)

Mapping from Specifications to Terraform arguments (AWS provider ~> 5.0). Values that equal a sanitizer placeholder produce the argument plus a `# REDACTED: set manually` comment and are added to `lifecycle.ignore_changes`.

| Type | Terraform arguments | Companion resources | Import id | `ignore_changes` |
|---|---|---|---|---|
| `aws_instance` | `ami`←ImageId, `instance_type`, `subnet_id`, `vpc_security_group_ids`←SecurityGroups[].GroupId, `key_name`, `iam_instance_profile`←last segment of IamInstanceProfile.Arn, `ebs_optimized`, `monitoring`←Monitoring.State=="enabled", `tags`←Tags | – | InstanceId | `user_data`, `user_data_base64` |
| `aws_vpc` | `cidr_block`, `instance_tenancy`, `enable_dns_support`, `enable_dns_hostnames`, `tags` | – | VpcId | – |
| `aws_security_group` | `name`←GroupName, `description`, `vpc_id`, `ingress`/`egress` blocks from IpPermissions/IpPermissionsEgress (`from_port`/`to_port` 0 when absent, `protocol`←IpProtocol, `cidr_blocks`, `ipv6_cidr_blocks`, `prefix_list_ids`, `security_groups`, `self`), `tags` | – | GroupId | – |
| `aws_lambda_function` | `function_name`, `role`, `handler`, `runtime`, `memory_size`, `timeout`, `description`, `architectures`, `layers`←Layers[].Arn, `environment { variables }`, `vpc_config { subnet_ids, security_group_ids }` (when SubnetIds non-empty), `tags`, `filename = "lambda_<name>.zip"` placeholder | – | FunctionName | `filename`, `source_code_hash` |
| `aws_db_instance` | `identifier`, `engine`, `engine_version`, `instance_class`, `allocated_storage`, `storage_type`, `multi_az`, `publicly_accessible`, `storage_encrypted`, `kms_key_id`, `db_subnet_group_name`, `vpc_security_group_ids`, `username`←MasterUsername, `backup_retention_period`, `tags`←TagList | – | DBInstanceIdentifier | `password` |
| `aws_cloudwatch_log_group` | `name`, `retention_in_days`, `kms_key_id`, `tags` | – | logGroupName | – |
| `aws_sfn_state_machine` | `name`, `role_arn`, `definition` (string, heredoc), `type`, `tags` | – | stateMachineArn | – |
| `aws_dynamodb_table` | `name`, `billing_mode`, `hash_key`, `range_key`, `attribute {}` blocks, `read_capacity`/`write_capacity` (PROVISIONED only), `global_secondary_index {}` blocks, `stream_enabled`, `stream_view_type`, `tags` | – | TableName | – |
| `aws_s3_bucket` | `bucket`, `tags`←bucket-tagging.TagSet | `aws_s3_bucket_versioning` (when Status present), `aws_s3_bucket_policy` (when Policy present), `aws_s3_bucket_server_side_encryption_configuration` (when rules present) | bucket name (all) | – |
| `aws_iam_role` | `name`, `path`, `assume_role_policy` (jsonencode), `description`, `max_session_duration`, `tags` | `aws_iam_role_policy_attachment` per AttachedPolicies (id `<role>/<policy_arn>`), `aws_iam_role_policy` per InlinePolicies (id `<role>:<policy>`) | RoleName | – |

Unknown types fall back to emitting every identifier-like top-level key as an argument (debug aid only). Terraform resource names are `file_id` with `.` → `_` (hyphens are valid in Terraform names), prefixed with `r_` when not starting with a letter or `_`, and de-duplicated per (region, type) with `_2`, `_3`, ... Companion resources reuse the bucket name (S3) or use `<role name>_<policy name>` (IAM).

Above each block the generator writes `# Resource`, `# Source specification` (spec path relative to Output_Dir), `# ARN`, `# Region`, `# mapped: ...` and one `# unmapped: <key>` per unconsumed key. Strings are emitted as JSON-escaped HCL literals with `${`/`%{` escaped; policy and state machine documents as `<<-EOT` heredocs of pretty JSON.

Terraform only loads `.tf` files of the root directory, so each region directory is a module: root `main.tf` declares `module "<region_with_underscores>" { source = "./<region>"; providers = { aws = aws.<alias> } }` (`global` uses the default provider), root `providers.tf` holds the `terraform {}` requirements, the default `us-east-1` provider and one aliased provider per region; each region directory has a `versions.tf` with `required_providers`. Import addresses are therefore `module.<module>.<type>.<name>`. The generated project passes `terraform validate` (checked against the sample account).

`verify_terraform_plan(tf_dir) -> (bool, str)` runs `terraform plan -detailed-exitcode -no-color -input=false` and decides **only by exit code** (0 = ok, 2 = changes, else error; missing `terraform` binary = error).

Known limitations (documented in README): resource types outside the registry are not generated; S3 lifecycle/CORS/website/ACL and DynamoDB TTL/PITR are not mapped (left unmanaged, so they do not cause plan diffs); security group rules with differing per-range descriptions are emitted without descriptions.

## Documentation Generator (`src/documentation.py`)

`generate_infrastructure_doc(report: AnalysisReport, specs) -> str` (and `document_citations(report, specs) -> list[dict]`, the distinct citations it uses) produces `docs/infrastructure.md`: inventory counts, one section per pattern ("what interacts with what"), one bullet per relationship, security findings, each followed by `[cite: <spec_file>#<property_path> sha256:<first 12 chars>]` markers. No sentence is emitted without at least one citation marker except headings and counts derived from `resources.json`.

## MCP Server

### Core (`src/mcp_server.py`)

```python
class MCPServer:
    def __init__(self, cache_dir: str, clock: Callable[[], float] = time.monotonic): ...
    def handle_request(self, operation: str, params: dict | None = None) -> dict: ...
    def get_security_logs(self) -> list[SecurityLogEntry]: ...   # {timestamp, operation, reason}
```

Each request re-reads the cache with `load_cache()`: only `<canonical_type>/<region>/*.json` (registry types), each file sanitized on load; unreadable files are skipped with a WARNING. Parameters whose value is `null` count as absent. Only accepted requests are recorded by the rate limiter; whitelist/parameter rejections and rate-limited requests are not. The security log keeps the last 1000 entries (timestamp = UTC ISO-8601 with `Z`).

Processing order: (1) whitelist check → `Unauthorized operation` + security log; (2) parameter validation against the schema below → `Invalid parameters` + security log; (3) rate limit (sliding 1 s window, max 10 accepted) → `rate_limited`; (4) dispatch; (5) sanitize the whole response. Exceptions inside handlers become `{"status": "error", "message": <type>: <msg>}`. The module must not import `boto3`/`botocore` (enforced by a test that imports it in a fresh interpreter and inspects `sys.modules`).

| Tool | Parameters | `data` on success |
|---|---|---|
| `list-resources` | `region?: str`, `resource_type?: str` (canonical or alias) | list of `{arn, resource_type, region, account_id, resource_id, spec_file, checksum}` sorted by `spec_file` |
| `get-resource-spec` | `arn: str` (required) | the sanitized spec file content + `spec_file` |
| `analyze-activity-flow` | `arn?: str` | `AnalysisReport.to_dict()` for all cached specs; with `arn`, only relationships/patterns/findings involving that ARN |
| `generate-documentation` | – | `{"markdown": <docs/infrastructure.md content>, "citations": [...]}` generated in memory (no files written) |

Unknown `resource_type` values are invalid parameters. An ARN not in the cache → `status: error` with "not found in collected data ... run `aws-inventory collect`". An empty cache → the same message for every tool.

### Transport (`src/mcp_stdio.py`)

`build_server(cache_dir) -> FastMCP` registers the four tools with the hyphenated names above; each tool calls `MCPServer.handle_request` and returns its dict (JSON). `sandbox_environment(environ)` deletes every `AWS_*` variable and sets `AWS_SHARED_CREDENTIALS_FILE` / `AWS_CONFIG_FILE` to `/nonexistent/aws-resource-inventory` (Req 9.7). `aws-inventory mcp-serve --cache-dir DIR` = `sandbox_environment(os.environ)` + `build_server(DIR).run("stdio")`. `python -m src.mcp_stdio --cache-dir DIR` does the same (used by the stdio integration tests).

Client configuration example (Claude Desktop / Claude Code `.mcp.json`):

```json
{"mcpServers": {"aws-inventory": {"command": "aws-inventory", "args": ["mcp-serve", "--cache-dir", "/abs/path/output"]}}}
```

## CLI (`src/cli.py`)

Entry point `aws-inventory = "src.cli:main"`. Global options: `--log-level [DEBUG|INFO|WARNING|ERROR]` (default INFO), `--no-color`.

| Command | Options | Online? | Writes |
|---|---|---|---|
| `discover` | `--region` (repeatable), `--profile`, `--role-arn`, `--external-id`, `--output-dir` (default `./output`) | yes | `discovery.json` |
| `collect` | same as discover + `--max-workers` (default 10) | yes | everything in "Output directory layout" up to `summary_report.md`, plus checksums |
| `analyze` | `--output-dir`, `--validate-diagram` | no | `analysis/`, `diagrams/`, checksums |
| `generate-iac` | `--output-dir`, `--terraform-dir` | no | `terraform/`, checksums |
| `generate-docs` | `--output-dir` | no | `docs/infrastructure.md` (runs analysis in memory), checksums |
| `verify` | `--output-dir` | no | nothing |
| `mcp-serve` | `--cache-dir` (required) | no | nothing |

Exit codes: 0 success; 1 completed with errors (discovery/collection errors, verification discrepancies); 2 could not start (Click usage errors, no credentials, assume-role failure, Output_Dir without specs for offline commands).

Logging: root handler to stderr with `SanitizingFilter`, which runs `DataSanitizer` on `record.getMessage()` and additionally replaces the literal access key, secret key and session token of the active session if they appear. Credentials are never passed to log calls or written to files.

## Metrics (`src/metrics.py`)

`PhaseTimer` records `{name, started_at, ended_at, duration_seconds}`. `RunMetrics` holds the Req 10.2 counters. `time_savings(resources, duration_seconds)` implements the Req 10.4 formulas; `OutputGenerator.generate_summary_report` and the CLI summary both use it. `files_size(paths)` sums the sizes of the files a run wrote (`data_volume_bytes`).

`collection_report.json` (written by `collect`, sanitized):

```json
{"account_id": "...", "regions": [...], "started_at": "...Z", "finished_at": "...Z",
 "phases": [{"name": "discovery|collection|output", "started_at", "ended_at", "duration_seconds"}],
 "metrics": {"resources_discovered", "specs_collected", "specs_failed", "api_calls", "data_volume_bytes"},
 "time_savings": {"manual_hours", "automated_hours", "hours_saved", "percent_saved"},
 "operations": [{"resource_arn", "operation", "status": "success|failed", "outcome": "success|not_configured|denied|failed",
                 "attempts", "error_type", "detail", "timestamp"}],
 "discovery_errors": [{"region", "resource_type", "message"}],
 "collection_errors": [{"resource_arn", "operation", "error_type", "error_message", "timestamp", "retry_count"}]}
```

`specs_failed = resources_discovered − specs_collected`; `api_calls` = STS calls (GetCallerIdentity, AssumeRole) + discovery list calls + every collector attempt. `summary_report.md` holds the metrics table, phase durations and the time-savings table. Progress lines go to stderr, results to stdout; all CLI output passes through the same `SanitizingFilter.scrub`.

## Error Handling

| Situation | Handling |
|---|---|
| Region/type list call fails | `DiscoveryError`, continue (Req 1.4) |
| Primary spec call fails after retries | `CollectionError`, resource skipped (Req 12.2) |
| Secondary call access denied / not configured | key omitted, logged, resource still collected |
| Unreadable/invalid spec file during offline commands | logged as error, file skipped, exit code 1 |
| No credentials / assume-role fails | message on stderr, exit 2 |
| Parse failure | `Result.err(ParseError)` with excerpt and original input (Req 4.2, 4.5) |

## Correctness Properties

| # | Property | Requirement | Test |
|---|---|---|---|
| 1 | `parse(print(spec)) == spec` for all valid specs | 4.4 | `test_property_parse_print_roundtrip_req_4_4` |
| 2 | Sanitization preserves keys, list lengths and nesting, and is idempotent | 9.5, 9.6 | `test_property_sanitizer_preserves_structure_req_9_5`, `test_property_sanitizer_idempotent_req_9_6` |
| 3 | Every top-level Specifications key appears in the generated Terraform block | 7.3 | `test_property_iac_generator_includes_all_specs_req_7_3` |
| 4 | Every spec ARN appears in the diagram | 6.4 | `test_property_diagram_includes_all_resources_req_6_4` |
| 5 | Every citation produced by the engine resolves against its sealed spec | 8.5 | `test_property_citations_resolve_req_8_5` |
| 6 | No MCP response contains a credential pattern | 5.2 | `test_property_mcp_server_no_credentials_req_5_2` |

## Performance Targets

- Discovery: < 5 min for 1000 resources at ≤ 100 ms/call (Req 1.5) — `test_discovery_completes_under_5_minutes_req_1_5` checks 1000 resources from mocked clients (no simulated latency); `scripts/benchmark.py` measures 1000 resources in 17 regions on moto with 100 ms per call (results in `docs/ACCURACY_AND_SECURITY.md`).
- Collection: ≥ 10 resources/s with 10 workers against moto.
- MCP: 10 requests/s accepted (Req 5.7).
- IaC generation: < 10 s for 1000 specs.

## Security Checklist

- [ ] Only `Describe*`/`List*`/`Get*` + `sts:AssumeRole`/`GetCallerIdentity` invoked (static test over the registry and collector method tables).
- [ ] `docs/iam-policy.json` lists exactly those permissions.
- [ ] Sanitizer applied to spec JSON, Markdown, raw responses, MCP responses and log records.
- [ ] MCP module has no boto3 import; `mcp-serve` strips AWS env vars.
- [ ] `bandit -r src -ll` clean.
- [ ] Tests run with fake credentials only (conftest), live tests opt-in.
