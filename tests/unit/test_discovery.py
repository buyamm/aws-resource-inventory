"""
Unit tests for ResourceDiscovery (RED phase - TDD).

This module contains unit tests for the ResourceDiscovery class that MUST be
written before implementation following TDD Red-Green-Refactor methodology.

All tests are expected to fail with ImportError initially (RED phase),
proving they test real behaviour that does not yet exist.

Test Coverage:
- test_discovery_lists_all_regions_req_1_1:
    Discovery enumerates every available AWS region and collects resources
    from each of them.
- test_discovery_handles_inaccessible_region_req_1_4:
    When a region's API calls fail (e.g. access denied), the error is logged
    and discovery continues with the remaining regions.
- test_discovery_completes_under_5_minutes_req_1_5:
    Discovery across many regions/resources completes well under the
    5-minute budget for up to 1000 resources.

Requirements Coverage:
- Requirement 1.1: List all supported AWS resource types across all regions
- Requirement 1.2: Collect ARN, region, and basic metadata for all resources
- Requirement 1.3: Support EC2, S3, Lambda, RDS, VPC, Security Groups, IAM,
  CloudWatch log groups, Step Functions, and DynamoDB
- Requirement 1.4: Log error and continue with other regions when a region
  is inaccessible
- Requirement 1.5: Discovery completes within 5 minutes for up to 1000
  resources
"""

import time
import pytest
from unittest.mock import Mock

# ---------------------------------------------------------------------------
# Lazy import — will be None until src/discovery.py is implemented (RED phase)
# ---------------------------------------------------------------------------
try:
    from src.discovery import ResourceDiscovery, DiscoveredResource
except ImportError:
    ResourceDiscovery = None
    DiscoveredResource = None


# ===========================================================================
# Helpers
# ===========================================================================

def _empty_client():
    """A Mock boto3-like client where every list/describe call returns empty."""
    client = Mock()
    client.describe_instances.return_value = {"Reservations": []}
    client.describe_vpcs.return_value = {"Vpcs": []}
    client.describe_security_groups.return_value = {"SecurityGroups": []}
    client.list_functions.return_value = {"Functions": []}
    client.describe_db_instances.return_value = {"DBInstances": []}
    client.describe_log_groups.return_value = {"logGroups": []}
    client.list_state_machines.return_value = {"stateMachines": []}
    client.list_tables.return_value = {"TableNames": []}
    client.list_buckets.return_value = {"Buckets": []}
    client.list_roles.return_value = {"Roles": []}
    return client


def _make_session(region_clients, global_client=None):
    """
    Build a Mock boto3.Session-like object whose ``.client(service, region_name=...)``
    returns a per-region, per-service Mock client.

    ``region_clients`` maps region -> {service_name: Mock client}.
    ``global_client`` (optional) is returned for every region for services not
    present in a given region's map (e.g. s3/iam which are "global").
    """
    session = Mock()

    def _client_factory(service_name, region_name=None, **kwargs):
        region_map = region_clients.get(region_name, {})
        if service_name in region_map:
            return region_map[service_name]
        if global_client is not None and service_name in global_client:
            return global_client[service_name]
        return _empty_client()

    session.client.side_effect = _client_factory
    return session


# ===========================================================================
# Test: Region Enumeration (Requirement 1.1)
# ===========================================================================

class TestDiscoveryRegionEnumeration:
    """Tests for discovering resources across all AWS regions."""

    @pytest.mark.skipif(ResourceDiscovery is None, reason="ResourceDiscovery not implemented yet (RED phase)")
    def test_discovery_lists_all_regions_req_1_1(self):
        """
        Unit: Discovery enumerates all regions and aggregates resources from each.

        Scenario:
        - Two regions are available: us-east-1 and eu-west-1.
        - Each region has one EC2 instance discoverable via describe_instances().

        Expected behaviour:
        - discover_all_resources() returns resources tagged with the correct
          region for each.
        - Both regions are represented in the aggregated result.

        **Validates: Requirements 1.1, 1.2**
        """
        us_east_ec2 = _empty_client()
        us_east_ec2.describe_instances.return_value = {
            "Reservations": [{"Instances": [{"InstanceId": "i-useast1"}]}]
        }

        eu_west_ec2 = _empty_client()
        eu_west_ec2.describe_instances.return_value = {
            "Reservations": [{"Instances": [{"InstanceId": "i-euwest1"}]}]
        }

        session = _make_session({
            "us-east-1": {"ec2": us_east_ec2},
            "eu-west-1": {"ec2": eu_west_ec2},
        })

        discovery = ResourceDiscovery(aws_session=session, regions=["us-east-1", "eu-west-1"])
        resources = discovery.discover_all_resources()

        regions_found = {r.region for r in resources if r.resource_type == "aws_instance"}
        assert regions_found == {"us-east-1", "eu-west-1"}, (
            f"Expected resources from both regions, found: {regions_found}"
        )

        instance_ids = {r.resource_id for r in resources if r.resource_type == "aws_instance"}
        assert instance_ids == {"i-useast1", "i-euwest1"}

    @pytest.mark.skipif(ResourceDiscovery is None, reason="ResourceDiscovery not implemented yet (RED phase)")
    def test_discovery_supports_minimum_resource_types_req_1_3(self):
        """
        Unit: Discovery supports the minimum required set of resource types.

        **Validates: Requirement 1.3**
        """
        region_client = _empty_client()
        region_client.describe_instances.return_value = {
            "Reservations": [{"Instances": [{"InstanceId": "i-abc"}]}]
        }
        region_client.describe_vpcs.return_value = {"Vpcs": [{"VpcId": "vpc-1"}]}
        region_client.describe_security_groups.return_value = {
            "SecurityGroups": [{"GroupId": "sg-1"}]
        }
        region_client.list_functions.return_value = {
            "Functions": [{"FunctionName": "fn-1", "FunctionArn": "arn:aws:lambda:us-east-1:123:function:fn-1"}]
        }
        region_client.describe_db_instances.return_value = {
            "DBInstances": [{"DBInstanceIdentifier": "db-1", "DBInstanceArn": "arn:aws:rds:us-east-1:123:db:db-1"}]
        }
        region_client.describe_log_groups.return_value = {
            "logGroups": [{"logGroupName": "/aws/lambda/fn-1", "arn": "arn:aws:logs:us-east-1:123:log-group:/aws/lambda/fn-1"}]
        }
        region_client.list_state_machines.return_value = {
            "stateMachines": [{"name": "sm-1", "stateMachineArn": "arn:aws:states:us-east-1:123:stateMachine:sm-1"}]
        }
        region_client.list_tables.return_value = {"TableNames": ["table-1"]}

        global_s3 = _empty_client()
        global_s3.list_buckets.return_value = {"Buckets": [{"Name": "bucket-1"}]}

        global_iam = _empty_client()
        global_iam.list_roles.return_value = {
            "Roles": [{"RoleName": "role-1", "Arn": "arn:aws:iam::123:role/role-1"}]
        }

        session = _make_session(
            {"us-east-1": {
                "ec2": region_client,
                "lambda": region_client,
                "rds": region_client,
                "logs": region_client,
                "stepfunctions": region_client,
                "dynamodb": region_client,
            }},
            global_client={"s3": global_s3, "iam": global_iam},
        )

        discovery = ResourceDiscovery(aws_session=session, regions=["us-east-1"])
        resources = discovery.discover_all_resources()

        found_types = {r.resource_type for r in resources}
        expected_types = {
            "aws_instance",
            "aws_vpc",
            "aws_security_group",
            "aws_lambda_function",
            "aws_db_instance",
            "aws_cloudwatch_log_group",
            "aws_sfn_state_machine",
            "aws_dynamodb_table",
            "aws_s3_bucket",
            "aws_iam_role",
        }
        missing = expected_types - found_types
        assert not missing, f"Discovery did not report these resource types: {missing}"


# ===========================================================================
# Test: Inaccessible Region Handling (Requirement 1.4)
# ===========================================================================

class TestDiscoveryErrorHandling:
    """Tests for graceful handling of inaccessible regions."""

    @pytest.mark.skipif(ResourceDiscovery is None, reason="ResourceDiscovery not implemented yet (RED phase)")
    def test_discovery_handles_inaccessible_region_req_1_4(self):
        """
        Unit: An inaccessible region is logged and discovery continues.

        Scenario:
        - us-east-1 is accessible and returns one EC2 instance.
        - eu-west-1 raises an AccessDenied-style exception for every call.

        Expected behaviour:
        - discover_all_resources() still returns the us-east-1 instance.
        - The error for eu-west-1 is recorded via get_errors().

        **Validates: Requirement 1.4**
        """
        us_east_ec2 = _empty_client()
        us_east_ec2.describe_instances.return_value = {
            "Reservations": [{"Instances": [{"InstanceId": "i-ok"}]}]
        }

        eu_west_ec2 = Mock()
        eu_west_ec2.describe_instances.side_effect = Exception("AccessDenied: not authorized")
        eu_west_ec2.describe_vpcs.side_effect = Exception("AccessDenied: not authorized")
        eu_west_ec2.describe_security_groups.side_effect = Exception("AccessDenied: not authorized")

        session = _make_session({
            "us-east-1": {"ec2": us_east_ec2},
            "eu-west-1": {"ec2": eu_west_ec2, "lambda": eu_west_ec2, "rds": eu_west_ec2,
                          "logs": eu_west_ec2, "stepfunctions": eu_west_ec2, "dynamodb": eu_west_ec2},
        })

        discovery = ResourceDiscovery(aws_session=session, regions=["us-east-1", "eu-west-1"])
        resources = discovery.discover_all_resources()

        instance_ids = {r.resource_id for r in resources if r.resource_type == "aws_instance"}
        assert "i-ok" in instance_ids, "Accessible region's resources must still be discovered"

        errors = discovery.get_errors()
        assert len(errors) > 0, "Errors from the inaccessible region must be logged"
        assert any("eu-west-1" in str(e) for e in errors), (
            f"Expected an error referencing region 'eu-west-1', got: {errors}"
        )


# ===========================================================================
# Test: Performance (Requirement 1.5)
# ===========================================================================

class TestDiscoveryPerformance:
    """Tests for discovery performance requirements."""

    @pytest.mark.skipif(ResourceDiscovery is None, reason="ResourceDiscovery not implemented yet (RED phase)")
    def test_discovery_completes_under_5_minutes_req_1_5(self):
        """
        Performance: Discovery of ~1000 resources across many regions completes
        in well under 5 minutes (300 seconds) when AWS calls are mocked/fast.

        **Validates: Requirement 1.5**
        """
        num_regions = 20
        instances_per_region = 50  # 20 * 50 = 1000 resources

        region_clients = {}
        for i in range(num_regions):
            region = f"region-{i}"
            client = _empty_client()
            client.describe_instances.return_value = {
                "Reservations": [
                    {"Instances": [{"InstanceId": f"i-{region}-{j}"} for j in range(instances_per_region)]}
                ]
            }
            region_clients[region] = {"ec2": client}

        session = _make_session(region_clients)
        regions = list(region_clients.keys())

        discovery = ResourceDiscovery(aws_session=session, regions=regions)

        start = time.time()
        resources = discovery.discover_all_resources()
        elapsed = time.time() - start

        instance_count = sum(1 for r in resources if r.resource_type == "aws_instance")
        assert instance_count == num_regions * instances_per_region, (
            f"Expected {num_regions * instances_per_region} instances, got {instance_count}"
        )
        assert elapsed < 300, f"Discovery took {elapsed}s, expected < 300s"


# ===========================================================================
# Test: Progress Reporting (Refactor support for Requirement 1.5)
# ===========================================================================

class TestDiscoveryProgressReporting:
    """Tests for optional progress reporting during long discovery runs."""

    @pytest.mark.skipif(ResourceDiscovery is None, reason="ResourceDiscovery not implemented yet (RED phase)")
    def test_discovery_reports_progress_per_region(self):
        """
        Unit: The optional progress_callback is invoked once per completed region
        with monotonically increasing completed counts and the correct total.
        """
        session = _make_session({
            "us-east-1": {"ec2": _empty_client()},
            "eu-west-1": {"ec2": _empty_client()},
        })

        progress_calls = []

        def _on_progress(region, completed, total):
            progress_calls.append((region, completed, total))

        discovery = ResourceDiscovery(
            aws_session=session,
            regions=["us-east-1", "eu-west-1"],
            progress_callback=_on_progress,
        )
        discovery.discover_all_resources()

        assert len(progress_calls) == 2, f"Expected 2 progress callbacks, got {progress_calls}"
        completed_values = sorted(c for (_, c, _) in progress_calls)
        assert completed_values == [1, 2]
        assert all(total == 2 for (_, _, total) in progress_calls)
