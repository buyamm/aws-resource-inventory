"""
Tests for the repository documentation (README, docs/, instruction.md, IAM policy).

Validates: Requirements 9.4, 11.1, 11.2, 11.4
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from src.cli import cli

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
COMMANDS = sorted(cli.commands)


def _read(relpath: str) -> str:
    path = ROOT / relpath
    assert path.is_file(), f"{relpath} is missing"
    return path.read_text(encoding="utf-8")


def _headings(text: str) -> str:
    return "\n".join(line.lower() for line in text.splitlines() if line.startswith("#"))


@pytest.mark.parametrize("command", COMMANDS)
def test_docs_readme_documents_every_command_req_11_1(command):
    readme = _read("README.md")
    assert re.search(rf"aws-inventory(\s+--[\w-]+)*\s+{command}\b", readme), command


def test_docs_readme_has_required_sections_req_11_1():
    headings = _headings(_read("README.md"))
    for section in ("prerequisites", "install", "mcp", "troubleshooting", "known limitations"):
        assert section in headings, section
    assert '"mcpServers"' in _read("README.md")


def test_docs_testing_guide_exists_req_11_1():
    headings = _headings(_read("docs/TESTING.md"))
    assert "resource type" in headings
    assert "marker" in headings


def test_docs_architecture_has_mermaid_diagrams_req_11_2():
    text = _read("docs/ARCHITECTURE.md")
    assert text.count("```mermaid") >= 2
    for name in ("MCP", "AI", "Output_Dir", "collect"):
        assert name in text, name


def test_docs_accuracy_and_security_sections_req_11_4():
    headings = _headings(_read("docs/ACCURACY_AND_SECURITY.md"))
    for section in ("citation", "verif", "security", "benchmark"):
        assert section in headings, section


def test_docs_iam_policy_is_read_only_req_9_4():
    policy = json.loads(_read("docs/iam-policy.json"))
    assert policy["Version"] == "2012-10-17"
    actions = [a for s in policy["Statement"] for a in s["Action"]]
    assert actions
    for action in actions:
        service, name = action.split(":")
        assert "*" not in action, action
        assert name.startswith(("Describe", "List", "Get")) or action in (
            "sts:AssumeRole",
            "sts:GetCallerIdentity",
        ), action


@pytest.mark.parametrize("command", COMMANDS)
def test_docs_user_guide_documents_every_command(command):
    assert re.search(rf"aws-inventory(\s+--[\w-]+)*\s+{command}\b", _read("instruction.md"))


def test_docs_no_obsolete_task_notes():
    assert sorted(p.name for p in ROOT.glob("TASK_*_COMPLETED.md")) == []
