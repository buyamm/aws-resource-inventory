"""
The benchmark script (scripts/benchmark.py) at a small scale.

Validates: Requirements 1.5, 10.1, 10.2
"""

from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path

import pytest

from src import cli as cli_module

pytestmark = [pytest.mark.e2e, pytest.mark.slow]

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset_cli_logging():
    yield
    root = logging.getLogger()
    for handler in list(root.handlers):
        if isinstance(handler, cli_module.CliLogHandler):
            root.removeHandler(handler)
    root.setLevel(logging.WARNING)


@pytest.fixture
def benchmark():
    spec = importlib.util.spec_from_file_location("benchmark", ROOT / "scripts" / "benchmark.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_benchmark_collects_requested_resource_count_req_1_5(benchmark, tmp_path):
    result_file = tmp_path / "result.json"
    code = benchmark.main(
        [
            "--resources",
            "40",
            "--regions",
            "2",
            "--latency-ms",
            "5",
            "--output-dir",
            str(tmp_path / "out"),
            "--json",
            str(result_file),
        ]
    )
    assert code == 0
    result = json.loads(result_file.read_text(encoding="utf-8"))
    assert result["resources_discovered"] == 40
    assert result["specs_collected"] == 40
    assert result["specs_failed"] == 0
    assert len(result["regions"]) == 2
    assert {"discovery", "collection", "output"} <= set(result["phases"])
    # Every AWS call made by collect (discovery and collection) got the simulated latency.
    assert result["delayed_calls"] >= result["api_calls"] > 40
    assert result["targets_met"] is True


def test_benchmark_rejects_too_few_resources(benchmark, tmp_path, capsys):
    code = benchmark.main(["--resources", "3", "--regions", "2", "--output-dir", str(tmp_path)])
    assert code == 2
    assert "at least" in capsys.readouterr().err
