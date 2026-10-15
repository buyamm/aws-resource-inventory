# AWS Resource Inventory

`aws-inventory` takes over an AWS account that has no Infrastructure as Code, documentation or diagrams and produces all three, using **read-only** API calls:

- collects the full configuration of 10 resource types into a local, checksummed **Output_Dir**;
- analyzes relationships, architecture patterns and security findings, where **every statement carries a citation** that `aws-inventory verify` checks mechanically;
- draws a draw.io architecture diagram with official AWS stencils;
- generates Terraform plus `terraform import` and plan-verification scripts;
- serves the collected data to an AI agent (Claude Desktop, Claude Code, ...) over **MCP**, with no AWS credentials in the server process.

Only `discover` and `collect` talk to AWS. Every other command works offline on the Output_Dir, so its results can be reproduced and audited.

Supported resource types (canonical id = Terraform type): `aws_instance`, `aws_vpc`, `aws_security_group`, `aws_lambda_function`, `aws_db_instance`, `aws_cloudwatch_log_group`, `aws_sfn_state_machine`, `aws_dynamodb_table`, `aws_s3_bucket`, `aws_iam_role`.

More documentation:

| Document | Contents |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Components, data flow from AWS to Output_Dir, CLI/MCP/AI agent interaction |
| [docs/ACCURACY_AND_SECURITY.md](docs/ACCURACY_AND_SECURITY.md) | Citation and verification method, security measures, benchmark |
| [docs/TESTING.md](docs/TESTING.md) | TDD workflow, test layout, markers, how to add a resource type |
| [docs/iam-policy.json](docs/iam-policy.json) | Minimal IAM policy for `collect` |
| [instruction.md](instruction.md) | User guide in Vietnamese |
| [examples/output/](examples/output/) | Output_Dir produced by the demo |

## Prerequisites

- Python 3.11 or newer.
- AWS credentials reachable through the standard boto3 credential chain (environment variables, `~/.aws/credentials` / `~/.aws/config`, AWS SSO, or a container/instance role). Only `discover` and `collect` need them.
- An identity allowed to perform the read-only actions in [docs/iam-policy.json](docs/iam-policy.json). AWS's managed `ReadOnlyAccess` policy also works.
- Optional: [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.5 to run the generated import and plan scripts.
- Optional: the `drawio-ai` CLI (drawio-ai-kit) for `analyze --validate-diagram`.

## Installation

```bash
git clone <this repository> aws-resource-inventory
cd aws-resource-inventory
python3.11 -m venv venv
venv/bin/pip install -e .                  # runtime only
venv/bin/pip install -r requirements-dev.txt && venv/bin/pip install -e .   # + tests, moto, linters (needed for the demo)
venv/bin/aws-inventory --version
```

The rest of this README assumes the virtualenv is active (`source venv/bin/activate`), so `aws-inventory` is on `PATH`.

## Quick start: the demo

The demo creates a sample account in [moto](https://github.com/getmoto/moto) (one resource of each type, including a few deliberately insecure settings) and runs the whole pipeline. It needs the dev dependencies and makes no network calls.

```bash
python scripts/demo.py                              # writes ./demo-output
python scripts/demo.py --output-dir examples/output # regenerate the committed example
python scripts/demo.py --live --profile audit --region eu-west-1   # real account, read-only
```

It runs `collect → analyze → generate-iac → generate-docs → verify` and stops at the first failing step. The output directory is emptied first, but only if it is empty or an earlier Output_Dir (contains `manifest.json`); any other directory is left untouched and the demo exits with code 2.

`python scripts/benchmark.py` times `collect` on a moto account with 1000 resources in 17 regions and 100 ms added to every API call; the results are in [docs/ACCURACY_AND_SECURITY.md](docs/ACCURACY_AND_SECURITY.md#performance-benchmark).

## Commands

Global options (before the command): `--log-level DEBUG|INFO|WARNING|ERROR` (default `INFO`; logs go to stderr), `--no-color`, `--version`, `-h/--help`. Every command prints examples with `--help`.

| Command | AWS? | Writes |
|---|---|---|
| `discover` | yes | `discovery.json` |
| `collect` | yes | specs, aggregates, raw responses, reports, checksums |
| `analyze` | no | `analysis/`, `diagrams/architecture.drawio` |
| `generate-iac` | no | `terraform/` |
| `generate-docs` | no | `docs/infrastructure.md` |
| `verify` | no | nothing |
| `mcp-serve` | no | nothing (stdio server) |

### discover

Lists resources of the supported types and writes `<output-dir>/discovery.json`. Useful as a dry run to check permissions and scope.

```bash
aws-inventory discover --region us-east-1 --region eu-west-1 --profile prod
```

Options: `--region` (repeatable; default: every region enabled for the account), `--project-tag KEY=VALUE`, `--include-defaults`, `--profile`, `--role-arn`, `--external-id`, `--output-dir` (default `./output`).

### collect

Discovers and collects every resource's specification, then writes the Output_Dir and prints the time saved compared with a manual inventory (5 minutes per resource).

```bash
aws-inventory collect --region us-east-1 --output-dir ./output
aws-inventory collect --profile audit --role-arn arn:aws:iam::123456789012:role/InventoryReader --external-id ext-42
```

Options: same as `discover`, plus `--max-workers` (default 10, concurrent regions and resources). With `--role-arn`, the tool calls `sts:AssumeRole` (session name `aws-resource-inventory`) and uses the temporary credentials for every later call.

**Project scope.** `--project-tag KEY=VALUE` (repeatable; a resource must carry every tag) starts from the tagged resources only (`tag:GetResources`; IAM roles via `iam:ListRoleTags`). Without `--region`, all enabled regions are searched and the regions holding tagged resources become the run's regions. With or without project tags, the tool then follows references inside the collected specs (VPC, security groups, IAM roles, log groups, ...) and collects what they point to, so untagged dependencies are not lost. Default VPCs, their `default` security group and service-linked roles (`/aws-service-role/`) are skipped unless something references them; `--include-defaults` keeps them. The scope (tags, regions, excluded defaults, and which spec referenced each added resource) is recorded in `manifest.json` and `collection_report.json`.

```bash
aws-inventory collect --project-tag service=shop --project-tag environment=prod --output-dir ./shop
```

Main outputs (full layout in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#output_dir-layout)):

```
output/
├── <type>/<region>/<id>.json|.md   one file per resource (S3 and IAM use region "global")
├── resources.json  resources.md    aggregates
├── raw_responses/                  sanitized raw API responses
├── manifest.json  discovery.json
├── collection_report.json          every API operation, errors, phase timings, metrics
├── summary_report.md               manual vs automated effort
└── checksums.sha256  checksums.json
```

### analyze

Finds relationships (`vpc_connection`, `iam_role_usage`, `security_group`, `dynamodb_access`, `log_group`), patterns ("Serverless Application", "Compute in VPC") and security findings (`OVERLY_PERMISSIVE_IAM_POLICY`, `PUBLIC_S3_BUCKET`, `UNRESTRICTED_SECURITY_GROUP_ACCESS`), each with a confidence score and citations. Writes `analysis/analysis.json`, `analysis/analysis.md` and `diagrams/architecture.drawio` (open it at <https://app.diagrams.net> or in the draw.io desktop app).

```bash
aws-inventory analyze --output-dir ./output
aws-inventory analyze --output-dir ./output --validate-diagram   # also runs `drawio-ai validate` if installed
```

### generate-iac

Generates Terraform (AWS provider `~> 5.0`): one module per region, one `<type>.tf` per (region, type), plus `import.sh` and `verify_state.sh`. Every block is preceded by comments naming its source spec file, ARN, region, and the mapped/unmapped specification keys.

```bash
aws-inventory generate-iac --output-dir ./output                       # -> ./output/terraform
aws-inventory generate-iac --output-dir ./output --terraform-dir ./infra
cd output/terraform && terraform init && ./import.sh && ./verify_state.sh
```

`verify_state.sh` runs `terraform plan -detailed-exitcode` and exits 0 when there are no changes, 2 when there are changes, and 1 on error.

### generate-docs

Writes `docs/infrastructure.md`: inventory, one section per pattern, one bullet per relationship, and the security findings. Every statement ends with a `[cite: <spec_file>#<property_path> sha256:<checksum prefix>]` marker.

```bash
aws-inventory generate-docs --output-dir ./output
```

### verify

Recomputes every hash in `checksums.sha256` and resolves every citation in `analysis/analysis.json` against the spec files. It prints `OK: <n> files, <m> citations verified`, or one `path:line: reason` line per discrepancy and exits 1.

```bash
aws-inventory verify --output-dir ./output
```

### mcp-serve

Serves the Output_Dir to an AI agent over MCP (stdio). Before serving, it removes every `AWS_*` environment variable and points the AWS config and credential files at a non-existent path, so the server process cannot reach AWS.

```bash
aws-inventory mcp-serve --cache-dir /abs/path/to/output
```

Tools: `list-resources(region?, resource_type?)`, `get-resource-spec(arn)`, `analyze-activity-flow(arn?)`, `generate-documentation()`. Other operations and unexpected parameters are rejected and logged; at most 10 requests per second are accepted. Every response is sanitized.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Completed with errors: discovery/collection errors (listed on stderr and in `collection_report.json`), unreadable spec files, verification discrepancies, failed diagram validation |
| 2 | Could not start: invalid arguments, no credentials, `AssumeRole` failed, Output_Dir has no specs |

## MCP client configuration

Collect first, then register the server with an absolute `--cache-dir`.

Claude Code (`.mcp.json` in your project) or Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aws-inventory": {
      "command": "/abs/path/to/aws-resource-inventory/venv/bin/aws-inventory",
      "args": ["mcp-serve", "--cache-dir", "/abs/path/to/output"]
    }
  }
}
```

Claude Code can also add it from the command line:

```bash
claude mcp add aws-inventory -- /abs/path/to/venv/bin/aws-inventory mcp-serve --cache-dir /abs/path/to/output
```

Then ask, for example, "List the Lambda functions and explain which tables they write to, citing the spec files." The agent only sees what `collect` wrote; to refresh the data, run `collect` again (the server re-reads the cache on every request).

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `Unable to call sts:GetCallerIdentity (NoCredentialsError)` / exit 2 on `collect` | No credentials in the chain. Run `aws configure`, `aws sso login --profile <p>`, or export `AWS_PROFILE`. Check with `aws sts get-caller-identity`. |
| Exit 2 with `AssumeRole failed for <role>` | The caller lacks `sts:AssumeRole` on the role, the role's trust policy does not trust the caller, or `--external-id` is wrong. |
| `Missing <service>:<Action> permission` in the log, exit 1 | The identity lacks a read permission. Add it from [docs/iam-policy.json](docs/iam-policy.json). Denied secondary calls (tags, policies) only drop that key; denied primary calls skip the resource. Details per operation are in `collection_report.json`. |
| Discovery errors for some regions | The region is not enabled, or an SCP blocks it. Restrict the scan with `--region`. |
| Throttling / slow collection | Calls are retried up to 3 times (1 s, then 2 s, or the `Retry-After` value). Lower `--max-workers`. |
| `no resource specifications found in <dir>` (exit 2) | The offline command points at a directory without spec files. Run `collect` first or fix `--output-dir`. |
| `verify` reports `checksum mismatch` | A file changed after it was written. Re-run the command that produced it (`analyze`, `generate-iac`, `generate-docs` all refresh checksums), or re-collect. |
| `verify` reports a citation mismatch at `path:line` | The spec file was edited after `analyze`. Re-run `analyze` (and `generate-docs`). |
| MCP client shows no tools / server exits | Use absolute paths for both the executable and `--cache-dir`; the directory must exist. Run the same command in a terminal to see errors on stderr. |
| `terraform plan` shows changes after `import.sh` | Expected for the items under "Known limitations" below. Review the diff; values marked `# REDACTED: set manually` must be filled in by hand. |
| `analyze --validate-diagram` says validation was skipped | The `drawio-ai` CLI is not on `PATH`. The XML is still checked for well-formedness. |

## Known limitations

- Only the 10 resource types above are collected. Patterns that involve other services (API Gateway, load balancers, CloudFront) are listed as undetectable in `analysis.json` rather than guessed.
- The analysis is rule-based and deterministic; there is no embedded LLM. Free-form explanations come from the AI agent connected over MCP.
- The sanitizer redacts by key name as well as by value, so harmless fields whose names contain `token`, `secret`, `password`, ... (for example EC2 `ClientToken`) appear as `[REDACTED]`.
- Terraform: redacted values (for example secret environment variables) are emitted with a `# REDACTED: set manually` comment and listed in `ignore_changes`; Lambda code is a `lambda_<name>.zip` placeholder; the RDS master password is not available. S3 lifecycle/CORS/website/ACL and DynamoDB TTL/point-in-time recovery are not mapped, and security group rules with different per-range descriptions are emitted without descriptions.
- The zero-change `terraform plan` guarantee is tested against a real account only by the opt-in live test (`AWS_INVENTORY_LIVE_TESTS=1`).
- Collection of a single resource is not incremental; re-run `collect` to refresh the whole Output_Dir.

## Development

See [docs/TESTING.md](docs/TESTING.md). In short:

```bash
venv/bin/python -m pytest                       # full suite
venv/bin/ruff check src tests && venv/bin/black --check src tests && venv/bin/mypy src
venv/bin/bandit -r src -ll
```

The specification (requirements, design, task list) lives in [.kiro/specs/aws-resource-inventory/](.kiro/specs/aws-resource-inventory/).

## License

MIT
