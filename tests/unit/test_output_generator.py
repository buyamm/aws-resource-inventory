"""
Unit tests for OutputGenerator (TDD RED and GREEN phases).

Requirements Coverage:
- Requirement 3.1: Save data in both JSON and Markdown formats
- Requirement 3.2: Organize output files by resource type and region in directory structure
- Requirement 3.3: Include timestamps, AWS account ID, region, and metadata in JSON output
- Requirement 3.4: Format specifications in human-readable tables and sections in Markdown
- Requirement 3.5: Include checksums for data integrity verification
- Requirement 3.6: Store raw API responses in separate directory for audit purposes
- Requirement 9.5: Sanitize sensitive data from output files
- Requirement 10.3: Summary report comparing estimated manual effort vs automated collection time
"""

import hashlib
import json
from pathlib import Path

import pytest

from src.output_generator import OutputGenerator
from src.parser import ResourceSpec, SpecMetadata

# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_s3_spec() -> ResourceSpec:
    """Provide a sample S3 ResourceSpec object."""
    return ResourceSpec(
        resource_type="aws_s3_bucket",
        arn="arn:aws:s3:::my-test-bucket",
        region="us-east-1",
        account_id="123456789012",
        specifications={
            "bucket_name": "my-test-bucket",
            "versioning": {"status": "Enabled"},
            "encryption": {"rules": [{"sse_algorithm": "AES256"}]},
            "tags": {"Environment": "Production", "Project": "Inventory"},
        },
        metadata=SpecMetadata(
            collected_at="2026-10-07T12:00:00Z",
            collector_version="1.0.0",
            api_version="2006-03-01",
            checksum="test-checksum-s3-123",
        ),
        raw_response='{"Name": "my-test-bucket", "CreationDate": "2026-01-01T00:00:00Z"}',
    )


@pytest.fixture
def sample_ec2_spec() -> ResourceSpec:
    """Provide a sample EC2 ResourceSpec object."""
    return ResourceSpec(
        resource_type="aws_ec2_instance",
        arn="arn:aws:ec2:us-west-2:123456789012:instance/i-0123456789abcdef0",
        region="us-west-2",
        account_id="123456789012",
        specifications={
            "instance_id": "i-0123456789abcdef0",
            "instance_type": "t3.medium",
            "state": "running",
            "vpc_id": "vpc-01234567",
            "subnet_id": "subnet-01234567",
            "private_ip": "10.0.1.50",
            "security_groups": [{"group_id": "sg-12345", "group_name": "app-sg"}],
            "tags": {"Name": "app-server-01", "Env": "prod"},
        },
        metadata=SpecMetadata(
            collected_at="2026-10-07T12:05:00Z",
            collector_version="1.0.0",
            api_version="2016-11-15",
            checksum="test-checksum-ec2-456",
        ),
        raw_response='{"InstanceId": "i-0123456789abcdef0", "State": {"Name": "running"}}',
    )


@pytest.fixture
def sample_sensitive_spec() -> ResourceSpec:
    """Provide a ResourceSpec containing sensitive values."""
    return ResourceSpec(
        resource_type="aws_lambda_function",
        arn="arn:aws:lambda:us-east-1:123456789012:function:secret-worker",
        region="us-east-1",
        account_id="123456789012",
        specifications={
            "function_name": "secret-worker",
            "runtime": "python3.9",
            "environment_variables": {
                "DATABASE_URL": "postgres://user:password123@localhost/db",
                "DB_PASSWORD": "super-secret-password",
                "API_KEY": "AKIAIOSFODNN7EXAMPLE",
                "PUBLIC_CONFIG": "safe-value",
            },
        },
        metadata=SpecMetadata(
            collected_at="2026-10-07T12:10:00Z",
            collector_version="1.0.0",
            api_version="2015-03-31",
            checksum="test-checksum-lambda-789",
        ),
        raw_response='{"FunctionName": "secret-worker"}',
    )


# ============================================================================
# Unit Tests for OutputGenerator
# ============================================================================

class TestOutputGeneratorFormats:
    """Tests for JSON and Markdown generation (Requirement 3.1)."""

    def test_output_generator_creates_json_and_markdown_req_3_1(
        self, tmp_path: Path, sample_s3_spec: ResourceSpec, sample_ec2_spec: ResourceSpec
    ) -> None:
        """Requirement 3.1: Save data in both JSON and Markdown formats."""
        specs = [sample_s3_spec, sample_ec2_spec]
        generator = OutputGenerator(output_dir=tmp_path)

        json_files = generator.generate_json(specs)
        md_files = generator.generate_markdown(specs)

        assert len(json_files) > 0, "Should generate at least one JSON file"
        assert len(md_files) > 0, "Should generate at least one Markdown file"

        # Check all returned files exist and are non-empty
        for f in json_files:
            assert f.exists(), f"JSON file {f} does not exist"
            assert f.stat().st_size > 0, f"JSON file {f} is empty"

        for f in md_files:
            assert f.exists(), f"Markdown file {f} does not exist"
            assert f.stat().st_size > 0, f"Markdown file {f} is empty"


class TestOutputGeneratorOrganization:
    """Tests for directory organization (Requirement 3.2)."""

    def test_output_generator_organizes_by_type_and_region_req_3_2(
        self, tmp_path: Path, sample_s3_spec: ResourceSpec, sample_ec2_spec: ResourceSpec
    ) -> None:
        """Requirement 3.2: Organize output files by resource type and region."""
        specs = [sample_s3_spec, sample_ec2_spec]
        generator = OutputGenerator(output_dir=tmp_path)
        generator.generate_json(specs)
        generator.generate_markdown(specs)

        # Expected paths:
        # tmp_path / "aws_s3_bucket" / "us-east-1"
        # tmp_path / "aws_ec2_instance" / "us-west-2"
        s3_dir = tmp_path / "aws_s3_bucket" / "us-east-1"
        ec2_dir = tmp_path / "aws_ec2_instance" / "us-west-2"

        assert s3_dir.exists() and s3_dir.is_dir(), f"Expected directory {s3_dir} to exist"
        assert ec2_dir.exists() and ec2_dir.is_dir(), f"Expected directory {ec2_dir} to exist"

        # Check files inside the organized directories
        s3_json_files = list(s3_dir.glob("*.json"))
        s3_md_files = list(s3_dir.glob("*.md"))
        assert len(s3_json_files) >= 1
        assert len(s3_md_files) >= 1

        ec2_json_files = list(ec2_dir.glob("*.json"))
        ec2_md_files = list(ec2_dir.glob("*.md"))
        assert len(ec2_json_files) >= 1
        assert len(ec2_md_files) >= 1


class TestOutputGeneratorMetadata:
    """Tests for timestamps, account ID, region, and metadata in JSON (Requirement 3.3)."""

    def test_output_generator_includes_timestamps_account_metadata_req_3_3(
        self, tmp_path: Path, sample_s3_spec: ResourceSpec
    ) -> None:
        """Requirement 3.3: JSON output includes timestamps, account ID, region, and metadata."""
        generator = OutputGenerator(output_dir=tmp_path)
        json_files = generator.generate_json([sample_s3_spec])

        # Read the generated individual spec file
        spec_file = [f for f in json_files if "aws_s3_bucket" in str(f)][0]
        with open(spec_file, encoding="utf-8") as fp:
            data = json.load(fp)

        assert "account_id" in data
        assert data["account_id"] == "123456789012"
        assert "region" in data
        assert data["region"] == "us-east-1"
        assert "metadata" in data
        assert data["metadata"]["collected_at"] == "2026-10-07T12:00:00Z"
        assert data["metadata"]["collector_version"] == "1.0.0"
        assert "timestamp" in data or "generated_at" in data or "collected_at" in data["metadata"]


class TestOutputGeneratorMarkdownFormatting:
    """Tests for Markdown formatting with tables and sections (Requirement 3.4)."""

    def test_output_generator_formats_markdown_tables_and_sections_req_3_4(
        self, tmp_path: Path, sample_s3_spec: ResourceSpec, sample_ec2_spec: ResourceSpec
    ) -> None:
        """Requirement 3.4: Markdown formats specifications in human-readable tables and sections."""
        generator = OutputGenerator(output_dir=tmp_path)
        md_files = generator.generate_markdown([sample_s3_spec, sample_ec2_spec])

        # Verify summary resources.md or individual markdown files
        has_table = False
        has_sections = False

        for f in md_files:
            content = f.read_text(encoding="utf-8")
            # Tables in markdown use pipe symbols and hyphens
            if "| " in content and "---" in content:
                has_table = True
            # Sections use markdown headings
            if "# " in content or "## " in content:
                has_sections = True

        assert has_table, "Markdown output should contain at least one table"
        assert has_sections, "Markdown output should contain markdown sections (# / ##)"


class TestOutputGeneratorChecksums:
    """Tests for checksum verification (Requirement 3.5)."""

    def test_output_generator_includes_checksums_req_3_5(
        self, tmp_path: Path, sample_s3_spec: ResourceSpec, sample_ec2_spec: ResourceSpec
    ) -> None:
        """Requirement 3.5: Include checksums for all output files."""
        generator = OutputGenerator(output_dir=tmp_path)
        generator.generate_json([sample_s3_spec, sample_ec2_spec])
        generator.generate_markdown([sample_s3_spec, sample_ec2_spec])

        checksum_file = generator.generate_checksums()
        assert checksum_file.exists(), "Checksum file must be created"

        # Verify checksum file contents
        content = checksum_file.read_text(encoding="utf-8")
        assert len(content) > 0

        if checksum_file.suffix == ".json":
            checksums = json.loads(content)
            assert isinstance(checksums, dict)
            for rel_path, expected_hash in checksums.items():
                target_file = tmp_path / rel_path
                assert target_file.exists()
                actual_hash = hashlib.sha256(target_file.read_bytes()).hexdigest()
                assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}"
        else:
            # sha256sum format: <hash>  <filename>
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            assert len(lines) > 0
            for line in lines:
                parts = line.split(maxsplit=1)
                assert len(parts) == 2
                expected_hash, rel_path = parts[0], parts[1].strip()
                target_file = tmp_path / rel_path
                assert target_file.exists(), f"Target file {target_file} from checksum not found"
                actual_hash = hashlib.sha256(target_file.read_bytes()).hexdigest()
                assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}"


class TestOutputGeneratorRawResponses:
    """Tests for raw API response storage (Requirement 3.6)."""

    def test_output_generator_stores_raw_responses_in_separate_dir_req_3_6(
        self, tmp_path: Path, sample_s3_spec: ResourceSpec, sample_ec2_spec: ResourceSpec
    ) -> None:
        """Requirement 3.6: Store raw API responses in separate directory."""
        generator = OutputGenerator(output_dir=tmp_path)
        raw_files = generator.store_raw_responses([sample_s3_spec, sample_ec2_spec])

        raw_dir = tmp_path / "raw_responses"
        assert raw_dir.exists() and raw_dir.is_dir(), "raw_responses directory must exist"

        assert len(raw_files) == 2
        for f in raw_files:
            assert f.exists()
            assert raw_dir in f.parents or f.parent == raw_dir


class TestOutputGeneratorSanitization:
    """Tests for sensitive data sanitization in output files (Requirement 9.5)."""

    def test_output_generator_sanitizes_sensitive_data_req_9_5(
        self, tmp_path: Path, sample_sensitive_spec: ResourceSpec
    ) -> None:
        """Requirement 9.5: Sanitize sensitive data from output files."""
        generator = OutputGenerator(output_dir=tmp_path)
        json_files = generator.generate_json([sample_sensitive_spec])
        md_files = generator.generate_markdown([sample_sensitive_spec])

        # Verify plaintext secrets do NOT appear in any generated JSON or Markdown
        for f in json_files:
            content = f.read_text(encoding="utf-8")
            assert "super-secret-password" not in content
            assert "AKIAIOSFODNN7EXAMPLE" not in content
            # Placeholder text must appear
            assert "[REDACTED" in content

        for f in md_files:
            content = f.read_text(encoding="utf-8")
            assert "super-secret-password" not in content
            assert "AKIAIOSFODNN7EXAMPLE" not in content
            assert "[REDACTED" in content


class TestOutputGeneratorMetricsAndSummary:
    """Tests for time savings and summary report (Requirements 10.3, 10.4)."""

    def test_output_generator_summary_report_time_savings_req_10_3(
        self, tmp_path: Path, sample_s3_spec: ResourceSpec, sample_ec2_spec: ResourceSpec
    ) -> None:
        """Requirement 10.3 & 10.4: Summary report compares estimated manual effort vs automated time."""
        generator = OutputGenerator(output_dir=tmp_path)
        specs = [sample_s3_spec, sample_ec2_spec]
        # Automated time: 60 seconds (1 minute)
        # Manual time: 2 resources * 5 minutes = 10 minutes (0.167 hours)
        report = generator.generate_summary_report(specs, duration_seconds=60.0)

        assert "Manual Effort" in report or "manual" in report.lower()
        assert "Time Saved" in report or "savings" in report.lower()
        assert "5 minutes" in report or "baseline" in report.lower()
        assert "10" in report or "0.17" in report or "0.16" in report  # 10 minutes or ~0.17 hours manual


class TestOutputGeneratorCompleteWorkflow:
    """Tests for generate_all helper and aggregate output."""

    def test_output_generator_generate_all(
        self, tmp_path: Path, sample_s3_spec: ResourceSpec, sample_ec2_spec: ResourceSpec
    ) -> None:
        """Verify generate_all creates all required artifacts."""
        generator = OutputGenerator(output_dir=tmp_path)
        specs = [sample_s3_spec, sample_ec2_spec]

        result = generator.generate_all(specs, duration_seconds=45.0)

        assert "json_files" in result
        assert "markdown_files" in result
        assert "checksum_file" in result
        assert "raw_files" in result
        assert "summary_report" in result

        # Verify aggregated files exist
        assert (tmp_path / "resources.json").exists()
        assert (tmp_path / "resources.md").exists()
        assert (tmp_path / "checksums.sha256").exists() or (tmp_path / "checksums.json").exists()
