# Accuracy and Security

This document explains why the output of `aws-inventory` can be trusted: how every statement is tied to collected data and checked mechanically (accuracy), how credentials and secrets are protected (security), and how fast collection is (benchmark).

## Accuracy: no statement without a citation

The system does not embed or call an LLM. Relationships, patterns and security findings come from fixed rules in `src/analysis_engine.py` that read exact AWS API field names in the collected specs. An AI agent connected over MCP may phrase things freely, but it gets its facts from the same cited data.

### Spec checksums

Before a spec is written, `integrity.seal_specs` sanitizes it and stores its **Spec_Checksum** in `metadata.checksum`:

```
Spec_Checksum = sha256( json.dumps(specifications, sort_keys=True, separators=(",", ":"), ensure_ascii=False) )
```

The checksum covers the sanitized `specifications` only, so it does not change when timestamps or file formatting change, but it does change when any collected value changes.

### Citation format

Every relationship, pattern and finding in `analysis/analysis.json` carries at least one citation. This example is from [examples/output/](../examples/output/analysis/analysis.json):

```json
{
  "finding_type": "UNRESTRICTED_SECURITY_GROUP_ACCESS",
  "severity": "HIGH",
  "description": "Security group 'sg-7c880b8c4789c2216' allows ingress from 0.0.0.0/0 on tcp port 22.",
  "citation": {
    "resource_arn": "arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c880b8c4789c2216",
    "spec_file": "aws_security_group/us-east-1/sg-7c880b8c4789c2216.json",
    "property_path": "specifications.IpPermissions[0].IpRanges[0]",
    "source_checksum": "50964fd4d7dab9c6a168d909449fa5c327b7ad577bd9773adb9ec4df36fcecf5",
    "evidence_value": {"CidrIp": "0.0.0.0/0"}
  }
}
```

| Field | Meaning |
|---|---|
| `spec_file` | Spec file path relative to the Output_Dir |
| `property_path` | Path inside that file: `key(.key)*` with `[index]` for list items |
| `source_checksum` | Spec_Checksum of the file when the statement was made |
| `evidence_value` | The value found at `property_path` |

Citations are built by one function, `cite(spec, property_path)`, which reads `evidence_value` from the spec itself, so a citation always resolves at the time it is created. A property-based test (`test_property_citations_resolve_req_8_5`) checks this for generated specs. `docs/infrastructure.md` uses the same citations in compact form: `[cite: <spec_file>#<property_path> sha256:<first 12 hex chars>]`.

Confidence scores are fixed per rule: 1.0 for direct id references, 0.95 for role ARN/name matches, 0.9 for security group attachments, and 0.85 for environment-variable substring matches. A pattern's confidence is the minimum of its supporting relationships. Patterns no rule can detect from the collected data (API Gateway + Lambda + DynamoDB, EC2 + Load Balancer with instances registered directly in the target group) are listed in `undetectable_patterns` with the reason and are never asserted.

### Verification method

`aws-inventory verify --output-dir <dir>` (`integrity.verify_output_dir`) checks:

1. **File integrity.** Every file listed in `checksums.sha256` exists and its SHA-256 matches. Every command that writes files refreshes this list, so it always describes the latest run.
2. **Citations.** For every citation in `analysis/analysis.json`:
   - `spec_file` exists;
   - the Spec_Checksum recomputed from its `specifications` equals `source_checksum`;
   - `property_path` resolves inside the file;
   - the resolved value equals `evidence_value`.

On success it prints `OK: <n> files, <m> citations verified` and exits 0. Otherwise it prints one line per discrepancy, `path:line: reason`, where `line` is the 1-based line of the cited property in the pretty-printed JSON (0 if the property or file no longer exists), and exits 1.

If someone edits a cited value in a spec file after `analyze`, `verify` reports the file's checksum mismatch and the citation discrepancy with the line of the edited value. The end-to-end test `test_e2e_verify_detects_tampering` does exactly this.

### MCP guardrails against unsupported answers

- The MCP server answers only from the Output_Dir. `get-resource-spec` and `analyze-activity-flow` with an ARN that was not collected return an error telling the user to run `aws-inventory collect`, so an agent cannot get "facts" about resources outside the data.
- `analyze-activity-flow` and `generate-documentation` return the same citations, so the agent can quote `spec_file` and `property_path` and the user can check them with `verify`.

## Security measures

### Credentials (Requirement 9.1–9.3)

- Credentials come only from the boto3 default chain (environment, shared config/credentials files, SSO, container/instance role), optionally with `--profile`. There are no credential options on the command line.
- With `--role-arn` (and optional `--external-id`), the tool calls `sts:AssumeRole` with session name `aws-resource-inventory` and uses the temporary credentials for every later call.
- Credentials are never written to files or passed to log calls. The CLI installs one log handler on stderr whose `SanitizingFilter` runs the Data_Sanitizer on each message, including exception tracebacks, and additionally replaces the literal access key, secret key and session token of the active session; with `--role-arn` that covers both the assumed-role credentials and the credentials that called `sts:AssumeRole`. Console output passes through the same filter. Tests check that none of these values appear in stdout, stderr, logs or any file in the Output_Dir.

### Read-only access (Requirement 9.4)

- The tool only calls operations whose names start with `Describe`, `List` or `Get`, plus `sts:AssumeRole` and `sts:GetCallerIdentity`. `test_cli_only_read_only_api_calls_req_9_4` records every botocore call during a full `collect` and fails on any other operation.
- [iam-policy.json](iam-policy.json) is the minimal policy. `test_cli_api_calls_covered_by_iam_policy_req_9_4` checks that it allows every call made during `collect`. The `sts:AssumeRole` statement is only needed with `--role-arn`; narrow its `Resource` to the role you assume.
- botocore's own retries are disabled (`total_max_attempts=1`). The collector makes at most 3 attempts per call, so a run cannot multiply into retry storms.

### Data sanitization (Requirement 9.5, 9.6)

`DataSanitizer` (`src/sanitizer.py`) redacts:

| Detected | Placeholder |
|---|---|
| A string containing an AWS access key ID (`AKIA`/`ASIA` + 16 characters), or the value of a key containing `access_key_id` | `[REDACTED_AWS_KEY]` |
| The value of a key containing `secret_access_key` | `[REDACTED_AWS_SECRET]` |
| A string containing a PEM private key header | `[REDACTED_PRIVATE_KEY]` |
| The string value of a key containing `password`, `passwd`, `secret`, `private_key`, `token`, `api_key`, `credential` or `userdata` (keys containing `public` are exempt; launch template `UserData` is base64, so it cannot be scanned) | `[REDACTED]` |
| The `value` of a `{name, value}` entry (ECS container environment) whose `name` matches the previous row | `[REDACTED]` |

Keys, list lengths and nesting are always preserved, and sanitizing twice gives the same result (property tests). A dict or list referenced from several places (or from itself) is sanitized once and every reference gets the sanitized copy, so a shared object can never pass through unredacted. Names like `KeyName`, `KmsKeyId` and `KeyType` are not redacted. Each redaction is logged with its JSON path and placeholder, never the original value.

The sanitizer runs on per-resource JSON and Markdown, aggregates, raw responses, reports, analysis and documentation files, every MCP response, and every log record. In the example output the Lambda environment variable `DB_PASSWORD` and the ECS container variable `SESSION_SECRET` are stored as `[REDACTED]`. The Terraform generator turns placeholders into a `# REDACTED: set manually` comment plus a `lifecycle.ignore_changes` entry, so secrets are never written into IaC.

### MCP server isolation (Requirement 5, 9.7)

- `mcp-serve` deletes every `AWS_*` environment variable and points `AWS_SHARED_CREDENTIALS_FILE` and `AWS_CONFIG_FILE` at a non-existent path before it starts serving.
- `src/mcp_server.py` does not import `boto3` or `botocore`; a test imports it in a fresh interpreter and inspects `sys.modules`.
- Only the four whitelisted tools are accepted. Unknown operations, unknown parameters and wrong parameter types are rejected with `Unauthorized ...` / `Invalid parameters ...` and recorded in a security log (`{timestamp, operation, reason}`, also logged at WARNING).
- At most 10 requests are accepted in any sliding 1-second window; further requests get `rate_limited`.
- Only files matching `<registered type>/<region>/*.json` are read; reports, raw responses and Terraform files are never served.

### Development safeguards

- Tests run with fake credentials forced by `tests/conftest.py` and moto mocks. `AWS_ACCOUNT_ID_ENDPOINT_MODE=disabled` stops botocore's account-based DynamoDB endpoint from bypassing moto. Live tests are opt-in (`AWS_INVENTORY_LIVE_TESTS=1`, marker `aws`).
- `scripts/demo.py` applies the same fake credentials and endpoint setting in its default (moto) mode.
- `bandit -r src -ll` (medium and high severity) runs in CI and is clean. The remaining low-severity notes are intentional: `subprocess` runs fixed commands (`terraform plan`, `drawio-ai validate`) without a shell, `xml.etree` only parses the `.drawio` file the tool wrote itself, `assert` narrows a type in the collector, and `hunter2-demo` is the deliberately insecure Lambda variable of the moto sample account.

## Performance benchmark

Measured with `scripts/benchmark.py` on 2026-10-15 after the compute and data types were added (Apple M1, 8 cores, Python 3.11.9, moto 4.x, default 10 workers). The script creates **1000 resources in 17 regions** in moto (per region: moto's default VPC, security group, subnets and main route table, 9 instances, 9 security groups, 9 log groups, 9 DynamoDB tables, 5 Lambda functions, 4 state machines, 4 RDS instances; plus 30 IAM roles and 31 S3 buckets), adds a fixed delay to every AWS API call the CLI makes (a botocore `before-call` hook on each client of `InventorySession`), runs `aws-inventory collect` in-process and reads the phase timings from `collection_report.json`.

| Phase | 100 ms per API call | 0 ms (moto overhead only) | Target |
|---|---|---|---|
| Discovery (17 regions) | 12.73 s | 6.87 s | < 5 minutes (Requirement 1.5) |
| Collection (1000 specs) | 19.29 s = 51.9 resources/s | 2.17 s = 460.3 resources/s | ≥ 10 resources/s |
| Output (1000 spec files + reports) | 1.87 s | 2.04 s | - |
| `generate-iac` on the 1000 specs | - | 0.87 s (whole command, 2026-10-14 run) | < 10 s |

Both runs made 2150 API calls (every one delayed in the first run), collected 1000/1000 specs and had no failures. Discovery time is dominated by moto building each region's backend, not by the simulated latency: regions are scanned concurrently and each region needs about one list call per resource type (27 regional list calls per region since the compute and data types, plus one `ListRules` per event bus). Collection with 100 ms latency is bounded by `calls per resource × latency / workers` (≈ 1700 collection calls × 0.1 s / 10 ≈ 17 s plus moto time).

Reproduce:

```bash
python scripts/benchmark.py                               # 1000 resources, 17 regions, 100 ms per call
python scripts/benchmark.py --latency-ms 0 --json result.json
```

The script exits 1 when a target is missed. `tests/e2e/test_benchmark.py` runs it at a small scale (40 resources, 2 regions) and checks that every API call was delayed. `test_discovery_completes_under_5_minutes_req_1_5` (tests/unit/test_discovery.py) additionally checks 1000 instances across 20 regions from mocked clients. Every real run records its own phase timings in `collection_report.json` and `summary_report.md`.

The MCP server accepts at most 10 requests per sliding second by design (rate limit), so its throughput target is a limit, checked by the rate-limit tests rather than measured.
