"""
Live test (opt-in): generated Terraform shows zero changes against a real account.

Run with:  AWS_INVENTORY_LIVE_TESTS=1 venv/bin/python -m pytest -m aws tests/e2e/test_live_iac.py
Optional:  AWS_INVENTORY_LIVE_REGIONS=eu-west-1,us-east-1  (default: us-east-1)

Only read-only AWS calls are made; `terraform import` writes local state only.

Validates: Requirement 7.5
"""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from src.aws_session import create_session, get_account_id
from src.discovery import ResourceDiscovery
from src.iac_generator import IaCGenerator
from src.integrity import seal_specs
from src.inventory import InventoryCollector
from src.sanitizer import DataSanitizer

pytestmark = [pytest.mark.aws, pytest.mark.e2e, pytest.mark.slow]


@pytest.mark.skipif(shutil.which("terraform") is None, reason="terraform CLI not installed")
def test_live_iac_terraform_plan_zero_changes_req_7_5(tmp_path):
    regions = os.environ.get("AWS_INVENTORY_LIVE_REGIONS", "us-east-1").split(",")
    session = create_session()
    account_id = get_account_id(session)
    resources = ResourceDiscovery(
        session, regions=regions, account_id=account_id
    ).discover_all_resources()
    result = InventoryCollector(session, account_id).collect_all(resources)
    specs = seal_specs(result.specs, DataSanitizer())

    generator = IaCGenerator()
    generator.generate_terraform(specs, target_dir=tmp_path)
    subprocess.run(["terraform", "init", "-input=false", "-no-color"], cwd=tmp_path, check=True)
    subprocess.run(["bash", "import.sh"], cwd=tmp_path, check=True)

    ok, message = generator.verify_terraform_plan(tmp_path)
    assert ok, message
