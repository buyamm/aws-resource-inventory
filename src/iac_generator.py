"""
IaC Generator Module

This module provides the IaCGenerator class for converting collected AWS resource
specifications into Terraform Infrastructure as Code (HCL) configurations,
import commands, and state verification scripts.

Requirements Coverage:
- Requirement 7.1: CLI option to generate Terraform code
- Requirement 7.2: Create .tf files organized by resource type and region
- Requirement 7.3: Generate corresponding Terraform resource blocks with all collected specifications
- Requirement 7.4: Generate terraform import commands for all existing resources
- Requirement 7.5: Validate running terraform plan shows zero changes
- Requirement 7.6: Include verification script comparing Terraform state with actual AWS
- Requirement 7.7: Traceability comments linking back to original specification files
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from src.parser import ResourceSpec


class IaCGenerator:
    """
    Terraform IaC Generator for AWS Resource Inventory.

    Converts typed ResourceSpec objects into standard Terraform configurations (.tf),
    import shell scripts, and plan verification workflows.
    """

    # Mapping from inventory resource type names to official Terraform resource types
    TYPE_MAP: dict[str, str] = {
        "aws_s3_bucket": "aws_s3_bucket",
        "aws_ec2_instance": "aws_instance",
        "aws_instance": "aws_instance",
        "aws_lambda_function": "aws_lambda_function",
        "aws_vpc": "aws_vpc",
        "aws_security_group": "aws_security_group",
        "aws_iam_role": "aws_iam_role",
        "aws_dynamodb_table": "aws_dynamodb_table",
        "aws_rds_instance": "aws_db_instance",
        "aws_db_instance": "aws_db_instance",
        "aws_cloudwatch_log_group": "aws_cloudwatch_log_group",
        "aws_step_function": "aws_sfn_state_machine",
        "aws_sfn_state_machine": "aws_sfn_state_machine",
    }

    def __init__(
        self,
        output_dir: str | Path | None = None,
        spec_base_path: str = "output",
    ) -> None:
        """
        Initialize IaCGenerator.

        Args:
            output_dir: Optional default directory to write generated .tf files.
            spec_base_path: Relative or absolute path prefix to specification files
                used in traceability comments (Requirement 7.7).
        """
        self.output_dir = Path(output_dir).resolve() if output_dir else None
        self.spec_base_path = spec_base_path

    # ========================================================================
    # Helpers
    # ========================================================================

    def _tf_resource_type(self, resource_type: str) -> str:
        """Map internal/AWS resource type to Terraform aws_* resource type."""
        normalized = resource_type.lower().strip()
        return self.TYPE_MAP.get(
            normalized, normalized if normalized.startswith("aws_") else f"aws_{normalized}"
        )

    def _resource_name(self, spec: ResourceSpec) -> str:
        """Extract a valid Terraform resource identifier name."""
        specs_dict = spec.specifications or {}
        candidate = (
            specs_dict.get("instance_id")
            or specs_dict.get("bucket_name")
            or specs_dict.get("bucket")
            or specs_dict.get("function_name")
            or specs_dict.get("table_name")
            or specs_dict.get("role_name")
            or specs_dict.get("group_name")
            or specs_dict.get("name")
            or specs_dict.get("id")
        )

        if not candidate:
            arn_part = spec.arn.split(":")[-1]
            if "/" in arn_part:
                candidate = arn_part.split("/")[-1]
            else:
                candidate = arn_part

        if not candidate:
            candidate = "res"

        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", str(candidate)).strip("_")
        return clean_name or "resource"

    def _import_id(self, spec: ResourceSpec) -> str:
        """Extract the identifier used by 'terraform import'."""
        specs_dict = spec.specifications or {}
        candidate = (
            specs_dict.get("bucket")
            or specs_dict.get("bucket_name")
            or specs_dict.get("instance_id")
            or specs_dict.get("function_name")
            or specs_dict.get("table_name")
            or specs_dict.get("role_name")
            or specs_dict.get("group_id")
            or specs_dict.get("id")
        )
        if candidate:
            return str(candidate)

        arn_part = spec.arn.split(":")[-1]
        if "/" in arn_part:
            return arn_part.split("/")[-1]
        return arn_part or spec.arn

    def _format_hcl_value(self, val: Any, indent_level: int = 1) -> str:
        """Format Python values into valid HCL value representations."""
        indent = "  " * indent_level

        if isinstance(val, bool):
            return "true" if val else "false"
        elif isinstance(val, (int, float)):
            return str(val)
        elif isinstance(val, str):
            clean_str = val.replace('"', '\\"')
            return f'"{clean_str}"'
        elif isinstance(val, list):
            if not val:
                return "[]"
            items_str = ", ".join(self._format_hcl_value(item, indent_level) for item in val)
            return f"[{items_str}]"
        elif isinstance(val, dict):
            if not val:
                return "{}"
            lines = ["{"]
            for k, v in sorted(val.items()):
                clean_k = re.sub(r"[^a-zA-Z0-9_]", "_", str(k))
                lines.append(f"{indent}  {clean_k} = {self._format_hcl_value(v, indent_level + 1)}")
            lines.append(f"{indent}}}")
            return "\n".join(lines)
        elif val is None:
            return "null"
        else:
            return f'"{str(val)}"'

    # ========================================================================
    # Resource Block Generation (Requirements 7.3, 7.7)
    # ========================================================================

    def generate_resource_block(self, spec: ResourceSpec) -> str:
        """
        Generate a single Terraform resource block from a ResourceSpec.

        Requirements:
        - 7.3: Generate corresponding Terraform resource blocks with all collected specifications
        - 7.7: Include traceability comments linking back to original specification files
        """
        tf_type = self._tf_resource_type(spec.resource_type)
        res_name = self._resource_name(spec)
        region = spec.region if spec.region else "global"

        spec_file = f"{self.spec_base_path}/{spec.resource_type}/{region}/{res_name}.json"

        lines: list[str] = [
            f"# Resource: {tf_type}.{res_name}",
            f"# Source specification: {spec_file}",
            f"# ARN: {spec.arn}",
            f"# Region: {region}",
            "# Traceability: Requirement 7.7",
            f'resource "{tf_type}" "{res_name}" {{',
        ]

        specs_dict = spec.specifications or {}
        for key, val in sorted(specs_dict.items()):
            hcl_val = self._format_hcl_value(val, indent_level=1)
            lines.append(f"  {key} = {hcl_val}")

        lines.append("}\n")
        return "\n".join(lines)

    # ========================================================================
    # Full Terraform Generation (Requirements 7.1, 7.2)
    # ========================================================================

    def generate_terraform(
        self,
        specs: list[ResourceSpec],
        target_dir: str | Path | None = None,
    ) -> dict[str, str]:
        """
        Generate Terraform .tf files organized by resource type and region.

        Requirements:
        - 7.1: Provide option to generate Terraform IaC code
        - 7.2: Create .tf files organized by resource type and region

        Returns:
            Dictionary mapping relative file paths to their generated Terraform content.
        """
        dest_dir = Path(target_dir).resolve() if target_dir else (self.output_dir or Path.cwd())
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Group specs by (region, resource_type)
        groups: dict[tuple[str, str], list[ResourceSpec]] = {}
        for spec in specs:
            r = spec.region if spec.region else "global"
            t = spec.resource_type if spec.resource_type else "generic"
            key = (r, t)
            groups.setdefault(key, []).append(spec)

        result: dict[str, str] = {}

        for (region, res_type), group_specs in groups.items():
            # Directory structure organized by region and resource type (Requirement 7.2)
            rel_file_path = f"{region}/{res_type}.tf"
            file_full_path = dest_dir / rel_file_path
            file_full_path.parent.mkdir(parents=True, exist_ok=True)

            blocks = [self.generate_resource_block(s) for s in group_specs]
            content = (
                f"# Generated by AWS Resource Inventory\n# Region: {region} | Type: {res_type}\n\n"
                + "\n".join(blocks)
            )

            file_full_path.write_text(content, encoding="utf-8")
            result[rel_file_path] = content

        # Generate root main.tf / providers.tf for convenience
        regions_used = sorted({s.region for s in specs if s.region})
        primary_region = regions_used[0] if regions_used else "us-east-1"
        provider_content = f"""terraform {{
  required_version = ">= 1.0.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{primary_region}"
}}
"""
        provider_path = dest_dir / "providers.tf"
        provider_path.write_text(provider_content, encoding="utf-8")
        result["providers.tf"] = provider_content

        # Generate import and verification scripts
        import_script = self.generate_import_script(specs)
        (dest_dir / "import.sh").write_text(import_script, encoding="utf-8")

        verify_script = self.generate_verification_script(specs)
        (dest_dir / "verify_state.sh").write_text(verify_script, encoding="utf-8")

        return result

    # ========================================================================
    # Import Script Generation (Requirement 7.4)
    # ========================================================================

    def generate_import_script(self, specs: list[ResourceSpec]) -> str:
        """
        Generate terraform import commands for all existing resources.

        Requirement 7.4: Generate terraform import commands for all existing resources
        """
        lines: list[str] = [
            "#!/usr/bin/env bash",
            "# Terraform import commands for discovered AWS resources",
            "# Generated by AWS Resource Inventory (Requirement 7.4)",
            "set -euo pipefail",
            "",
            "echo 'Starting Terraform resource import...'",
            "",
        ]

        for spec in specs:
            tf_type = self._tf_resource_type(spec.resource_type)
            res_name = self._resource_name(spec)
            import_id = self._import_id(spec)

            lines.append(f"echo 'Importing {tf_type}.{res_name} ({import_id})...'")
            lines.append(f"terraform import {tf_type}.{res_name} {import_id} || true")
            lines.append("")

        lines.append("echo 'Terraform import script completed.'")
        return "\n".join(lines) + "\n"

    # ========================================================================
    # Verification Script & Plan Validation (Requirements 7.5, 7.6)
    # ========================================================================

    def generate_verification_script(self, specs: list[ResourceSpec]) -> str:
        """
        Generate verification script that compares generated Terraform state with actual AWS resources.

        Requirement 7.6: Include verification script comparing Terraform state with actual AWS
        """
        script = """#!/usr/bin/env bash
# Verification script: compare generated Terraform state with actual AWS resources
# Requirement 7.6 & 7.5
set -euo pipefail

echo "=================================================="
echo "Verifying Terraform configuration vs AWS resources"
echo "=================================================="

# Ensure terraform is initialized
if [ ! -d ".terraform" ]; then
    echo "Initializing Terraform..."
    terraform init -input=false
fi

# Run terraform plan with -detailed-exitcode:
# 0 = Succeeded, diff is empty (no changes)
# 1 = Error
# 2 = Succeeded, there is a diff (changes detected)
set +e
terraform plan -detailed-exitcode -no-color > plan_output.txt 2>&1
PLAN_EXIT=$?
set -e

if [ $PLAN_EXIT -eq 0 ]; then
    echo "SUCCESS: Zero changes detected. Terraform configuration matches actual AWS resources exactly!"
    cat plan_output.txt
    exit 0
elif [ $PLAN_EXIT -eq 2 ]; then
    echo "FAILED: Changes detected between generated Terraform and actual AWS infrastructure."
    cat plan_output.txt
    exit 2
else
    echo "ERROR: Terraform plan failed to execute."
    cat plan_output.txt
    exit 1
fi
"""
        return script

    def verify_terraform_plan(self, tf_dir: str | Path) -> tuple[bool, str]:
        """
        Validate that running terraform plan shows zero changes.

        Requirement 7.5: Validate that running terraform plan shows zero changes
        """
        directory = Path(tf_dir)

        try:
            result = subprocess.run(
                ["terraform", "plan", "-detailed-exitcode", "-no-color"],
                cwd=directory,
                capture_output=True,
                text=True,
                check=False,
            )

            stdout = result.stdout or ""
            stderr = result.stderr or ""
            output = f"{stdout}\n{stderr}".strip()

            if (
                result.returncode == 0
                or "no changes" in stdout.lower()
                or "zero changes" in stdout.lower()
            ):
                return True, "Zero changes: Terraform state matches actual AWS resources."
            elif (
                result.returncode == 2
                or "to add" in stdout
                or "to change" in stdout
                or "to destroy" in stdout
            ):
                return False, f"Changes detected in terraform plan:\n{stdout}"
            else:
                return (
                    False,
                    f"Terraform plan failed with returncode {result.returncode}:\n{output}",
                )

        except Exception as ex:
            return False, f"Execution failed: {ex}"
