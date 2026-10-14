"""
Documentation Generator Module

Renders ``docs/infrastructure.md`` from an AnalysisReport and the collected specs.
Every statement ends with ``[cite: <spec_file>#<property_path> sha256:<12>]``
markers; only headings and the inventory counts table carry no citation.

Requirements Coverage:
- Requirement 6.3: Documentation of what interacts with what
- Requirement 8.1: Every statement is backed by a citation
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from src.analysis_engine import AnalysisReport, Citation, cite
from src.parser import ResourceSpec
from src.resource_types import GLOBAL_REGION, REGISTRY, canonical_type, resource_id


def _marker(citation: Citation) -> str:
    return (
        f"[cite: {citation.spec_file}#{citation.property_path} "
        f"sha256:{citation.source_checksum[:12]}]"
    )


def _markers(citations: list[Citation]) -> str:
    return " ".join(_marker(c) for c in citations)


def _id_citation(spec: ResourceSpec) -> Citation | None:
    """Citation of the spec's id field, or None when the field is absent."""
    info = REGISTRY.get(canonical_type(spec.resource_type) or "")
    if info is None or not isinstance((spec.specifications or {}).get(info.id_field), str):
        return None
    return cite(spec, f"specifications.{info.id_field}")


def _type_name(spec: ResourceSpec) -> str:
    return canonical_type(spec.resource_type) or spec.resource_type


def _all_citations(report: AnalysisReport, specs: list[ResourceSpec]) -> list[Citation]:
    citations: list[Citation] = []
    for spec in specs:
        id_citation = _id_citation(spec)
        if id_citation is not None:
            citations.append(id_citation)
    citations += [c for p in report.patterns for c in p.citations]
    citations += [c for r in report.relationships for c in r.citations]
    citations += [f.citation for f in report.security_findings]
    return citations


def document_citations(report: AnalysisReport, specs: list[ResourceSpec]) -> list[dict[str, Any]]:
    """Distinct citations used by the document, keyed by (spec_file, property_path)."""
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for citation in _all_citations(report, specs):
        key = (citation.spec_file, citation.property_path)
        if key not in seen:
            seen.add(key)
            result.append(citation.to_dict())
    return result


def generate_infrastructure_doc(report: AnalysisReport, specs: list[ResourceSpec]) -> str:
    """Markdown content of ``docs/infrastructure.md``."""
    lines = ["# Infrastructure Documentation", "", "## Inventory", ""]
    counts = Counter((_type_name(s), s.region or GLOBAL_REGION) for s in specs)
    lines += ["| Resource Type | Region | Count |", "| :--- | :--- | ---: |"]
    lines += [f"| {kind} | {region} | {n} |" for (kind, region), n in sorted(counts.items())]
    lines.append("")

    by_type: dict[str, list[ResourceSpec]] = {}
    for spec in sorted(specs, key=lambda s: (_type_name(s), s.region, s.arn)):
        by_type.setdefault(_type_name(spec), []).append(spec)
    for kind, members in by_type.items():
        bullets = []
        for spec in members:
            citation = _id_citation(spec)
            if citation is not None:
                bullets.append(
                    f"- `{resource_id(spec)}` ({spec.region or GLOBAL_REGION}, `{spec.arn}`) "
                    f"{_marker(citation)}"
                )
        if bullets:
            lines += [f"### {kind}", "", *bullets, ""]

    lines += ["## Architecture Patterns", ""]
    for pattern in report.patterns:
        lines += [
            f"### {pattern.pattern_name}",
            "",
            f"{pattern.description} (confidence {pattern.confidence:.2f}) "
            f"{_markers(pattern.citations)}",
            "",
        ]
        for arn in pattern.participating_resources:
            supporting = [c for c in pattern.citations if c.resource_arn == arn]
            if supporting:
                lines.append(f"- Participant `{arn}` {_markers(supporting)}")
        lines.append("")

    lines += ["## Interactions", ""]
    for rel in report.relationships:
        lines.append(
            f"- `{rel.from_arn}` → `{rel.to_arn}` ({rel.relationship_type}, confidence "
            f"{rel.confidence:.2f}) {_markers(rel.citations)}"
        )
    lines.append("")

    lines += ["## Security Findings", ""]
    for finding in report.security_findings:
        lines.append(
            f"- [{finding.severity}] {finding.finding_type}: {finding.description} "
            f"{_marker(finding.citation)}"
        )
    lines.append("")
    return "\n".join(lines)
