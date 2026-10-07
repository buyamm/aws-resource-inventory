"""
Output Generator Module

This module provides the OutputGenerator class for persisting AWS resource
specifications into structured JSON, human-readable Markdown, checksums,
sanitized data, and raw API responses.

Requirements Coverage:
- Requirement 3.1: Save data in both JSON and Markdown formats
- Requirement 3.2: Organize output files by resource type and region in directory structure
- Requirement 3.3: Include timestamps, AWS account ID, region, and metadata in JSON output
- Requirement 3.4: Format specifications in human-readable tables and sections in Markdown
- Requirement 3.5: Include checksums for data integrity verification
- Requirement 3.6: Store raw API responses in separate directory for audit
- Requirement 9.5: Sanitize sensitive data before writing
- Requirement 9.6: Replace detected sensitive values with placeholder text
- Requirement 10.3: Include summary report comparing manual effort vs automated time
- Requirement 10.4: Calculate time savings using baseline: 5 minutes per resource
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.parser import ResourceSpec
from src.sanitizer import DataSanitizer


class OutputGenerator:
    """
    Generator for persistence, formatting, sanitization, and verification
    of collected AWS resource specifications.
    """

    def __init__(
        self,
        output_dir: str | Path,
        sanitizer: DataSanitizer | None = None,
    ) -> None:
        """
        Initialize the OutputGenerator.

        Args:
            output_dir: Directory where outputs will be stored.
            sanitizer: Optional custom DataSanitizer instance.
        """
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sanitizer = sanitizer or DataSanitizer()
        self._written_files: list[Path] = []

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _safe_filename(self, spec: ResourceSpec) -> str:
        """
        Derive a safe filesystem-friendly base filename from a ResourceSpec.

        Args:
            spec: The ResourceSpec to extract filename from.

        Returns:
            A sanitized string safe for file names.
        """
        # Attempt to use resource-specific ID/Name from specifications
        specs_dict = spec.specifications or {}
        candidate = (
            specs_dict.get("instance_id")
            or specs_dict.get("bucket_name")
            or specs_dict.get("function_name")
            or specs_dict.get("name")
            or specs_dict.get("id")
        )

        if not candidate:
            # Fall back to ARN fragment
            arn_part = spec.arn.split(":")[-1]
            if "/" in arn_part:
                candidate = arn_part.split("/")[-1]
            else:
                candidate = arn_part

        if not candidate:
            candidate = spec.arn

        # Sanitize for filesystem safety
        safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", str(candidate))
        return safe_name.strip("_") or "resource"

    def _resource_dir(self, spec: ResourceSpec) -> Path:
        """
        Get and create the destination directory organized by resource_type and region.

        (Requirement 3.2: organize output files by resource type and region)
        """
        region = spec.region if spec.region else "global"
        res_type = spec.resource_type if spec.resource_type else "unknown"
        target_dir = self.output_dir / res_type / region
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    def _register_written_file(self, file_path: Path) -> None:
        """Keep track of files written in the current generator instance."""
        if file_path not in self._written_files:
            self._written_files.append(file_path)

    # ========================================================================
    # JSON Generation (Requirements 3.1, 3.2, 3.3, 9.5)
    # ========================================================================

    def generate_json(self, specs: list[ResourceSpec]) -> list[Path]:
        """
        Save specifications in JSON format organized by type and region.
        Also creates aggregate resources.json in root output directory.

        Requirements:
        - 3.1: Save in JSON format
        - 3.2: Organize by resource type and region
        - 3.3: Include timestamps, account ID, region, and metadata
        - 9.5: Sanitize sensitive data before saving
        """
        generated_paths: list[Path] = []
        now_iso = datetime.utcnow().isoformat() + "Z"
        sanitized_specs_list: list[dict[str, Any]] = []

        for spec in specs:
            res_dir = self._resource_dir(spec)
            filename = f"{self._safe_filename(spec)}.json"
            target_path = res_dir / filename

            spec_dict = spec.to_dict()
            # Ensure timestamp field is present in addition to metadata
            spec_dict["generated_at"] = now_iso

            # Sanitize sensitive data (Requirement 9.5)
            sanitized_dict = self.sanitizer.sanitize(spec_dict)
            sanitized_specs_list.append(sanitized_dict)

            json_content = json.dumps(sanitized_dict, indent=2, sort_keys=True)
            target_path.write_text(json_content, encoding="utf-8")

            self._register_written_file(target_path)
            generated_paths.append(target_path)

        # Aggregate resources.json (Requirement 3.1)
        aggregate_path = self.output_dir / "resources.json"
        aggregate_data = {
            "total_resources": len(specs),
            "generated_at": now_iso,
            "resources": sanitized_specs_list,
        }
        aggregate_content = json.dumps(aggregate_data, indent=2, sort_keys=True)
        aggregate_path.write_text(aggregate_content, encoding="utf-8")

        self._register_written_file(aggregate_path)
        generated_paths.append(aggregate_path)

        return generated_paths

    # ========================================================================
    # Markdown Generation (Requirements 3.1, 3.2, 3.4, 9.5)
    # ========================================================================

    def _format_markdown_table(self, headers: list[str], rows: list[list[str]]) -> str:
        """Format rows and headers into a GitHub-flavored Markdown table."""
        if not headers or not rows:
            return ""

        col_widths = [len(h) for h in headers]
        for row in rows:
            for idx, cell in enumerate(row):
                if idx < len(col_widths):
                    col_widths[idx] = max(col_widths[idx], len(str(cell)))

        header_line = (
            "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
        )
        sep_line = (
            "| " + " | ".join("-" * max(3, col_widths[i]) for i in range(len(headers))) + " |"
        )
        row_lines = [
            "| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
            for row in rows
        ]

        return "\n".join([header_line, sep_line] + row_lines)

    def _render_spec_markdown(self, spec: ResourceSpec, sanitized_dict: dict[str, Any]) -> str:
        """Render a single ResourceSpec into human-readable Markdown with tables and sections."""
        lines: list[str] = []
        name = self._safe_filename(spec)

        lines.append(f"# AWS Resource: `{spec.resource_type}` - `{name}`\n")

        # Section: Overview
        lines.append("## Overview\n")
        overview_rows = [
            ["Resource Type", str(spec.resource_type)],
            ["ARN", str(spec.arn)],
            ["Region", str(spec.region)],
            ["Account ID", str(spec.account_id)],
            ["Collected At", str(spec.metadata.collected_at)],
            ["Collector Version", str(spec.metadata.collector_version)],
        ]
        lines.append(self._format_markdown_table(["Property", "Value"], overview_rows))
        lines.append("\n")

        # Section: Specifications
        specs_data = sanitized_dict.get("specifications", {})
        lines.append("## Configuration Specifications\n")

        scalar_specs: list[list[str]] = []
        complex_specs: dict[str, Any] = {}

        for k, v in sorted(specs_data.items()):
            if isinstance(v, (str, int, float, bool)) or v is None:
                scalar_specs.append([str(k), str(v)])
            else:
                complex_specs[k] = v

        if scalar_specs:
            lines.append(self._format_markdown_table(["Configuration Key", "Value"], scalar_specs))
            lines.append("\n")

        # Tags table if available
        tags = specs_data.get("tags")
        if isinstance(tags, dict) and tags:
            lines.append("## Resource Tags\n")
            tag_rows = [[str(k), str(v)] for k, v in sorted(tags.items())]
            lines.append(self._format_markdown_table(["Tag Key", "Tag Value"], tag_rows))
            lines.append("\n")

        # Additional complex configurations
        for complex_key, complex_val in complex_specs.items():
            if complex_key == "tags":
                continue
            lines.append(f"### {complex_key.replace('_', ' ').title()}\n")
            if (
                isinstance(complex_val, list)
                and complex_val
                and all(isinstance(i, dict) for i in complex_val)
            ):
                # Try table format if list of dicts
                keys = list({k for item in complex_val for k in item.keys()})
                keys.sort()
                table_rows = [[str(item.get(k, "")) for k in keys] for item in complex_val]
                lines.append(self._format_markdown_table(keys, table_rows))
            else:
                lines.append("```json")
                lines.append(json.dumps(complex_val, indent=2, sort_keys=True))
                lines.append("```")
            lines.append("\n")

        return "\n".join(lines)

    def generate_markdown(
        self, specs: list[ResourceSpec], duration_seconds: float | None = None
    ) -> list[Path]:
        """
        Save specifications in Markdown format organized by type and region.
        Also creates aggregate resources.md in root output directory.

        Requirements:
        - 3.1: Save in Markdown format
        - 3.2: Organize by resource type and region
        - 3.4: Format specifications in human-readable tables and sections
        - 9.5: Sanitize sensitive data before saving
        """
        generated_paths: list[Path] = []
        sanitized_specs: list[tuple[ResourceSpec, dict[str, Any]]] = []

        for spec in specs:
            res_dir = self._resource_dir(spec)
            filename = f"{self._safe_filename(spec)}.md"
            target_path = res_dir / filename

            spec_dict = spec.to_dict()
            sanitized_dict = self.sanitizer.sanitize(spec_dict)
            sanitized_specs.append((spec, sanitized_dict))

            md_content = self._render_spec_markdown(spec, sanitized_dict)
            target_path.write_text(md_content, encoding="utf-8")

            self._register_written_file(target_path)
            generated_paths.append(target_path)

        # Aggregate resources.md
        aggregate_path = self.output_dir / "resources.md"
        agg_lines: list[str] = [
            "# AWS Infrastructure Resource Inventory\n",
            f"**Generated:** {datetime.utcnow().isoformat()}Z  ",
            f"**Total Resources Discovered:** {len(specs)}\n",
            "## Summary by Resource Type\n",
        ]

        # Count by resource type
        type_counts: dict[str, int] = {}
        region_counts: dict[str, int] = {}
        for spec in specs:
            type_counts[spec.resource_type] = type_counts.get(spec.resource_type, 0) + 1
            r = spec.region or "global"
            region_counts[r] = region_counts.get(r, 0) + 1

        summary_rows = [[res_type, str(count)] for res_type, count in sorted(type_counts.items())]
        agg_lines.append(self._format_markdown_table(["Resource Type", "Count"], summary_rows))
        agg_lines.append("\n")

        # Regional Breakdown
        agg_lines.append("## Regional Distribution\n")
        region_rows = [[region, str(count)] for region, count in sorted(region_counts.items())]
        agg_lines.append(self._format_markdown_table(["Region", "Resource Count"], region_rows))
        agg_lines.append("\n")

        # Resource Inventory Table
        agg_lines.append("## Discovered Resources List\n")
        res_rows: list[list[str]] = []
        for spec, _ in sanitized_specs:
            name = self._safe_filename(spec)
            res_rows.append(
                [
                    spec.resource_type,
                    name,
                    spec.region or "global",
                    spec.arn,
                ]
            )
        agg_lines.append(
            self._format_markdown_table(["Resource Type", "Identifier", "Region", "ARN"], res_rows)
        )
        agg_lines.append("\n")

        # Detailed Resource Specifications
        agg_lines.append("## Detailed Resource Specifications\n")
        for spec, s_dict in sanitized_specs:
            agg_lines.append(self._render_spec_markdown(spec, s_dict))
            agg_lines.append("\n---\n")

        # If collection duration provided, append performance report
        if duration_seconds is not None:
            agg_lines.append(self.generate_summary_report(specs, duration_seconds))

        aggregate_path.write_text("\n".join(agg_lines), encoding="utf-8")
        self._register_written_file(aggregate_path)
        generated_paths.append(aggregate_path)

        return generated_paths

    # ========================================================================
    # Raw API Responses (Requirement 3.6)
    # ========================================================================

    def store_raw_responses(self, specs: list[ResourceSpec]) -> list[Path]:
        """
        Store all raw API responses in a separate raw_responses directory for audit purposes.

        Requirement 3.6: Store raw API responses in separate directory
        """
        raw_dir = self.output_dir / "raw_responses"
        raw_dir.mkdir(parents=True, exist_ok=True)
        stored_paths: list[Path] = []

        for spec in specs:
            if spec.raw_response is None:
                continue

            region = spec.region if spec.region else "global"
            res_type = spec.resource_type if spec.resource_type else "unknown"
            dest_dir = raw_dir / res_type / region
            dest_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{self._safe_filename(spec)}_raw.json"
            target_path = dest_dir / filename

            # Write raw response as preserved string
            target_path.write_text(spec.raw_response, encoding="utf-8")
            self._register_written_file(target_path)
            stored_paths.append(target_path)

        return stored_paths

    # ========================================================================
    # Checksums (Requirement 3.5)
    # ========================================================================

    def generate_checksums(self) -> Path:
        """
        Calculate SHA-256 checksums for all written output files and store
        in checksums.sha256 and checksums.json for data integrity verification.

        Requirement 3.5: Include checksums for data integrity verification
        """
        checksums: dict[str, str] = {}
        sha256_lines: list[str] = []

        # Scan all non-checksum files in output_dir
        for file_path in sorted(self.output_dir.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("checksums."):
                rel_path = file_path.relative_to(self.output_dir).as_posix()
                content = file_path.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()
                checksums[rel_path] = file_hash
                sha256_lines.append(f"{file_hash}  {rel_path}")

        # Write checksums.sha256 (standard format)
        sha256_path = self.output_dir / "checksums.sha256"
        sha256_path.write_text("\n".join(sha256_lines) + "\n", encoding="utf-8")

        # Also write checksums.json for programmatic access
        json_path = self.output_dir / "checksums.json"
        json_path.write_text(json.dumps(checksums, indent=2, sort_keys=True), encoding="utf-8")

        return sha256_path

    # ========================================================================
    # Performance & Summary Report (Requirements 10.3, 10.4, 10.5)
    # ========================================================================

    def generate_summary_report(self, specs: list[ResourceSpec], duration_seconds: float) -> str:
        """
        Generate summary report comparing estimated manual effort versus automated time.

        Baseline: 5 minutes per resource for manual documentation (Requirement 10.4).
        """
        total_resources = len(specs)
        manual_minutes = total_resources * 5
        manual_hours = manual_minutes / 60.0
        automated_hours = duration_seconds / 3600.0
        hours_saved = max(0.0, manual_hours - automated_hours)
        percent_saved = (hours_saved / manual_hours * 100.0) if manual_hours > 0 else 0.0

        headers = ["Metric", "Manual Effort (Baseline)", "Automated Collection", "Savings"]
        rows = [
            ["Baseline Rate", "5 minutes / resource", "N/A", "-"],
            ["Total Resources", str(total_resources), str(total_resources), "-"],
            [
                "Total Duration",
                f"{manual_hours:.2f} hours ({manual_minutes} min)",
                f"{duration_seconds:.2f} seconds ({automated_hours:.4f} hrs)",
                f"{hours_saved:.2f} hours saved",
            ],
            [
                "Efficiency Gain",
                "Baseline (100%)",
                f"+{percent_saved:.1f}% faster",
                f"{percent_saved:.1f}% time saved",
            ],
        ]

        table_md = self._format_markdown_table(headers, rows)

        report = f"""## Performance & Time Savings Summary Report

> [!NOTE]
> Based on industry baseline calculation of 5 minutes per resource for manual documentation.

{table_md}
"""
        return report

    def format_terminal_summary(
        self, specs: list[ResourceSpec], duration_seconds: float
    ) -> str:
        """
        Format a colorful summary report suitable for display in terminal CLI.

        Uses ANSI color codes for terminal highlighting (Task 9.4).
        """
        green = "\033[92m"
        cyan = "\033[96m"
        yellow = "\033[93m"
        bold = "\033[1m"
        reset = "\033[0m"

        total_resources = len(specs)
        manual_minutes = total_resources * 5
        manual_hours = manual_minutes / 60.0
        hours_saved = max(0.0, manual_hours - (duration_seconds / 3600.0))
        percent_saved = (hours_saved / manual_hours * 100.0) if manual_hours > 0 else 0.0

        lines = [
            f"{bold}{cyan}=== AWS Resource Inventory Summary ==={reset}",
            f"Total Resources: {bold}{green}{total_resources}{reset}",
            f"Automated Time:  {yellow}{duration_seconds:.2f}s{reset}",
            f"Manual Baseline: {manual_hours:.2f}h ({manual_minutes} min)",
            f"Time Saved:      {bold}{green}{hours_saved:.2f} hours ({percent_saved:.1f}%){reset}",
        ]
        return "\n".join(lines)

    # ========================================================================
    # Full Generation Workflow (Requirement 3.1-3.6)
    # ========================================================================

    def generate_all(
        self, specs: list[ResourceSpec], duration_seconds: float | None = None
    ) -> dict[str, Any]:
        """
        Execute full output generation workflow:
        1. JSON specs (organized & sanitized)
        2. Markdown reports (tables, sections & sanitized)
        3. Raw API response persistence
        4. Summary & performance report
        5. SHA-256 integrity checksums
        """
        duration = duration_seconds if duration_seconds is not None else 0.0
        json_files = self.generate_json(specs)
        md_files = self.generate_markdown(specs, duration_seconds=duration)
        raw_files = self.store_raw_responses(specs)
        summary_report = self.generate_summary_report(specs, duration_seconds=duration)
        checksum_file = self.generate_checksums()

        return {
            "json_files": json_files,
            "markdown_files": md_files,
            "raw_files": raw_files,
            "checksum_file": checksum_file,
            "summary_report": summary_report,
        }
