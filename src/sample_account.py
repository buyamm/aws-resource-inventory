"""
Sample AWS account builder used by the demo script and the test suite.

Creates at least one resource of each Supported_Resource_Type in ``us-east-1`` (plus
the global S3 buckets, IAM roles, CloudFront distribution, Route 53 zone and
CloudFront-scope web ACL), including deliberately insecure settings so the
Analysis_Engine has something to report:

- IAM role ``order-lambda-role`` with an inline ``Allow * on *`` policy (CRITICAL)
- S3 bucket with a ``public-read`` ACL (HIGH)
- Security group allowing SSH from ``0.0.0.0/0`` (HIGH)

The "storefront" web stack (tag ``service=storefront``) lives in the same VPC:
Route 53 ``shop.example.com`` -> CloudFront (WAF, ACM certificate) -> ALB in two
public subnets -> HTTPS listener -> target group, plus an S3 origin for static files,
an internet gateway, a NAT gateway and an S3 gateway endpoint on the private route
table of the instance subnet.

Only call this inside a moto mock (``scripts/demo.py`` and tests do). It issues
create calls and must never be pointed at a real account.
"""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass
from typing import Any

SAMPLE_REGION = "us-east-1"

LAMBDA_ASSUME_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}
EC2_ASSUME_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}
ADMIN_POLICY = {
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}],
}


@dataclass
class SampleAccount:
    """Identifiers of the created sample resources."""

    vpc_id: str
    subnet_id: str
    security_group_id: str
    instance_id: str
    lambda_role_arn: str
    app_role_arn: str
    function_name: str
    table_name: str
    bucket_name: str
    log_group_name: str
    state_machine_arn: str
    db_instance_id: str
    public_subnet_ids: tuple[str, str]
    internet_gateway_id: str
    nat_gateway_id: str
    public_route_table_id: str
    private_route_table_id: str
    vpc_endpoint_id: str
    alb_security_group_id: str
    alb_arn: str
    listener_arn: str
    target_group_arn: str
    certificate_arn: str
    web_acl_arn: str
    static_bucket_name: str
    distribution_id: str
    hosted_zone_id: str


def _lambda_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("handler.py", "def handler(event, context):\n    return event\n")
    return buffer.getvalue()


def build_sample_account(session: Any, region: str = SAMPLE_REGION) -> SampleAccount:
    """Create the sample resources with ``session`` (a boto3.Session inside moto)."""
    ec2 = session.client("ec2", region_name=region)
    iam = session.client("iam", region_name=region)

    vpc_id = ec2.create_vpc(CidrBlock="10.0.0.0/16")["Vpc"]["VpcId"]
    ec2.create_tags(Resources=[vpc_id], Tags=[{"Key": "Name", "Value": "orders-vpc"}])
    subnet_id = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock="10.0.1.0/24",
        AvailabilityZone=f"{region}a",
        TagSpecifications=[
            {"ResourceType": "subnet", "Tags": [{"Key": "Name", "Value": "orders-private-a"}]}
        ],
    )["Subnet"]["SubnetId"]
    sg_id = ec2.create_security_group(
        GroupName="orders-web-sg", Description="Web tier", VpcId=vpc_id
    )["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            }
        ],
    )

    app_role = iam.create_role(
        RoleName="orders-app-role", AssumeRolePolicyDocument=json.dumps(EC2_ASSUME_POLICY)
    )["Role"]
    iam.create_instance_profile(InstanceProfileName="orders-app-role")
    iam.add_role_to_instance_profile(
        InstanceProfileName="orders-app-role", RoleName="orders-app-role"
    )
    lambda_role = iam.create_role(
        RoleName="order-lambda-role",
        AssumeRolePolicyDocument=json.dumps(LAMBDA_ASSUME_POLICY),
        Description="Execution role for order-processor",
    )["Role"]
    iam.put_role_policy(
        RoleName="order-lambda-role",
        PolicyName="too-broad",
        PolicyDocument=json.dumps(ADMIN_POLICY),
    )

    instance_id = ec2.run_instances(
        ImageId="ami-12c6146b",
        InstanceType="t3.micro",
        MinCount=1,
        MaxCount=1,
        SubnetId=subnet_id,
        SecurityGroupIds=[sg_id],
        IamInstanceProfile={"Name": "orders-app-role"},
        TagSpecifications=[
            {"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": "orders-web-1"}]}
        ],
    )["Instances"][0]["InstanceId"]

    dynamodb = session.client("dynamodb", region_name=region)
    table_name = "orders"
    dynamodb.create_table(
        TableName=table_name,
        BillingMode="PAY_PER_REQUEST",
        KeySchema=[{"AttributeName": "order_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "order_id", "AttributeType": "S"}],
        Tags=[{"Key": "team", "Value": "orders"}],
    )

    function_name = "order-processor"
    session.client("lambda", region_name=region).create_function(
        FunctionName=function_name,
        Runtime="python3.11",
        Role=lambda_role["Arn"],
        Handler="handler.handler",
        Code={"ZipFile": _lambda_zip()},
        Timeout=30,
        MemorySize=256,
        Environment={"Variables": {"TABLE_NAME": table_name, "DB_PASSWORD": "hunter2-demo"}},
        Tags={"team": "orders"},
    )

    logs = session.client("logs", region_name=region)
    log_group_name = f"/aws/lambda/{function_name}"
    logs.create_log_group(logGroupName=log_group_name, tags={"team": "orders"})
    logs.put_retention_policy(logGroupName=log_group_name, retentionInDays=14)

    s3 = session.client("s3", region_name="us-east-1")
    bucket_name = "orders-public-assets"
    s3.create_bucket(Bucket=bucket_name)
    s3.put_bucket_acl(Bucket=bucket_name, ACL="public-read")
    s3.put_bucket_versioning(Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"})
    s3.put_bucket_tagging(
        Bucket=bucket_name, Tagging={"TagSet": [{"Key": "team", "Value": "orders"}]}
    )

    definition = {
        "StartAt": "Process",
        "States": {
            "Process": {
                "Type": "Task",
                "Resource": f"arn:aws:lambda:{region}:123456789012:function:{function_name}",
                "End": True,
            }
        },
    }
    state_machine_arn = session.client("stepfunctions", region_name=region).create_state_machine(
        name="order-flow",
        definition=json.dumps(definition),
        roleArn=lambda_role["Arn"],
        tags=[{"key": "team", "value": "orders"}],
    )["stateMachineArn"]

    db_instance_id = "orders-db"
    session.client("rds", region_name=region).create_db_instance(
        DBInstanceIdentifier=db_instance_id,
        DBInstanceClass="db.t3.micro",
        Engine="postgres",
        AllocatedStorage=20,
        MasterUsername="orders_admin",
        MasterUserPassword="demo-password-123",
        VpcSecurityGroupIds=[sg_id],
        PubliclyAccessible=False,
        Tags=[{"Key": "team", "Value": "orders"}],
    )

    web = _build_web_stack(session, region, vpc_id, subnet_id)

    return SampleAccount(
        vpc_id=vpc_id,
        subnet_id=subnet_id,
        security_group_id=sg_id,
        instance_id=instance_id,
        lambda_role_arn=lambda_role["Arn"],
        app_role_arn=app_role["Arn"],
        function_name=function_name,
        table_name=table_name,
        bucket_name=bucket_name,
        log_group_name=log_group_name,
        state_machine_arn=state_machine_arn,
        db_instance_id=db_instance_id,
        **web,
    )


STOREFRONT_TAGS = [{"Key": "service", "Value": "storefront"}]


def _ec2_tags(resource_type: str, name: str) -> list[dict[str, Any]]:
    return [
        {
            "ResourceType": resource_type,
            "Tags": [{"Key": "Name", "Value": name}, *STOREFRONT_TAGS],
        }
    ]


def _build_web_stack(session: Any, region: str, vpc_id: str, private_subnet_id: str) -> dict:
    """The storefront stack: network, ALB, CloudFront, WAF, ACM and Route 53."""
    ec2 = session.client("ec2", region_name=region)
    public_subnets = tuple(
        ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=cidr,
            AvailabilityZone=f"{region}{zone}",
            TagSpecifications=_ec2_tags("subnet", f"storefront-public-{zone}"),
        )["Subnet"]["SubnetId"]
        for zone, cidr in (("a", "10.0.10.0/24"), ("b", "10.0.11.0/24"))
    )
    igw_id = ec2.create_internet_gateway(
        TagSpecifications=_ec2_tags("internet-gateway", "storefront-igw")
    )["InternetGateway"]["InternetGatewayId"]
    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    public_rtb = ec2.create_route_table(
        VpcId=vpc_id, TagSpecifications=_ec2_tags("route-table", "storefront-public")
    )["RouteTable"]["RouteTableId"]
    ec2.create_route(RouteTableId=public_rtb, DestinationCidrBlock="0.0.0.0/0", GatewayId=igw_id)
    for subnet in public_subnets:
        ec2.associate_route_table(RouteTableId=public_rtb, SubnetId=subnet)

    allocation = ec2.allocate_address(Domain="vpc")["AllocationId"]
    nat_id = ec2.create_nat_gateway(
        SubnetId=public_subnets[0],
        AllocationId=allocation,
        TagSpecifications=_ec2_tags("natgateway", "storefront-nat"),
    )["NatGateway"]["NatGatewayId"]
    private_rtb = ec2.create_route_table(
        VpcId=vpc_id, TagSpecifications=_ec2_tags("route-table", "storefront-private")
    )["RouteTable"]["RouteTableId"]
    ec2.create_route(
        RouteTableId=private_rtb, DestinationCidrBlock="0.0.0.0/0", NatGatewayId=nat_id
    )
    ec2.associate_route_table(RouteTableId=private_rtb, SubnetId=private_subnet_id)
    endpoint_id = ec2.create_vpc_endpoint(
        VpcId=vpc_id,
        ServiceName=f"com.amazonaws.{region}.s3",
        VpcEndpointType="Gateway",
        RouteTableIds=[private_rtb],
        TagSpecifications=_ec2_tags("vpc-endpoint", "storefront-s3"),
    )["VpcEndpoint"]["VpcEndpointId"]

    alb_sg = ec2.create_security_group(
        GroupName="storefront-alb-sg", Description="Public HTTPS", VpcId=vpc_id
    )["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=alb_sg,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            }
        ],
    )

    acm = session.client("acm", region_name="us-east-1")
    certificate_arn = acm.request_certificate(
        DomainName="shop.example.com",
        ValidationMethod="DNS",
        SubjectAlternativeNames=["shop.example.com", "api.example.com"],
        Tags=STOREFRONT_TAGS,
    )["CertificateArn"]

    elbv2 = session.client("elbv2", region_name=region)
    alb = elbv2.create_load_balancer(
        Name="storefront-alb",
        Subnets=list(public_subnets),
        SecurityGroups=[alb_sg],
        Scheme="internet-facing",
        Type="application",
        Tags=STOREFRONT_TAGS,
    )["LoadBalancers"][0]
    target_group_arn = elbv2.create_target_group(
        Name="storefront-tg",
        Protocol="HTTP",
        Port=80,
        VpcId=vpc_id,
        TargetType="ip",
        HealthCheckPath="/health",
        Tags=STOREFRONT_TAGS,
    )["TargetGroups"][0]["TargetGroupArn"]
    listener_arn = elbv2.create_listener(
        LoadBalancerArn=alb["LoadBalancerArn"],
        Protocol="HTTPS",
        Port=443,
        Certificates=[{"CertificateArn": certificate_arn}],
        DefaultActions=[{"Type": "forward", "TargetGroupArn": target_group_arn}],
    )["Listeners"][0]["ListenerArn"]

    web_acl_arn = session.client("wafv2", region_name="us-east-1").create_web_acl(
        Name="storefront-waf",
        Scope="CLOUDFRONT",
        DefaultAction={"Allow": {}},
        Description="Edge protection for the storefront",
        VisibilityConfig={
            "SampledRequestsEnabled": True,
            "CloudWatchMetricsEnabled": True,
            "MetricName": "storefront-waf",
        },
        Tags=STOREFRONT_TAGS,
    )["Summary"]["ARN"]

    s3 = session.client("s3", region_name="us-east-1")
    static_bucket = "storefront-static"
    s3.create_bucket(Bucket=static_bucket)
    s3.put_bucket_tagging(Bucket=static_bucket, Tagging={"TagSet": STOREFRONT_TAGS})

    forwarded = {"QueryString": False, "Cookies": {"Forward": "none"}}
    cloudfront = session.client("cloudfront", region_name="us-east-1")
    distribution = cloudfront.create_distribution_with_tags(
        DistributionConfigWithTags={
            "DistributionConfig": {
                "CallerReference": "storefront",
                "Aliases": {"Quantity": 1, "Items": ["shop.example.com"]},
                "Comment": "storefront",
                "Enabled": True,
                "WebACLId": web_acl_arn,
                "ViewerCertificate": {
                    "ACMCertificateArn": certificate_arn,
                    "SSLSupportMethod": "sni-only",
                    "MinimumProtocolVersion": "TLSv1.2_2021",
                },
                "Origins": {
                    "Quantity": 2,
                    "Items": [
                        {
                            "Id": "static-s3",
                            "DomainName": f"{static_bucket}.s3.{region}.amazonaws.com",
                            "S3OriginConfig": {"OriginAccessIdentity": ""},
                        },
                        {
                            "Id": "web-alb",
                            "DomainName": alb["DNSName"],
                            "CustomOriginConfig": {
                                "HTTPPort": 80,
                                "HTTPSPort": 443,
                                "OriginProtocolPolicy": "https-only",
                                "OriginSslProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]},
                            },
                        },
                    ],
                },
                "DefaultCacheBehavior": {
                    "TargetOriginId": "web-alb",
                    "ViewerProtocolPolicy": "redirect-to-https",
                    "ForwardedValues": forwarded,
                    "MinTTL": 0,
                },
                "CacheBehaviors": {
                    "Quantity": 1,
                    "Items": [
                        {
                            "PathPattern": "/static/*",
                            "TargetOriginId": "static-s3",
                            "ViewerProtocolPolicy": "redirect-to-https",
                            "ForwardedValues": forwarded,
                            "MinTTL": 0,
                        }
                    ],
                },
            },
            "Tags": {"Items": STOREFRONT_TAGS},
        }
    )["Distribution"]

    route53 = session.client("route53", region_name="us-east-1")
    zone_id = route53.create_hosted_zone(Name="example.com", CallerReference="storefront")[
        "HostedZone"
    ]["Id"].split("/")[-1]
    route53.change_tags_for_resource(
        ResourceType="hostedzone", ResourceId=zone_id, AddTags=STOREFRONT_TAGS
    )
    aliases = (
        ("shop.example.com", "Z2FDTNDATAQYW2", distribution["DomainName"], False),
        ("api.example.com", alb["CanonicalHostedZoneId"], f"dualstack.{alb['DNSName']}", True),
    )
    route53.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            "Changes": [
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": name,
                        "Type": "A",
                        "AliasTarget": {
                            "HostedZoneId": hosted_zone,
                            "DNSName": dns_name,
                            "EvaluateTargetHealth": health,
                        },
                    },
                }
                for name, hosted_zone, dns_name, health in aliases
            ]
        },
    )

    return {
        "public_subnet_ids": public_subnets,
        "internet_gateway_id": igw_id,
        "nat_gateway_id": nat_id,
        "public_route_table_id": public_rtb,
        "private_route_table_id": private_rtb,
        "vpc_endpoint_id": endpoint_id,
        "alb_security_group_id": alb_sg,
        "alb_arn": alb["LoadBalancerArn"],
        "listener_arn": listener_arn,
        "target_group_arn": target_group_arn,
        "certificate_arn": certificate_arn,
        "web_acl_arn": web_acl_arn,
        "static_bucket_name": static_bucket,
        "distribution_id": distribution["Id"],
        "hosted_zone_id": zone_id,
    }
