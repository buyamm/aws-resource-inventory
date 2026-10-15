# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Source of truth

The spec lives in `.kiro/specs/aws-resource-inventory/`: `requirements.md` (numbered acceptance criteria), `design.md` (contracts: spec schema per type, output layout, MCP tools, CLI, Terraform mapping, citation/verification), and `tasks.md` (ordered TDD task list; tick `[x]` when done). Read the relevant requirement and design section before changing behavior, and keep the three files consistent with the code. When the user asks to "continue the tasks", take the next unchecked top-level task in `tasks.md`, then commit and push it on completion (one commit per top-level task, message format given in the task).

## Commands

Python 3.11 virtualenv in `./venv` (always call its interpreter explicitly):

```bash
venv/bin/pip install -r requirements-dev.txt && venv/bin/pip install -e .   # setup
venv/bin/python -m pytest                                  # full suite (pytest.ini: --maxfail=1, warnings are errors)
venv/bin/python -m pytest tests/unit/test_parser.py::TestX::test_y   # single test
venv/bin/python -m pytest -k property                      # property tests (hypothesis, 100 examples via conftest profile)
venv/bin/python -m pytest -m "not slow" --cov=src --cov-report=term-missing
AWS_INVENTORY_LIVE_TESTS=1 venv/bin/python -m pytest -m aws   # live tests against the real credential chain (opt-in)
venv/bin/ruff check src tests && venv/bin/black --check src tests && venv/bin/mypy src
venv/bin/bandit -r src -ll
```

`pytest.ini` is the effective pytest config (pyproject has none). `tests/conftest.py` forces fake AWS credentials unless `AWS_INVENTORY_LIVE_TESTS=1`, so ordinary tests can never reach a real account.

## Architecture

The package import root is `src` (`from src.parser import ResourceSpec`); the console script is `aws-inventory = src.cli:main`.

The pipeline is split into an online phase and an offline phase:
- **Online (needs AWS creds):** `discovery.ResourceDiscovery` lists resources per region in parallel → `inventory.InventoryCollector` drives one `collector.SpecCollector` per (service, region) client → `integrity.seal_specs` sanitizes and sets `metadata.checksum` → `output_generator.OutputGenerator` writes the Output_Dir.
- **Offline (reads Output_Dir only):** `analysis_engine` (relationships/patterns/security findings with citations), `diagram_generator` (.drawio), `iac_generator` (Terraform + import/verify scripts), `documentation`, `integrity.verify_output_dir`, and the MCP server.

Cross-cutting rules that span several modules:
- `ResourceSpec.resource_type` is always a canonical id = Terraform type name (`aws_instance`, `aws_db_instance`, `aws_sfn_state_machine`, ...). Type names, resource ids and file names come from `src/resource_types.py`; don't hard-code alternates.
- `specifications` keeps AWS API field names (PascalCase, logs/stepfunctions camelCase) minus `ResponseMetadata`; S3 uses `bucket-*` sub-keys. Analysis, IaC and diagram rules read these exact fields (see design.md "Specification schema").
- Per-resource files at `<out>/<type>/<region>/<file_id>.json` are the cache the MCP server reads; other top-level dirs (`raw_responses/`, `analysis/`, `terraform/`, ...) must never be treated as specs.
- Everything written to disk, returned by MCP or logged passes through `DataSanitizer`. `mcp_server.py` must not import boto3/botocore.
- Citations (`resource_arn, spec_file, property_path, source_checksum, evidence_value`) must resolve against the sealed spec files; `aws-inventory verify` checks them.
- Collector errors return `Result.err(...)` instead of raising; retries (3 attempts, 1 s/2 s backoff) live only in `collector.with_retry`, with botocore retries disabled.

## Conventions

- TDD: write or adjust the failing test first. Test names carry the requirement id: `test_<component>_<behavior>_req_<X>_<Y>`; property tests are `test_property_..._req_<X>_<Y>`.
- AWS mocking uses moto 4.x per-service decorators (`mock_s3`, `mock_ec2`, ...), not moto 5's `mock_aws`.
- `instruction.md` is the Vietnamese end-user guide; keep it in sync with the real CLI.

## Skills

Vendored third-party skills live in `.claude/skills/` (sources, commits and licenses in `.claude/skills/README.md`). Load them before touching these areas:
- `src/diagram_generator.py` or anything `.drawio`: `aws-architecture-diagram` (group nesting, verified `mxgraph.aws4.*` stencils, layout/edge rules, `templates/three-tier-web-app.drawio`) and `drawio` (XML rules, ELK layout, export CLI).
- `src/iac_generator.py` or generated HCL: `terraform-style-guide` (files, naming, variable/output contracts), `refactor-module` (module interfaces), `terraform-search-import` (`import` blocks), `terraform-skill` (modules/env layout, state, security scanning).
The skills describe hand-authored output; the generators must apply the same rules deterministically from the sealed specs (no guessed values, every element traceable to a spec).
