"""
Integration tests (moto): discovery → InventoryCollector over the sample account.

Validates: Requirements 1.1, 1.3, 2.1, 3.3, 12.2, 12.4
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from src.aws_session import InventorySession
from src.discovery import ResourceDiscovery
from src.inventory import InventoryCollector
from src.resource_types import REGISTRY

pytestmark = pytest.mark.integration


def test_integration_inventory_collects_all_discovered_types_req_2_1(sample_account):
    session, _ = sample_account
    inv_session = InventorySession(session)
    resources = ResourceDiscovery(inv_session, regions=["us-east-1"]).discover_all_resources()
    assert {r.resource_type for r in resources} == set(REGISTRY)

    result = InventoryCollector(inv_session, account_id="123456789012").collect_all(resources)
    assert not result.errors, result.errors
    assert len(result.specs) == len(resources)
    assert {s.resource_type for s in result.specs} == set(REGISTRY)
    assert result.api_calls >= len(resources)
    assert all(op.status == "success" or op.status == "not_configured" for op in result.operations)


def test_inventory_sets_region_and_account_req_3_3(sample_account):
    session, _ = sample_account
    inv_session = InventorySession(session)
    resources = ResourceDiscovery(
        inv_session, regions=["us-east-1"], account_id="123456789012"
    ).discover_all_resources()
    result = InventoryCollector(inv_session, account_id="123456789012").collect_all(resources)
    for spec in result.specs:
        assert spec.account_id == "123456789012"
        expected_region = (
            "global" if REGISTRY[spec.resource_type].scope == "global" else "us-east-1"
        )
        assert spec.region == expected_region
        assert "unknown" not in spec.arn


def test_inventory_records_failed_operations_req_12_2(sample_account):
    session, ids = sample_account
    inv_session = InventorySession(session)
    resources = ResourceDiscovery(inv_session, regions=["us-east-1"]).discover_all_resources()

    from botocore.client import BaseClient

    original = BaseClient._make_api_call

    def deny_get_function(self, operation_name, api_params):
        if operation_name == "GetFunction":
            raise ClientError(
                {
                    "Error": {"Code": "AccessDeniedException", "Message": "no"},
                    "ResponseMetadata": {"HTTPStatusCode": 403},
                },
                operation_name,
            )
        return original(self, operation_name, api_params)

    with patch.object(BaseClient, "_make_api_call", deny_get_function):
        result = InventoryCollector(inv_session, account_id="123456789012").collect_all(resources)

    assert len(result.specs) == len(resources) - 1
    (error,) = result.errors
    assert error.resource_arn.endswith(f"function:{ids.function_name}")
    assert error.operation == "GetFunction"
    assert error.error_type == "AccessDenied"
    assert error.retry_count == 0
    failed = [op for op in result.operations if op.status == "denied"]
    assert [op.operation for op in failed] == ["GetFunction"]
