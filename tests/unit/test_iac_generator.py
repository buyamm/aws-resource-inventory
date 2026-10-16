"""
Unit & Property-based tests for IaCGenerator (TDD RED & GREEN phases).

Requirements Coverage:
- Requirement 7.2: Create .tf files organized by resource type and region
- Requirement 7.3: Generate corresponding Terraform resource blocks with all collected specifications
- Requirement 7.4: Generate terraform import commands for all existing resources
- Requirement 7.6: Include verification script comparing Terraform state with actual AWS
- Requirement 7.7: Traceability comments linking back to original specification files
- Requirement 14.1 / 14.4: Mappings for the network, edge, compute and data types
"""

from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.iac_generator import IaCGenerator
from src.parser import ResourceSpec, SpecMetadata

# ============================================================================
# Hypothesis Strategies for ResourceSpec
# ============================================================================

resource_type_strategy = st.sampled_from(
    [
        "aws_s3_bucket",
        "aws_ec2_instance",
        "aws_lambda_function",
        "aws_vpc",
        "aws_security_group",
        "aws_iam_role",
        "aws_dynamodb_table",
    ]
)

region_strategy = st.sampled_from(["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"])

specifications_strategy = st.dictionaries(
    keys=st.from_regex(r"[a-z][a-z0-9_]{2,15}", fullmatch=True),
    values=st.one_of(
        st.text(min_size=1, max_size=20),
        st.integers(min_value=1, max_value=65535),
        st.booleans(),
    ),
    min_size=1,
    max_size=6,
)

spec_metadata_strategy = st.builds(
    SpecMetadata,
    collected_at=st.just("2026-10-07T12:00:00Z"),
    collector_version=st.just("1.0.0"),
    api_version=st.just("2026-01-01"),
    checksum=st.just("dummy-checksum-123"),
)

resource_spec_strategy = st.builds(
    ResourceSpec,
    resource_type=resource_type_strategy,
    arn=st.from_regex(r"arn:aws:[a-z0-9-]+:[a-z0-9-]+:123456789012:[a-z0-9_/-]+", fullmatch=True),
    region=region_strategy,
    account_id=st.just("123456789012"),
    specifications=specifications_strategy,
    metadata=spec_metadata_strategy,
    raw_response=st.none(),
)


# ============================================================================
# Property-Based Tests (Task 10.1 & 10.2)
# ============================================================================


class TestIaCGeneratorPropertyTests:
    """Property tests for IaC completeness (Requirement 7.3)."""

    @given(resource_spec_strategy)
    @settings(max_examples=100)
    def test_property_iac_generator_includes_all_specs_req_7_3(self, spec: ResourceSpec) -> None:
        """
        Property 3: IaC Generation Completeness (Requirement 7.3).

        For all ResourceSpec objects, the generated Terraform resource block
        SHALL include all specification keys from the original spec.
        """
        generator = IaCGenerator()
        tf_code = generator.generate_resource_block(spec)

        assert tf_code.startswith("resource ") or "resource " in tf_code
        # Check that all specification keys appear in generated Terraform block
        for key in spec.specifications:
            assert key in tf_code, f"Specification key '{key}' missing from generated Terraform"


# ============================================================================
# Unit Tests (Task 10.1 & 10.2)
# ============================================================================


class TestIaCGeneratorUnitTests:
    """Unit tests for IaC generator operations."""

    @pytest.fixture
    def sample_specs(self) -> list[ResourceSpec]:
        """Sample list of specs for unit tests."""
        s3_spec = ResourceSpec(
            resource_type="aws_s3_bucket",
            arn="arn:aws:s3:::production-assets-bucket",
            region="us-east-1",
            account_id="123456789012",
            specifications={
                "bucket": "production-assets-bucket",
                "versioning": {"enabled": True},
            },
            metadata=SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "v1", "chk1"),
        )
        lambda_spec = ResourceSpec(
            resource_type="aws_lambda_function",
            arn="arn:aws:lambda:us-west-2:123456789012:function:process-order",
            region="us-west-2",
            account_id="123456789012",
            specifications={
                "function_name": "process-order",
                "runtime": "python3.11",
                "handler": "app.handler",
            },
            metadata=SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "v1", "chk2"),
        )
        return [s3_spec, lambda_spec]

    def test_iac_generator_includes_import_commands_req_7_4(
        self, sample_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 7.4: Generate terraform import commands for all existing resources."""
        generator = IaCGenerator()
        imports = generator.generate_imports(sample_specs)

        assert imports.count("import {") == 2
        assert 'id = "production-assets-bucket"' in imports
        assert 'id = "process-order"' in imports
        assert "to = module.data.aws_s3_bucket.production_assets_bucket" in imports
        assert "to = module.compute.aws_lambda_function.process_order" in imports

    def test_iac_generator_organizes_by_type_and_region_req_7_2(
        self, tmp_path: Path, sample_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 7.2: Create .tf files organized by resource type and region."""
        generator = IaCGenerator(output_dir=tmp_path)
        tf_files = generator.generate_terraform(sample_specs, target_dir=tmp_path)

        assert len(tf_files) > 0

        # modules/<module>/ holds the resources, envs/<env>/ the root configuration.
        assert "modules/data/main.tf" in tf_files
        assert "modules/compute/main.tf" in tf_files
        assert "envs/default/main.tf" in tf_files
        assert "aws_lambda_function" in tf_files["modules/compute/main.tf"]

        for rel_path, code in tf_files.items():
            full_path = tmp_path / rel_path
            assert full_path.exists()
            assert full_path.read_text(encoding="utf-8") == code

    def test_iac_generator_traceability_comments_req_7_7(
        self, sample_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 7.7: Traceability comments linking back to original specification files."""
        generator = IaCGenerator()
        for spec in sample_specs:
            block = generator.generate_resource_block(spec)
            assert "# Source specification:" in block or "# Specification source:" in block
            assert spec.resource_type in block
            assert spec.region in block

    def test_iac_generator_verification_script_req_7_6(
        self, sample_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 7.6: Include verification script comparing Terraform state with actual AWS."""
        generator = IaCGenerator()
        script = generator.generate_verification_script(sample_specs)

        assert "terraform plan" in script
        assert "exit" in script or "diff" in script or "changes" in script.lower()


# ============================================================================
# Task 18: per-type Terraform mapping (AWS field names → Terraform arguments)
# ============================================================================

import json  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402

import hcl2  # noqa: E402

ACCOUNT = "123456789012"


def _s(resource_type, arn, specifications, region="us-east-1"):
    return ResourceSpec(
        resource_type=resource_type,
        arn=arn,
        region=region,
        account_id=ACCOUNT,
        specifications=specifications,
        metadata=SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "v1", "chk"),
    )


INSTANCE = _s(
    "aws_instance",
    f"arn:aws:ec2:us-east-1:{ACCOUNT}:instance/i-0abc",
    {
        "InstanceId": "i-0abc",
        "ImageId": "ami-123",
        "InstanceType": "t3.micro",
        "SubnetId": "subnet-1",
        "VpcId": "vpc-1",
        "KeyName": "ops-key",
        "EbsOptimized": False,
        "Monitoring": {"State": "disabled"},
        "SecurityGroups": [{"GroupId": "sg-1", "GroupName": "web"}],
        "IamInstanceProfile": {
            "Arn": f"arn:aws:iam::{ACCOUNT}:instance-profile/web-role",
            "Id": "x",
        },
        "Tags": [{"Key": "Name", "Value": "web-1"}],
        "State": {"Name": "running"},
    },
)
VPC = _s(
    "aws_vpc",
    f"arn:aws:ec2:us-east-1:{ACCOUNT}:vpc/vpc-1",
    {
        "VpcId": "vpc-1",
        "CidrBlock": "10.0.0.0/16",
        "InstanceTenancy": "default",
        "EnableDnsSupport": True,
        "EnableDnsHostnames": False,
        "IsDefault": False,
        "Tags": [{"Key": "Name", "Value": "main"}],
    },
)
SECURITY_GROUP = _s(
    "aws_security_group",
    f"arn:aws:ec2:us-east-1:{ACCOUNT}:security-group/sg-1",
    {
        "GroupId": "sg-1",
        "GroupName": "web",
        "Description": "Web tier",
        "VpcId": "vpc-1",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "https"}],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "UserIdGroupPairs": [],
            },
            {
                "IpProtocol": "-1",
                "IpRanges": [],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "UserIdGroupPairs": [
                    {"GroupId": "sg-1", "UserId": ACCOUNT},
                    {"GroupId": "sg-2", "UserId": ACCOUNT},
                ],
            },
        ],
        "IpPermissionsEgress": [
            {
                "IpProtocol": "-1",
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                "Ipv6Ranges": [],
                "PrefixListIds": [],
                "UserIdGroupPairs": [],
            }
        ],
        # DescribeSecurityGroupRules: one rule per source (Requirement 16.3).
        "SecurityGroupRules": [
            {
                "SecurityGroupRuleId": "sgr-1",
                "GroupId": "sg-1",
                "IsEgress": False,
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "CidrIpv4": "0.0.0.0/0",
                "Description": "https",
                "Tags": [],
            },
            {
                "SecurityGroupRuleId": "sgr-2",
                "GroupId": "sg-1",
                "IsEgress": False,
                "IpProtocol": "-1",
                "FromPort": -1,
                "ToPort": -1,
                "ReferencedGroupInfo": {"GroupId": "sg-1", "UserId": ACCOUNT},
                "Tags": [],
            },
            {
                "SecurityGroupRuleId": "sgr-3",
                "GroupId": "sg-1",
                "IsEgress": False,
                "IpProtocol": "-1",
                "FromPort": -1,
                "ToPort": -1,
                "ReferencedGroupInfo": {"GroupId": "sg-2", "UserId": ACCOUNT},
                "Tags": [{"Key": "Name", "Value": "from-sg-2"}],
            },
            {
                "SecurityGroupRuleId": "sgr-4",
                "GroupId": "sg-1",
                "IsEgress": True,
                "IpProtocol": "-1",
                "FromPort": -1,
                "ToPort": -1,
                "CidrIpv4": "0.0.0.0/0",
                "Tags": [],
            },
        ],
        "OwnerId": ACCOUNT,
    },
)
FUNCTION = _s(
    "aws_lambda_function",
    f"arn:aws:lambda:us-west-2:{ACCOUNT}:function:process-order",
    {
        "FunctionName": "process-order",
        "FunctionArn": f"arn:aws:lambda:us-west-2:{ACCOUNT}:function:process-order",
        "Role": f"arn:aws:iam::{ACCOUNT}:role/lambda-role",
        "Handler": "app.handler",
        "Runtime": "python3.11",
        "MemorySize": 256,
        "Timeout": 30,
        "Description": 'Processes "orders" ${not_interpolated}',
        "Architectures": ["x86_64"],
        "PackageType": "Zip",
        "Layers": [{"Arn": f"arn:aws:lambda:us-west-2:{ACCOUNT}:layer:common:3", "CodeSize": 10}],
        "Environment": {"Variables": {"TABLE_NAME": "orders", "DB_PASSWORD": "[REDACTED]"}},
        "VpcConfig": {"SubnetIds": ["subnet-1"], "SecurityGroupIds": ["sg-1"], "VpcId": "vpc-1"},
        "Tags": {"team": "orders"},
        "CodeSha256": "abc",
        "LastModified": "2026-01-01",
    },
    region="us-west-2",
)
DATABASE = _s(
    "aws_db_instance",
    f"arn:aws:rds:us-east-1:{ACCOUNT}:db:orders-db",
    {
        "DBInstanceIdentifier": "orders-db",
        "Engine": "postgres",
        "EngineVersion": "15.4",
        "DBInstanceClass": "db.t3.micro",
        "AllocatedStorage": 20,
        "StorageType": "gp2",
        "MultiAZ": False,
        "PubliclyAccessible": False,
        "StorageEncrypted": True,
        "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/k",
        "MasterUsername": "admin",
        "BackupRetentionPeriod": 7,
        "DBSubnetGroup": {"DBSubnetGroupName": "db-subnets", "VpcId": "vpc-1"},
        "VpcSecurityGroups": [{"VpcSecurityGroupId": "sg-1", "Status": "active"}],
        "TagList": [{"Key": "team", "Value": "orders"}],
    },
)
LOG_GROUP = _s(
    "aws_cloudwatch_log_group",
    f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/aws/lambda/process-order",
    {
        "logGroupName": "/aws/lambda/process-order",
        "retentionInDays": 14,
        "tags": {"team": "orders"},
        "storedBytes": 0,
    },
)
DEFINITION = {"StartAt": "A", "States": {"A": {"Type": "Pass", "End": True}}}
STATE_MACHINE = _s(
    "aws_sfn_state_machine",
    f"arn:aws:states:us-east-1:{ACCOUNT}:stateMachine:flow",
    {
        "stateMachineArn": f"arn:aws:states:us-east-1:{ACCOUNT}:stateMachine:flow",
        "name": "flow",
        "roleArn": f"arn:aws:iam::{ACCOUNT}:role/sfn",
        "definition": json.dumps(DEFINITION),
        "type": "STANDARD",
        "tags": [{"key": "team", "value": "orders"}],
    },
)
TABLE = _s(
    "aws_dynamodb_table",
    f"arn:aws:dynamodb:us-east-1:{ACCOUNT}:table/orders",
    {
        "TableName": "orders",
        "KeySchema": [
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "gpk", "AttributeType": "S"},
        ],
        "BillingModeSummary": {"BillingMode": "PAY_PER_REQUEST"},
        "ProvisionedThroughput": {"ReadCapacityUnits": 0, "WriteCapacityUnits": 0},
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "by-g",
                "KeySchema": [{"AttributeName": "gpk", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "INCLUDE", "NonKeyAttributes": ["sk"]},
            }
        ],
        "StreamSpecification": {"StreamEnabled": True, "StreamViewType": "NEW_IMAGE"},
        "Tags": [{"Key": "team", "Value": "orders"}],
        "ItemCount": 3,
    },
)
POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::assets/*",
        }
    ],
}
BUCKET = _s(
    "aws_s3_bucket",
    "arn:aws:s3:::assets",
    {
        "Name": "assets",
        "bucket-tagging": {"TagSet": [{"Key": "team", "Value": "web"}]},
        "bucket-versioning": {"Status": "Enabled"},
        "bucket-policy": {"Policy": json.dumps(POLICY)},
        "bucket-encryption": {
            "ServerSideEncryptionConfiguration": {
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "aws:kms",
                            "KMSMasterKeyID": "k-1",
                        },
                        "BucketKeyEnabled": True,
                    }
                ]
            }
        },
        "bucket-acl": {"Grants": []},
    },
    region="global",
)
ASSUME = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}
ROLE = _s(
    "aws_iam_role",
    f"arn:aws:iam::{ACCOUNT}:role/lambda-role",
    {
        "RoleName": "lambda-role",
        "Path": "/",
        "Arn": f"arn:aws:iam::{ACCOUNT}:role/lambda-role",
        "AssumeRolePolicyDocument": ASSUME,
        "Description": "exec",
        "MaxSessionDuration": 3600,
        "Tags": [{"Key": "team", "Value": "orders"}],
        "AttachedPolicies": [
            {"PolicyName": "ReadOnly", "PolicyArn": "arn:aws:iam::aws:policy/ReadOnlyAccess"}
        ],
        "InlinePolicies": {
            "logs": {"Statement": [{"Effect": "Allow", "Action": "logs:*", "Resource": "*"}]}
        },
        "RoleId": "AROAEXAMPLE",
    },
    region="global",
)

ALL = [
    INSTANCE,
    VPC,
    SECURITY_GROUP,
    FUNCTION,
    DATABASE,
    LOG_GROUP,
    STATE_MACHINE,
    TABLE,
    BUCKET,
    ROLE,
]


def _resources(tf_text: str) -> dict:
    """{(type, name): body} from HCL text parsed with python-hcl2."""
    parsed = hcl2.loads(tf_text)
    out = {}
    for item in parsed.get("resource", []):
        for tf_type, named in item.items():
            for name, body in named.items():
                out[(tf_type.strip('"'), name.strip('"'))] = body
    return out


def _body(spec, tf_type=None, name=None):
    resources = _resources(IaCGenerator().generate_resource_block(spec))
    tf_type = tf_type or spec.resource_type
    matches = [
        body for (t, n), body in resources.items() if t == tf_type and (name is None or n == name)
    ]
    assert len(matches) == 1, resources.keys()
    return matches[0]


def _unquote(value):
    if isinstance(value, str) and len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    if isinstance(value, list):
        return [_unquote(v) for v in value]
    if isinstance(value, dict):
        return {_unquote(k): _unquote(v) for k, v in value.items() if k != "__is_block__"}
    return value


def _arg(body, key):
    return _unquote(body[key])


def _json_arg(body, key):
    """Decode a JSON document emitted as an HCL heredoc (<<-EOT ... EOT)."""
    import textwrap

    raw = _unquote(body[key])
    assert raw.startswith("<<-EOT\n"), raw
    content = raw[len("<<-EOT\n") : raw.rindex("EOT")]
    return json.loads(textwrap.dedent(content).replace("$${", "${").replace("%%{", "%{"))


class TestIaCTypeMappings:
    def test_iac_aws_instance_maps_arguments_req_7_3(self):
        body = _body(INSTANCE)
        assert _arg(body, "ami") == "ami-123"
        assert _arg(body, "instance_type") == "t3.micro"
        assert _arg(body, "subnet_id") == "subnet-1"
        assert _arg(body, "vpc_security_group_ids") == ["sg-1"]
        assert _arg(body, "key_name") == "ops-key"
        assert _arg(body, "iam_instance_profile") == "web-role"
        assert _arg(body, "monitoring") is False
        assert _arg(body, "tags") == {"Name": "web-1"}

    def test_iac_aws_vpc_maps_arguments_req_7_3(self):
        body = _body(VPC)
        assert _arg(body, "cidr_block") == "10.0.0.0/16"
        assert _arg(body, "enable_dns_support") is True
        assert _arg(body, "enable_dns_hostnames") is False
        assert _arg(body, "instance_tenancy") == "default"

    def test_iac_aws_security_group_maps_arguments_req_7_3(self):
        body = _body(SECURITY_GROUP)
        assert _arg(body, "name") == "web"
        assert _arg(body, "vpc_id") == "vpc-1"
        # Rules are separate resources (Requirement 16.3).
        assert "ingress" not in body and "egress" not in body

    def test_iac_security_group_rules_separate_resources_req_16_3(self):
        resources = _resources(IaCGenerator().generate_resource_block(SECURITY_GROUP))
        ingress = {
            n: _unquote(b)
            for (t, n), b in resources.items()
            if t == "aws_vpc_security_group_ingress_rule"
        }
        egress = {
            n: _unquote(b)
            for (t, n), b in resources.items()
            if t == "aws_vpc_security_group_egress_rule"
        }
        assert sorted(ingress) == ["web_ingress_all", "web_ingress_all_2", "web_ingress_tcp_443"]
        https = ingress["web_ingress_tcp_443"]
        assert https["security_group_id"] == "${aws_security_group.web.id}"
        assert https["ip_protocol"] == "tcp"
        assert https["from_port"] == 443 and https["to_port"] == 443
        assert https["cidr_ipv4"] == "0.0.0.0/0" and https["description"] == "https"
        # The rule that references its own group points at the group resource.
        assert ingress["web_ingress_all"]["referenced_security_group_id"] == (
            "${aws_security_group.web.id}"
        )
        other = ingress["web_ingress_all_2"]
        assert other["referenced_security_group_id"] == "sg-2"
        assert other["tags"] == {"Name": "from-sg-2"}
        # All-protocol rules carry no ports.
        assert "from_port" not in other and "to_port" not in other
        assert egress["web_egress_all"]["cidr_ipv4"] == "0.0.0.0/0"
        assert egress["web_egress_all"]["ip_protocol"] == "-1"
        block = IaCGenerator().generate_resource_block(SECURITY_GROUP)
        assert "# unmapped: IpPermissions" not in block

    def test_iac_security_group_without_rule_ids_leaves_rules_unmanaged_req_16_3(self):
        specs = dict(SECURITY_GROUP.specifications)
        del specs["SecurityGroupRules"]
        spec = _s("aws_security_group", SECURITY_GROUP.arn, specs)
        resources = _resources(IaCGenerator().generate_resource_block(spec))
        assert {t for t, _ in resources} == {"aws_security_group"}
        block = IaCGenerator().generate_resource_block(spec)
        assert "# unmapped: IpPermissions" in block

    def test_iac_aws_lambda_function_maps_arguments_req_7_3(self):
        body = _body(FUNCTION)
        assert _arg(body, "function_name") == "process-order"
        assert _arg(body, "role").endswith(":role/lambda-role")
        assert _arg(body, "memory_size") == 256
        assert _arg(body, "layers") == [f"arn:aws:lambda:us-west-2:{ACCOUNT}:layer:common:3"]
        assert _unquote(body["environment"][0])["variables"]["TABLE_NAME"] == "orders"
        vpc = _unquote(body["vpc_config"][0])
        assert vpc == {"subnet_ids": ["subnet-1"], "security_group_ids": ["sg-1"]}
        assert _arg(body, "filename") == "lambda_process-order.zip"
        assert "orders" in str(body["description"]) and "not_interpolated" in str(
            body["description"]
        )

    def test_iac_aws_db_instance_maps_arguments_req_7_3(self):
        body = _body(DATABASE)
        assert _arg(body, "identifier") == "orders-db"
        assert _arg(body, "instance_class") == "db.t3.micro"
        assert _arg(body, "db_subnet_group_name") == "db-subnets"
        assert _arg(body, "vpc_security_group_ids") == ["sg-1"]
        assert _arg(body, "username") == "admin"
        assert _arg(body, "tags") == {"team": "orders"}

    def test_iac_aws_cloudwatch_log_group_maps_arguments_req_7_3(self):
        body = _body(LOG_GROUP)
        assert _arg(body, "name") == "/aws/lambda/process-order"
        assert _arg(body, "retention_in_days") == 14

    def test_iac_aws_sfn_state_machine_maps_arguments_req_7_3(self):
        body = _body(STATE_MACHINE)
        assert _arg(body, "name") == "flow"
        assert _json_arg(body, "definition") == DEFINITION
        assert _arg(body, "tags") == {"team": "orders"}

    def test_iac_aws_dynamodb_table_maps_arguments_req_7_3(self):
        body = _body(TABLE)
        assert _arg(body, "billing_mode") == "PAY_PER_REQUEST"
        assert _arg(body, "hash_key") == "pk" and _arg(body, "range_key") == "sk"
        assert "read_capacity" not in body
        attributes = sorted(_unquote(a)["name"] for a in body["attribute"])
        assert attributes == ["gpk", "pk", "sk"]
        gsi = _unquote(body["global_secondary_index"][0])
        assert gsi["name"] == "by-g" and gsi["projection_type"] == "INCLUDE"
        assert _arg(body, "stream_view_type") == "NEW_IMAGE"

    def test_iac_aws_s3_bucket_maps_arguments_req_7_3(self):
        body = _body(BUCKET)
        assert _arg(body, "bucket") == "assets"
        assert _arg(body, "tags") == {"team": "web"}

    def test_iac_aws_iam_role_maps_arguments_req_7_3(self):
        body = _body(ROLE)
        assert _arg(body, "name") == "lambda-role"
        assert _json_arg(body, "assume_role_policy") == ASSUME
        assert _arg(body, "max_session_duration") == 3600

    def test_iac_companion_resources_s3_iam_req_7_4(self):
        s3 = _resources(IaCGenerator().generate_resource_block(BUCKET))
        types = {t for t, _ in s3}
        assert types == {
            "aws_s3_bucket",
            "aws_s3_bucket_versioning",
            "aws_s3_bucket_policy",
            "aws_s3_bucket_server_side_encryption_configuration",
        }
        iam = _resources(IaCGenerator().generate_resource_block(ROLE))
        assert {t for t, _ in iam} == {
            "aws_iam_role",
            "aws_iam_role_policy_attachment",
            "aws_iam_role_policy",
        }
        policy = next(body for (t, _n), body in iam.items() if t == "aws_iam_role_policy")
        assert _json_arg(policy, "policy")["Statement"][0]["Action"] == "logs:*"

    def test_iac_unmapped_keys_listed_in_comments_req_7_3(self):
        block = IaCGenerator().generate_resource_block(TABLE)
        assert "# unmapped: ItemCount" in block
        assert "# mapped: " in block and "TableName" in block

    def test_iac_redacted_values_ignored_req_7_5(self):
        block = IaCGenerator().generate_resource_block(FUNCTION)
        body = _body(FUNCTION)
        ignore = _unquote(body["lifecycle"][0])["ignore_changes"]
        assert "environment" in str(ignore)
        assert "filename" in str(ignore)
        assert "# REDACTED: set manually" in block

    def test_iac_rds_ignores_password_req_7_5(self):
        ignore = _unquote(_body(DATABASE)["lifecycle"][0])["ignore_changes"]
        assert "password" in str(ignore)


def _imports(text: str) -> dict[str, str]:
    """{to address: id} of the import blocks of an imports.tf."""
    out = {}
    for block in hcl2.loads(text).get("import", []):
        to = _unquote(block["to"])
        out[to.removeprefix("${").removesuffix("}")] = _unquote(block["id"])
    return out


class TestIaCFiles:
    def test_iac_generated_files_parse_as_hcl_req_7_2(self, tmp_path):
        files = IaCGenerator().generate_terraform(ALL, target_dir=tmp_path)
        assert "aws_s3_bucket" in files["modules/data/main.tf"]
        assert "aws_lambda_function" in files["modules/compute/main.tf"]
        total = 0
        for rel, text in files.items():
            if rel.endswith(".tf"):
                parsed = hcl2.loads(text)
                total += len(parsed.get("resource", []))
        assert total >= len(ALL)

    def test_iac_import_ids_per_type_req_7_4(self):
        imports = _imports(IaCGenerator().generate_imports(ALL))
        expected = {
            "module.compute.aws_instance.web_1": "i-0abc",
            "module.network.aws_vpc.main": "vpc-1",
            "module.network.aws_security_group.web": "sg-1",
            "module.network.aws_vpc_security_group_ingress_rule.web_ingress_tcp_443": "sgr-1",
            "module.network.aws_vpc_security_group_egress_rule.web_egress_all": "sgr-4",
            "module.compute.aws_lambda_function.process_order": "process-order",
            "module.data.aws_db_instance.orders_db": "orders-db",
            "module.observability.aws_cloudwatch_log_group.aws_lambda_process_order": (
                "/aws/lambda/process-order"
            ),
            "module.compute.aws_sfn_state_machine.flow": STATE_MACHINE.arn,
            "module.data.aws_dynamodb_table.orders": "orders",
            "module.data.aws_s3_bucket.assets": "assets",
            "module.data.aws_s3_bucket_versioning.assets": "assets",
            "module.iam.aws_iam_role.lambda_role": "lambda-role",
            "module.iam.aws_iam_role_policy_attachment.lambda_role_readonly": (
                "lambda-role/arn:aws:iam::aws:policy/ReadOnlyAccess"
            ),
            "module.iam.aws_iam_role_policy.lambda_role_logs": "lambda-role:logs",
        }
        for address, import_id in expected.items():
            assert imports.get(address) == import_id, address
        # 10 primaries, 3 S3 companions, 2 IAM companions, 4 security group rules.
        assert len(imports) == 19

    def test_iac_resource_names_are_unique_and_valid_req_16_2(self):
        a = _s("aws_s3_bucket", "arn:aws:s3:::1-data", {"Name": "1-data"}, region="global")
        b = _s("aws_s3_bucket", "arn:aws:s3:::1_data", {"Name": "1_data"}, region="global")
        names = IaCGenerator().assign_names([a, b])
        assert names[a.arn] == "r_1_data"
        assert names[b.arn] == "r_1_data_2"
        c = _s("aws_s3_bucket", "arn:aws:s3:::x.y", {"Name": "x.y"}, region="global")
        d = _s("aws_s3_bucket", "arn:aws:s3:::x_y", {"Name": "x_y"}, region="global")
        names = IaCGenerator().assign_names([d, c])
        assert names == {c.arn: "x_y", d.arn: "x_y_2"}, "order-independent"


class TestIaCPlanVerification:
    PLAN = ["terraform", "plan", "-detailed-exitcode", "-no-color", "-input=false"]

    def _run(self, returncode, stdout="", plan_json=None):
        plan = MagicMock(returncode=returncode, stdout=stdout, stderr="")
        show = MagicMock(returncode=0, stdout=json.dumps(plan_json or {}), stderr="")
        with patch("src.iac_generator.subprocess.run", side_effect=[plan, show]) as run:
            outcome = IaCGenerator().verify_terraform_plan("/tmp/tf")
        return outcome, run

    def test_iac_verify_plan_uses_exit_code_req_7_5(self):
        (ok, _msg), run = self._run(0, "Plan: 1 to add")
        assert ok is True
        assert run.call_args_list[0].args[0][:5] == self.PLAN
        assert run.call_count == 1
        (ok, msg), _ = self._run(1, "No changes.")
        assert ok is False and "error" in msg.lower()

    def test_iac_verify_plan_accepts_pending_imports_only_req_7_5(self):
        imports_only = {
            "resource_changes": [
                {
                    "address": "module.network.aws_vpc.main",
                    "change": {"actions": ["no-op"], "importing": {"id": "vpc-1"}},
                }
            ]
        }
        (ok, msg), run = self._run(2, "Plan: 1 to import", imports_only)
        assert ok is True and "1 import" in msg
        assert run.call_args_list[1].args[0][:3] == ["terraform", "show", "-json"]

        with_update = {
            "resource_changes": [
                {
                    "address": "module.network.aws_vpc.main",
                    "change": {"actions": ["update"], "importing": {"id": "vpc-1"}},
                }
            ]
        }
        (ok, msg), _ = self._run(2, "Plan: 1 to import, 1 to change", with_update)
        assert ok is False and "changes detected" in msg.lower()
        assert "module.network.aws_vpc.main" in msg

    def test_iac_verify_plan_terraform_missing_req_7_5(self):
        with patch("src.iac_generator.subprocess.run", side_effect=FileNotFoundError("terraform")):
            ok, msg = IaCGenerator().verify_terraform_plan("/tmp/tf")
        assert ok is False and "terraform" in msg.lower()


def test_iac_empty_values_count_as_mapped_req_7_3():
    spec = _s(
        "aws_lambda_function",
        f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:f",
        {"FunctionName": "f", "Description": "", "Layers": []},
    )
    block = IaCGenerator().generate_resource_block(spec)
    assert "# unmapped: Description" not in block and "# unmapped: Layers" not in block
    assert "description =" not in block


# ============================================================================
# Network, edge and load-balancing types (Requirements 7.3, 7.4, 14.1)
# ============================================================================

EC2_ARN = f"arn:aws:ec2:us-east-1:{ACCOUNT}"
ELB_ARN = f"arn:aws:elasticloadbalancing:us-east-1:{ACCOUNT}"
LB_ARN = f"{ELB_ARN}:loadbalancer/app/web-alb/abc"
LISTENER_ARN = f"{ELB_ARN}:listener/app/web-alb/abc/def"
TG_ARN = f"{ELB_ARN}:targetgroup/web-tg/123"
CERT_ARN = f"arn:aws:acm:us-east-1:{ACCOUNT}:certificate/uuid-1"
WAF_ARN = f"arn:aws:wafv2:us-east-1:{ACCOUNT}:global/webacl/web-acl/uuid-2"
TAGS = [{"Key": "service", "Value": "shop"}]

SUBNET = _s(
    "aws_subnet",
    f"{EC2_ARN}:subnet/subnet-a",
    {
        "SubnetId": "subnet-a",
        "VpcId": "vpc-1",
        "CidrBlock": "10.0.10.0/24",
        "AvailabilityZone": "us-east-1a",
        "MapPublicIpOnLaunch": True,
        "DefaultForAz": False,
        "Tags": TAGS,
    },
)
ROUTE_TABLE = _s(
    "aws_route_table",
    f"{EC2_ARN}:route-table/rtb-1",
    {
        "RouteTableId": "rtb-1",
        "VpcId": "vpc-1",
        "Routes": [
            {
                "DestinationCidrBlock": "10.0.0.0/16",
                "GatewayId": "local",
                "Origin": "CreateRouteTable",
            },
            {"DestinationCidrBlock": "0.0.0.0/0", "GatewayId": "igw-1", "Origin": "CreateRoute"},
            {
                "DestinationCidrBlock": "10.9.0.0/16",
                "NatGatewayId": "nat-1",
                "Origin": "CreateRoute",
            },
            {"DestinationPrefixListId": "pl-1", "GatewayId": "vpce-1", "Origin": "CreateRoute"},
        ],
        "Associations": [
            {"Main": True, "RouteTableAssociationId": "rtbassoc-main"},
            {"Main": False, "SubnetId": "subnet-a", "RouteTableAssociationId": "rtbassoc-1"},
        ],
        "Tags": TAGS,
    },
)
INTERNET_GATEWAY = _s(
    "aws_internet_gateway",
    f"{EC2_ARN}:internet-gateway/igw-1",
    {"InternetGatewayId": "igw-1", "Attachments": [{"VpcId": "vpc-1"}], "Tags": TAGS},
)
NAT_GATEWAY = _s(
    "aws_nat_gateway",
    f"{EC2_ARN}:natgateway/nat-1",
    {
        "NatGatewayId": "nat-1",
        "SubnetId": "subnet-a",
        "VpcId": "vpc-1",
        "ConnectivityType": "public",
        "NatGatewayAddresses": [{"AllocationId": "eipalloc-1", "PublicIp": "1.2.3.4"}],
        "Tags": TAGS,
    },
)
VPC_ENDPOINT = _s(
    "aws_vpc_endpoint",
    f"{EC2_ARN}:vpc-endpoint/vpce-1",
    {
        "VpcEndpointId": "vpce-1",
        "VpcId": "vpc-1",
        "ServiceName": "com.amazonaws.us-east-1.s3",
        "VpcEndpointType": "Gateway",
        "RouteTableIds": ["rtb-1"],
        "PolicyDocument": '{"Statement": [{"Effect": "Allow", "Principal": "*"}]}',
        "Tags": TAGS,
    },
)
LOAD_BALANCER = _s(
    "aws_lb",
    LB_ARN,
    {
        "LoadBalancerArn": LB_ARN,
        "LoadBalancerName": "web-alb",
        "Scheme": "internet-facing",
        "Type": "application",
        "IpAddressType": "ipv4",
        "AvailabilityZones": [{"SubnetId": "subnet-a"}, {"SubnetId": "subnet-b"}],
        "SecurityGroups": ["sg-alb"],
        "Attributes": [
            {"Key": "deletion_protection.enabled", "Value": "true"},
            {"Key": "idle_timeout.timeout_seconds", "Value": "60"},
        ],
        "Listeners": [{"ListenerArn": LISTENER_ARN}],
        "Tags": TAGS,
    },
)
LISTENER = _s(
    "aws_lb_listener",
    LISTENER_ARN,
    {
        "ListenerArn": LISTENER_ARN,
        "LoadBalancerArn": LB_ARN,
        "Port": 443,
        "Protocol": "HTTPS",
        "SslPolicy": "ELBSecurityPolicy-2016-08",
        "Certificates": [{"CertificateArn": CERT_ARN}],
        "DefaultActions": [{"Type": "forward", "TargetGroupArn": TG_ARN, "Order": 1}],
    },
)
TARGET_GROUP = _s(
    "aws_lb_target_group",
    TG_ARN,
    {
        "TargetGroupArn": TG_ARN,
        "TargetGroupName": "web-tg",
        "Protocol": "HTTP",
        "Port": 80,
        "VpcId": "vpc-1",
        "TargetType": "ip",
        "HealthCheckEnabled": True,
        "HealthCheckPath": "/health",
        "HealthCheckProtocol": "HTTP",
        "HealthCheckPort": "traffic-port",
        "HealthCheckIntervalSeconds": 30,
        "HealthCheckTimeoutSeconds": 5,
        "HealthyThresholdCount": 5,
        "UnhealthyThresholdCount": 2,
        "Matcher": {"HttpCode": "200"},
        "Attributes": [{"Key": "deregistration_delay.timeout_seconds", "Value": "30"}],
        "Tags": TAGS,
    },
)
DISTRIBUTION = _s(
    "aws_cloudfront_distribution",
    f"arn:aws:cloudfront::{ACCOUNT}:distribution/E1",
    {
        "Id": "E1",
        "DomainName": "d1.cloudfront.net",
        "DistributionConfig": {
            "Aliases": {"Quantity": 1, "Items": ["shop.example.com"]},
            "Comment": "shop",
            "Enabled": True,
            "PriceClass": "PriceClass_100",
            "HttpVersion": "http2",
            "IsIPV6Enabled": True,
            "DefaultRootObject": "index.html",
            "WebACLId": WAF_ARN,
            "Origins": {
                "Quantity": 2,
                "Items": [
                    {
                        "Id": "static-s3",
                        "DomainName": "static.s3.us-east-1.amazonaws.com",
                        "OriginPath": "",
                        "S3OriginConfig": {"OriginAccessIdentity": ""},
                    },
                    {
                        "Id": "web-alb",
                        "DomainName": "web-alb-1.us-east-1.elb.amazonaws.com",
                        "OriginPath": "",
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
                "AllowedMethods": {
                    "Quantity": 2,
                    "Items": ["GET", "HEAD"],
                    "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                },
                "Compress": True,
                "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
            },
            "CacheBehaviors": {
                "Quantity": 1,
                "Items": [
                    {
                        "PathPattern": "/static/*",
                        "TargetOriginId": "static-s3",
                        "ViewerProtocolPolicy": "redirect-to-https",
                        "ForwardedValues": {"QueryString": False, "Cookies": {"Forward": "none"}},
                        "MinTTL": 0,
                    }
                ],
            },
            "Restrictions": {"GeoRestriction": {"RestrictionType": "none", "Quantity": 0}},
            "ViewerCertificate": {
                "ACMCertificateArn": CERT_ARN,
                "SSLSupportMethod": "sni-only",
                "MinimumProtocolVersion": "TLSv1.2_2021",
            },
        },
        "Tags": TAGS,
    },
    region="global",
)
ZONE = _s(
    "aws_route53_zone",
    "arn:aws:route53:::hostedzone/Z1",
    {
        "Id": "/hostedzone/Z1",
        "Name": "example.com.",
        "Config": {"Comment": "public zone", "PrivateZone": False},
        "ResourceRecordSets": [
            {"Name": "example.com.", "Type": "NS", "TTL": 172800, "ResourceRecords": []},
            {"Name": "example.com.", "Type": "SOA", "TTL": 900, "ResourceRecords": []},
            {
                "Name": "shop.example.com.",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z2FDTNDATAQYW2",
                    "DNSName": "d1.cloudfront.net.",
                    "EvaluateTargetHealth": False,
                },
            },
            {
                "Name": "www.example.com.",
                "Type": "CNAME",
                "TTL": 300,
                "ResourceRecords": [{"Value": "shop.example.com"}],
            },
        ],
        "Tags": TAGS,
    },
    region="global",
)
CERTIFICATE = _s(
    "aws_acm_certificate",
    CERT_ARN,
    {
        "CertificateArn": CERT_ARN,
        "DomainName": "shop.example.com",
        "SubjectAlternativeNames": ["shop.example.com", "www.example.com"],
        "Type": "AMAZON_ISSUED",
        "KeyAlgorithm": "RSA_2048",
        "DomainValidationOptions": [{"DomainName": "shop.example.com", "ValidationMethod": "DNS"}],
        "Tags": TAGS,
    },
)
WEB_ACL = _s(
    "aws_wafv2_web_acl",
    WAF_ARN,
    {
        "Name": "web-acl",
        "Id": "uuid-2",
        "ARN": WAF_ARN,
        "Description": "edge",
        "DefaultAction": {"Allow": {}},
        "Rules": [{"Name": "rate", "Priority": 1}],
        "VisibilityConfig": {
            "SampledRequestsEnabled": True,
            "CloudWatchMetricsEnabled": True,
            "MetricName": "web-acl",
        },
        "Tags": TAGS,
    },
    region="global",
)
NETWORK_EDGE = [
    SUBNET,
    ROUTE_TABLE,
    INTERNET_GATEWAY,
    NAT_GATEWAY,
    VPC_ENDPOINT,
    LOAD_BALANCER,
    LISTENER,
    TARGET_GROUP,
    DISTRIBUTION,
    ZONE,
    CERTIFICATE,
    WEB_ACL,
]


def _block(body, name):
    value = body[name]
    return _unquote(value[0] if isinstance(value, list) else value)


class TestIaCNetworkEdgeMappings:
    def test_iac_network_types_map_arguments_req_7_3(self):
        subnet = _body(SUBNET)
        assert _arg(subnet, "vpc_id") == "vpc-1"
        assert _arg(subnet, "cidr_block") == "10.0.10.0/24"
        assert _arg(subnet, "availability_zone") == "us-east-1a"
        assert _arg(subnet, "map_public_ip_on_launch") is True
        assert _arg(subnet, "tags") == {"service": "shop"}

        routes = _body(ROUTE_TABLE)
        assert _arg(routes, "vpc_id") == "vpc-1"
        # The local route and the gateway endpoint route are managed by AWS / the endpoint.
        assert [_unquote(r) for r in routes["route"]] == [
            {"cidr_block": "0.0.0.0/0", "gateway_id": "igw-1"},
            {"cidr_block": "10.9.0.0/16", "nat_gateway_id": "nat-1"},
        ]
        association = _body(ROUTE_TABLE, "aws_route_table_association")
        assert _arg(association, "subnet_id") == "subnet-a"
        assert _arg(association, "route_table_id") == "${aws_route_table.rtb_1.id}"

        assert _arg(_body(INTERNET_GATEWAY), "vpc_id") == "vpc-1"
        nat = _body(NAT_GATEWAY)
        assert _arg(nat, "subnet_id") == "subnet-a"
        assert _arg(nat, "allocation_id") == "eipalloc-1"
        assert _arg(nat, "connectivity_type") == "public"

        endpoint = _body(VPC_ENDPOINT)
        assert _arg(endpoint, "service_name") == "com.amazonaws.us-east-1.s3"
        assert _arg(endpoint, "vpc_endpoint_type") == "Gateway"
        assert _arg(endpoint, "route_table_ids") == ["rtb-1"]
        assert _json_arg(endpoint, "policy")["Statement"][0]["Effect"] == "Allow"

    def test_iac_load_balancer_types_map_arguments_req_7_3(self):
        lb = _body(LOAD_BALANCER)
        assert _arg(lb, "name") == "web-alb"
        assert _arg(lb, "internal") is False
        assert _arg(lb, "load_balancer_type") == "application"
        assert _arg(lb, "subnets") == ["subnet-a", "subnet-b"]
        assert _arg(lb, "security_groups") == ["sg-alb"]
        assert _arg(lb, "enable_deletion_protection") is True
        assert _arg(lb, "idle_timeout") == 60

        listener = _body(LISTENER)
        assert _arg(listener, "load_balancer_arn") == LB_ARN
        assert _arg(listener, "port") == 443
        assert _arg(listener, "protocol") == "HTTPS"
        assert _arg(listener, "certificate_arn") == CERT_ARN
        assert _block(listener, "default_action") == {
            "type": "forward",
            "target_group_arn": TG_ARN,
            "order": 1,
        }

        tg = _body(TARGET_GROUP)
        assert _arg(tg, "name") == "web-tg"
        assert _arg(tg, "target_type") == "ip"
        assert _arg(tg, "deregistration_delay") == "30"
        health = _block(tg, "health_check")
        assert health["path"] == "/health" and health["matcher"] == "200"

    def test_iac_edge_types_map_arguments_req_7_3(self):
        cf = _body(DISTRIBUTION)
        assert _arg(cf, "enabled") is True
        assert _arg(cf, "aliases") == ["shop.example.com"]
        assert _arg(cf, "web_acl_id") == WAF_ARN
        origins = [_unquote(o) for o in cf["origin"]]
        assert [o["origin_id"] for o in origins] == ["static-s3", "web-alb"]
        assert "s3_origin_config" in origins[0]
        custom = origins[1]["custom_origin_config"]
        custom = custom[0] if isinstance(custom, list) else custom
        assert custom["origin_protocol_policy"] == "https-only"
        assert custom["origin_ssl_protocols"] == ["TLSv1.2"]
        default = _block(cf, "default_cache_behavior")
        assert default["target_origin_id"] == "web-alb"
        assert default["cache_policy_id"] == "658327ea-f89d-4fab-a63d-7e88639e58f6"
        ordered = _block(cf, "ordered_cache_behavior")
        assert ordered["path_pattern"] == "/static/*"
        assert "forwarded_values" in ordered
        certificate = _block(cf, "viewer_certificate")
        assert certificate["acm_certificate_arn"] == CERT_ARN
        assert "restrictions" in cf

        zone = _body(ZONE)
        assert _arg(zone, "name") == "example.com"
        assert _arg(zone, "comment") == "public zone"
        records = _resources(IaCGenerator().generate_resource_block(ZONE))
        record_bodies = {n: b for (t, n), b in records.items() if t == "aws_route53_record"}
        # Apex NS and SOA records belong to the zone itself.
        assert sorted(record_bodies) == ["example_com_shop_a", "example_com_www_cname"]
        alias = _block(record_bodies["example_com_shop_a"], "alias")
        assert alias["name"] == "d1.cloudfront.net."
        assert _arg(record_bodies["example_com_www_cname"], "records") == ["shop.example.com"]

        cert = _body(CERTIFICATE)
        assert _arg(cert, "domain_name") == "shop.example.com"
        assert _arg(cert, "subject_alternative_names") == ["shop.example.com", "www.example.com"]
        assert _arg(cert, "validation_method") == "DNS"

        acl = _body(WEB_ACL)
        assert _arg(acl, "scope") == "CLOUDFRONT"
        assert "allow" in _block(acl, "default_action")
        assert _block(acl, "visibility_config")["metric_name"] == "web-acl"
        # WAF rules are not mapped; they are kept out of the plan.
        assert "rule" in str(_unquote(acl["lifecycle"][0])["ignore_changes"])
        assert "# unmapped: Rules" in IaCGenerator().generate_resource_block(WEB_ACL)

    def test_iac_network_edge_import_ids_req_7_4(self):
        imports = _imports(IaCGenerator().generate_imports(NETWORK_EDGE))
        net, edge = "module.network.", "module.edge."
        expected = {
            net + "aws_subnet.subnet_a": "subnet-a",
            net + "aws_route_table.rtb_1": "rtb-1",
            net + "aws_route_table_association.rtb_1_subnet_a": "subnet-a/rtb-1",
            net + "aws_internet_gateway.igw_1": "igw-1",
            net + "aws_nat_gateway.nat_1": "nat-1",
            net + "aws_vpc_endpoint.vpce_1": "vpce-1",
            edge + "aws_lb.web_alb": LB_ARN,
            edge + "aws_lb_listener.https_443": LISTENER_ARN,
            edge + "aws_lb_target_group.web_tg": TG_ARN,
            # "shop" (the service tag) is stripped from shop.example.com.
            edge + "aws_acm_certificate.example_com": CERT_ARN,
            edge + "aws_cloudfront_distribution.example_com": "E1",
            edge + "aws_route53_zone.example_com": "Z1",
            edge + "aws_route53_record.example_com_shop_a": "Z1_shop.example.com_A",
            edge + "aws_route53_record.example_com_www_cname": "Z1_www.example.com_CNAME",
            edge + "aws_wafv2_web_acl.web_acl": "uuid-2/web-acl/CLOUDFRONT",
        }
        assert imports == expected

    def test_iac_network_edge_files_parse_as_hcl_req_7_2(self, tmp_path):
        files = IaCGenerator().generate_terraform(NETWORK_EDGE, target_dir=tmp_path)
        assert "aws_cloudfront_distribution" in files["modules/edge/main.tf"]
        assert "aws_lb_listener" in files["modules/edge/main.tf"]
        for rel, text in files.items():
            if rel.endswith(".tf"):
                hcl2.loads(text)
            if rel.endswith("/main.tf") and rel.startswith("modules/"):
                assert "# unmapped: Tags" not in text, rel


# ============================================================================
# Compute and data types (Requirement 14.4)
# ============================================================================

ECS = f"arn:aws:ecs:us-east-1:{ACCOUNT}"
CLUSTER_ARN = f"{ECS}:cluster/web"
TASK_ARN = f"{ECS}:task-definition/api:7"
ROLE_PREFIX = f"arn:aws:iam::{ACCOUNT}:role"
QUEUE_ARN = f"arn:aws:sqs:us-east-1:{ACCOUNT}:jobs"
TOPIC_ARN = f"arn:aws:sns:us-east-1:{ACCOUNT}:events"
FUNCTION_ARN = f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:worker"
ECS_TAGS = [{"key": "service", "value": "shop"}]
CONTAINERS = [
    {
        "name": "api",
        "image": f"{ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/api:1.2.3",
        "cpu": 0,
        "essential": True,
        "portMappings": [{"containerPort": 80, "hostPort": 80, "protocol": "tcp"}],
        "environment": [{"name": "SESSION_SECRET", "value": "[REDACTED]"}],
        "logConfiguration": {"logDriver": "awslogs", "options": {"awslogs-group": "/ecs/api"}},
    }
]

CLUSTER = _s(
    "aws_ecs_cluster",
    CLUSTER_ARN,
    {
        "clusterArn": CLUSTER_ARN,
        "clusterName": "web",
        "status": "ACTIVE",
        "settings": [{"name": "containerInsights", "value": "enabled"}],
        "capacityProviders": ["FARGATE"],
        "tags": ECS_TAGS,
    },
)
SERVICE = _s(
    "aws_ecs_service",
    f"{ECS}:service/web/api",
    {
        "serviceArn": f"{ECS}:service/web/api",
        "serviceName": "api",
        "clusterArn": CLUSTER_ARN,
        "taskDefinition": TASK_ARN,
        "desiredCount": 2,
        "launchType": "FARGATE",
        "platformVersion": "LATEST",
        "schedulingStrategy": "REPLICA",
        "deploymentConfiguration": {"maximumPercent": 200, "minimumHealthyPercent": 100},
        "healthCheckGracePeriodSeconds": 60,
        "enableExecuteCommand": False,
        "propagateTags": "SERVICE",
        "loadBalancers": [{"targetGroupArn": TG_ARN, "containerName": "api", "containerPort": 80}],
        "networkConfiguration": {
            "awsvpcConfiguration": {
                "subnets": ["subnet-a"],
                "securityGroups": ["sg-app"],
                "assignPublicIp": "DISABLED",
            }
        },
        "runningCount": 2,
        "deployments": [{"status": "PRIMARY"}],
        "tags": ECS_TAGS,
    },
)
TASK_DEFINITION = _s(
    "aws_ecs_task_definition",
    TASK_ARN,
    {
        "taskDefinitionArn": TASK_ARN,
        "family": "api",
        "revision": 7,
        "taskRoleArn": f"{ROLE_PREFIX}/api-task",
        "executionRoleArn": f"{ROLE_PREFIX}/api-exec",
        "networkMode": "awsvpc",
        "requiresCompatibilities": ["FARGATE"],
        "cpu": "256",
        "memory": "512",
        "runtimePlatform": {"cpuArchitecture": "ARM64", "operatingSystemFamily": "LINUX"},
        "containerDefinitions": CONTAINERS,
        "status": "ACTIVE",
        "tags": ECS_TAGS,
    },
)
REPOSITORY = _s(
    "aws_ecr_repository",
    f"arn:aws:ecr:us-east-1:{ACCOUNT}:repository/team/api",
    {
        "repositoryName": "team/api",
        "repositoryUri": f"{ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/team/api",
        "imageTagMutability": "IMMUTABLE",
        "imageScanningConfiguration": {"scanOnPush": True},
        "encryptionConfiguration": {"encryptionType": "AES256"},
        "tags": TAGS,
    },
)
AUTOSCALING_GROUP = _s(
    "aws_autoscaling_group",
    f"arn:aws:autoscaling:us-east-1:{ACCOUNT}:autoScalingGroup:uuid:autoScalingGroupName/workers",
    {
        "AutoScalingGroupName": "workers",
        "LaunchTemplate": {"LaunchTemplateId": "lt-1", "Version": "$Default"},
        "MinSize": 1,
        "MaxSize": 4,
        "DesiredCapacity": 2,
        "DefaultCooldown": 300,
        "HealthCheckType": "ELB",
        "HealthCheckGracePeriod": 120,
        "VPCZoneIdentifier": "subnet-a,subnet-b",
        "TargetGroupARNs": [TG_ARN],
        "TerminationPolicies": ["Default"],
        "Instances": [{"InstanceId": "i-1"}],
        "Tags": [
            {
                "ResourceId": "workers",
                "ResourceType": "auto-scaling-group",
                "Key": "service",
                "Value": "shop",
                "PropagateAtLaunch": True,
            }
        ],
    },
)
LAUNCH_TEMPLATE = _s(
    "aws_launch_template",
    f"arn:aws:ec2:us-east-1:{ACCOUNT}:launch-template/lt-1",
    {
        "LaunchTemplateId": "lt-1",
        "LaunchTemplateName": "worker",
        "DefaultVersionNumber": 3,
        "LatestVersionNumber": 3,
        "LaunchTemplateData": {
            "ImageId": "ami-123",
            "InstanceType": "t3.small",
            "SecurityGroupIds": ["sg-app"],
            "IamInstanceProfile": {"Name": "worker-profile"},
            "UserData": "[REDACTED]",
            "MetadataOptions": {"HttpTokens": "required", "HttpEndpoint": "enabled"},
        },
        "Tags": TAGS,
    },
)
REPLICATION_GROUP = _s(
    "aws_elasticache_replication_group",
    f"arn:aws:elasticache:us-east-1:{ACCOUNT}:replicationgroup:cache",
    {
        "ReplicationGroupId": "cache",
        "Description": "session cache",
        "MemberClusters": ["cache-001", "cache-002"],
        "NodeGroups": [
            {"PrimaryEndpoint": {"Address": "cache.x.cache.amazonaws.com", "Port": 6379}}
        ],
        "AutomaticFailover": "enabled",
        "MultiAZ": "enabled",
        "ClusterEnabled": False,
        "CacheNodeType": "cache.t4g.micro",
        "TransitEncryptionEnabled": True,
        "AtRestEncryptionEnabled": True,
        "SnapshotRetentionLimit": 1,
        "SnapshotWindow": "05:00-06:00",
        "Engine": "redis",
        "CacheCluster": {
            "Engine": "redis",
            "EngineVersion": "7.1.0",
            "CacheParameterGroup": {"CacheParameterGroupName": "default.redis7"},
            "CacheSubnetGroupName": "cache-subnets",
            "SecurityGroups": [{"SecurityGroupId": "sg-app", "Status": "active"}],
            "PreferredMaintenanceWindow": "sun:23:00-mon:01:30",
        },
        "CacheSubnetGroup": {"CacheSubnetGroupName": "cache-subnets", "VpcId": "vpc-1"},
        "TagList": TAGS,
    },
)
QUEUE = _s(
    "aws_sqs_queue",
    QUEUE_ARN,
    {
        "QueueUrl": f"https://sqs.us-east-1.amazonaws.com/{ACCOUNT}/jobs",
        "Attributes": {
            "QueueArn": QUEUE_ARN,
            "VisibilityTimeout": "60",
            "MessageRetentionPeriod": "345600",
            "DelaySeconds": "0",
            "MaximumMessageSize": "262144",
            "ReceiveMessageWaitTimeSeconds": "20",
            "SqsManagedSseEnabled": "true",
            "ApproximateNumberOfMessages": "3",
            "RedrivePolicy": json.dumps(
                {"deadLetterTargetArn": f"{QUEUE_ARN}-dlq", "maxReceiveCount": 5}
            ),
        },
        "Tags": {"service": "shop"},
    },
)
TOPIC = _s(
    "aws_sns_topic",
    TOPIC_ARN,
    {
        "Attributes": {
            "TopicArn": TOPIC_ARN,
            "DisplayName": "Shop events",
            "Policy": json.dumps({"Version": "2012-10-17", "Statement": []}),
            "DeliveryPolicy": "",
            "SubscriptionsConfirmed": "1",
        },
        "Subscriptions": [{"Protocol": "sqs", "Endpoint": QUEUE_ARN}],
        "Tags": TAGS,
    },
)
EVENT_RULE = _s(
    "aws_cloudwatch_event_rule",
    f"arn:aws:events:us-east-1:{ACCOUNT}:rule/nightly",
    {
        "Name": "nightly",
        "Arn": f"arn:aws:events:us-east-1:{ACCOUNT}:rule/nightly",
        "ScheduleExpression": "cron(0 2 * * ? *)",
        "State": "ENABLED",
        "Description": "Nightly report",
        "EventBusName": "default",
        "Targets": [
            {"Id": "worker", "Arn": FUNCTION_ARN, "Input": '{"report": true}'},
            {
                "Id": "cleanup",
                "Arn": CLUSTER_ARN,
                "RoleArn": f"{ROLE_PREFIX}/events",
                "EcsParameters": {"TaskDefinitionArn": TASK_ARN, "TaskCount": 1},
            },
        ],
        "Tags": TAGS,
    },
)
BUS_RULE = _s(
    "aws_cloudwatch_event_rule",
    f"arn:aws:events:us-east-1:{ACCOUNT}:rule/orders-bus/created",
    {
        "Name": "created",
        "EventBusName": "orders-bus",
        "EventPattern": json.dumps({"source": ["shop.orders"]}),
        "State": "DISABLED",
        "Targets": [{"Id": "q", "Arn": QUEUE_ARN}],
    },
)
SCHEDULE = _s(
    "aws_scheduler_schedule",
    f"arn:aws:scheduler:us-east-1:{ACCOUNT}:schedule/default/report",
    {
        "Name": "report",
        "GroupName": "default",
        "Arn": f"arn:aws:scheduler:us-east-1:{ACCOUNT}:schedule/default/report",
        "ScheduleExpression": "rate(1 hour)",
        "ScheduleExpressionTimezone": "UTC",
        "State": "ENABLED",
        "FlexibleTimeWindow": {"Mode": "FLEXIBLE", "MaximumWindowInMinutes": 15},
        "Target": {
            "Arn": QUEUE_ARN,
            "RoleArn": f"{ROLE_PREFIX}/scheduler",
            "Input": '{"task": "report"}',
            "RetryPolicy": {"MaximumEventAgeInSeconds": 86400, "MaximumRetryAttempts": 185},
        },
    },
)
COMPUTE_DATA = [
    CLUSTER,
    SERVICE,
    TASK_DEFINITION,
    REPOSITORY,
    AUTOSCALING_GROUP,
    LAUNCH_TEMPLATE,
    REPLICATION_GROUP,
    QUEUE,
    TOPIC,
    EVENT_RULE,
    BUS_RULE,
    SCHEDULE,
]


class TestIaCComputeDataMappings:
    def test_iac_ecs_types_map_arguments_req_7_3(self):
        cluster = _body(CLUSTER)
        assert _arg(cluster, "name") == "web"
        assert _block(cluster, "setting") == {"name": "containerInsights", "value": "enabled"}
        assert _arg(cluster, "tags") == {"service": "shop"}

        service = _body(SERVICE)
        assert _arg(service, "name") == "api"
        assert _arg(service, "cluster") == CLUSTER_ARN
        assert _arg(service, "task_definition") == TASK_ARN
        assert _arg(service, "desired_count") == 2
        assert _arg(service, "launch_type") == "FARGATE"
        assert _arg(service, "deployment_maximum_percent") == 200
        assert _arg(service, "deployment_minimum_healthy_percent") == 100
        assert _arg(service, "health_check_grace_period_seconds") == 60
        assert _arg(service, "propagate_tags") == "SERVICE"
        assert _block(service, "load_balancer") == {
            "target_group_arn": TG_ARN,
            "container_name": "api",
            "container_port": 80,
        }
        assert _block(service, "network_configuration") == {
            "subnets": ["subnet-a"],
            "security_groups": ["sg-app"],
            "assign_public_ip": False,
        }
        assert _arg(service, "tags") == {"service": "shop"}

        task = _body(TASK_DEFINITION)
        assert _arg(task, "family") == "api"
        assert _arg(task, "task_role_arn") == f"{ROLE_PREFIX}/api-task"
        assert _arg(task, "network_mode") == "awsvpc"
        assert _arg(task, "requires_compatibilities") == ["FARGATE"]
        assert _arg(task, "cpu") == "256" and _arg(task, "memory") == "512"
        assert _block(task, "runtime_platform") == {
            "cpu_architecture": "ARM64",
            "operating_system_family": "LINUX",
        }
        assert _json_arg(task, "container_definitions") == CONTAINERS
        # A redacted environment value stays out of the plan.
        text = IaCGenerator().generate_resource_block(TASK_DEFINITION)
        assert "# REDACTED: set manually" in text
        assert "container_definitions" in str(_unquote(task["lifecycle"][0])["ignore_changes"])

        repository = _body(REPOSITORY)
        assert _arg(repository, "name") == "team/api"
        assert _arg(repository, "image_tag_mutability") == "IMMUTABLE"
        assert _block(repository, "image_scanning_configuration") == {"scan_on_push": True}
        assert _block(repository, "encryption_configuration") == {"encryption_type": "AES256"}

    def test_iac_autoscaling_types_map_arguments_req_7_3(self):
        asg = _body(AUTOSCALING_GROUP)
        assert _arg(asg, "name") == "workers"
        assert _arg(asg, "min_size") == 1 and _arg(asg, "max_size") == 4
        assert _arg(asg, "desired_capacity") == 2
        assert _arg(asg, "vpc_zone_identifier") == ["subnet-a", "subnet-b"]
        assert _arg(asg, "target_group_arns") == [TG_ARN]
        assert _arg(asg, "health_check_type") == "ELB"
        assert _block(asg, "launch_template") == {"id": "lt-1", "version": "$Default"}
        assert _block(asg, "tag") == {
            "key": "service",
            "value": "shop",
            "propagate_at_launch": True,
        }
        assert "# unmapped: Instances" in IaCGenerator().generate_resource_block(AUTOSCALING_GROUP)

        template = _body(LAUNCH_TEMPLATE)
        assert _arg(template, "name") == "worker"
        assert _arg(template, "image_id") == "ami-123"
        assert _arg(template, "instance_type") == "t3.small"
        assert _arg(template, "vpc_security_group_ids") == ["sg-app"]
        assert _block(template, "iam_instance_profile") == {"name": "worker-profile"}
        assert _block(template, "metadata_options") == {
            "http_endpoint": "enabled",
            "http_tokens": "required",
        }
        assert "user_data" in str(_unquote(template["lifecycle"][0])["ignore_changes"])

    def test_iac_data_and_messaging_types_map_arguments_req_7_3(self):
        cache = _body(REPLICATION_GROUP)
        assert _arg(cache, "replication_group_id") == "cache"
        assert _arg(cache, "description") == "session cache"
        assert _arg(cache, "node_type") == "cache.t4g.micro"
        assert _arg(cache, "engine") == "redis"
        assert _arg(cache, "engine_version") == "7.1"
        assert _arg(cache, "port") == 6379
        assert _arg(cache, "num_cache_clusters") == 2
        assert _arg(cache, "parameter_group_name") == "default.redis7"
        assert _arg(cache, "subnet_group_name") == "cache-subnets"
        assert _arg(cache, "security_group_ids") == ["sg-app"]
        assert _arg(cache, "automatic_failover_enabled") is True
        assert _arg(cache, "multi_az_enabled") is True
        assert _arg(cache, "at_rest_encryption_enabled") is True
        assert _arg(cache, "transit_encryption_enabled") is True
        assert _arg(cache, "tags") == {"service": "shop"}

        queue = _body(QUEUE)
        assert _arg(queue, "name") == "jobs"
        assert _arg(queue, "visibility_timeout_seconds") == 60
        assert _arg(queue, "message_retention_seconds") == 345600
        assert _arg(queue, "receive_wait_time_seconds") == 20
        assert _arg(queue, "sqs_managed_sse_enabled") is True
        assert _json_arg(queue, "redrive_policy")["maxReceiveCount"] == 5
        assert "approximate" not in json.dumps(queue).lower()
        assert _arg(queue, "tags") == {"service": "shop"}

        topic = _body(TOPIC)
        assert _arg(topic, "name") == "events"
        assert _arg(topic, "display_name") == "Shop events"
        assert _json_arg(topic, "policy") == {"Version": "2012-10-17", "Statement": []}
        # An empty policy attribute means "not set", not an empty JSON document.
        assert "delivery_policy" not in topic
        assert "# unmapped: Subscriptions" in IaCGenerator().generate_resource_block(TOPIC)

    def test_iac_event_types_map_arguments_req_7_3(self):
        rule = _body(EVENT_RULE)
        assert _arg(rule, "name") == "nightly"
        assert _arg(rule, "schedule_expression") == "cron(0 2 * * ? *)"
        assert _arg(rule, "state") == "ENABLED"
        assert "event_bus_name" not in rule
        targets = _resources(IaCGenerator().generate_resource_block(EVENT_RULE))
        bodies = {n: b for (t, n), b in targets.items() if t == "aws_cloudwatch_event_target"}
        assert sorted(bodies) == ["nightly_cleanup", "nightly_worker"]
        worker = bodies["nightly_worker"]
        assert _arg(worker, "rule") == "${aws_cloudwatch_event_rule.nightly.name}"
        assert _arg(worker, "arn") == FUNCTION_ARN and _arg(worker, "target_id") == "worker"
        # HCL string escapes are JSON escapes.
        assert json.loads(f'"{_arg(worker, "input")}"') == '{"report": true}'
        cleanup = bodies["nightly_cleanup"]
        assert _arg(cleanup, "role_arn") == f"{ROLE_PREFIX}/events"
        assert _block(cleanup, "ecs_target") == {"task_definition_arn": TASK_ARN, "task_count": 1}

        bus_rule = _body(BUS_RULE)
        assert _arg(bus_rule, "event_bus_name") == "orders-bus"
        assert _json_arg(bus_rule, "event_pattern") == {"source": ["shop.orders"]}
        assert _arg(bus_rule, "state") == "DISABLED"

        schedule = _body(SCHEDULE)
        assert _arg(schedule, "name") == "report"
        assert _arg(schedule, "group_name") == "default"
        assert _arg(schedule, "schedule_expression") == "rate(1 hour)"
        assert _arg(schedule, "schedule_expression_timezone") == "UTC"
        assert _block(schedule, "flexible_time_window") == {
            "mode": "FLEXIBLE",
            "maximum_window_in_minutes": 15,
        }
        target = _block(schedule, "target")
        assert target["arn"] == QUEUE_ARN and target["role_arn"] == f"{ROLE_PREFIX}/scheduler"
        assert json.loads(f'"{target["input"]}"') == '{"task": "report"}'
        retry = target["retry_policy"]
        retry = _unquote(retry[0] if isinstance(retry, list) else retry)
        assert retry == {"maximum_event_age_in_seconds": 86400, "maximum_retry_attempts": 185}

    def test_iac_compute_data_import_ids_req_7_4(self):
        imports = _imports(IaCGenerator().generate_imports(COMPUTE_DATA))
        compute, data = "module.compute.", "module.data."
        expected = {
            compute + "aws_ecs_cluster.web": "web",
            compute + "aws_ecs_service.api": "web/api",
            compute + "aws_ecs_task_definition.api_7": TASK_ARN,
            compute + "aws_ecr_repository.team_api": "team/api",
            compute + "aws_autoscaling_group.workers": "workers",
            compute + "aws_launch_template.worker": "lt-1",
            data + "aws_elasticache_replication_group.cache": "cache",
            data + "aws_sqs_queue.jobs": f"https://sqs.us-east-1.amazonaws.com/{ACCOUNT}/jobs",
            data + "aws_sns_topic.events": TOPIC_ARN,
            compute + "aws_cloudwatch_event_rule.nightly": "nightly",
            compute + "aws_cloudwatch_event_target.nightly_worker": "nightly/worker",
            compute + "aws_cloudwatch_event_target.nightly_cleanup": "nightly/cleanup",
            compute + "aws_cloudwatch_event_rule.created": "orders-bus/created",
            compute + "aws_cloudwatch_event_target.created_q": "orders-bus/created/q",
            compute + "aws_scheduler_schedule.report": "default/report",
        }
        assert imports == expected

    def test_iac_compute_data_files_parse_as_hcl_req_7_2(self, tmp_path):
        files = IaCGenerator().generate_terraform(COMPUTE_DATA, target_dir=tmp_path)
        assert "aws_ecs_service" in files["modules/compute/main.tf"]
        for rel, text in files.items():
            if rel.endswith(".tf"):
                hcl2.loads(text)
            if rel.endswith("/main.tf") and rel.startswith("modules/"):
                assert "# unmapped: Tags" not in text, rel
                assert "# unmapped: tags" not in text, rel


# ============================================================================
# modules/ + envs/<env>/ layout (Requirements 7.2, 7.4, 16.1, 16.2, 16.3)
# ============================================================================

import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402

PROJECT = ALL + NETWORK_EDGE + COMPUTE_DATA
MODULE_FILES = ("README.md", "main.tf", "outputs.tf", "variables.tf", "versions.tf")
ENV_FILES = (
    "backend.tf",
    "imports.tf",
    "main.tf",
    "outputs.tf",
    "providers.tf",
    "terraform.tfvars",
    "variables.tf",
    "verify_state.sh",
    "versions.tf",
)


def _blocks(text: str, kind: str) -> dict:
    """{name: body} of the top-level `kind` blocks (variable, output, module, provider)."""
    out = {}
    for item in hcl2.loads(text).get(kind, []):
        for name, body in item.items():
            out[_unquote(name)] = body
    return out


def _code_lines(text: str) -> list[str]:
    """Lines that are not comments (heredoc bodies included)."""
    return [line for line in text.splitlines() if not line.lstrip().startswith("#")]


@pytest.fixture
def project(tmp_path):
    files = IaCGenerator().generate_terraform(PROJECT, target_dir=tmp_path)
    return tmp_path, files


class TestIaCProjectLayout:
    def test_iac_directory_snapshot_req_16_1(self, project):
        root, files = project
        modules = ("compute", "data", "edge", "iam", "network", "observability")
        expected = sorted(
            ["README.md"]
            + [f"modules/{m}/{f}" for m in modules for f in MODULE_FILES]
            + [f"envs/default/{f}" for f in ENV_FILES]
        )
        assert sorted(files) == expected
        on_disk = sorted(
            str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file()
        )
        assert on_disk == expected
        for rel, text in files.items():
            assert (root / rel).read_text(encoding="utf-8") == text
        assert (root / "envs/default/verify_state.sh").stat().st_mode & 0o111

    def test_iac_each_resource_once_in_module_and_imports_req_7_4(self, project):
        _root, files = project
        addresses = []
        for rel, text in files.items():
            if rel.startswith("modules/") and rel.endswith("/main.tf"):
                module = rel.split("/")[1]
                addresses += [f"module.{module}.{t}.{n}" for t, n in _resources(text)]
        assert len(addresses) == len(set(addresses))
        imports = _imports(files["envs/default/imports.tf"])
        assert sorted(imports) == sorted(addresses), "one import block per resource block"
        primaries = [a for a in addresses if a.split(".")[2] in {s.resource_type for s in PROJECT}]
        assert len(primaries) == len(PROJECT)
        assert imports["module.network.aws_vpc.main"] == "vpc-1"
        assert imports["module.edge.aws_lb.web_alb"] == LB_ARN
        assert "aws_" not in "".join(rel for rel in files if rel.startswith("envs/"))

    def test_iac_module_assignment_req_16_1(self, project):
        _root, files = project
        types = {
            rel.split("/")[1]: {t for t, _n in _resources(text)}
            for rel, text in files.items()
            if rel.startswith("modules/") and rel.endswith("/main.tf")
        }
        assert {"aws_vpc", "aws_subnet", "aws_security_group"} <= types["network"]
        assert {"aws_lb", "aws_cloudfront_distribution", "aws_route53_zone"} <= types["edge"]
        assert {"aws_ecs_service", "aws_lambda_function", "aws_instance"} <= types["compute"]
        assert {"aws_db_instance", "aws_s3_bucket", "aws_sqs_queue"} <= types["data"]
        assert types["iam"] == {
            "aws_iam_role",
            "aws_iam_role_policy",
            "aws_iam_role_policy_attachment",
        }
        assert types["observability"] == {"aws_cloudwatch_log_group"}

    def test_iac_cross_module_references_req_16_2(self, project):
        _root, files = project
        network = files["modules/network/main.tf"]
        edge = files["modules/edge/main.tf"]
        compute = files["modules/compute/main.tf"]
        data = files["modules/data/main.tf"]
        security_group = _resources(network)[("aws_security_group", "web")]
        assert _arg(security_group, "vpc_id") == "${aws_vpc.main.id}"
        lb = _resources(edge)[("aws_lb", "web_alb")]
        # Managed subnet through the network module; unmanaged ids stay literal.
        assert _arg(lb, "subnets") == ['${var.subnet_ids["subnet_a"]}', "subnet-b"]
        listener = _resources(edge)[("aws_lb_listener", "https_443")]
        assert _arg(listener, "load_balancer_arn") == "${aws_lb.web_alb.arn}"
        assert _arg(listener, "certificate_arn") == "${aws_acm_certificate.example_com.arn}"
        distribution = _resources(edge)[("aws_cloudfront_distribution", "example_com")]
        assert _arg(distribution, "web_acl_id") == "${aws_wafv2_web_acl.web_acl.arn}"
        service = _resources(compute)[("aws_ecs_service", "api")]
        assert _arg(service, "cluster") == "${aws_ecs_cluster.web.arn}"
        assert _arg(service, "task_definition") == "${aws_ecs_task_definition.api_7.arn}"
        assert _block(service, "load_balancer")["target_group_arn"] == (
            '${var.lb_target_group_arns["web_tg"]}'
        )
        function = _resources(compute)[("aws_lambda_function", "process_order")]
        assert _arg(function, "role") == '${var.iam_role_arns["lambda_role"]}'
        instance = _resources(compute)[("aws_instance", "web_1")]
        assert _arg(instance, "vpc_security_group_ids") == ['${var.security_group_ids["web"]}']
        schedule = _resources(compute)[("aws_scheduler_schedule", "report")]
        assert _block(schedule, "target")["arn"] == '${var.sqs_queue_arns["jobs"]}'
        database = _resources(data)[("aws_db_instance", "orders_db")]
        assert _arg(database, "vpc_security_group_ids") == ['${var.security_group_ids["web"]}']

        managed = ["vpc-1", "subnet-a", "sg-1", "rtb-1", "igw-1", "nat-1", "vpce-1", "lt-1"]
        managed += [LB_ARN, TG_ARN, CERT_ARN, WAF_ARN, CLUSTER_ARN, TASK_ARN, QUEUE_ARN, ROLE.arn]
        for rel, text in files.items():
            if rel.startswith("modules/") and rel.endswith("/main.tf"):
                for line in _code_lines(text):
                    for value in managed:
                        assert f'"{value}"' not in line, (rel, line)

        modules = _blocks(files["envs/default/main.tf"], "module")
        assert _unquote(modules["compute"]["lb_target_group_arns"]) == (
            "${module.edge.lb_target_group_arns}"
        )
        assert _unquote(modules["edge"]["subnet_ids"]) == "${module.network.subnet_ids}"
        assert _unquote(modules["network"]["source"]) == "../../modules/network"

    def test_iac_variables_and_outputs_typed_and_described_req_16_2(self, project):
        _root, files = project
        env_modules = _blocks(files["envs/default/main.tf"], "module")
        for rel, text in files.items():
            if not rel.endswith(".tf"):
                continue
            for name, body in _blocks(text, "variable").items():
                assert body.get("type") and body.get("description"), (rel, name)
            for name, body in _blocks(text, "output").items():
                assert body.get("description") and "value" in body, (rel, name)
            if rel.startswith("modules/") and rel.endswith("/main.tf"):
                module = rel.split("/")[1]
                declared = set(_blocks(files[f"modules/{module}/variables.tf"], "variable"))
                used = set(re.findall(r"\bvar\.([a-z_0-9]+)", text))
                assert used == declared, module
                wired = set(env_modules[module]) - {"source", "providers", "__is_block__"}
                assert wired == declared, module
                outputs = _blocks(files[f"modules/{module}/outputs.tf"], "output")
                assert outputs, module
        env_outputs = _blocks(files["envs/default/outputs.tf"], "output")
        assert _unquote(env_outputs["subnet_ids"]["value"]) == "${module.network.subnet_ids}"
        assert "default_tags" in _blocks(files["envs/default/variables.tf"], "variable")

    def test_iac_providers_backend_versions_req_16_1(self, project):
        _root, files = project
        providers = [p['"aws"'] for p in hcl2.loads(files["envs/default/providers.tf"])["provider"]]
        default = next(p for p in providers if "alias" not in p)
        assert _unquote(default["region"]) == "us-east-1"
        assert _unquote(default["default_tags"][0]["tags"]) == "${var.default_tags}"
        aliases = {_unquote(p["alias"]): _unquote(p["region"]) for p in providers if "alias" in p}
        assert aliases == {"us_west_2": "us-west-2"}
        function = _resources(files["modules/compute/main.tf"])[
            ("aws_lambda_function", "process_order")
        ]
        assert _unquote(function["provider"]) == "${aws.us_west_2}"
        assert "aws.us_west_2" in files["modules/compute/versions.tf"]
        assert "configuration_aliases" not in files["modules/network/versions.tf"]
        compute = _blocks(files["envs/default/main.tf"], "module")["compute"]
        assert "aws.us_west_2" in str(compute["providers"])
        backend = hcl2.loads(files["envs/default/backend.tf"])["terraform"][0]["backend"][0]
        assert '"s3"' in backend or "s3" in backend
        assert "-backend-config" in files["envs/default/backend.tf"]
        assert 'required_version = ">= 1.5.0"' in files["envs/default/versions.tf"]
        assert 'version = "~> 5.0"' in re.sub(r" +", " ", files["envs/default/versions.tf"])
        assert "terraform plan" in files["envs/default/verify_state.sh"]
        assert "show -json" in files["envs/default/verify_state.sh"]

    def test_iac_names_and_environment_from_tags_req_16_2(self, tmp_path):
        tags = [
            {"Key": "Project", "Value": "storefront"},
            {"Key": "environment", "Value": "prod"},
        ]
        subnet = _s(
            "aws_subnet",
            f"{EC2_ARN}:subnet/subnet-1",
            {
                "SubnetId": "subnet-1",
                "Tags": [*tags, {"Key": "Name", "Value": "storefront-public-a"}],
            },
        )
        cluster = _s(
            "aws_ecs_cluster",
            f"{ECS}:cluster/storefront",
            {"clusterName": "storefront", "clusterArn": f"{ECS}:cluster/storefront"},
        )
        database = _s(
            "aws_db_instance",
            f"arn:aws:rds:us-east-1:{ACCOUNT}:db:storefront-prod-db",
            {"DBInstanceIdentifier": "storefront-prod-db", "TagList": tags},
        )
        generator = IaCGenerator()
        names = generator.assign_names([subnet, cluster, database])
        assert names == {subnet.arn: "public_a", cluster.arn: "main", database.arn: "db"}
        files = generator.generate_terraform([subnet, cluster, database], target_dir=tmp_path)
        assert "envs/prod/main.tf" in files
        for rel, text in files.items():
            if rel.startswith("modules/") and rel.endswith("/main.tf"):
                for _t, name in _resources(text):
                    assert re.fullmatch(r"[a-z_][a-z0-9_]*", name), name

    def test_iac_explicit_project_tags_strip_prefix_req_16_2(self):
        spec = _s(
            "aws_sqs_queue",
            f"arn:aws:sqs:us-east-1:{ACCOUNT}:acme-jobs",
            {"QueueUrl": f"https://sqs.us-east-1.amazonaws.com/{ACCOUNT}/acme-jobs"},
        )
        assert IaCGenerator().assign_names([spec]) == {spec.arn: "acme_jobs"}
        generator = IaCGenerator(project_tags={"team": "acme"})
        assert generator.assign_names([spec]) == {spec.arn: "jobs"}

    def test_iac_default_tags_hold_tags_common_to_every_resource_req_16_1(self, tmp_path):
        tags = [{"Key": "service", "Value": "shop"}, {"Key": "aws:cloudformation:x", "Value": "y"}]
        vpc = _s("aws_vpc", f"{EC2_ARN}:vpc/vpc-9", {"VpcId": "vpc-9", "Tags": tags})
        subnet = _s(
            "aws_subnet",
            f"{EC2_ARN}:subnet/subnet-9",
            {
                "SubnetId": "subnet-9",
                "VpcId": "vpc-9",
                "Tags": [*tags, {"Key": "Name", "Value": "a"}],
            },
        )
        files = IaCGenerator().generate_terraform([vpc, subnet], target_dir=tmp_path)
        tfvars = hcl2.loads(files["envs/default/terraform.tfvars"])
        assert _unquote(tfvars["default_tags"]) == {"service": "shop"}
        resources = _resources(files["modules/network/main.tf"])
        # aws: tags belong to AWS and cannot be set through Terraform.
        assert _arg(resources[("aws_subnet", "a")], "tags") == {"Name": "a"}
        assert "tags" not in resources[("aws_vpc", "vpc_9")]

        # One taggable resource without the tag: nothing is common.
        bare = _s(
            "aws_internet_gateway",
            f"{EC2_ARN}:internet-gateway/igw-9",
            {"InternetGatewayId": "igw-9"},
        )
        files = IaCGenerator().generate_terraform([vpc, subnet, bare], target_dir=tmp_path / "b")
        assert _unquote(hcl2.loads(files["envs/default/terraform.tfvars"])["default_tags"]) == {}

    @pytest.mark.skipif(shutil.which("terraform") is None, reason="terraform CLI not installed")
    def test_iac_terraform_fmt_check_req_7_2(self, project):
        root, _files = project
        result = subprocess.run(
            ["terraform", "fmt", "-check", "-recursive", "-diff", "-no-color"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
