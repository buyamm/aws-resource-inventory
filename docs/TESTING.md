# Testing

The project is built test-first. This guide covers the TDD workflow, how the suite is organized, the markers and fixtures, the quality gates, and the full checklist for adding a resource type.

## TDD workflow

Every behavior starts as a failing test that names the requirement it covers:

1. **Red.** Read the acceptance criterion in [requirements.md](../.kiro/specs/aws-resource-inventory/requirements.md) and the contract in [design.md](../.kiro/specs/aws-resource-inventory/design.md). Write the test and run it to see it fail for the right reason.
2. **Green.** Write the smallest implementation that passes.
3. **Refactor.** Clean up while the suite stays green, then run the linters.

Work is tracked in [tasks.md](../.kiro/specs/aws-resource-inventory/tasks.md). Each top-level task is one commit, and the RED tests are committed together with their GREEN implementation. If behavior changes, update requirements.md, design.md and the tests in the same change.

### Naming

- `test_<component>_<behavior>_req_<X>_<Y>`, for example `test_cli_exits_2_without_credentials_req_12_5`.
- Property tests: `test_property_<behavior>_req_<X>_<Y>`, for example `test_property_sanitizer_idempotent_req_9_6`.
- Test module docstrings list the requirements they validate.

## Running tests

Always use the virtualenv interpreter:

```bash
venv/bin/python -m pytest                                   # full suite
venv/bin/python -m pytest tests/unit/test_parser.py::TestX::test_y   # one test
venv/bin/python -m pytest -k property                       # property tests (Hypothesis)
venv/bin/python -m pytest -m "not slow"                     # skip e2e/slow tests
venv/bin/python -m pytest -m "not slow" --cov=src --cov-report=term-missing
AWS_INVENTORY_LIVE_TESTS=1 venv/bin/python -m pytest -m aws  # live tests, real credentials
```

`pytest.ini` is the effective configuration: `--strict-markers`, `--maxfail=1`, and warnings are errors. Debug logs of the last run are written to `tests/logs/pytest.log`.

## Layout

```
tests/
├── conftest.py            fake credentials, Hypothesis profile, moto fixtures, sample account
├── fixtures/              sample API responses and specs (JSON)
├── unit/                  one module per src module; moto where AWS calls are involved
├── integration/           real boto3 clients against moto, MCP stdio subprocess, Terraform output
└── e2e/                   CLI workflows (Click CliRunner + moto), demo script, opt-in live tests
```

| Level | What it covers | Examples |
|---|---|---|
| Unit | One component in isolation | `test_sanitizer.py`, `test_integrity.py`, `test_cli.py`, `test_docs.py` |
| Integration | Components together against moto or a subprocess | `test_collector_types.py` (all 10 types), `test_mcp_stdio.py` (real MCP client over stdio), `test_iac_generator.py` (plan verification with a mocked `terraform`) |
| End-to-end | Whole CLI workflows | `test_workflows.py` (collect → analyze → IaC → MCP → verify, tampering, partial failure), `test_demo.py`, `test_benchmark.py` (`scripts/benchmark.py` at 40 resources) |
| Live (opt-in) | Real account | `test_live_iac.py`: import and `terraform plan` with zero changes |

## Markers

| Marker | Meaning |
|---|---|
| `unit`, `integration`, `e2e` | Test level (set with `pytestmark` per module) |
| `slow` | Takes more than about a second; end-to-end tests carry it |
| `property` | Available for Hypothesis tests; select them with `-k property` (they are named `test_property_*`) |
| `aws` | Talks to a real account. Skipped by `conftest.py` unless `AWS_INVENTORY_LIVE_TESTS=1` |

Markers are declared in `pytest.ini`; `--strict-markers` rejects unknown ones.

## Fixtures and AWS safety

`tests/conftest.py` runs before boto3 is imported:

- Unless `AWS_INVENTORY_LIVE_TESTS=1`, it removes `AWS_PROFILE` and sets fake credentials (`testing`). An ordinary test can therefore never authenticate against a real account.
- It sets `AWS_ACCOUNT_ID_ENDPOINT_MODE=disabled`. Without it, newer botocore versions send DynamoDB calls to account-based endpoints that moto 4.x does not intercept, and the request goes to real AWS.
- It registers a Hypothesis profile with `max_examples=100` and no deadline (`HYPOTHESIS_PROFILE` selects another).

AWS is mocked with **moto 4.x per-service decorators/context managers** (`mock_s3`, `mock_ec2`, ...), not moto 5's `mock_aws`.

| Fixture | Provides |
|---|---|
| `aws_credentials` | Fake credential environment |
| `mock_s3_client`, `mock_ec2_client`, `mock_lambda_client`, `mock_iam_client`, `mock_dynamodb_client` | A boto3 client inside the corresponding moto mock |
| `moto_all_services` | moto mocks for every service the inventory touches (EC2, IAM, Lambda, Logs, S3, Step Functions, RDS, DynamoDB, STS, tagging, ELBv2, CloudFront, Route 53, ACM, WAFv2, ECS, ECR, Auto Scaling, ElastiCache, SQS, SNS, EventBridge, Scheduler) plus `src.moto_compat.mock_elasticache_replication_groups()`, because moto 4.x does not implement ElastiCache replication groups |
| `sample_account` | `moto_all_services` populated by `src/sample_account.py`: one resource of each type, a public bucket, an SSH-open security group and an admin inline policy. Returns `(session, SampleAccount ids)` |
| `sample_*_response`, `sample_*_resource_spec`, `sample_collection_report` | Static sample data |
| `fixtures_dir`, `sample_aws_responses_dir`, `sample_specs_dir`, `load_fixture_json`, `load_fixture_text` | Access to files under `tests/fixtures/` |

CLI tests use Click's `CliRunner` and remove the CLI's log handler after each test (see the `_reset_cli_logging` fixtures). To see which AWS operations a test makes, patch `botocore.client.BaseClient._make_api_call`, as the `api_calls` fixture in `tests/unit/test_cli.py` does.

## Quality gates

```bash
venv/bin/ruff check src tests
venv/bin/black --check src tests
venv/bin/mypy src
venv/bin/bandit -r src -ll
```

CI (`.github/workflows/tdd-pipeline.yml`) runs type checking, lint and format checks, unit tests with an 80% overall coverage gate, property tests, and integration tests. The target for `src/parser.py` and `src/sanitizer.py` is 100% coverage; the CI step for it still points at old package paths and is fixed in Task 24.4.

## Adding a resource type

A new type touches every stage of the pipeline. Write the failing test for each step first.

1. **Spec.** Add the type to the "Supported resource types" table and aliases in requirements.md, and its API calls and `specifications` shape to design.md ("Specification schema"), the Terraform mapping table, and the relationship rules if any. Use the Terraform resource type name as the canonical id.
2. **Registry** (`src/resource_types.py`). Add a `ResourceTypeInfo(type_id, service, scope, id_field, aliases, drawio_style)` to `REGISTRY`. Tests: `tests/unit/test_resource_types.py` (count, aliases, `resource_id`, `drawio_style`).
3. **Discovery** (`src/discovery.py`). Add a `(type, service, list method, extractor, kwargs)` row and an `_extract_*` function that builds `DiscoveredResource`s with full ARNs. Tests: `tests/unit/test_discovery.py`.
4. **Collection** (`src/collector.py`). Add a `collect_*_spec` method using `_Context.primary` for the call that defines the resource and `_Context.secondary` for best-effort extras, and register it in `SpecCollector.collect_resource`. Keep AWS field names and drop `ResponseMetadata`. Tests: `tests/unit/test_collector.py` and `tests/integration/test_collector_types.py` (moto). If moto does not support the service, add its mock to `moto_all_services`.
5. **Read-only and IAM.** Only `Describe*`/`List*`/`Get*` calls are allowed. Add the IAM actions to [iam-policy.json](iam-policy.json) (`test_cli_api_calls_covered_by_iam_policy_req_9_4` fails until you do; add an entry to `IAM_ACTION_OVERRIDES` there if the IAM action name differs from the API operation).
6. **Terraform** (`src/iac_generator.py`). Add a `_map_*` function to `MAPPERS` that consumes the spec keys it maps (the rest become `# unmapped:` comments), with import id format and `ignore_changes`. Tests: `tests/unit/test_iac_generator.py`; the property test `test_property_iac_generator_includes_all_specs_req_7_3` already covers every registered type.
7. **Analysis** (`src/analysis_engine.py`), if the type takes part in relationships or findings. Build every citation with `cite(spec, property_path)`. Tests: `tests/unit/test_analysis_engine.py`.
8. **Sample account and demo.** Add a resource to `src/sample_account.py`, then regenerate the example with `python scripts/demo.py --output-dir examples/output`. `tests/e2e/test_demo.py` checks that every registered type appears in the demo output and in `examples/output/`.
9. **Docs.** Update the type list in README.md and instruction.md.
