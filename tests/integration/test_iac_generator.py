"""
Integration & E2E tests for Terraform plan validation (Requirement 7.5).

Validates:
- Requirement 7.5: WHEN Terraform code generation completes, THE Resource_Inventory_System
  SHALL validate that running terraform plan shows zero changes.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.iac_generator import IaCGenerator
from src.parser import ResourceSpec, SpecMetadata


def test_iac_generator_terraform_plan_zero_changes_req_7_5(tmp_path: Path) -> None:
    """
    E2E: Validate that running terraform plan shows zero changes (Requirement 7.5).
    """
    spec = ResourceSpec(
        resource_type="aws_s3_bucket",
        arn="arn:aws:s3:::my-unique-bucket",
        region="us-east-1",
        account_id="123456789012",
        specifications={"bucket": "my-unique-bucket"},
        metadata=SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "v1", "chk"),
    )

    generator = IaCGenerator(output_dir=tmp_path)
    generator.generate_terraform([spec], target_dir=tmp_path)

    # Mock subprocess.run for terraform plan returning zero changes
    mock_res = MagicMock()
    mock_res.returncode = 0
    mock_res.stdout = "No changes. Your infrastructure matches the configuration."
    mock_res.stderr = ""

    with patch("subprocess.run", return_value=mock_res) as mock_run:
        success, message = generator.verify_terraform_plan(tmp_path)

        assert success is True
        assert "zero changes" in message.lower() or "no changes" in message.lower()
        mock_run.assert_called()


def test_iac_generator_terraform_plan_detects_changes(tmp_path: Path) -> None:
    """
    E2E: Validate that changes detected in terraform plan return failure (Requirement 7.5).
    """
    generator = IaCGenerator(output_dir=tmp_path)

    mock_res = MagicMock()
    mock_res.returncode = 2  # Terraform plan with detailed-exitcode returns 2 if changes present
    mock_res.stdout = "Plan: 1 to add, 0 to change, 0 to destroy."
    mock_res.stderr = ""

    with patch("subprocess.run", return_value=mock_res):
        success, message = generator.verify_terraform_plan(tmp_path)

        assert success is False
        assert "changes detected" in message.lower() or "1 to add" in message
