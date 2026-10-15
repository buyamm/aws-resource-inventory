"""
Tests for project scoping: tag seeds, region inference, dependency closure,
default-resource exclusion and the scope record.

Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5
"""

from __future__ import annotations

import json
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from src.aws_session import InventorySession
from src.cli import cli
from src.discovery import DiscoveredResource, ResourceDiscovery
from src.inventory import InventoryCollector
from src.resource_types import build_arn, parse_arn
from src.scope import (
    TagScopedDiscovery,
    exclude_defaults,
    extract_references,
    parse_project_tags,
    seed_regions,
)

ACCOUNT = "123456789012"
PROJECT = {"project": "orders"}


def _tag_project(session, ids) -> None:
    """Tag the Lambda function, the EC2 instance and the app role with project=orders."""
    region = "us-east-1"
    session.client("lambda", region_name=region).tag_resource(
        Resource=f"arn:aws:lambda:{region}:{ACCOUNT}:function:{ids.function_name}",
        Tags={"project": "orders", "env": "prod"},
    )
    session.client("ec2", region_name=region).create_tags(
        Resources=[ids.instance_id], Tags=[{"Key": "project", "Value": "orders"}]
    )
    session.client("iam").tag_role(
        RoleName="orders-app-role", Tags=[{"Key": "project", "Value": "orders"}]
    )


# ============================================================================
# Registry ARN helpers
# ============================================================================


@pytest.mark.parametrize(
    ("arn", "expected"),
    [
        (f"arn:aws:ec2:us-east-1:{ACCOUNT}:instance/i-1", ("aws_instance", "i-1", "us-east-1")),
        ("arn:aws:ec2:us-east-1::instance/i-1", ("aws_instance", "i-1", "us-east-1")),
        (f"arn:aws:ec2:eu-west-1:{ACCOUNT}:vpc/vpc-1", ("aws_vpc", "vpc-1", "eu-west-1")),
        (
            f"arn:aws:ec2:us-east-1:{ACCOUNT}:security-group/sg-1",
            ("aws_security_group", "sg-1", "us-east-1"),
        ),
        (
            f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:fn",
            ("aws_lambda_function", "fn", "us-east-1"),
        ),
        (f"arn:aws:rds:us-east-1:{ACCOUNT}:db:db1", ("aws_db_instance", "db1", "us-east-1")),
        (
            f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/aws/lambda/fn:*",
            ("aws_cloudwatch_log_group", "/aws/lambda/fn", "us-east-1"),
        ),
        (
            f"arn:aws:states:us-east-1:{ACCOUNT}:stateMachine:flow",
            ("aws_sfn_state_machine", "flow", "us-east-1"),
        ),
        (
            f"arn:aws:dynamodb:us-east-1:{ACCOUNT}:table/orders",
            ("aws_dynamodb_table", "orders", "us-east-1"),
        ),
        ("arn:aws:s3:::bucket-1", ("aws_s3_bucket", "bucket-1", "global")),
        (f"arn:aws:iam::{ACCOUNT}:role/app/svc-role", ("aws_iam_role", "svc-role", "global")),
        ("arn:aws:s3:::bucket-1/key", None),
        (
            f"arn:aws:ec2:us-east-1:{ACCOUNT}:subnet/subnet-1",
            ("aws_subnet", "subnet-1", "us-east-1"),
        ),
        (f"arn:aws:ec2:us-east-1:{ACCOUNT}:network-acl/acl-1", None),
        ("not-an-arn", None),
    ],
)
def test_scope_parse_arn_maps_supported_types_req_13_1(arn, expected):
    assert parse_arn(arn) == expected


def test_scope_build_arn_matches_discovery_format_req_13_3():
    assert build_arn("aws_vpc", "vpc-1", "us-east-1", ACCOUNT) == (
        f"arn:aws:ec2:us-east-1:{ACCOUNT}:vpc/vpc-1"
    )
    assert build_arn("aws_iam_role", "r", "global", ACCOUNT) == f"arn:aws:iam::{ACCOUNT}:role/r"
    assert build_arn("aws_s3_bucket", "b", "global", ACCOUNT) == "arn:aws:s3:::b"
    assert build_arn("aws_cloudwatch_log_group", "/a/b", "eu-west-1", ACCOUNT) == (
        f"arn:aws:logs:eu-west-1:{ACCOUNT}:log-group:/a/b"
    )


# ============================================================================
# Tag seed (Requirement 13.1)
# ============================================================================


def test_scope_parse_project_tags_req_13_1():
    assert parse_project_tags(["service=monetkit-prod", "environment=prod"]) == {
        "service": "monetkit-prod",
        "environment": "prod",
    }
    assert parse_project_tags(["k=a=b"]) == {"k": "a=b"}
    for bad in (["novalue"], ["=v"], ["k=v", "k=w"]):
        with pytest.raises(ValueError):
            parse_project_tags(bad)


def test_scope_seeds_from_tagging_api_req_13_1(sample_account):
    session, ids = sample_account
    _tag_project(session, ids)
    discovery = TagScopedDiscovery(
        InventorySession(session), PROJECT, regions=["us-east-1"], account_id=ACCOUNT
    )
    seeds = discovery.discover_all_resources()

    assert discovery.get_errors() == []
    assert discovery.get_api_calls() >= 3  # GetResources, ListRoles, ListRoleTags per role
    by_arn = {r.arn: r for r in seeds}
    assert set(by_arn) == {
        f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:{ids.function_name}",
        f"arn:aws:ec2:us-east-1:{ACCOUNT}:instance/{ids.instance_id}",
        ids.app_role_arn,
    }
    function = by_arn[f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:{ids.function_name}"]
    assert function.resource_type == "aws_lambda_function"
    assert function.resource_id == ids.function_name
    assert function.region == "us-east-1"
    assert function.tags["project"] == "orders"
    assert by_arn[ids.app_role_arn].region == "global"
    assert by_arn[ids.app_role_arn].resource_id == "orders-app-role"


def test_scope_tag_filters_are_anded_req_13_1(sample_account):
    session, ids = sample_account
    _tag_project(session, ids)
    seeds = TagScopedDiscovery(
        InventorySession(session),
        {"project": "orders", "env": "prod"},
        regions=["us-east-1"],
        account_id=ACCOUNT,
    ).discover_all_resources()
    assert [r.resource_id for r in seeds] == [ids.function_name]


# ============================================================================
# Regions (Requirement 13.2)
# ============================================================================


def _tagging_client(arns):
    client = Mock()
    client.can_paginate.return_value = False
    client.get_resources.return_value = {
        "ResourceTagMappingList": [
            {"ResourceARN": arn, "Tags": [{"Key": "project", "Value": "orders"}]} for arn in arns
        ]
    }
    return client


def test_scope_infers_regions_from_seed_req_13_2():
    clients = {
        "us-east-1": _tagging_client(["arn:aws:s3:::orders-assets"]),
        "eu-west-1": _tagging_client([f"arn:aws:lambda:eu-west-1:{ACCOUNT}:function:fn"]),
        "ap-southeast-1": _tagging_client([]),
    }
    ec2 = Mock()
    ec2.describe_regions.return_value = {"Regions": [{"RegionName": r} for r in clients]}
    iam = Mock()
    iam.can_paginate.return_value = False
    iam.list_roles.return_value = {"Roles": []}

    def client(service, region_name=None, **_):
        return {"ec2": ec2, "iam": iam}.get(service) or clients[region_name]

    session = Mock()
    session.client.side_effect = client
    discovery = TagScopedDiscovery(session, PROJECT, account_id=ACCOUNT)
    seeds = discovery.discover_all_resources()

    assert sorted(discovery.get_regions()) == sorted(clients)
    for tagging in clients.values():
        tagging.get_resources.assert_called_once_with(
            TagFilters=[{"Key": "project", "Values": ["orders"]}]
        )
    assert {(r.resource_type, r.region) for r in seeds} == {
        ("aws_s3_bucket", "global"),
        ("aws_lambda_function", "eu-west-1"),
    }
    # The bucket is global, so only eu-west-1 holds regional seeds.
    assert seed_regions(seeds, requested=()) == ["eu-west-1"]
    assert seed_regions(seeds, requested=("us-east-1", "eu-west-1")) == ["eu-west-1", "us-east-1"]


def test_scope_global_types_seeded_from_us_east_1_only_req_13_2():
    """With --region, us-east-1 is still queried, but only for global types."""
    us_east = _tagging_client(
        ["arn:aws:s3:::orders-assets", f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:other"]
    )
    eu_west = _tagging_client([f"arn:aws:lambda:eu-west-1:{ACCOUNT}:function:fn"])
    iam = Mock()
    iam.can_paginate.return_value = False
    iam.list_roles.return_value = {"Roles": []}

    def client(service, region_name=None, **_):
        if service == "iam":
            return iam
        return {"us-east-1": us_east, "eu-west-1": eu_west}[region_name]

    session = Mock()
    session.client.side_effect = client
    seeds = TagScopedDiscovery(
        session, PROJECT, regions=["eu-west-1"], account_id=ACCOUNT
    ).discover_all_resources()
    assert {r.arn for r in seeds} == {
        "arn:aws:s3:::orders-assets",
        f"arn:aws:lambda:eu-west-1:{ACCOUNT}:function:fn",
    }


def test_scope_tagging_failure_is_a_discovery_error_req_13_2():
    failing = Mock()
    failing.can_paginate.return_value = False
    failing.get_resources.side_effect = RuntimeError("boom")
    iam = Mock()
    iam.can_paginate.return_value = False
    iam.list_roles.return_value = {"Roles": []}
    session = Mock()
    session.client.side_effect = lambda service, region_name=None, **_: (
        iam if service == "iam" else failing
    )
    discovery = TagScopedDiscovery(session, PROJECT, regions=["us-east-1"], account_id=ACCOUNT)
    assert discovery.discover_all_resources() == []
    (error,) = discovery.get_errors()
    assert error.region == "us-east-1" and "boom" in error.message


# ============================================================================
# Dependency closure (Requirement 13.3)
# ============================================================================


def _seed(resource_type, resource_id, region="us-east-1"):
    return DiscoveredResource(
        resource_type=resource_type,
        resource_id=resource_id,
        arn=build_arn(resource_type, resource_id, region, ACCOUNT),
        region=region,
    )


def test_scope_closure_pulls_referenced_resources_req_13_3(sample_account):
    session, ids = sample_account
    seeds = [
        _seed("aws_lambda_function", ids.function_name),
        _seed("aws_instance", ids.instance_id),
    ]
    result = InventoryCollector(InventorySession(session), ACCOUNT).collect_all(seeds)

    assert result.errors == []
    collected = {(s.resource_type, s.arn) for s in result.specs}
    assert collected == {
        ("aws_lambda_function", seeds[0].arn),
        ("aws_instance", seeds[1].arn),
        ("aws_iam_role", ids.lambda_role_arn),
        (
            "aws_security_group",
            build_arn("aws_security_group", ids.security_group_id, "us-east-1", ACCOUNT),
        ),
        ("aws_vpc", build_arn("aws_vpc", ids.vpc_id, "us-east-1", ACCOUNT)),
        ("aws_subnet", build_arn("aws_subnet", ids.subnet_id, "us-east-1", ACCOUNT)),
    }
    referenced = {r.arn: r for r in result.referenced}
    assert set(referenced) == {arn for _, arn in collected} - {seeds[0].arn, seeds[1].arn}
    assert referenced[ids.lambda_role_arn].referenced_by == [f"{seeds[0].arn}#specifications.Role"]
    sg_arn = build_arn("aws_security_group", ids.security_group_id, "us-east-1", ACCOUNT)
    assert f"{seeds[1].arn}#specifications.SecurityGroups[0].GroupId" in (
        referenced[sg_arn].referenced_by
    )
    # The VPC is reached from the instance directly (and from the SG in the next wave).
    vpc_arn = build_arn("aws_vpc", ids.vpc_id, "us-east-1", ACCOUNT)
    assert referenced[vpc_arn].referenced_by == [f"{seeds[1].arn}#specifications.VpcId"]


def test_scope_closure_disabled_collects_only_given_resources_req_13_3(sample_account):
    session, ids = sample_account
    seeds = [_seed("aws_lambda_function", ids.function_name)]
    result = InventoryCollector(InventorySession(session), ACCOUNT).collect_all(
        seeds, follow_references=False
    )
    assert [s.arn for s in result.specs] == [seeds[0].arn]
    assert result.referenced == []


def test_scope_closure_follows_state_machine_role_and_log_group_req_13_3():
    """Reference rules read the exact spec fields (camelCase for Step Functions)."""
    from src.parser import ResourceSpec, SpecMetadata
    from src.scope import extract_references

    log_arn = f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/aws/vendedlogs/states/flow:*"
    spec = ResourceSpec(
        resource_type="aws_sfn_state_machine",
        arn=f"arn:aws:states:us-east-1:{ACCOUNT}:stateMachine:flow",
        region="us-east-1",
        account_id=ACCOUNT,
        specifications={
            "name": "flow",
            "roleArn": f"arn:aws:iam::{ACCOUNT}:role/flow-role",
            "loggingConfiguration": {
                "destinations": [{"cloudWatchLogsLogGroup": {"logGroupArn": log_arn}}]
            },
        },
        metadata=SpecMetadata("", "", "", ""),
    )
    refs = {r.arn: r for r in extract_references(spec, ACCOUNT)}
    assert set(refs) == {
        f"arn:aws:iam::{ACCOUNT}:role/flow-role",
        f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/aws/vendedlogs/states/flow",
    }
    log_group = refs[f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/aws/vendedlogs/states/flow"]
    assert log_group.resource_type == "aws_cloudwatch_log_group"
    assert log_group.resource_id == "/aws/vendedlogs/states/flow"
    assert log_group.referenced_by == [
        f"{spec.arn}#specifications.loggingConfiguration.destinations[0]"
        ".cloudWatchLogsLogGroup.logGroupArn"
    ]


def _spec_of(resource_type: str, resource_id: str, specifications: dict, region="us-east-1"):
    from src.parser import ResourceSpec, SpecMetadata

    return ResourceSpec(
        resource_type=resource_type,
        arn=build_arn(resource_type, resource_id, region, ACCOUNT),
        region=region,
        account_id=ACCOUNT,
        specifications=specifications,
        metadata=SpecMetadata("", "", "", ""),
    )


def _refs(spec) -> dict[tuple[str, str], list[str]]:
    return {
        (r.resource_type, r.resource_id): r.referenced_by for r in extract_references(spec, ACCOUNT)
    }


def test_scope_reference_rules_subnets_req_13_3():
    """Instances, Lambda functions and RDS instances pull in their subnets."""
    instance = _spec_of("aws_instance", "i-1", {"SubnetId": "subnet-a", "VpcId": "vpc-1"})
    assert ("aws_subnet", "subnet-a") in _refs(instance)
    function = _spec_of(
        "aws_lambda_function", "fn", {"VpcConfig": {"SubnetIds": ["subnet-a", "subnet-b"]}}
    )
    assert _refs(function)[("aws_subnet", "subnet-b")] == [
        f"{function.arn}#specifications.VpcConfig.SubnetIds[1]"
    ]
    db = _spec_of(
        "aws_db_instance",
        "db1",
        {"DBSubnetGroup": {"VpcId": "vpc-1", "Subnets": [{"SubnetIdentifier": "subnet-c"}]}},
    )
    assert _refs(db)[("aws_subnet", "subnet-c")] == [
        f"{db.arn}#specifications.DBSubnetGroup.Subnets[0].SubnetIdentifier"
    ]


def test_scope_reference_rules_network_types_req_13_3():
    route_table = _spec_of(
        "aws_route_table",
        "rtb-1",
        {
            "VpcId": "vpc-1",
            "Routes": [
                {"DestinationCidrBlock": "10.0.0.0/16", "GatewayId": "local"},
                {"DestinationCidrBlock": "0.0.0.0/0", "GatewayId": "igw-1"},
                {"DestinationPrefixListId": "pl-1", "GatewayId": "vpce-1"},
                {"DestinationCidrBlock": "10.9.0.0/16", "NatGatewayId": "nat-1"},
            ],
            "Associations": [{"Main": True}, {"Main": False, "SubnetId": "subnet-a"}],
        },
    )
    assert set(_refs(route_table)) == {
        ("aws_vpc", "vpc-1"),
        ("aws_internet_gateway", "igw-1"),
        ("aws_vpc_endpoint", "vpce-1"),
        ("aws_nat_gateway", "nat-1"),
        ("aws_subnet", "subnet-a"),
    }
    nat = _spec_of("aws_nat_gateway", "nat-1", {"SubnetId": "subnet-a", "VpcId": "vpc-1"})
    assert set(_refs(nat)) == {("aws_subnet", "subnet-a"), ("aws_vpc", "vpc-1")}
    igw = _spec_of("aws_internet_gateway", "igw-1", {"Attachments": [{"VpcId": "vpc-1"}]})
    assert set(_refs(igw)) == {("aws_vpc", "vpc-1")}
    endpoint = _spec_of(
        "aws_vpc_endpoint",
        "vpce-1",
        {
            "VpcId": "vpc-1",
            "RouteTableIds": ["rtb-1"],
            "SubnetIds": ["subnet-a"],
            "Groups": [{"GroupId": "sg-1"}],
        },
    )
    assert set(_refs(endpoint)) == {
        ("aws_vpc", "vpc-1"),
        ("aws_route_table", "rtb-1"),
        ("aws_subnet", "subnet-a"),
        ("aws_security_group", "sg-1"),
    }


def test_scope_reference_rules_load_balancer_and_edge_req_13_3():
    lb_arn = f"arn:aws:elasticloadbalancing:us-east-1:{ACCOUNT}:loadbalancer/app/web/abc"
    listener_arn = f"arn:aws:elasticloadbalancing:us-east-1:{ACCOUNT}:listener/app/web/abc/def"
    tg_arn = f"arn:aws:elasticloadbalancing:us-east-1:{ACCOUNT}:targetgroup/web-tg/123"
    cert_arn = f"arn:aws:acm:us-east-1:{ACCOUNT}:certificate/uuid-1"
    waf_arn = f"arn:aws:wafv2:us-east-1:{ACCOUNT}:global/webacl/web-acl/uuid-2"

    lb = _spec_of(
        "aws_lb",
        "app/web/abc",
        {
            "LoadBalancerArn": lb_arn,
            "VpcId": "vpc-1",
            "AvailabilityZones": [{"SubnetId": "subnet-a"}, {"SubnetId": "subnet-b"}],
            "SecurityGroups": ["sg-1"],
            "Listeners": [{"ListenerArn": listener_arn}],
        },
    )
    assert set(_refs(lb)) == {
        ("aws_vpc", "vpc-1"),
        ("aws_subnet", "subnet-a"),
        ("aws_subnet", "subnet-b"),
        ("aws_security_group", "sg-1"),
        ("aws_lb_listener", "app/web/abc/def"),
    }
    listener = _spec_of(
        "aws_lb_listener",
        "app/web/abc/def",
        {
            "LoadBalancerArn": lb_arn,
            "Certificates": [{"CertificateArn": cert_arn}],
            "DefaultActions": [
                {"Type": "forward", "TargetGroupArn": tg_arn},
                {
                    "Type": "forward",
                    "ForwardConfig": {"TargetGroups": [{"TargetGroupArn": tg_arn}]},
                },
            ],
        },
    )
    refs = _refs(listener)
    assert set(refs) == {
        ("aws_lb", "app/web/abc"),
        ("aws_acm_certificate", "uuid-1"),
        ("aws_lb_target_group", "web-tg/123"),
    }
    assert refs[("aws_lb_target_group", "web-tg/123")] == [
        f"{listener.arn}#specifications.DefaultActions[0].TargetGroupArn",
        f"{listener.arn}#specifications.DefaultActions[1].ForwardConfig.TargetGroups[0]"
        ".TargetGroupArn",
    ]
    target_group = _spec_of(
        "aws_lb_target_group", "web-tg/123", {"VpcId": "vpc-1", "LoadBalancerArns": [lb_arn]}
    )
    assert set(_refs(target_group)) == {("aws_vpc", "vpc-1"), ("aws_lb", "app/web/abc")}

    distribution = _spec_of(
        "aws_cloudfront_distribution",
        "E1",
        {
            "Id": "E1",
            "DistributionConfig": {
                "Origins": {
                    "Items": [
                        {"Id": "s3", "DomainName": "static-site.s3.us-east-1.amazonaws.com"},
                        {"Id": "alb", "DomainName": "web-1.us-east-1.elb.amazonaws.com"},
                        {"Id": "api", "DomainName": "api.example.com"},
                    ]
                },
                "WebACLId": waf_arn,
                "ViewerCertificate": {"ACMCertificateArn": cert_arn},
            },
        },
        region="global",
    )
    refs = _refs(distribution)
    assert set(refs) == {
        ("aws_s3_bucket", "static-site"),
        ("aws_wafv2_web_acl", "web-acl/uuid-2"),
        ("aws_acm_certificate", "uuid-1"),
    }
    assert refs[("aws_s3_bucket", "static-site")] == [
        f"{distribution.arn}#specifications.DistributionConfig.Origins.Items[0].DomainName"
    ]
    targets = {r.resource_type: r for r in extract_references(distribution, ACCOUNT)}
    assert targets["aws_acm_certificate"].region == "us-east-1"
    assert targets["aws_wafv2_web_acl"].region == "global"
    assert targets["aws_wafv2_web_acl"].arn == waf_arn


def test_scope_closure_follows_load_balancer_and_cloudfront_req_13_3(sample_account):
    session, ids = sample_account
    alb = DiscoveredResource(
        resource_type="aws_lb",
        resource_id=ids.alb_arn.split(":loadbalancer/")[1],
        arn=ids.alb_arn,
        region="us-east-1",
    )
    seeds = [alb, _seed("aws_cloudfront_distribution", ids.distribution_id, region="global")]
    result = InventoryCollector(InventorySession(session), ACCOUNT).collect_all(seeds)

    assert result.errors == []
    collected = {(s.resource_type, s.arn) for s in result.specs}
    assert {
        ("aws_lb_listener", ids.listener_arn),
        ("aws_lb_target_group", ids.target_group_arn),
        ("aws_acm_certificate", ids.certificate_arn),
        ("aws_wafv2_web_acl", ids.web_acl_arn),
        ("aws_s3_bucket", f"arn:aws:s3:::{ids.static_bucket_name}"),
        (
            "aws_security_group",
            build_arn("aws_security_group", ids.alb_security_group_id, "us-east-1", ACCOUNT),
        ),
        ("aws_vpc", build_arn("aws_vpc", ids.vpc_id, "us-east-1", ACCOUNT)),
    } <= collected
    subnets = {arn for kind, arn in collected if kind == "aws_subnet"}
    assert subnets == {
        build_arn("aws_subnet", s, "us-east-1", ACCOUNT) for s in ids.public_subnet_ids
    }
    referenced = {r.arn: r for r in result.referenced}
    assert referenced[ids.listener_arn].referenced_by == [
        f"{ids.alb_arn}#specifications.Listeners[0].ListenerArn"
    ]
    # The S3 origin bucket is named by the origin domain of the distribution.
    bucket = referenced[f"arn:aws:s3:::{ids.static_bucket_name}"]
    assert bucket.referenced_by[0].endswith(
        "#specifications.DistributionConfig.Origins.Items[0].DomainName"
    )


# ----------------------------------------------------------------------------
# Compute and data types (Requirements 13.3, 14.4)
# ----------------------------------------------------------------------------

ECS_ARN = f"arn:aws:ecs:us-east-1:{ACCOUNT}"
TG_ARN = f"arn:aws:elasticloadbalancing:us-east-1:{ACCOUNT}:targetgroup/web-tg/123"
ROLE = f"arn:aws:iam::{ACCOUNT}:role"


def test_scope_reference_rules_ecs_req_13_3():
    service = _spec_of(
        "aws_ecs_service",
        "web/api",
        {
            "clusterArn": f"{ECS_ARN}:cluster/web",
            "taskDefinition": f"{ECS_ARN}:task-definition/api:7",
            "loadBalancers": [{"targetGroupArn": TG_ARN, "containerName": "api"}],
            "networkConfiguration": {
                "awsvpcConfiguration": {"subnets": ["subnet-a"], "securityGroups": ["sg-app"]}
            },
        },
    )
    refs = _refs(service)
    assert set(refs) == {
        ("aws_ecs_cluster", "web"),
        ("aws_ecs_task_definition", "api:7"),
        ("aws_lb_target_group", "web-tg/123"),
        ("aws_subnet", "subnet-a"),
        ("aws_security_group", "sg-app"),
    }
    assert refs[("aws_lb_target_group", "web-tg/123")] == [
        f"{service.arn}#specifications.loadBalancers[0].targetGroupArn"
    ]

    image = f"{ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/team/api"
    task = _spec_of(
        "aws_ecs_task_definition",
        "api:7",
        {
            "taskRoleArn": f"{ROLE}/api-task",
            "executionRoleArn": f"{ROLE}/api-exec",
            "containerDefinitions": [
                {
                    "image": f"{image}:1.2.3",
                    "logConfiguration": {"options": {"awslogs-group": "/ecs/api"}},
                },
                # Public images and images of other accounts are not followed.
                {"image": "public.ecr.aws/nginx/nginx:1.27"},
                {"image": "999999999999.dkr.ecr.us-east-1.amazonaws.com/shared@sha256:abc"},
                {"image": f"{image}@sha256:def"},
            ],
        },
    )
    refs = _refs(task)
    assert set(refs) == {
        ("aws_iam_role", "api-task"),
        ("aws_iam_role", "api-exec"),
        ("aws_cloudwatch_log_group", "/ecs/api"),
        ("aws_ecr_repository", "team/api"),
    }
    assert refs[("aws_ecr_repository", "team/api")] == [
        f"{task.arn}#specifications.containerDefinitions[0].image",
        f"{task.arn}#specifications.containerDefinitions[3].image",
    ]
    assert refs[("aws_cloudwatch_log_group", "/ecs/api")] == [
        f"{task.arn}#specifications.containerDefinitions[0].logConfiguration.options.awslogs-group"
    ]


def test_scope_reference_rules_autoscaling_and_cache_req_13_3():
    asg = _spec_of(
        "aws_autoscaling_group",
        "workers",
        {
            "LaunchTemplate": {"LaunchTemplateId": "lt-1", "Version": "$Default"},
            "VPCZoneIdentifier": "subnet-a,subnet-b",
            "TargetGroupARNs": [TG_ARN],
        },
    )
    refs = _refs(asg)
    assert set(refs) == {
        ("aws_launch_template", "lt-1"),
        ("aws_subnet", "subnet-a"),
        ("aws_subnet", "subnet-b"),
        ("aws_lb_target_group", "web-tg/123"),
    }
    # One comma-separated property names both subnets.
    assert refs[("aws_subnet", "subnet-b")] == [f"{asg.arn}#specifications.VPCZoneIdentifier"]
    mixed = _spec_of(
        "aws_autoscaling_group",
        "spot",
        {
            "MixedInstancesPolicy": {
                "LaunchTemplate": {"LaunchTemplateSpecification": {"LaunchTemplateId": "lt-2"}}
            }
        },
    )
    assert set(_refs(mixed)) == {("aws_launch_template", "lt-2")}

    template = _spec_of(
        "aws_launch_template",
        "lt-1",
        {
            "LaunchTemplateData": {
                "SecurityGroupIds": ["sg-1"],
                "NetworkInterfaces": [{"Groups": ["sg-2"], "SubnetId": "subnet-c"}],
            }
        },
    )
    assert set(_refs(template)) == {
        ("aws_security_group", "sg-1"),
        ("aws_security_group", "sg-2"),
        ("aws_subnet", "subnet-c"),
    }

    cache = _spec_of(
        "aws_elasticache_replication_group",
        "cache",
        {
            "CacheCluster": {"SecurityGroups": [{"SecurityGroupId": "sg-cache"}]},
            "CacheSubnetGroup": {"VpcId": "vpc-1", "Subnets": [{"SubnetIdentifier": "subnet-a"}]},
        },
    )
    assert set(_refs(cache)) == {
        ("aws_security_group", "sg-cache"),
        ("aws_subnet", "subnet-a"),
        ("aws_vpc", "vpc-1"),
    }


def test_scope_reference_rules_messaging_and_events_req_13_3():
    fn = f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:worker"
    queue = f"arn:aws:sqs:us-east-1:{ACCOUNT}:jobs"
    rule = _spec_of(
        "aws_cloudwatch_event_rule",
        "nightly",
        {
            "Targets": [
                {"Id": "1", "Arn": f"{fn}:live"},  # alias-qualified Lambda ARN
                {"Id": "2", "Arn": queue},
                {"Id": "3", "Arn": f"{ECS_ARN}:cluster/web", "RoleArn": f"{ROLE}/events"},
                {"Id": "4", "Arn": f"arn:aws:states:us-east-1:{ACCOUNT}:stateMachine:flow"},
                {"Id": "5", "Arn": f"arn:aws:sns:us-east-1:{ACCOUNT}:alerts"},
            ]
        },
    )
    assert set(_refs(rule)) == {
        ("aws_lambda_function", "worker"),
        ("aws_sqs_queue", "jobs"),
        ("aws_ecs_cluster", "web"),
        ("aws_iam_role", "events"),
        ("aws_sfn_state_machine", "flow"),
        ("aws_sns_topic", "alerts"),
    }
    schedule = _spec_of(
        "aws_scheduler_schedule",
        "default/report",
        {"Target": {"Arn": queue, "RoleArn": f"{ROLE}/scheduler"}},
    )
    assert set(_refs(schedule)) == {("aws_sqs_queue", "jobs"), ("aws_iam_role", "scheduler")}
    topic = _spec_of(
        "aws_sns_topic",
        "events",
        {
            "Subscriptions": [
                {"Protocol": "sqs", "Endpoint": queue},
                {"Protocol": "lambda", "Endpoint": fn},
                {"Protocol": "email", "Endpoint": "ops@example.com"},
            ]
        },
    )
    assert set(_refs(topic)) == {("aws_sqs_queue", "jobs"), ("aws_lambda_function", "worker")}


def test_scope_references_to_other_accounts_are_not_followed_req_13_3():
    function = _spec_of("aws_lambda_function", "fn", {"Role": "arn:aws:iam::999999999999:role/x"})
    assert _refs(function) == {}


def test_scope_tag_seeds_skip_task_definition_revisions_req_14_4():
    """Task definitions enter through the services that run them, not through tags."""
    tagging = _tagging_client(
        [f"{ECS_ARN}:task-definition/api:1", f"{ECS_ARN}:service/web/api", "arn:aws:s3:::b"]
    )
    iam = Mock()
    iam.can_paginate.return_value = False
    iam.list_roles.return_value = {"Roles": []}
    session = Mock()
    session.client.side_effect = lambda service, region_name=None, **_: (
        iam if service == "iam" else tagging
    )
    seeds = TagScopedDiscovery(
        session, PROJECT, regions=["us-east-1"], account_id=ACCOUNT
    ).discover_all_resources()
    assert {r.resource_type for r in seeds} == {"aws_ecs_service", "aws_s3_bucket"}


def test_scope_closure_follows_ecs_service_req_13_3(sample_account):
    session, ids = sample_account
    seed = DiscoveredResource(
        resource_type="aws_ecs_service",
        resource_id="storefront/web",
        arn=ids.ecs_service_arn,
        region="us-east-1",
    )
    result = InventoryCollector(InventorySession(session), ACCOUNT).collect_all([seed])
    assert result.errors == []
    collected = {(s.resource_type, s.arn) for s in result.specs}
    assert {
        ("aws_ecs_cluster", ids.ecs_cluster_arn),
        ("aws_ecs_task_definition", ids.task_definition_arn),
        ("aws_lb_target_group", ids.target_group_arn),
        ("aws_iam_role", ids.task_role_arn),
        ("aws_iam_role", ids.execution_role_arn),
        ("aws_ecr_repository", ids.ecr_repository_arn),
        (
            "aws_cloudwatch_log_group",
            f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:{ids.ecs_log_group_name}",
        ),
        # ... and onwards: target group -> load balancer -> listener -> certificate.
        ("aws_lb", ids.alb_arn),
        ("aws_acm_certificate", ids.certificate_arn),
    } <= collected


# ============================================================================
# Default exclusion (Requirement 13.4)
# ============================================================================


def _discover_with_defaults(session):
    iam = session.client("iam")
    iam.create_role(
        RoleName="AWSServiceRoleForECS",
        Path="/aws-service-role/ecs.amazonaws.com/",
        AssumeRolePolicyDocument="{}",
    )
    return ResourceDiscovery(
        InventorySession(session), regions=["us-east-1"], account_id=ACCOUNT
    ).discover_all_resources()


def test_scope_excludes_default_vpc_and_service_linked_roles_req_13_4(sample_account):
    session, ids = sample_account
    resources = _discover_with_defaults(session)
    default_vpc = next(
        r for r in resources if r.resource_type == "aws_vpc" and r.resource_id != ids.vpc_id
    )

    kept, excluded = exclude_defaults(resources)

    excluded_ids = {(r.resource_type, r.resource_id) for r in excluded}
    default_sg = next(
        r.resource_id
        for r in resources
        if r.resource_type == "aws_security_group"
        and r.attributes.get("VpcId") == default_vpc.resource_id
    )
    default_subnets = {
        r.resource_id
        for r in resources
        if r.resource_type == "aws_subnet" and r.attributes.get("VpcId") == default_vpc.resource_id
    }
    default_route_tables = {
        r.resource_id
        for r in resources
        if r.resource_type == "aws_route_table"
        and r.attributes.get("VpcId") == default_vpc.resource_id
    }
    assert default_subnets and default_route_tables
    assert excluded_ids == {
        ("aws_vpc", default_vpc.resource_id),
        ("aws_security_group", default_sg),
        ("aws_iam_role", "AWSServiceRoleForECS"),
        *(("aws_subnet", s) for s in default_subnets),
        *(("aws_route_table", r) for r in default_route_tables),
    }
    kept_ids = {r.resource_id for r in kept}
    assert {ids.vpc_id, ids.security_group_id, "orders-app-role"} <= kept_ids
    # The default SG of a non-default VPC is project network, not account default.
    assert any(
        r.resource_type == "aws_security_group"
        and r.attributes.get("GroupName") == "default"
        and r.attributes.get("VpcId") == ids.vpc_id
        for r in kept
    )
    assert len(kept) + len(excluded) == len(resources)


def test_scope_excluded_default_kept_when_referenced_req_13_4(sample_account):
    session, _ = sample_account
    ec2 = session.client("ec2", region_name="us-east-1")
    default_vpc = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])["Vpcs"][0]
    default_sg = ec2.describe_security_groups(
        Filters=[
            {"Name": "vpc-id", "Values": [default_vpc["VpcId"]]},
            {"Name": "group-name", "Values": ["default"]},
        ]
    )["SecurityGroups"][0]["GroupId"]
    # No SubnetId: the instance lands in the default VPC (moto needs the SG spelled out).
    instance_id = ec2.run_instances(
        ImageId="ami-12c6146b", MinCount=1, MaxCount=1, SecurityGroupIds=[default_sg]
    )["Instances"][0]["InstanceId"]
    resources = _discover_with_defaults(session)
    kept, excluded = exclude_defaults(resources)
    assert any(r.resource_type == "aws_vpc" for r in excluded)

    result = InventoryCollector(InventorySession(session), ACCOUNT).collect_all(kept)

    pulled_back = {r.arn for r in result.referenced}
    instance = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]
    default_network = {
        r.arn for r in excluded if r.resource_type in ("aws_vpc", "aws_security_group")
    } | {build_arn("aws_subnet", instance["SubnetId"], "us-east-1", ACCOUNT)}
    assert default_network <= pulled_back
    assert {s.arn for s in result.specs} >= default_network
    assert all(
        ref.startswith(build_arn("aws_instance", instance_id, "us-east-1", ACCOUNT) + "#")
        for r in result.referenced
        if r.arn in default_network
        for ref in r.referenced_by
    )
    service_role = next(r for r in excluded if r.resource_type == "aws_iam_role")
    assert service_role.arn not in {s.arn for s in result.specs}
    # Default subnets nothing references stay excluded.
    unused = {r.arn for r in excluded if r.resource_type == "aws_subnet"} - default_network
    assert unused and not unused & {s.arn for s in result.specs}


def test_scope_excludes_default_vpc_network_req_13_4():
    def res(kind, rid, **attributes):
        return DiscoveredResource(
            kind,
            rid,
            build_arn(kind, rid, "us-east-1", ACCOUNT),
            "us-east-1",
            attributes=attributes,
        )

    resources = [
        res("aws_vpc", "vpc-default", IsDefault=True),
        res("aws_vpc", "vpc-app", IsDefault=False),
        res("aws_subnet", "subnet-d1", VpcId="vpc-default", DefaultForAz=True),
        res("aws_subnet", "subnet-d2", VpcId="vpc-default", DefaultForAz=False),
        res("aws_subnet", "subnet-app", VpcId="vpc-app", DefaultForAz=False),
        res("aws_route_table", "rtb-default", VpcId="vpc-default"),
        res("aws_route_table", "rtb-app", VpcId="vpc-app"),
        res("aws_internet_gateway", "igw-default", VpcIds=["vpc-default"]),
        res("aws_internet_gateway", "igw-app", VpcIds=["vpc-app"]),
        res("aws_internet_gateway", "igw-detached", VpcIds=[]),
    ]
    kept, excluded = exclude_defaults(resources)
    assert {r.resource_id for r in excluded} == {
        "vpc-default",
        "subnet-d1",
        "rtb-default",
        "igw-default",
    }
    # A subnet the user added to the default VPC is not an account default.
    assert {r.resource_id for r in kept} == {
        "vpc-app",
        "subnet-d2",
        "subnet-app",
        "rtb-app",
        "igw-app",
        "igw-detached",
    }


def test_scope_include_defaults_keeps_everything_req_13_4(sample_account):
    session, _ = sample_account
    resources = _discover_with_defaults(session)
    kept, excluded = exclude_defaults(resources, include_defaults=True)
    assert kept == resources and excluded == []


# ============================================================================
# Scope record (Requirement 13.5)
# ============================================================================


def test_scope_recorded_in_manifest_req_13_5(sample_account, tmp_path):
    session, ids = sample_account
    _tag_project(session, ids)
    out = tmp_path / "out"
    result = CliRunner().invoke(
        cli,
        [
            "--no-color",
            "collect",
            "--region",
            "us-east-1",
            "--project-tag",
            "project=orders",
            "--output-dir",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    report = json.loads((out / "collection_report.json").read_text(encoding="utf-8"))
    discovery = json.loads((out / "discovery.json").read_text(encoding="utf-8"))
    scope = manifest["scope"]
    assert scope == report["scope"]
    assert scope["mode"] == "project_tag"
    assert scope["project_tags"] == PROJECT
    assert scope["include_defaults"] is False
    assert scope["regions"] == ["us-east-1"]
    assert scope["seed_resources"] == 3
    referenced = {r["arn"]: r for r in scope["referenced"]}
    assert referenced[ids.lambda_role_arn]["resource_type"] == "aws_iam_role"
    assert referenced[ids.lambda_role_arn]["referenced_by"] == [
        f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:{ids.function_name}#specifications.Role"
    ]
    assert discovery["scope"]["project_tags"] == PROJECT
    assert manifest["total_resources"] == 3 + len(referenced)
    assert not (out / "aws_dynamodb_table").exists()


def test_scope_account_mode_records_excluded_defaults_req_13_5(sample_account, tmp_path):
    session, ids = sample_account
    out = tmp_path / "out"
    result = CliRunner().invoke(
        cli, ["--no-color", "collect", "--region", "us-east-1", "--output-dir", str(out)]
    )
    assert result.exit_code == 0, result.output
    scope = json.loads((out / "manifest.json").read_text(encoding="utf-8"))["scope"]
    assert scope["mode"] == "account"
    assert scope["project_tags"] == {}
    excluded = scope["excluded_defaults"]
    assert any(":vpc/" in arn for arn in excluded)
    assert not any(ids.vpc_id in arn for arn in excluded)
