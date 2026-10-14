"""
Sample AWS account builder used by the demo script and the test suite.

Creates one resource of each Supported_Resource_Type in ``us-east-1`` (plus the
global S3 bucket and IAM roles), including deliberately insecure settings so the
Analysis_Engine has something to report:

- IAM role ``order-lambda-role`` with an inline ``Allow * on *`` policy (CRITICAL)
- S3 bucket with a ``public-read`` ACL (HIGH)
- Security group allowing SSH from ``0.0.0.0/0`` (HIGH)

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
    subnet_id = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.1.0/24")["Subnet"]["SubnetId"]
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
    )
