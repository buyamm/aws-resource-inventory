"""
Unit & Property-based tests for IaCGenerator (TDD RED & GREEN phases).

Requirements Coverage:
- Requirement 7.2: Create .tf files organized by resource type and region
- Requirement 7.3: Generate corresponding Terraform resource blocks with all collected specifications
- Requirement 7.4: Generate terraform import commands for all existing resources
- Requirement 7.6: Include verification script comparing Terraform state with actual AWS
- Requirement 7.7: Traceability comments linking back to original specification files
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
        import_script = generator.generate_import_script(sample_specs)

        assert "terraform import" in import_script
        assert "production-assets-bucket" in import_script
        assert "process-order" in import_script
        assert "aws_s3_bucket" in import_script
        assert "aws_lambda_function" in import_script

    def test_iac_generator_organizes_by_type_and_region_req_7_2(
        self, tmp_path: Path, sample_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 7.2: Create .tf files organized by resource type and region."""
        generator = IaCGenerator(output_dir=tmp_path)
        tf_files = generator.generate_terraform(sample_specs, target_dir=tmp_path)

        assert len(tf_files) > 0

        # Check directory structure on disk
        # Expect either <tmp_path>/<region>/<resource_type>.tf or <tmp_path>/<resource_type>/<region>/
        created_paths = [Path(p) for p in tf_files.keys()]
        assert any("us-east-1" in str(p) for p in created_paths)
        assert any("us-west-2" in str(p) for p in created_paths)

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
        ingress = [_unquote(b) for b in body["ingress"]]
        https = next(r for r in ingress if r["protocol"] == "tcp")
        assert https["from_port"] == 443 and https["to_port"] == 443
        assert https["cidr_blocks"] == ["0.0.0.0/0"]
        assert https["description"] == "https"
        internal = next(r for r in ingress if r["protocol"] == "-1")
        assert internal["self"] is True and internal["security_groups"] == ["sg-2"]
        assert internal["from_port"] == 0 and internal["to_port"] == 0
        assert _unquote(body["egress"][0])["cidr_blocks"] == ["0.0.0.0/0"]

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


class TestIaCFiles:
    def test_iac_generated_files_parse_as_hcl_req_7_2(self, tmp_path):
        files = IaCGenerator().generate_terraform(ALL, target_dir=tmp_path)
        assert "global/aws_s3_bucket.tf" in files
        assert "us-west-2/aws_lambda_function.tf" in files
        total = 0
        for rel, text in files.items():
            if rel.endswith(".tf"):
                parsed = hcl2.loads(text)
                total += len(parsed.get("resource", []))
        assert total >= len(ALL)

    def test_iac_provider_alias_per_region_req_7_2(self, tmp_path):
        files = IaCGenerator().generate_terraform(ALL, target_dir=tmp_path)
        providers = hcl2.loads(files["providers.tf"])["provider"]
        aliases = {_unquote(p['"aws"'].get("alias")) for p in providers}
        assert {"us_east_1", "us_west_2"} <= aliases
        assert None in aliases, "a default provider (us-east-1) is needed for global resources"
        modules = {}
        for item in hcl2.loads(files["main.tf"])["module"]:
            for name, body in item.items():
                modules[_unquote(name)] = _unquote(body)
        assert modules["us_west_2"]["source"] == "./us-west-2"
        assert "aws.us_west_2" in str(modules["us_west_2"]["providers"])
        assert modules["global"]["source"] == "./global"
        assert "versions.tf" in str(sorted(files))
        assert "us-west-2/versions.tf" in files
        for spec in ALL:
            assert "provider" not in _body(spec)

    def test_iac_import_ids_per_type_req_7_4(self):
        script = IaCGenerator().generate_import_script(ALL)
        east, west, glob = "module.us_east_1.", "module.us_west_2.", "module.global."
        expected = [
            (east + "aws_instance.i-0abc", "i-0abc"),
            (east + "aws_vpc.vpc-1", "vpc-1"),
            (east + "aws_security_group.sg-1", "sg-1"),
            (west + "aws_lambda_function.process-order", "process-order"),
            (east + "aws_db_instance.orders-db", "orders-db"),
            (
                east + "aws_cloudwatch_log_group.aws_lambda_process-order",
                "/aws/lambda/process-order",
            ),
            (east + "aws_sfn_state_machine.flow", STATE_MACHINE.arn),
            (east + "aws_dynamodb_table.orders", "orders"),
            (glob + "aws_s3_bucket.assets", "assets"),
            (glob + "aws_s3_bucket_versioning.assets", "assets"),
            (glob + "aws_iam_role.lambda-role", "lambda-role"),
            (
                glob + "aws_iam_role_policy_attachment.lambda-role_ReadOnly",
                "lambda-role/arn:aws:iam::aws:policy/ReadOnlyAccess",
            ),
            (glob + "aws_iam_role_policy.lambda-role_logs", "lambda-role:logs"),
        ]
        for address, import_id in expected:
            assert f"terraform import {address} {import_id}" in script.replace("'", ""), address
        assert script.count("terraform import ") == 15

    def test_iac_resource_names_are_unique_and_valid_req_7_2(self):
        a = _s("aws_s3_bucket", "arn:aws:s3:::1-data", {"Name": "1-data"}, region="global")
        b = _s("aws_s3_bucket", "arn:aws:s3:::1_data", {"Name": "1_data"}, region="global")
        names = IaCGenerator().assign_names([a, b])
        assert names[a.arn] == "r_1-data"
        assert names[b.arn] == "r_1_data"
        c = _s("aws_s3_bucket", "arn:aws:s3:::x.y", {"Name": "x.y"}, region="global")
        d = _s("aws_s3_bucket", "arn:aws:s3:::x_y", {"Name": "x_y"}, region="global")
        names = IaCGenerator().assign_names([c, d])
        assert sorted(names.values()) == ["x_y", "x_y_2"]


class TestIaCPlanVerification:
    def _run(self, returncode, stdout=""):
        result = MagicMock(returncode=returncode, stdout=stdout, stderr="")
        with patch("src.iac_generator.subprocess.run", return_value=result) as run:
            outcome = IaCGenerator().verify_terraform_plan("/tmp/tf")
        return outcome, run

    def test_iac_verify_plan_uses_exit_code_only_req_7_5(self):
        (ok, _msg), run = self._run(0, "Plan: 1 to add")
        assert ok is True
        assert run.call_args.args[0] == [
            "terraform",
            "plan",
            "-detailed-exitcode",
            "-no-color",
            "-input=false",
        ]
        (ok, msg), _ = self._run(2, "No changes.")
        assert ok is False and "changes detected" in msg.lower()
        (ok, msg), _ = self._run(1, "No changes.")
        assert ok is False and "error" in msg.lower()

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
