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
| `src/resource_types.py` | Registry of the Supported_Resource_Types: canonical id, aliases, service, scope, id extraction, file id, Terraform type, import id, draw.io style. |
| `src/parser.py` | `ResourceSpec`, `SpecMetadata`, `Result`, `ParseError`, `ResourceParser` (parse/print JSON). |
| `src/sanitizer.py` | `DataSanitizer`: structure-preserving redaction with a redaction log. |
| `src/discovery.py` | `ResourceDiscovery`: concurrent per-region listing with pagination; `DiscoveredResource`, `DiscoveryError`. |
| `src/scope.py` | Project scope (Req 13): `TagScopedDiscovery`, `exclude_defaults()`, reference rules + `extract_references()` for the dependency closure, `scope_document()`. |
| `src/collector.py` | `SpecCollector`: per-type spec collection for one boto3 client, retry/backoff, error classification, API call counting. |
| `src/inventory.py` | `InventoryCollector`: turns `DiscoveredResource`s into `ResourceSpec`s (one SpecCollector per service+region), `CollectionError`, `CollectionResult`. |
| `src/integrity.py` | Canonical JSON, Spec_Checksum, `seal_specs()`, citation path resolution, `verify_output_dir()`. |
| `src/output_generator.py` | JSON/Markdown/raw/checksum/summary files, `load_specs()` from Output_Dir. |
| `src/analysis_engine.py` | Relationship rules (single source), patterns, security findings, citations, `AnalysisReport` (+ JSON serialization, `analysis.md`). |
| `src/diagram_generator.py` | `.drawio` generation (Overview + Network detail pages) from specs + relationships; optional `drawio-ai validate` and draw.io PNG export. |
| `src/iac_generator.py` | Terraform generation per type mapping, `import.sh`, `verify_state.sh`, `verify_terraform_plan()`. |
| `src/documentation.py` | `docs/infrastructure.md` from an `AnalysisReport` (every statement cited). |
| `src/metrics.py` | Phase timer, run metrics, time-savings computation, `collection_report.json`. |
| `src/aws_session.py` | boto3 session creation (profile, assume-role, botocore retry config), account id lookup. |
| `src/mcp_server.py` | `MCPServer` core (no boto3 import). |
| `src/mcp_stdio.py` | FastMCP stdio adapter + environment sandboxing. |
| `src/cli.py` | Click CLI `aws-inventory`, logging setup with sanitizing filter, exit codes. |
| `src/sample_account.py` | Demo/test only: builds the sample account (every Supported_Resource_Type) inside moto. |
| `src/moto_compat.py` | Demo/test only: ElastiCache replication groups and cache subnet groups, which moto 4.x lacks, served from memory by a botocore `before-call` handler (registered last, per account and region) inside `mock_elasticache_replication_groups()`; the same context restores the ECS service `networkConfiguration` moto drops (`after-call` on `CreateService`/`DescribeServices`). Imported before any session is created (`tests/conftest.py`, `scripts/demo.py`, `scripts/benchmark.py`). |

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
    attributes: dict[str, Any]       # IsDefault (VPC), GroupName/VpcId (SG), Path (IAM role) — Req 13.4
    referenced_by: list[str]         # "<arn>#<property path>" for closure-added resources — Req 13.3

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
- `resource_id(spec: ResourceSpec) -> str`: the id from the "Resource id" column of requirements.md, read from the Specifications `id_field`; types without one (`aws_lb`, `aws_lb_listener`, `aws_lb_target_group`, `aws_route53_zone`, `aws_acm_certificate`, `aws_wafv2_web_acl`, `aws_ecs_service`, `aws_ecs_task_definition`, `aws_sqs_queue`, `aws_sns_topic`, `aws_cloudwatch_event_rule`, `aws_scheduler_schedule`) take the id `parse_arn` reads from the ARN; anything else falls back to the last ARN segment (after the last `/` or `:`).
- `file_id(resource_id: str) -> str`: `re.sub(r"[^A-Za-z0-9_.-]", "_", id).strip("_") or "resource"`.
- `spec_relpath(spec) -> str`: `f"{resource_type}/{region}/{file_id}.json"` (posix, relative to Output_Dir).
- `build_arn(type_id, resource_id, region, account_id) -> str` / `parse_arn(arn) -> (type_id, resource_id, region) | None`: driven by the `arn_service` / `arn_resource` registry fields (e.g. `ec2` + `security-group/{id}`). `parse_arn` drops IAM role paths and the `:*` log group suffix, maps global types to region `"global"`, maps CloudFront-scope web ACLs (`global/webacl/<name>/<id>`) to `"global"` and REGIONAL ones (`regional/webacl/...`) to their region, checks the optional `id_pattern` (load balancers `(app|net|gwy)/<name>/<hash>`, listeners one more segment, target groups and web ACLs `<name>/<id>`, ECS services `<cluster>/<service>`, task definitions `<family>:<revision>`, rules `<name>` or `<bus>/<name>`, schedules `<group>/<name>`, queues and topics one segment), drops the UUID of Auto Scaling group ARNs (`autoScalingGroup:<uuid>:autoScalingGroupName/<name>` → `<name>`), and returns None for unsupported kinds (classic load balancers, listener rules, WAF IP sets, network ACLs, S3 objects, old-format ECS service ARNs, ECS tasks, SNS subscriptions, scheduler groups, launch configurations). `build_arn` writes Route 53 ARNs without region and account (`arn:aws:route53:::hostedzone/<id>`), CloudFront-scope web ACLs as `arn:aws:wafv2:us-east-1:<account>:global/webacl/<name>/<id>` and Auto Scaling groups in the IAM wildcard form `...:autoScalingGroup:*:autoScalingGroupName/<name>` (the UUID is only known from the API; the collector records the real ARN).
- `s3_bucket_from_domain(domain) -> str | None`: the bucket of an S3 REST or website endpoint (`<bucket>.s3.amazonaws.com`, `<bucket>.s3.<region>.amazonaws.com`, `<bucket>.s3-website-<region>.amazonaws.com`, ...); used for CloudFront origins by the closure and the Analysis_Engine.
- Draw.io styles (all names verified against the vendored skill references, `test_registry_styles_use_verified_stencils_req_15_3`): VPC `vpc_virtual_private_cloud_vpc` and IAM role `role` are resource-level shapes; service icons use `shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.<icon>` (ECS cluster `ecs`, ECR `ecr`, ElastiCache `elasticache`, SQS `sqs`, SNS `sns`), resource-level icons (ALB, NAT/internet gateway, VPC endpoint, Route 53 hosted zone, route table = `router`, ECS service `ecs_service`, task definition `ecs_task`, Auto Scaling group `auto_scaling_group`, launch template `ami`, EventBridge rule `rule_3`, schedule `eventbridge_scheduler`) use `shape=mxgraph.aws4.<shape>`, subnets use the subnet group `shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group` (verified stencil names from the `aws-architecture-diagram` skill).

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
| `aws_subnet` | `ec2.describe_subnets(SubnetIds=[id])` | `Subnets[0]` |
| `aws_route_table` | `ec2.describe_route_tables(RouteTableIds=[id])` | `RouteTables[0]` (`Routes`, `Associations`) |
| `aws_internet_gateway` | `ec2.describe_internet_gateways(InternetGatewayIds=[id])` | `InternetGateways[0]` (`Attachments`) |
| `aws_nat_gateway` | `ec2.describe_nat_gateways(NatGatewayIds=[id])` | `NatGateways[0]` |
| `aws_vpc_endpoint` | `ec2.describe_vpc_endpoints(VpcEndpointIds=[id])` | `VpcEndpoints[0]` (`PolicyDocument` is a JSON string) |
| `aws_lb` | `elbv2.describe_load_balancers(LoadBalancerArns=[arn])`, `describe_load_balancer_attributes`, `describe_tags(ResourceArns=[arn])`, `describe_listeners(LoadBalancerArn=arn)` (all pages) | `LoadBalancers[0]` + `Attributes: [{Key, Value}]` + `Tags` + `Listeners` (full listener objects, followed by the closure) |
| `aws_lb_listener` | `elbv2.describe_listeners(ListenerArns=[arn])`, `describe_tags` | `Listeners[0]` + `Tags` |
| `aws_lb_target_group` | `elbv2.describe_target_groups(TargetGroupArns=[arn])`, `describe_target_group_attributes`, `describe_tags` | `TargetGroups[0]` + `Attributes` + `Tags` |
| `aws_cloudfront_distribution` | `cloudfront.get_distribution(Id=id)`, `cloudfront.list_tags_for_resource(Resource=Distribution.ARN)`, client `us-east-1` | the `Distribution` object (`Id`, `ARN`, `DomainName`, `Status`, `DistributionConfig`, ...) + `Tags` (the `Tags.Items` list). `ETag` is dropped; edge locations and IP ranges are never read |
| `aws_route53_zone` | `route53.get_hosted_zone(Id=id)`, `list_resource_record_sets(HostedZoneId=id)` (all pages), `list_tags_for_resource(ResourceType="hostedzone")`, client `us-east-1` | `HostedZone` fields + `DelegationSet`/`VPCs` when returned + `ResourceRecordSets` + `Tags` |
| `aws_acm_certificate` | `acm.describe_certificate(CertificateArn=arn)`, `list_tags_for_certificate` | `Certificate` + `Tags` |
| `aws_wafv2_web_acl` | `wafv2.get_web_acl(Name, Scope, Id)` (Scope `CLOUDFRONT` for region `global`, else `REGIONAL`), `list_tags_for_resource(ResourceARN)` | `WebACL` + `Tags` (`TagInfoForResource.TagList`); `LockToken` is dropped |
| `aws_ecs_cluster` | `ecs.describe_clusters(clusters=[arn], include=[TAGS, SETTINGS, CONFIGURATIONS])` | `clusters[0]` (`tags`, `settings`, `capacityProviders`, ...) |
| `aws_ecs_service` | `ecs.describe_services(cluster=<cluster>, services=[arn], include=[TAGS])` | `services[0]` without `events` (the service event log is operational history; `raw_response` keeps it) |
| `aws_ecs_task_definition` | `ecs.describe_task_definition(taskDefinition=arn, include=[TAGS])` | `taskDefinition` + `tags` |
| `aws_ecr_repository` | `ecr.describe_repositories(repositoryNames=[name])`, `ecr.list_tags_for_resource(resourceArn)` | `repositories[0]` + `tags` (`Key`/`Value`) |
| `aws_autoscaling_group` | `autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[name])` | `AutoScalingGroups[0]` (with `Tags`); the spec ARN is its `AutoScalingGroupARN` |
| `aws_launch_template` | `ec2.describe_launch_templates(LaunchTemplateIds=[id])`, `ec2.describe_launch_template_versions(Versions=["$Default"])` | `LaunchTemplates[0]` + `LaunchTemplateData` of the default version |
| `aws_elasticache_replication_group` | `elasticache.describe_replication_groups(ReplicationGroupId)`, `describe_cache_clusters(CacheClusterId=MemberClusters[0])`, `describe_cache_subnet_groups(CacheSubnetGroupName)`, `list_tags_for_resource(ResourceName=ARN)` | `ReplicationGroups[0]` + `CacheCluster` (first member: subnet group, security groups, engine version, parameter group are shared by all members) + `CacheSubnetGroup` + `TagList` |
| `aws_sqs_queue` | `sqs.get_queue_url(QueueName, QueueOwnerAWSAccountId)`, `get_queue_attributes(AttributeNames=[All])` (both primary), `list_queue_tags` | `{"QueueUrl", "Attributes": {...strings...}, "Tags": {...}}` |
| `aws_sns_topic` | `sns.get_topic_attributes(TopicArn)`, `list_tags_for_resource`, `list_subscriptions_by_topic` (all pages) | `{"Attributes", "Tags", "Subscriptions"}` |
| `aws_cloudwatch_event_rule` | `events.describe_rule(Name, EventBusName)`, `list_targets_by_rule` (all pages), `list_tags_for_resource(ResourceARN)` | DescribeRule response + `Targets` + `Tags` |
| `aws_scheduler_schedule` | `scheduler.get_schedule(Name, GroupName)` | the GetSchedule response (schedules have no tags; only groups do) |

Paginated secondary calls (load balancer listeners, Route 53 record sets) are one recorded operation whose pages are merged: list fields concatenated, the first page's `ResponseMetadata` kept in `raw_response`. Secondary calls (tags, attributes, policies) are best-effort: an access-denied secondary call omits that key and is logged (Req 2.5); a failure of the **primary** call (first call in the row) makes the resource fail (Req 12.2). `datetime` values are converted to ISO-8601 strings so Specifications are JSON-serializable.

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

`ResourceDiscovery(session, regions, max_workers, progress_callback, account_id)` uses `account_id` for ARNs that list APIs do not return (EC2, DynamoDB, CloudFront, Route 53, SQS — built with `build_arn`) and strips the `:*` suffix from log group ARNs. ECS clusters (`list_clusters`), ECR, Auto Scaling, ElastiCache, SNS and Scheduler list APIs return ARNs (ids via `parse_arn`); ECS services are listed per cluster (`list_services(cluster=arn)`), task definitions are taken from `describe_services` (batches of 10: `taskDefinition` and `deployments[].taskDefinition`, so revisions still running during a deployment are included), EventBridge rules are listed per bus (`list_event_buses`, then `list_rules(EventBusName)`, skipping rules with `ManagedBy`), SQS queue names come from the queue URLs. ELB, ACM and WAF list APIs return ARNs; their ids and regions come from `parse_arn`. Listeners are listed per discovered load balancer (`describe_listeners(LoadBalancerArn=...)`). Web ACLs are listed with `Scope=REGIONAL` per region and once with `Scope=CLOUDFRONT` through `us-east-1` (one call each: boto3 cannot paginate `ListWebACLs`, a call returns up to 100 ACLs). NAT gateways in state `deleted`, `deleting` or `failed` are skipped. Subnets record `VpcId`/`DefaultForAz`, route tables `VpcId`, internet gateways `VpcIds` in `attributes` for the default exclusion.

`src/aws_session.py` builds the session: `boto3.Session(profile_name=profile)`; with `role_arn`, calls `sts.assume_role(RoleArn, RoleSessionName="aws-resource-inventory", ExternalId?)` and builds a new session from the temporary credentials. All clients are created with `botocore.config.Config(retries={"total_max_attempts": 1, "mode": "standard"}, user_agent_extra="aws-resource-inventory")` (`total_max_attempts` counts the initial call, so 1 disables botocore retries; the legacy `max_attempts` key counts retries only). `get_account_id(session)` calls `sts.get_caller_identity()`.

### InventoryCollector

```python
class InventoryCollector:
    def __init__(self, session, account_id: str, retry_config: RetryConfig | None = None,
                 max_workers: int = 10, progress_callback=None): ...
    def collect_all(self, resources: list[DiscoveredResource]) -> CollectionResult: ...
```

Groups resources by (service, client region), creates one client + `SpecCollector` per group, and collects resources concurrently (`max_workers`). Each result gets `region` and `account_id` from discovery/STS — never `"unknown"`.

`collect_all(resources, follow_references=True)` runs the dependency closure (Req 13.3) in waves: after each wave, `scope.extract_references()` is applied to the new specs; targets whose identity `(resource_type, region, resource_id)` is not yet known form the next wave (sorted by ARN; `referenced_by` merged when several specs name the same target). Identity, not the ARN string, is compared because discovery may build EC2 ARNs without the account id. `CollectionResult.referenced` lists the closure-added resources.

### Discovery pagination

`ResourceDiscovery` uses `client.get_paginator(method)` when `client.can_paginate(method)` is true, else a single call. `get_api_calls()` reports the number of list calls made.

## Project scope (`src/scope.py`, Req 13)

**Seeds.** Without `--project-tag`, `ResourceDiscovery` lists every resource of the supported types. With it, `TagScopedDiscovery(session, tags, regions, max_workers, progress_callback, account_id)` (same interface: `discover_all_resources`, `get_regions`, `get_api_calls`, `get_errors`) calls `resourcegroupstaggingapi.get_resources(TagFilters=[{"Key": k, "Values": [v]}, ...])` (paginated) in every queried region — enabled regions, or `--region` plus `us-east-1` restricted to global types — and maps each ARN with `parse_arn` (unsupported ARNs are ignored; seed ARNs are rebuilt with `build_arn` so they match closure ARNs). IAM roles come from `iam.list_roles` + `iam.list_role_tags` per role. Task definition ARNs are not used as seeds (`TAG_SEED_EXCLUDED_TYPES`): every registered revision carries its family's tags, while only the revisions services run are wanted, and the closure reaches those from the services. A failing region is a `DiscoveryError(region, "tagging", message)`. `seed_regions(resources, requested)` returns `--region` values when given, else the sorted regions of regional seeds.

**Default exclusion.** `exclude_defaults(resources, include_defaults=False) -> (kept, excluded)`: a VPC with `attributes.IsDefault`, a security group named `default` whose `VpcId` is such a VPC (same region), a subnet with `DefaultForAz` (only default VPCs have default subnets; a subnet a user added to the default VPC is kept), a route table whose `VpcId` is a default VPC, an internet gateway attached only to default VPCs, and an IAM role whose path starts with `/aws-service-role/`. Tag-seeded resources carry no list attributes, so only the role rule can apply to them.

**Reference rules** (`REFERENCE_RULES`, source type → `Rule(path, target, resolve=None)`; `[]` walks list elements via `integrity.iter_property_paths`). Values may be ids, names or ARNs; `resolve` maps a raw value to the target id/ARN first (a list for comma-separated values such as `VPCZoneIdentifier`, or None to skip it); an ARN that `parse_arn` does not map to the target type, or that belongs to another account, is ignored (it cannot be collected with the run's credentials); ids/names are resolved in the source spec's region (`global` for global types).

| Source | Path | Target |
|---|---|---|
| `aws_instance` | `VpcId`, `SecurityGroups[].GroupId` | VPC, SG |
| `aws_security_group` | `VpcId`, `IpPermissions[].UserIdGroupPairs[].GroupId`, `IpPermissionsEgress[].UserIdGroupPairs[].GroupId` | VPC, SG |
| `aws_lambda_function` | `Role`, `VpcConfig.VpcId`, `VpcConfig.SecurityGroupIds[]`, `LoggingConfig.LogGroup` | role, VPC, SG, log group |
| `aws_db_instance` | `VpcSecurityGroups[].VpcSecurityGroupId`, `DBSubnetGroup.VpcId`, `MonitoringRoleArn`, `AssociatedRoles[].RoleArn` | SG, VPC, role |
| `aws_sfn_state_machine` | `roleArn`, `loggingConfiguration.destinations[].cloudWatchLogsLogGroup.logGroupArn` | role, log group |
| `aws_instance` (Req 14) | `SubnetId` | subnet |
| `aws_lambda_function` | `VpcConfig.SubnetIds[]` | subnet |
| `aws_db_instance` | `DBSubnetGroup.Subnets[].SubnetIdentifier` | subnet |
| `aws_subnet` | `VpcId` | VPC |
| `aws_route_table` | `VpcId`, `Associations[].SubnetId`, `Routes[].GatewayId` (`igw-` → internet gateway, `vpce-` → VPC endpoint), `Routes[].NatGatewayId` | VPC, subnet, gateways, endpoint |
| `aws_internet_gateway` | `Attachments[].VpcId` | VPC |
| `aws_nat_gateway` | `VpcId`, `SubnetId` | VPC, subnet |
| `aws_vpc_endpoint` | `VpcId`, `RouteTableIds[]`, `SubnetIds[]`, `Groups[].GroupId` | VPC, route table, subnet, SG |
| `aws_lb` | `VpcId`, `AvailabilityZones[].SubnetId`, `SecurityGroups[]`, `Listeners[].ListenerArn` | VPC, subnet, SG, listener |
| `aws_lb_listener` | `LoadBalancerArn`, `Certificates[].CertificateArn`, `DefaultActions[].TargetGroupArn`, `DefaultActions[].ForwardConfig.TargetGroups[].TargetGroupArn` | load balancer, certificate, target group |
| `aws_lb_target_group` | `VpcId`, `LoadBalancerArns[]` | VPC, load balancer |
| `aws_cloudfront_distribution` | `DistributionConfig.Origins.Items[].DomainName` (resolved with `s3_bucket_from_domain`), `DistributionConfig.WebACLId`, `DistributionConfig.ViewerCertificate.ACMCertificateArn` | S3 bucket, web ACL, certificate |
| `aws_ecs_service` (Req 14.4) | `clusterArn`, `taskDefinition`, `loadBalancers[].targetGroupArn`, `networkConfiguration.awsvpcConfiguration.subnets[]` / `.securityGroups[]` | cluster, task definition, target group, subnet, SG |
| `aws_ecs_task_definition` | `taskRoleArn`, `executionRoleArn`, `containerDefinitions[].logConfiguration.options.awslogs-group`, `containerDefinitions[].image` (private ECR image URIs `<acct>.dkr.ecr.<region>.amazonaws.com/<repo>[:tag|@digest]` → repository ARN; public images ignored) | role, log group, ECR repository |
| `aws_autoscaling_group` | `LaunchTemplate.LaunchTemplateId`, `MixedInstancesPolicy.LaunchTemplate.LaunchTemplateSpecification.LaunchTemplateId`, `VPCZoneIdentifier` (comma-separated), `TargetGroupARNs[]` | launch template, subnet, target group |
| `aws_launch_template` | `LaunchTemplateData.SecurityGroupIds[]`, `LaunchTemplateData.NetworkInterfaces[].Groups[]` / `.SubnetId` | SG, subnet |
| `aws_elasticache_replication_group` | `CacheCluster.SecurityGroups[].SecurityGroupId`, `CacheSubnetGroup.VpcId`, `CacheSubnetGroup.Subnets[].SubnetIdentifier` | SG, VPC, subnet |
| `aws_sns_topic` | `Subscriptions[].Endpoint` (ARNs only) | SQS queue, Lambda function |
| `aws_cloudwatch_event_rule` | `Targets[].Arn` (ARNs only; Lambda qualifiers dropped), `Targets[].RoleArn` | Lambda function, SQS queue, SNS topic, state machine, ECS cluster, role |
| `aws_scheduler_schedule` | `Target.Arn`, `Target.RoleArn` | same as rules |

Load balancer origins of a distribution are named by DNS name only, which does not identify an ARN, so the closure does not follow them (the Analysis_Engine still matches them by `DNSName`). Route 53 aliases are DNS names too and are not followed. Children that their parent does not name (route tables of a VPC, target group members, the services of an ECS cluster, the schedules of a group) are only collected when seeded. `referenced_by` entries use the concrete path, e.g. `arn:...:instance/i-1#specifications.SecurityGroups[0].GroupId`.

**Scope record.** `scope_document(config, regions, seeds, excluded, referenced=None)` builds the `scope` block of Req 13.5; `excluded_defaults` omits ARNs the closure pulled back. `collect` reports `resources_discovered = seeds + referenced` in the metrics. `scripts/benchmark.py` passes `--include-defaults` because moto's default network resources (VPC, security group, subnets, main route table per region, counted by `count_defaults`) are part of its resource budget.

## Integrity (`src/integrity.py`)

```python
def canonical_json(value) -> str            # json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
def spec_checksum(specifications: dict) -> str   # sha256(canonical_json(specifications).encode()).hexdigest()
def seal_specs(specs, sanitizer) -> list[ResourceSpec]
    # returns NEW specs: specifications and raw_response sanitized; metadata.checksum = spec_checksum(sanitized specifications)
def resolve_property_path(document: dict, path: str) -> Any   # raises KeyError if not resolvable
def iter_property_paths(specifications, pattern) -> Iterator[(path, value)]   # "Routes[].GatewayId" -> ("specifications.Routes[1].GatewayId", value), ...
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
├── manifest.json                     # account_id, regions, started_at, finished_at, tool version, resource counts, scope (Req 13.5)
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
| `vpc_connection` (Req 14.2) | `VpcId` of subnet, route table, NAT gateway, VPC endpoint, load balancer, target group; internet gateway `Attachments[].VpcId` | VPC `VpcId` | 1.0 |
| `subnet_placement` | EC2 `SubnetId`, Lambda `VpcConfig.SubnetIds[]`, RDS `DBSubnetGroup.Subnets[].SubnetIdentifier`, NAT `SubnetId`, VPC endpoint `SubnetIds[]`, LB `AvailabilityZones[].SubnetId` | subnet `SubnetId` | 1.0 |
| `route_table_association` | route table `Associations[].SubnetId` | subnet | 1.0 |
| `route_target` | route table `Routes[].GatewayId`, `Routes[].NatGatewayId` | internet gateway, VPC endpoint, NAT gateway id | 1.0 |
| `security_group` | LB `SecurityGroups[]` | SG `GroupId` | 0.9 |
| `lb_listener` | listener `LoadBalancerArn` | load balancer ARN | 1.0 |
| `forwards_to` | listener `DefaultActions[].TargetGroupArn`, `DefaultActions[].ForwardConfig.TargetGroups[].TargetGroupArn` | target group ARN | 1.0 |
| `certificate` | listener `Certificates[].CertificateArn`; CloudFront `DistributionConfig.ViewerCertificate.ACMCertificateArn` | certificate ARN | 1.0 |
| `waf_protection` (Req 14.3) | CloudFront `DistributionConfig.WebACLId` | web ACL ARN | 1.0 |
| `cdn_origin` | CloudFront `DistributionConfig.Origins.Items[].DomainName` | S3 bucket named by the endpoint domain (cites bucket `Name` too); load balancer with equal `DNSName` (cites `DNSName` too) | 1.0 |
| `dns_alias` | Route 53 `ResourceRecordSets[].AliasTarget.DNSName` | CloudFront `DomainName` / LB `DNSName` (lower case, no trailing dot, no `dualstack.`; cites the matched field too) | 1.0 |
| `ecs_cluster` (Req 14.4) | ECS service `clusterArn` | cluster ARN | 1.0 |
| `task_definition` | ECS service `taskDefinition` | task definition ARN | 1.0 |
| `lb_target` | target group → ECS service (`loadBalancers[].targetGroupArn`) / Auto Scaling group (`TargetGroupARNs[]`); the citation is the service's/group's property | target group ARN | 1.0 |
| `iam_role_usage` | task definition `taskRoleArn`/`executionRoleArn`, rule `Targets[].RoleArn`, schedule `Target.RoleArn`, launch template `LaunchTemplateData.IamInstanceProfile.Arn`/`.Name` (profile name == role name) | role ARN / name | 0.95 |
| `log_group` | task definition `containerDefinitions[].logConfiguration.options.awslogs-group` | log group name | 1.0 |
| `container_image` | task definition `containerDefinitions[].image` without tag/digest | ECR `repositoryUri` (cited too) | 1.0 |
| `launch_template` | Auto Scaling `LaunchTemplate.LaunchTemplateId`, `MixedInstancesPolicy...LaunchTemplateSpecification.LaunchTemplateId` | launch template id | 1.0 |
| `subnet_placement` | ECS service `networkConfiguration.awsvpcConfiguration.subnets[]`, Auto Scaling `VPCZoneIdentifier` (split on `,`; cites the whole property), ElastiCache `CacheSubnetGroup.Subnets[].SubnetIdentifier`, launch template `LaunchTemplateData.NetworkInterfaces[].SubnetId` | subnet | 1.0 |
| `security_group` | ECS service `...awsvpcConfiguration.securityGroups[]`, ElastiCache `CacheCluster.SecurityGroups[].SecurityGroupId`, launch template `SecurityGroupIds[]`, `NetworkInterfaces[].Groups[]` | SG | 0.9 |
| `vpc_connection` | ElastiCache `CacheSubnetGroup.VpcId` | VPC | 1.0 |
| `subscription` | SNS `Subscriptions[].Endpoint` | any collected spec with that ARN (SQS queue, Lambda) | 1.0 |
| `event_target` | rule `Targets[].Arn`, schedule `Target.Arn` (Lambda version/alias qualifier dropped) | any collected spec with that ARN | 1.0 |
| `network_access` (Req 15.2) | security group rule `IpPermissions[].UserIdGroupPairs[].GroupId` of an RDS instance / ElastiCache group naming a group of an EC2 instance, Lambda, ECS service or Auto Scaling group (via its launch template); computed after the other relationships from their `security_group` / `launch_template` edges; citations: the rule, then the source's group reference | compute → data store | 0.9 |

Patterns (confidence = min of supporting relationship confidences):
- **Serverless Application**: Lambda with ≥1 `iam_role_usage` or `dynamodb_access`.
- **Compute in VPC**: EC2 instance with a `vpc_connection`.
- **Static site: S3 + CloudFront** (Req 14.4): one per CloudFront distribution and S3 bucket it has a `cdn_origin` to.
- **Web app: CloudFront + ALB + ECS**: one per CloudFront distribution and ECS service reached through `cdn_origin` (distribution → load balancer), `lb_listener` (listener → that load balancer), `forwards_to` (listener → target group) and `lb_target` (target group → ECS service). Participants: distribution, load balancer, listener, target group, service; citations are those of the four relationships.
- **API Gateway + Lambda + DynamoDB** (API Gateway is not a Supported_Resource_Type), **EC2 + Load Balancer** (instances registered directly in a target group — `DescribeTargetHealth` — are not collected; target groups of Auto Scaling groups and ECS services are `lb_target` relationships): listed in `undetectable_patterns` with these reasons (`UNDETECTABLE_PATTERNS` holds `(pattern, reason)`); no pattern statement is made about them.

`ArchitecturePattern.participating_resources` starts with the pattern's anchor resource, then lists each supporting relationship's target (and its source when that is not the anchor), without duplicates.

Citations are built by `cite(spec, property_path)`, which resolves `evidence_value` from the spec itself, so every citation resolves by construction (Property 5). `source_checksum` is `metadata.checksum`, or the computed Spec_Checksum when the spec is not sealed. Environment variable or policy names containing `.`, `[` or `]` are cited at their parent object.

Security findings: exactly the three rules of Req 6.6 (citation to the offending statement/grant/permission). `AnalysisReport.to_dict()` is what `analysis/analysis.json` stores: `{generated_at, resource_count, relationships, patterns, security_findings, undetectable_patterns}`; `summary_markdown` goes to `analysis/analysis.md`.

## Diagram Generator (`src/diagram_generator.py`, Req 6.4, 15)

Applies the `aws-architecture-diagram` / `drawio` skill rules deterministically from the specs and relationships; nothing is guessed.

- Output: uncompressed mxGraph XML, `<mxfile host="aws-resource-inventory">` with two `<diagram>` pages, `Overview` and `Network detail`. Each `<root>`: cells `0`, `1`, a `#F5F5F5` background (lowest z-order, page size), a title block (`AWS architecture` + account, regions, latest `collected_at` date), then the content.
- Facts (`_Context`): subnets/VPCs by id; public subnet = explicit route table association, else the VPC's main route table, has a `GatewayId` `igw-*` route; placement = `subnet_placement` targets ordered (AZ, public first, id); VPC = `vpc_connection` target or the subnet's VPC; Auto Scaling members = instances whose `aws:autoscaling:groupName` tag names a collected group.
- Overview containers: page row [Users] [AWS Cloud]; AWS Cloud = row [edge columns: Route 53 | WAF, CloudFront] [Regions] [global services (S3)], then the "Supporting resources" panel (grid, 8 per row). Region = row [VPCs] [regional services, one column per layer]. VPC = row [IGW] [AZ rows] [VPC endpoints without subnets]. AZ = row of subnets (public first, then by name); the i-th subnet of every AZ row has the same width. Subnet = row of icons by layer (0 events, 1 load balancer/NAT/IGW, 2 compute, 3 messaging/endpoints, 4 data), then type, name.
- Network detail: same VPC/AZ/subnet containers with NAT gateways and VPC endpoints in their subnets, IGW left, route tables and gateway endpoints right, security groups in a row below; edges `route_target` (label = route destination CIDR/prefix list) and `route_table_association` (dashed, to the subnet container).
- Cells: icons and VPC/subnet containers are `UserObject`s (`label`, `tooltip` = `arns` = newline-separated ARNs, `resource_type`, subnets also `subnet_type`); ids `<page>-res|grp|box|edge-<sha1(key)[:12]>`. Icons 78×78 in 160×130 slots, 60 px gaps (≥ 220 px between icon centres), group padding 50/30/30/30. Group styles: AWS Cloud `group_aws_cloud_alt`, Region `group_region` (dashed), VPC `group_vpc`, subnets `group_security_group` (`#7AA116` public / `#147EBA` private), AZ and panel dashed generic boxes; all `container=1;dropTarget=1;fillColor=none`. Icon style = registry `drawio_style`; unknown types use `resIcon=mxgraph.aws4.general_AWScloud`. Labels: `<b>name[ ×N]</b><br>type name[ (N instances)]`, names truncated to 30 characters, XML-invalid characters replaced.
- Edges (Req 15.2): `UserObject` (`label`, `relationships`, `evidence`) wrapping an `mxCell edge="1"` with `source`, `target`, `<mxGeometry relative="1">`, parent = innermost common container. Style: orthogonal, rounded, `strokeWidth=2`, exit/entry on the facing sides (horizontal when |dx| ≥ |dy|), `dashed=1` for DNS/WAF/async, `labelBackgroundColor=#F5F5F5;fontSize=11` when labelled. Edges between the same pair of cells are merged.
- `aws-inventory analyze --validate-diagram` runs `drawio-ai validate <file>` when the `drawio-ai` CLI is on PATH; otherwise prints that validation was skipped. `--export-png` runs `<drawio> -x -f png -e -b 10 -o architecture.drawio.png architecture.drawio` (CLI from `drawio`/`draw.io` on PATH or `/Applications/draw.io.app/Contents/MacOS/draw.io`); skipped with a message when absent, exit 1 on failure.
- Golden file: `examples/output/diagrams/architecture.drawio` must equal the generator output for `examples/output` (regenerated by `scripts/demo.py --output-dir examples/output`).

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
| `aws_subnet` | `vpc_id`, `cidr_block`, `availability_zone`, `map_public_ip_on_launch`, `assign_ipv6_address_on_creation`, `ipv6_cidr_block` (associated block), `tags` | – | SubnetId | – |
| `aws_route_table` | `vpc_id`, `route {}` per route (`cidr_block`/`ipv6_cidr_block`/`destination_prefix_list_id` + `gateway_id`, `nat_gateway_id`, `vpc_endpoint_id` (vpce- gateway), `transit_gateway_id`, `vpc_peering_connection_id`, `egress_only_gateway_id`, ...; the `local` route, propagated routes and gateway-endpoint prefix-list routes are skipped), `propagating_vgws`, `tags` | `aws_route_table_association` per non-main association (subnet or gateway; id `<subnet-or-gateway>/<rtb>`) | RouteTableId | – |
| `aws_internet_gateway` | `vpc_id`←Attachments[0].VpcId, `tags` | – | InternetGatewayId | – |
| `aws_nat_gateway` | `subnet_id`, `connectivity_type` (public/private), `allocation_id`/`private_ip`←NatGatewayAddresses[0], `tags` | – | NatGatewayId | – |
| `aws_vpc_endpoint` | `vpc_id`, `service_name`, `vpc_endpoint_type`, `route_table_ids`, `subnet_ids`, `security_group_ids`←Groups[].GroupId, `private_dns_enabled` (Interface only), `ip_address_type`, `policy` (heredoc), `tags` | – | VpcEndpointId | – |
| `aws_lb` | `name`, `internal`←Scheme, `load_balancer_type`←Type, `subnets`←AvailabilityZones[].SubnetId, `security_groups`, `ip_address_type`, from Attributes: `enable_deletion_protection`, `idle_timeout`, `enable_http2`, `drop_invalid_header_fields`, `access_logs {}`; `tags` | – | LoadBalancerArn | – |
| `aws_lb_listener` | `load_balancer_arn`, `port`, `protocol`, `ssl_policy`, `certificate_arn` (default certificate), `alpn_policy`, `default_action {}` (`type`, `order`, `target_group_arn` or `forward { target_group {} stickiness {} }` for several groups, `redirect {}`, `fixed_response {}`), `tags` | – | ListenerArn | – |
| `aws_lb_target_group` | `name`, `port`, `protocol`, `protocol_version`, `vpc_id`, `target_type`, `ip_address_type`, `health_check {}` from HealthCheck* and Matcher, from Attributes: `deregistration_delay`, `slow_start`, `load_balancing_algorithm_type`, `stickiness {}`; `tags` | – | TargetGroupArn | – |
| `aws_cloudfront_distribution` | from DistributionConfig: `enabled`, `aliases`, `comment`, `default_root_object`, `price_class`, `http_version`, `is_ipv6_enabled`, `web_acl_id`, `origin {}` (`s3_origin_config` / `custom_origin_config` with `origin_ssl_protocols` whenever collected, `custom_header`), `default_cache_behavior {}` / `ordered_cache_behavior {}` (methods, policies, TTLs, `forwarded_values` when no cache policy, function associations), `custom_error_response {}`, `logging_config {}`, `restrictions { geo_restriction }`, `viewer_certificate {}` (ACM/IAM certificate or `cloudfront_default_certificate`); `tags` | – | Id | – |
| `aws_route53_zone` | `name` (no trailing dot), `comment`←Config.Comment, `vpc {}` per VPCs, `tags` | `aws_route53_record` per record set except the apex NS/SOA (`name`, `type`, `set_identifier`, `ttl`+`records` or `alias {}`, `weighted_routing_policy`, `health_check_id`; id `<zone>_<name>_<type>[_<set id>]`) | zone id | – |
| `aws_acm_certificate` | `domain_name`, `subject_alternative_names`, `validation_method`←DomainValidationOptions, `key_algorithm`, `options {}`, `tags` (Type `IMPORTED`: a comment that `certificate_body`/`private_key` must be set) | – | CertificateArn | `certificate_body`, `private_key`, `certificate_chain` (imported only) |
| `aws_wafv2_web_acl` | `name`, `scope` (CLOUDFRONT for region `global`), `description`, `default_action { allow/block {} }`, `visibility_config {}`, `tags`; `Rules` stay unmapped | – | `<id>/<name>/<scope>` | `rule` (when Rules exist) |
| `aws_ecs_cluster` | `name`, `setting {}` per settings entry, `tags` | – | cluster name | – |
| `aws_ecs_service` | `name`, `cluster`←clusterArn, `task_definition`, `desired_count`, `launch_type` (or `capacity_provider_strategy {}` blocks), `platform_version` (Fargate / capacity providers), `scheduling_strategy`, `deployment_maximum_percent`/`deployment_minimum_healthy_percent`/`deployment_circuit_breaker {}`, `health_check_grace_period_seconds` (with load balancers), `enable_execute_command`, `enable_ecs_managed_tags`, `propagate_tags`, `load_balancer {}`, `service_registries {}`, `network_configuration { subnets, security_groups, assign_public_ip }`, `iam_role` (unless service-linked), `tags` | – | `<cluster>/<service>` | – |
| `aws_ecs_task_definition` | `family`, `container_definitions` (heredoc of `containerDefinitions`), `task_role_arn`, `execution_role_arn`, `network_mode`, `requires_compatibilities`, `cpu`, `memory`, `ipc_mode`, `pid_mode`, `runtime_platform {}`, `ephemeral_storage {}`, `volume {}` (host path, EFS), `tags` | – | task definition ARN | `container_definitions` when it holds a redacted value |
| `aws_ecr_repository` | `name`, `image_tag_mutability`, `image_scanning_configuration {}`, `encryption_configuration {}`, `tags` | – | repository name | – |
| `aws_autoscaling_group` | `name`, `min_size`, `max_size`, `desired_capacity`, `default_cooldown`, `health_check_type`, `health_check_grace_period`, `vpc_zone_identifier` (split; else `availability_zones`), `target_group_arns`, `load_balancers`, `termination_policies`, `capacity_rebalance`, `protect_from_scale_in`, `max_instance_lifetime`, `launch_template { id, version }`, `tag {}` per tag; `MixedInstancesPolicy` and `Instances` unmapped | – | group name | – |
| `aws_launch_template` | `name`, from the default version's `LaunchTemplateData`: `image_id`, `instance_type`, `key_name`, `vpc_security_group_ids`, `security_group_names`, `user_data` (always redacted, so ignored), `ebs_optimized`, `iam_instance_profile {}`, `monitoring {}`, `metadata_options {}`, `network_interfaces {}`, `block_device_mappings { ebs {} }`, `tag_specifications {}` (Terraform resource types only); `tags` | – | LaunchTemplateId | `user_data` (redacted) |
| `aws_elasticache_replication_group` | `replication_group_id`, `description`, `node_type`, `engine`, `engine_version` (`major.minor` for Redis/Valkey ≥ 6), `port`, `num_cache_clusters` (or `num_node_groups` + `replicas_per_node_group` when cluster mode is on), `parameter_group_name`, `subnet_group_name`, `security_group_ids`, `maintenance_window` (from `CacheCluster`), `automatic_failover_enabled`, `multi_az_enabled`, `at_rest_encryption_enabled`, `transit_encryption_enabled`, `kms_key_id`, `snapshot_retention_limit`, `snapshot_window`, `data_tiering_enabled`, `tags`←TagList | – | ReplicationGroupId | `auth_token` (when AuthTokenEnabled; comment to set it) |
| `aws_sqs_queue` | `name`, from `Attributes` (strings converted to numbers/booleans): `fifo_queue`, `content_based_deduplication`, `deduplication_scope`, `fifo_throughput_limit`, `delay_seconds`, `max_message_size`, `message_retention_seconds`, `receive_wait_time_seconds`, `visibility_timeout_seconds`, `kms_master_key_id`, `kms_data_key_reuse_period_seconds`, `sqs_managed_sse_enabled`, `policy`/`redrive_policy`/`redrive_allow_policy` (heredocs); `tags` | – | QueueUrl | – |
| `aws_sns_topic` | `name`, from `Attributes`: `display_name`, `policy`, `delivery_policy` (heredocs; empty strings = not set), `kms_master_key_id`, `fifo_topic`, `content_based_deduplication`; `tags`; `Subscriptions` unmapped | – | TopicArn | – |
| `aws_cloudwatch_event_rule` | `name`, `event_bus_name` (custom buses), `description`, `schedule_expression`, `event_pattern` (heredoc), `state`, `role_arn`, `tags` | `aws_cloudwatch_event_target` per target (`rule` reference, `target_id`, `arn`, `role_arn`, `input`, `input_path`, `input_transformer {}`, `ecs_target {}`, `retry_policy {}`, `dead_letter_config {}`; id `[<bus>/]<rule>/<target id>`) | `[<bus>/]<name>` | – |
| `aws_scheduler_schedule` | `name`, `group_name`, `description`, `schedule_expression`, `schedule_expression_timezone`, `start_date`, `end_date`, `state`, `kms_key_arn`, `flexible_time_window {}`, `target { arn, role_arn, input, retry_policy {}, dead_letter_config {}, sqs_parameters {} }` | – | `<group>/<name>` | – |

JSON documents given as strings (policies, redrive policies) become heredocs of pretty JSON; an empty string means the attribute is not set and emits no argument. Unknown types fall back to emitting every identifier-like top-level key as an argument (debug aid only). Terraform resource names are `file_id` with `.` → `_` (hyphens are valid in Terraform names), prefixed with `r_` when not starting with a letter or `_`, and de-duplicated per (region, type) with `_2`, `_3`, ... Companion resources reuse the bucket name (S3) or use `<role name>_<policy name>` (IAM).

Above each block the generator writes `# Resource`, `# Source specification` (spec path relative to Output_Dir), `# ARN`, `# Region`, `# mapped: ...` and one `# unmapped: <key>` per unconsumed key. Strings are emitted as JSON-escaped HCL literals with `${`/`%{` escaped; policy and state machine documents as `<<-EOT` heredocs of pretty JSON.

Terraform only loads `.tf` files of the root directory, so each region directory is a module: root `main.tf` declares `module "<region_with_underscores>" { source = "./<region>"; providers = { aws = aws.<alias> } }` (`global` uses the default provider), root `providers.tf` holds the `terraform {}` requirements, the default `us-east-1` provider and one aliased provider per region; each region directory has a `versions.tf` with `required_providers`. Import addresses are therefore `module.<module>.<type>.<name>`. The generated project passes `terraform validate` (checked against the sample account).

`verify_terraform_plan(tf_dir) -> (bool, str)` runs `terraform plan -detailed-exitcode -no-color -input=false` and decides **only by exit code** (0 = ok, 2 = changes, else error; missing `terraform` binary = error).

Known limitations (documented in README): resource types outside the registry are not generated; WAF rules and non-default listener certificates are not mapped; SNS subscriptions, Auto Scaling mixed-instances policies and ECS cluster capacity-provider associations are not mapped; S3 lifecycle/CORS/website/ACL and DynamoDB TTL/PITR are not mapped (left unmanaged, so they do not cause plan diffs); security group rules with differing per-range descriptions are emitted without descriptions.

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
| `discover` | `--region` (repeatable), `--project-tag KEY=VALUE` (repeatable, AND), `--include-defaults`, `--profile`, `--role-arn`, `--external-id`, `--output-dir` (default `./output`) | yes | `discovery.json` |
| `collect` | same as discover + `--max-workers` (default 10) | yes | everything in "Output directory layout" up to `summary_report.md`, plus checksums |
| `analyze` | `--output-dir`, `--validate-diagram`, `--export-png` | no | `analysis/`, `diagrams/`, checksums |
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
| 4 | Every spec ARN appears in the `arns` of an Overview vertex; ids unique; edges attached | 6.4 | `test_property_diagram_includes_all_resources_req_6_4` |
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
