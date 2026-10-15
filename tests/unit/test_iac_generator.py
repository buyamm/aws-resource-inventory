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
        assert _arg(association, "route_table_id") == "${aws_route_table.rtb-1.id}"

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
        assert sorted(record_bodies) == ["Z1_shop_example_com_A", "Z1_www_example_com_CNAME"]
        alias = _block(record_bodies["Z1_shop_example_com_A"], "alias")
        assert alias["name"] == "d1.cloudfront.net."
        assert _arg(record_bodies["Z1_www_example_com_CNAME"], "records") == ["shop.example.com"]

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
        script = IaCGenerator().generate_import_script(NETWORK_EDGE).replace("'", "")
        east, glob = "module.us_east_1.", "module.global."
        expected = [
            (east + "aws_subnet.subnet-a", "subnet-a"),
            (east + "aws_route_table.rtb-1", "rtb-1"),
            (east + "aws_route_table_association.rtb-1_subnet-a", "subnet-a/rtb-1"),
            (east + "aws_internet_gateway.igw-1", "igw-1"),
            (east + "aws_nat_gateway.nat-1", "nat-1"),
            (east + "aws_vpc_endpoint.vpce-1", "vpce-1"),
            (east + "aws_lb.app_web-alb_abc", LB_ARN),
            (east + "aws_lb_listener.app_web-alb_abc_def", LISTENER_ARN),
            (east + "aws_lb_target_group.web-tg_123", TG_ARN),
            (east + "aws_acm_certificate.uuid-1", CERT_ARN),
            (glob + "aws_cloudfront_distribution.E1", "E1"),
            (glob + "aws_route53_zone.Z1", "Z1"),
            (glob + "aws_route53_record.Z1_shop_example_com_A", "Z1_shop.example.com_A"),
            (glob + "aws_route53_record.Z1_www_example_com_CNAME", "Z1_www.example.com_CNAME"),
            (glob + "aws_wafv2_web_acl.web-acl_uuid-2", "uuid-2/web-acl/CLOUDFRONT"),
        ]
        for address, import_id in expected:
            assert f"terraform import {address} {import_id}" in script, address
        assert script.count("terraform import ") == len(expected)

    def test_iac_network_edge_files_parse_as_hcl_req_7_2(self, tmp_path):
        files = IaCGenerator().generate_terraform(NETWORK_EDGE, target_dir=tmp_path)
        assert "global/aws_cloudfront_distribution.tf" in files
        assert "us-east-1/aws_lb_listener.tf" in files
        for rel, text in files.items():
            if rel.endswith(".tf"):
                hcl2.loads(text)
            if rel.endswith(".tf") and "/" in rel and not rel.endswith("versions.tf"):
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
        script = IaCGenerator().generate_import_script(COMPUTE_DATA).replace("'", "")
        east = "module.us_east_1."
        expected = [
            (east + "aws_ecs_cluster.web", "web"),
            (east + "aws_ecs_service.web_api", "web/api"),
            (east + "aws_ecs_task_definition.api_7", TASK_ARN),
            (east + "aws_ecr_repository.team_api", "team/api"),
            (east + "aws_autoscaling_group.workers", "workers"),
            (east + "aws_launch_template.lt-1", "lt-1"),
            (east + "aws_elasticache_replication_group.cache", "cache"),
            (east + "aws_sqs_queue.jobs", f"https://sqs.us-east-1.amazonaws.com/{ACCOUNT}/jobs"),
            (east + "aws_sns_topic.events", TOPIC_ARN),
            (east + "aws_cloudwatch_event_rule.nightly", "nightly"),
            (east + "aws_cloudwatch_event_target.nightly_worker", "nightly/worker"),
            (east + "aws_cloudwatch_event_target.nightly_cleanup", "nightly/cleanup"),
            (east + "aws_cloudwatch_event_rule.orders-bus_created", "orders-bus/created"),
            (east + "aws_cloudwatch_event_target.orders-bus_created_q", "orders-bus/created/q"),
            (east + "aws_scheduler_schedule.default_report", "default/report"),
        ]
        for address, import_id in expected:
            assert f"terraform import {address} {import_id}" in script, address
        assert script.count("terraform import ") == len(expected)

    def test_iac_compute_data_files_parse_as_hcl_req_7_2(self, tmp_path):
        files = IaCGenerator().generate_terraform(COMPUTE_DATA, target_dir=tmp_path)
        assert "us-east-1/aws_ecs_service.tf" in files
        for rel, text in files.items():
            if rel.endswith(".tf"):
                hcl2.loads(text)
            if rel.endswith(".tf") and "/" in rel and not rel.endswith("versions.tf"):
                assert "# unmapped: Tags" not in text, rel
                assert "# unmapped: tags" not in text, rel
