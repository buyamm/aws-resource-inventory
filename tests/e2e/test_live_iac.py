"""
Live test (opt-in): generated Terraform shows zero changes against a real account.

Run with:  AWS_INVENTORY_LIVE_TESTS=1 venv/bin/python -m pytest -m aws tests/e2e/test_live_iac.py
Optional:  AWS_INVENTORY_LIVE_REGIONS=eu-west-1,us-east-1  (default: us-east-1)
           AWS_INVENTORY_LIVE_PROJECT_TAGS=service=shop,environment=prod  (project scope)

Only read-only AWS calls are made. Nothing is applied: the plan is saved and every
resource change must be a no-op (pending imports only). State stays local
(``backend_override.tf`` replaces the S3 backend).

Validates: Requirements 7.2, 7.5, 16.1
"""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest
from click.testing import CliRunner

from src.cli import cli
from src.iac_generator import IaCGenerator

pytestmark = [pytest.mark.aws, pytest.mark.e2e, pytest.mark.slow]


def _terraform(*args: str, cwd) -> None:
    result = subprocess.run(
        ["terraform", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, f"terraform {' '.join(args)}:\n{result.stdout}{result.stderr}"


@pytest.mark.skipif(shutil.which("terraform") is None, reason="terraform CLI not installed")
def test_live_iac_terraform_plan_zero_changes_req_7_5(tmp_path):
    out = tmp_path / "output"
    args = ["collect", "--output-dir", str(out)]
    for region in os.environ.get("AWS_INVENTORY_LIVE_REGIONS", "us-east-1").split(","):
        args += ["--region", region.strip()]
    for pair in os.environ.get("AWS_INVENTORY_LIVE_PROJECT_TAGS", "").split(","):
        if pair.strip():
            args += ["--project-tag", pair.strip()]
    runner = CliRunner()
    result = runner.invoke(cli, args)
    assert result.exit_code in (0, 1), result.output
    result = runner.invoke(cli, ["generate-iac", "--output-dir", str(out)])
    assert result.exit_code == 0, result.output

    terraform_dir = out / "terraform"
    env_dir = next((terraform_dir / "envs").iterdir())
    (env_dir / "backend_override.tf").write_text(
        'terraform {\n  backend "local" {}\n}\n', encoding="utf-8"
    )
    _terraform("fmt", "-check", "-recursive", cwd=terraform_dir)
    _terraform("init", "-input=false", "-no-color", cwd=env_dir)
    _terraform("validate", "-no-color", cwd=env_dir)
    ok, message = IaCGenerator().verify_terraform_plan(env_dir)
    assert ok, message
