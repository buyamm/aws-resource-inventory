"""
The demo script (scripts/demo.py) and the committed example Output_Dir.

Validates: Requirements 11.3, 11.5
"""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path

import pytest

from src import cli as cli_module
from src.integrity import verify_output_dir
from src.output_generator import OutputGenerator
from src.resource_types import REGISTRY

pytestmark = [pytest.mark.e2e, pytest.mark.slow]

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_FILES = (
    "manifest.json",
    "resources.json",
    "resources.md",
    "collection_report.json",
    "summary_report.md",
    "analysis/analysis.json",
    "analysis/analysis.md",
    "diagrams/architecture.drawio",
    "docs/infrastructure.md",
    "terraform/main.tf",
    "terraform/providers.tf",
    "terraform/import.sh",
    "checksums.sha256",
)


@pytest.fixture(autouse=True)
def _reset_cli_logging():
    yield
    root = logging.getLogger()
    for handler in list(root.handlers):
        if isinstance(handler, cli_module.CliLogHandler):
            root.removeHandler(handler)
    root.setLevel(logging.WARNING)


@pytest.fixture
def demo():
    spec = importlib.util.spec_from_file_location("demo", ROOT / "scripts" / "demo.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _assert_complete_output(out: Path) -> None:
    for name in EXPECTED_FILES:
        assert (out / name).is_file(), name
    types = {s.resource_type for s in OutputGenerator.load_specs(out)}
    assert types == set(REGISTRY)
    report = verify_output_dir(out)
    assert report.ok, [str(d) for d in report.discrepancies]


def test_demo_mock_run_writes_verified_output_req_11_3(demo, tmp_path, capsys):
    out = tmp_path / "demo-output"
    assert demo.main(["--output-dir", str(out)]) == 0
    _assert_complete_output(out)
    stdout = capsys.readouterr().out
    for step in ("collect", "analyze", "generate-iac", "generate-docs", "verify"):
        assert step in stdout, step


def test_demo_refuses_to_overwrite_foreign_directory_req_11_3(demo, tmp_path):
    out = tmp_path / "not-an-output-dir"
    out.mkdir()
    (out / "keep.txt").write_text("user data", encoding="utf-8")
    assert demo.main(["--output-dir", str(out)]) == 2
    assert (out / "keep.txt").read_text(encoding="utf-8") == "user data"


def test_demo_replaces_previous_demo_output_req_11_3(demo, tmp_path):
    out = tmp_path / "demo-output"
    assert demo.main(["--output-dir", str(out)]) == 0
    stale = out / "aws_instance" / "us-east-1" / "i-stale.json"
    stale.write_text("{}", encoding="utf-8")
    assert demo.main(["--output-dir", str(out)]) == 0
    assert not stale.exists()


def test_examples_output_is_complete_and_verified_req_11_5():
    _assert_complete_output(ROOT / "examples" / "output")
