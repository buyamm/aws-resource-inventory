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
        generator = IaCGenerator(spec_base_path="output/specs")
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
