"""
Integrity Module

Checksums, sealing (sanitize + checksum), citation property paths and the
verification of a complete Output_Dir.

Requirements Coverage:
- Requirement 3.5: Spec_Checksum in metadata.checksum; checksums.sha256 verification
- Requirement 3.6: Raw responses sanitized with the same rules
- Requirement 8.2: Citations carry the Spec_Checksum of the cited file
- Requirement 8.3: verify recomputes file hashes and checks every citation
- Requirement 8.4: Discrepancies reported with file path and 1-based line number
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections.abc import Iterator
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from src.parser import ResourceSpec
from src.sanitizer import DataSanitizer

CHECKSUM_FILE = "checksums.sha256"
ANALYSIS_FILE = "analysis/analysis.json"


# ============================================================================
# Canonical JSON and checksums
# ============================================================================


def canonical_json(value: Any) -> str:
    """Canonical JSON: sorted keys, no whitespace, UTF-8 characters kept."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def spec_checksum(specifications: Any) -> str:
    """Spec_Checksum: SHA-256 of the canonical JSON of the Specifications."""
    return hashlib.sha256(canonical_json(specifications).encode("utf-8")).hexdigest()


def pretty_json(value: Any) -> str:
    """The on-disk JSON format of spec files (indent 2, sorted keys)."""
    return "\n".join(line for _path, line in _pretty_lines(value, "", 0, ""))


def seal_specs(specs: list[ResourceSpec], sanitizer: DataSanitizer) -> list[ResourceSpec]:
    """
    Return new specs whose Specifications and raw responses are sanitized and
    whose ``metadata.checksum`` is the Spec_Checksum. Inputs are not modified.
    """
    sealed: list[ResourceSpec] = []
    for spec in specs:
        specifications = sanitizer.sanitize(copy.deepcopy(spec.specifications or {}))
        raw = spec.raw_response
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                pass
        raw = sanitizer.sanitize(copy.deepcopy(raw)) if raw is not None else None
        metadata = replace(spec.metadata, checksum=spec_checksum(specifications))
        sealed.append(
            replace(spec, specifications=specifications, metadata=metadata, raw_response=raw)
        )
    return sealed


# ============================================================================
# Property paths
# ============================================================================

_SEGMENT = re.compile(r"^([^.\[\]]+)((?:\[\d+\])*)$")


def _parse_path(path: str) -> list[str | int]:
    if not path:
        raise KeyError("empty property path")
    steps: list[str | int] = []
    for segment in path.split("."):
        match = _SEGMENT.match(segment)
        if not match:
            raise KeyError(f"invalid property path segment '{segment}'")
        steps.append(match.group(1))
        steps.extend(int(i) for i in re.findall(r"\[(\d+)\]", match.group(2)))
    return steps


def resolve_property_path(document: Any, path: str) -> Any:
    """Value at ``path`` (``a.b[0].c``) inside ``document``; KeyError if absent."""
    current = document
    for step in _parse_path(path):
        if isinstance(step, int):
            if not isinstance(current, list) or step >= len(current):
                raise KeyError(f"index [{step}] not found in '{path}'")
        elif not isinstance(current, dict) or step not in current:
            raise KeyError(f"key '{step}' not found in '{path}'")
        current = current[step]
    return current


_PATTERN_SEGMENT = re.compile(r"^([^\[\]]+)((?:\[\])*)$")


def _walk(value: Any, segments: list[str], path: str) -> Iterator[tuple[str, Any]]:
    if not segments:
        yield path, value
        return
    match = _PATTERN_SEGMENT.match(segments[0])
    if match is None or not isinstance(value, dict) or match.group(1) not in value:
        return
    key, lists = match.group(1), match.group(2).count("[]")
    items: list[tuple[str, Any]] = [(f"{path}.{key}", value[key])]
    for _ in range(lists):
        items = [
            (f"{p}[{i}]", element)
            for p, v in items
            if isinstance(v, list)
            for i, element in enumerate(v)
        ]
    for item_path, item in items:
        yield from _walk(item, segments[1:], item_path)


def iter_property_paths(specifications: Any, pattern: str) -> Iterator[tuple[str, Any]]:
    """``(property path, value)`` for every match of ``pattern`` in ``specifications``.

    ``pattern`` is a dotted key path where ``key[]`` walks every element of a list,
    e.g. ``Routes[].GatewayId``; yielded paths are concrete citation paths such as
    ``specifications.Routes[1].GatewayId``. Missing keys yield nothing.
    """
    yield from _walk(specifications or {}, pattern.split("."), "specifications")


def _child_path(parent: str, key: str | int) -> str:
    if isinstance(key, int):
        return f"{parent}[{key}]"
    return f"{parent}.{key}" if parent else key


def _pretty_lines(value: Any, path: str, indent: int, prefix: str) -> Iterator[tuple[str, str]]:
    """Yield (path, line) pairs reproducing ``json.dumps(value, indent=2, sort_keys=True)``."""
    pad = "  " * indent
    if isinstance(value, dict) and value:
        yield path, f"{pad}{prefix}{{"
        items = sorted(value.items())
        for index, (key, child) in enumerate(items):
            comma = "," if index < len(items) - 1 else ""
            child_lines = list(
                _pretty_lines(child, _child_path(path, key), indent + 1, f"{json.dumps(key)}: ")
            )
            child_lines[-1] = (child_lines[-1][0], child_lines[-1][1] + comma)
            yield from child_lines
        yield path, f"{pad}}}"
    elif isinstance(value, list) and value:
        yield path, f"{pad}{prefix}["
        for index, child in enumerate(value):
            comma = "," if index < len(value) - 1 else ""
            child_lines = list(_pretty_lines(child, _child_path(path, index), indent + 1, ""))
            child_lines[-1] = (child_lines[-1][0], child_lines[-1][1] + comma)
            yield from child_lines
        yield path, f"{pad}]"
    else:
        yield path, f"{pad}{prefix}{json.dumps(value, sort_keys=True)}"


def find_property_line(json_text: str, path: str) -> int:
    """1-based line where ``path`` starts in the pretty JSON of ``json_text``; 0 if absent."""
    try:
        document = json.loads(json_text)
    except json.JSONDecodeError:
        return 0
    for number, (line_path, _line) in enumerate(_pretty_lines(document, "", 0, ""), start=1):
        if line_path == path:
            return number
    return 0


# ============================================================================
# Output_Dir verification
# ============================================================================


@dataclass
class Discrepancy:
    path: str
    line: int
    reason: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.reason}"


@dataclass
class VerificationReport:
    files_checked: int = 0
    citations_checked: int = 0
    discrepancies: list[Discrepancy] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.discrepancies

    def summary(self) -> str:
        if self.ok:
            return f"OK: {self.files_checked} files, {self.citations_checked} citations verified"
        return f"FAILED: {len(self.discrepancies)} discrepancies"


def iter_citations(value: Any) -> Iterator[dict[str, Any]]:
    """Every citation dict found under ``citation`` / ``citations`` keys."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "citation" and isinstance(child, dict):
                yield child
            elif key == "citations" and isinstance(child, list):
                yield from (c for c in child if isinstance(c, dict))
            else:
                yield from iter_citations(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_citations(child)


def _verify_checksums(root: Path, report: VerificationReport) -> None:
    checksum_path = root / CHECKSUM_FILE
    if not checksum_path.is_file():
        report.discrepancies.append(Discrepancy(CHECKSUM_FILE, 0, "missing checksum file"))
        return
    for raw_line in checksum_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        expected, _, rel_path = raw_line.partition("  ")
        target = root / rel_path
        report.files_checked += 1
        if not target.is_file():
            report.discrepancies.append(Discrepancy(rel_path, 0, "missing file"))
        elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            report.discrepancies.append(Discrepancy(rel_path, 0, "checksum mismatch"))


def _verify_citation(root: Path, citation: dict[str, Any], report: VerificationReport) -> None:
    spec_file = str(citation.get("spec_file", ""))
    property_path = str(citation.get("property_path", ""))
    target = root / spec_file
    if not spec_file or not target.is_file():
        report.discrepancies.append(Discrepancy(spec_file, 0, "spec file not found"))
        return
    text = target.read_text(encoding="utf-8")
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        report.discrepancies.append(Discrepancy(spec_file, exc.lineno, "invalid JSON"))
        return
    actual_checksum = spec_checksum(document.get("specifications", {}))
    if actual_checksum != citation.get("source_checksum"):
        report.discrepancies.append(
            Discrepancy(
                spec_file,
                find_property_line(text, "specifications"),
                f"source_checksum mismatch (expected {citation.get('source_checksum')}, "
                f"file has {actual_checksum})",
            )
        )
    try:
        value = resolve_property_path(document, property_path)
    except KeyError:
        report.discrepancies.append(
            Discrepancy(spec_file, 0, f"property_path not found: {property_path}")
        )
        return
    if value != citation.get("evidence_value"):
        report.discrepancies.append(
            Discrepancy(
                spec_file,
                find_property_line(text, property_path),
                f"evidence_value differs at {property_path}",
            )
        )


def verify_output_dir(output_dir: str | Path) -> VerificationReport:
    """Verify file checksums and every citation in analysis/analysis.json (Req 8.3, 8.4)."""
    root = Path(output_dir)
    report = VerificationReport()
    _verify_checksums(root, report)
    analysis_path = root / ANALYSIS_FILE
    if analysis_path.is_file():
        try:
            analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.discrepancies.append(Discrepancy(ANALYSIS_FILE, exc.lineno, "invalid JSON"))
            return report
        for citation in iter_citations(analysis):
            report.citations_checked += 1
            _verify_citation(root, citation, report)
    return report
