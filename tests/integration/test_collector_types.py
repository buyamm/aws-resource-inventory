"""
Integration tests (moto): SpecCollector produces the per-type Specifications
schema defined in design.md for every Supported_Resource_Type.

Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.6, 3.3, 14.1, 14.4
"""

from __future__ import annotations

import pytest

from src.collector import SpecCollector

pytestmark = pytest.mark.integration

ACCOUNT = "123456789012"
REGION = "us-east-1"


def _collect(session, service, resource_type, resource_id, arn, region=REGION):
    client = session.client(service, region_name="us-east-1" if region == "global" else region)
    collector = SpecCollector(api_client=client)
    result = collector.collect_resource(resource_type, resource_id, arn, region, ACCOUNT)
    assert result.is_ok(), result.error if result.is_err() else ""
    spec = result.value
    assert spec.resource_type == resource_type
    assert spec.region == region
    assert spec.account_id == ACCOUNT
    assert spec.arn == arn
    assert "ResponseMetadata" not in spec.specifications
    assert spec.raw_response, "raw_response must keep the full API responses (Req 2.6)"
    for response in spec.raw_response.values():
        assert "ResponseMetadata" in response
    return spec, collector


def test_integration_collector_instance_spec_req_2_3(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:instance/{ids.instance_id}"
    spec, _ = _collect(session, "ec2", "aws_instance", ids.instance_id, arn)
    specs = spec.specifications
    assert specs["InstanceId"] == ids.instance_id
    assert specs["SecurityGroups"][0]["GroupId"] == ids.security_group_id
    assert "NetworkInterfaces" in specs and "BlockDeviceMappings" in specs
    assert {"Key": "Name", "Value": "orders-web-1"} in specs["Tags"]
    assert isinstance(specs["LaunchTime"], str), "datetimes must be ISO strings"


def test_integration_collector_vpc_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:vpc/{ids.vpc_id}"
    spec, _ = _collect(session, "ec2", "aws_vpc", ids.vpc_id, arn)
    assert spec.specifications["VpcId"] == ids.vpc_id
    assert spec.specifications["CidrBlock"] == "10.0.0.0/16"
    assert spec.specifications["EnableDnsSupport"] is True
    assert isinstance(spec.specifications["EnableDnsHostnames"], bool)
    assert set(spec.raw_response) == {
        "DescribeVpcs",
        "DescribeVpcAttribute:enableDnsSupport",
        "DescribeVpcAttribute:enableDnsHostnames",
    }


def test_integration_collector_security_group_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:security-group/{ids.security_group_id}"
    spec, _ = _collect(session, "ec2", "aws_security_group", ids.security_group_id, arn)
    perms = spec.specifications["IpPermissions"]
    assert any(r["CidrIp"] == "0.0.0.0/0" for p in perms for r in p.get("IpRanges", []))
    assert spec.specifications["VpcId"] == ids.vpc_id


def test_integration_collector_lambda_spec_with_tags_req_2_4(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:lambda:{REGION}:{ACCOUNT}:function:{ids.function_name}"
    spec, _ = _collect(session, "lambda", "aws_lambda_function", ids.function_name, arn)
    specs = spec.specifications
    assert specs["FunctionName"] == ids.function_name
    assert specs["Role"] == ids.lambda_role_arn
    assert specs["Environment"]["Variables"]["TABLE_NAME"] == "orders"
    assert specs["Tags"] == {"team": "orders"}


def test_integration_collector_db_instance_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:rds:{REGION}:{ACCOUNT}:db:{ids.db_instance_id}"
    spec, _ = _collect(session, "rds", "aws_db_instance", ids.db_instance_id, arn)
    specs = spec.specifications
    assert specs["DBInstanceIdentifier"] == ids.db_instance_id
    assert specs["Engine"] == "postgres"
    assert specs["VpcSecurityGroups"][0]["VpcSecurityGroupId"] == ids.security_group_id


def test_integration_collector_log_group_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:logs:{REGION}:{ACCOUNT}:log-group:{ids.log_group_name}"
    spec, _ = _collect(session, "logs", "aws_cloudwatch_log_group", ids.log_group_name, arn)
    assert spec.specifications["logGroupName"] == ids.log_group_name
    assert spec.specifications["retentionInDays"] == 14
    assert spec.specifications["tags"] == {"team": "orders"}


def test_integration_collector_state_machine_spec_req_2_1(sample_account):
    session, ids = sample_account
    spec, _ = _collect(
        session, "stepfunctions", "aws_sfn_state_machine", "order-flow", ids.state_machine_arn
    )
    assert spec.specifications["name"] == "order-flow"
    assert spec.specifications["roleArn"] == ids.lambda_role_arn
    assert '"StartAt"' in spec.specifications["definition"]
    assert spec.specifications["tags"] == [{"key": "team", "value": "orders"}]


def test_integration_collector_dynamodb_spec_req_2_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:dynamodb:{REGION}:{ACCOUNT}:table/{ids.table_name}"
    spec, _ = _collect(session, "dynamodb", "aws_dynamodb_table", ids.table_name, arn)
    specs = spec.specifications
    assert specs["TableName"] == ids.table_name
    assert specs["KeySchema"] == [{"AttributeName": "order_id", "KeyType": "HASH"}]
    assert specs["Tags"] == [{"Key": "team", "Value": "orders"}]


def test_integration_collector_s3_spec_req_2_2(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:s3:::{ids.bucket_name}"
    spec, collector = _collect(
        session, "s3", "aws_s3_bucket", ids.bucket_name, arn, region="global"
    )
    specs = spec.specifications
    assert specs["Name"] == ids.bucket_name
    assert specs["bucket-versioning"]["Status"] == "Enabled"
    assert any(
        g["Grantee"].get("URI", "").endswith("AllUsers") for g in specs["bucket-acl"]["Grants"]
    )
    # Not configured in the sample account → omitted and not counted as failures (Req 2.2)
    for absent in (
        "bucket-cors",
        "bucket-website",
        "bucket-policy",
        "bucket-lifecycle-configuration",
    ):
        assert absent not in specs
    assert not collector.get_errors()


def test_integration_collector_iam_role_spec_req_2_1(sample_account):
    session, ids = sample_account
    spec, _ = _collect(
        session, "iam", "aws_iam_role", "order-lambda-role", ids.lambda_role_arn, region="global"
    )
    specs = spec.specifications
    assert specs["RoleName"] == "order-lambda-role"
    assert specs["AssumeRolePolicyDocument"]["Statement"][0]["Principal"] == {
        "Service": "lambda.amazonaws.com"
    }
    assert specs["AttachedPolicies"] == []
    assert specs["InlinePolicies"]["too-broad"]["Statement"][0]["Action"] == "*"


# ============================================================================
# Network, edge and load-balancing types (Requirement 14.1)
# ============================================================================


def _collect_clean(session, service, resource_type, resource_id, arn, region=REGION):
    spec, collector = _collect(session, service, resource_type, resource_id, arn, region)
    assert collector.get_errors() == [], [(e.operation, e.detail) for e in collector.get_errors()]
    return spec


def test_integration_collector_subnet_spec_req_14_1(sample_account):
    session, ids = sample_account
    subnet_id = ids.public_subnet_ids[0]
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:subnet/{subnet_id}"
    spec = _collect_clean(session, "ec2", "aws_subnet", subnet_id, arn)
    s = spec.specifications
    assert s["SubnetId"] == subnet_id
    assert s["VpcId"] == ids.vpc_id
    assert s["CidrBlock"] == "10.0.10.0/24"
    assert s["AvailabilityZone"] == "us-east-1a"
    assert s["DefaultForAz"] is False
    assert {"Key": "Name", "Value": "storefront-public-a"} in s["Tags"]


def test_integration_collector_route_table_spec_req_14_1(sample_account):
    session, ids = sample_account
    rtb = ids.public_route_table_id
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:route-table/{rtb}"
    spec = _collect_clean(session, "ec2", "aws_route_table", rtb, arn)
    s = spec.specifications
    assert s["RouteTableId"] == rtb and s["VpcId"] == ids.vpc_id
    assert any(r.get("GatewayId") == ids.internet_gateway_id for r in s["Routes"])
    assert {a["SubnetId"] for a in s["Associations"] if "SubnetId" in a} == set(
        ids.public_subnet_ids
    )


def test_integration_collector_internet_gateway_spec_req_14_1(sample_account):
    session, ids = sample_account
    igw = ids.internet_gateway_id
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:internet-gateway/{igw}"
    spec = _collect_clean(session, "ec2", "aws_internet_gateway", igw, arn)
    assert spec.specifications["InternetGatewayId"] == igw
    assert spec.specifications["Attachments"][0]["VpcId"] == ids.vpc_id


def test_integration_collector_nat_gateway_spec_req_14_1(sample_account):
    session, ids = sample_account
    nat = ids.nat_gateway_id
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:natgateway/{nat}"
    spec = _collect_clean(session, "ec2", "aws_nat_gateway", nat, arn)
    assert spec.specifications["NatGatewayId"] == nat
    assert spec.specifications["SubnetId"] == ids.public_subnet_ids[0]
    assert spec.specifications["NatGatewayAddresses"][0]["AllocationId"]


def test_integration_collector_vpc_endpoint_spec_req_14_1(sample_account):
    session, ids = sample_account
    vpce = ids.vpc_endpoint_id
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:vpc-endpoint/{vpce}"
    spec = _collect_clean(session, "ec2", "aws_vpc_endpoint", vpce, arn)
    s = spec.specifications
    assert s["VpcEndpointId"] == vpce
    assert s["ServiceName"] == f"com.amazonaws.{REGION}.s3"
    assert s["RouteTableIds"] == [ids.private_route_table_id]


def test_integration_collector_load_balancer_spec_req_14_1(sample_account):
    session, ids = sample_account
    raw_id = ids.alb_arn.split(":loadbalancer/")[1]
    spec = _collect_clean(session, "elbv2", "aws_lb", raw_id, ids.alb_arn)
    s = spec.specifications
    assert s["LoadBalancerArn"] == ids.alb_arn
    assert s["LoadBalancerName"] == "storefront-alb"
    assert s["Scheme"] == "internet-facing"
    assert {z["SubnetId"] for z in s["AvailabilityZones"]} == set(ids.public_subnet_ids)
    assert s["SecurityGroups"] == [ids.alb_security_group_id]
    assert any(a["Key"] == "deletion_protection.enabled" for a in s["Attributes"])
    assert {"Key": "service", "Value": "storefront"} in s["Tags"]
    assert [listener["ListenerArn"] for listener in s["Listeners"]] == [ids.listener_arn]


def test_integration_collector_listener_spec_req_14_1(sample_account):
    session, ids = sample_account
    raw_id = ids.listener_arn.split(":listener/")[1]
    spec = _collect_clean(session, "elbv2", "aws_lb_listener", raw_id, ids.listener_arn)
    s = spec.specifications
    assert s["ListenerArn"] == ids.listener_arn
    assert s["LoadBalancerArn"] == ids.alb_arn
    assert s["Port"] == 443 and s["Protocol"] == "HTTPS"
    assert s["Certificates"][0]["CertificateArn"] == ids.certificate_arn
    assert s["DefaultActions"][0]["TargetGroupArn"] == ids.target_group_arn


def test_integration_collector_target_group_spec_req_14_1(sample_account):
    session, ids = sample_account
    raw_id = ids.target_group_arn.split(":targetgroup/")[1]
    spec = _collect_clean(session, "elbv2", "aws_lb_target_group", raw_id, ids.target_group_arn)
    s = spec.specifications
    assert s["TargetGroupName"] == "storefront-tg"
    assert s["VpcId"] == ids.vpc_id
    assert s["LoadBalancerArns"] == [ids.alb_arn]
    assert any(a["Key"] == "deregistration_delay.timeout_seconds" for a in s["Attributes"])
    assert "Tags" in s


def test_integration_collector_cloudfront_distribution_spec_req_14_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:cloudfront::{ACCOUNT}:distribution/{ids.distribution_id}"
    spec = _collect_clean(
        session, "cloudfront", "aws_cloudfront_distribution", ids.distribution_id, arn, "global"
    )
    s = spec.specifications
    assert s["Id"] == ids.distribution_id
    assert s["DomainName"].endswith(".cloudfront.net")
    config = s["DistributionConfig"]
    assert {o["Id"] for o in config["Origins"]["Items"]} == {"static-s3", "web-alb"}
    assert config["WebACLId"] == ids.web_acl_arn
    # moto 4.x ignores ViewerCertificate.ACMCertificateArn; the certificate reference
    # is covered by the analysis and scope unit tests.
    assert "ViewerCertificate" in config
    assert config["Aliases"]["Items"] == ["shop.example.com"]
    assert {"Key": "service", "Value": "storefront"} in s["Tags"]
    # Distributions only: no edge-location or IP-range data is collected (Req 14.1).
    assert set(spec.raw_response) == {"GetDistribution", "ListTagsForResource"}


def test_integration_collector_route53_zone_spec_req_14_1(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:route53:::hostedzone/{ids.hosted_zone_id}"
    spec = _collect_clean(session, "route53", "aws_route53_zone", ids.hosted_zone_id, arn, "global")
    s = spec.specifications
    assert s["Id"] == f"/hostedzone/{ids.hosted_zone_id}"
    assert s["Name"] == "example.com."
    aliases = {
        r["Name"]: r["AliasTarget"]["DNSName"]
        for r in s["ResourceRecordSets"]
        if "AliasTarget" in r
    }
    assert set(aliases) == {"shop.example.com.", "api.example.com."}
    assert {"Key": "service", "Value": "storefront"} in s["Tags"]


def test_integration_collector_acm_certificate_spec_req_14_1(sample_account):
    session, ids = sample_account
    raw_id = ids.certificate_arn.split(":certificate/")[1]
    spec = _collect_clean(session, "acm", "aws_acm_certificate", raw_id, ids.certificate_arn)
    s = spec.specifications
    assert s["CertificateArn"] == ids.certificate_arn
    assert s["DomainName"] == "shop.example.com"
    assert {"Key": "service", "Value": "storefront"} in s["Tags"]


def test_integration_collector_wafv2_web_acl_spec_req_14_1(sample_account):
    session, ids = sample_account
    raw_id = ids.web_acl_arn.split("/webacl/")[1]
    spec = _collect_clean(session, "wafv2", "aws_wafv2_web_acl", raw_id, ids.web_acl_arn, "global")
    s = spec.specifications
    assert s["Name"] == "storefront-waf"
    assert s["ARN"] == ids.web_acl_arn
    assert "DefaultAction" in s and "VisibilityConfig" in s
    assert {"Key": "service", "Value": "storefront"} in s["Tags"]
    assert "LockToken" not in s


# ============================================================================
# Compute and data types (Requirement 14.4)
# ============================================================================


def test_integration_collector_ecs_cluster_spec_req_14_4(sample_account):
    session, ids = sample_account
    spec = _collect_clean(session, "ecs", "aws_ecs_cluster", "storefront", ids.ecs_cluster_arn)
    s = spec.specifications
    assert s["clusterArn"] == ids.ecs_cluster_arn and s["clusterName"] == "storefront"
    assert {"name": "containerInsights", "value": "enabled"} in s["settings"]
    assert {"key": "service", "value": "storefront"} in s["tags"]


def test_integration_collector_ecs_service_spec_req_14_4(sample_account):
    session, ids = sample_account
    spec = _collect_clean(session, "ecs", "aws_ecs_service", "storefront/web", ids.ecs_service_arn)
    s = spec.specifications
    assert s["serviceArn"] == ids.ecs_service_arn
    assert s["clusterArn"] == ids.ecs_cluster_arn
    assert s["taskDefinition"] == ids.task_definition_arn
    assert s["loadBalancers"][0]["targetGroupArn"] == ids.target_group_arn
    assert {"key": "service", "value": "storefront"} in s["tags"]
    # The service event log is operational history, not configuration (raw_response keeps it).
    assert "events" not in s


def test_integration_collector_ecs_task_definition_spec_req_14_4(sample_account):
    session, ids = sample_account
    spec = _collect_clean(
        session, "ecs", "aws_ecs_task_definition", "storefront-web:1", ids.task_definition_arn
    )
    s = spec.specifications
    assert s["taskDefinitionArn"] == ids.task_definition_arn
    assert s["family"] == "storefront-web" and s["revision"] == 1
    assert s["taskRoleArn"] == ids.task_role_arn
    assert s["executionRoleArn"] == ids.execution_role_arn
    container = s["containerDefinitions"][0]
    assert container["image"].endswith("/storefront-web:1.4.2")
    assert container["logConfiguration"]["options"]["awslogs-group"] == ids.ecs_log_group_name
    assert {"key": "service", "value": "storefront"} in s["tags"]


def test_integration_collector_ecr_repository_spec_req_14_4(sample_account):
    session, ids = sample_account
    spec = _collect_clean(
        session, "ecr", "aws_ecr_repository", "storefront-web", ids.ecr_repository_arn
    )
    s = spec.specifications
    assert s["repositoryName"] == "storefront-web"
    assert s["repositoryUri"].endswith("/storefront-web")
    assert s["imageScanningConfiguration"] == {"scanOnPush": True}
    assert {"Key": "service", "Value": "storefront"} in s["tags"]


def test_integration_collector_autoscaling_group_spec_req_14_4(sample_account):
    session, ids = sample_account
    # A closure target only knows the wildcard ARN; the collector records the real one.
    wildcard = (
        f"arn:aws:autoscaling:{REGION}:{ACCOUNT}:autoScalingGroup:*:"
        "autoScalingGroupName/storefront-workers"
    )
    client = session.client("autoscaling", region_name=REGION)
    result = SpecCollector(client).collect_resource(
        "aws_autoscaling_group", "storefront-workers", wildcard, REGION, ACCOUNT
    )
    assert result.is_ok()
    spec = result.value
    assert spec.arn == ids.autoscaling_group_arn
    s = spec.specifications
    assert s["AutoScalingGroupName"] == "storefront-workers"
    assert s["LaunchTemplate"]["LaunchTemplateId"] == ids.launch_template_id
    assert s["VPCZoneIdentifier"] == ids.subnet_id
    assert s["MinSize"] == 1 and s["MaxSize"] == 2


def test_integration_collector_launch_template_spec_req_14_4(sample_account):
    session, ids = sample_account
    lt = ids.launch_template_id
    arn = f"arn:aws:ec2:{REGION}:{ACCOUNT}:launch-template/{lt}"
    spec = _collect_clean(session, "ec2", "aws_launch_template", lt, arn)
    s = spec.specifications
    assert s["LaunchTemplateId"] == lt
    assert s["LaunchTemplateName"] == "storefront-worker"
    # The data of the default version (Req 14.4).
    assert s["LaunchTemplateData"]["InstanceType"] == "t3.small"
    assert s["LaunchTemplateData"]["SecurityGroupIds"] == [ids.app_security_group_id]
    assert {"Key": "service", "Value": "storefront"} in s["Tags"]


def test_integration_collector_elasticache_replication_group_spec_req_14_4(sample_account):
    session, ids = sample_account
    arn = f"arn:aws:elasticache:{REGION}:{ACCOUNT}:replicationgroup:storefront-cache"
    spec = _collect_clean(
        session, "elasticache", "aws_elasticache_replication_group", "storefront-cache", arn
    )
    s = spec.specifications
    assert s["ReplicationGroupId"] == "storefront-cache"
    assert s["MemberClusters"] == ["storefront-cache-001", "storefront-cache-002"]
    # Subnet group, security groups and engine version live on the member clusters.
    assert s["CacheCluster"]["CacheClusterId"] == "storefront-cache-001"
    assert s["CacheCluster"]["SecurityGroups"][0]["SecurityGroupId"] == ids.app_security_group_id
    assert s["CacheSubnetGroup"]["VpcId"] == ids.vpc_id
    assert [x["SubnetIdentifier"] for x in s["CacheSubnetGroup"]["Subnets"]] == [ids.subnet_id]
    assert {"Key": "service", "Value": "storefront"} in s["TagList"]


def test_integration_collector_sqs_queue_spec_req_14_4(sample_account):
    session, ids = sample_account
    spec = _collect_clean(session, "sqs", "aws_sqs_queue", "storefront-orders", ids.queue_arn)
    s = spec.specifications
    assert s["QueueUrl"] == ids.queue_url
    assert s["Attributes"]["QueueArn"] == ids.queue_arn
    assert s["Attributes"]["VisibilityTimeout"] == "60"
    assert s["Tags"] == {"service": "storefront"}


def test_integration_collector_sns_topic_spec_req_14_4(sample_account):
    session, ids = sample_account
    spec = _collect_clean(session, "sns", "aws_sns_topic", "storefront-events", ids.topic_arn)
    s = spec.specifications
    assert s["Attributes"]["TopicArn"] == ids.topic_arn
    assert s["Attributes"]["DisplayName"] == "Storefront events"
    assert [x["Endpoint"] for x in s["Subscriptions"]] == [ids.queue_arn]
    assert {"Key": "service", "Value": "storefront"} in s["Tags"]


def test_integration_collector_event_rule_spec_req_14_4(sample_account):
    session, ids = sample_account
    spec = _collect_clean(
        session, "events", "aws_cloudwatch_event_rule", "storefront-nightly-report",
        ids.event_rule_arn,
    )  # fmt: skip
    s = spec.specifications
    assert s["Name"] == "storefront-nightly-report"
    assert s["ScheduleExpression"] == "cron(0 2 * * ? *)"
    assert [t["Arn"] for t in s["Targets"]] == [
        f"arn:aws:lambda:{REGION}:{ACCOUNT}:function:{ids.function_name}"
    ]
    assert {"Key": "service", "Value": "storefront"} in s["Tags"]


def test_integration_collector_scheduler_schedule_spec_req_14_4(sample_account):
    session, ids = sample_account
    spec = _collect_clean(
        session, "scheduler", "aws_scheduler_schedule", "default/storefront-cleanup",
        ids.schedule_arn,
    )  # fmt: skip
    s = spec.specifications
    assert s["Name"] == "storefront-cleanup" and s["GroupName"] == "default"
    assert s["Target"]["Arn"] == ids.queue_arn
    assert s["ScheduleExpression"] == "rate(1 hour)"
