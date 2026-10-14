"""
The CI workflow runs the same quality gates as CLAUDE.md, against files that exist.

Validates: Task 24.4 (quality gates of Requirements 9.4 and 11.1)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "tdd-pipeline.yml"


@pytest.fixture(scope="module")
def workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _commands(workflow: dict, job: str) -> str:
    steps = workflow["jobs"][job]["steps"]
    return "\n".join(step.get("run", "") for step in steps)


def _all_commands(workflow: dict) -> str:
    return "\n".join(_commands(workflow, job) for job in workflow["jobs"])


def test_ci_critical_coverage_gates_point_at_module_files(workflow):
    unit = _commands(workflow, "unit-tests")
    for module in ("src/parser.py", "src/sanitizer.py"):
        assert (ROOT / module).is_file()
        assert f'coverage report --include="{module}" --fail-under=100' in unit
    assert "--fail-under=80" in unit
    # A gate that only prints a warning is not a gate.
    assert "|| echo" not in unit and "src/parser/" not in unit and "src/sanitizer/" not in unit


def test_ci_static_checks_match_project_commands(workflow):
    assert re.search(r"^\s*mypy src\s*$", _commands(workflow, "type-check"), re.M)
    lint = _commands(workflow, "lint")
    assert "ruff check src tests" in lint and "black --check src tests" in lint
    assert re.search(r"^\s*bandit -r src -ll\s*$", _commands(workflow, "security-scan"), re.M)


def test_ci_test_paths_exist(workflow):
    for path in re.findall(r"pytest (tests/[\w/]+)", _all_commands(workflow)):
        assert (ROOT / path).is_dir(), path


def test_ci_installs_package_and_gates_every_job(workflow):
    for name in workflow["jobs"]:
        if name in ("lint", "security-scan", "test-summary"):
            continue
        assert "pip install -e ." in _commands(workflow, name), name
    summary = workflow["jobs"]["test-summary"]
    assert set(summary["needs"]) == set(workflow["jobs"]) - {"test-summary"}
    gate = _commands(workflow, "test-summary")
    for needed in summary["needs"]:
        assert f"needs.{needed}.result" in gate, needed
