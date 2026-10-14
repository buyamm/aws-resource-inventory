"""
Unit tests for src/metrics.py (phase timings, run metrics, time savings).

Validates: Requirements 10.1, 10.2, 10.4
"""

from __future__ import annotations

import pytest

from src.metrics import PhaseTimer, RunMetrics, files_size, time_savings

pytestmark = pytest.mark.unit


def test_metrics_time_savings_formula_req_10_4():
    # 12 resources * 5 min = 1 h manual; 36 s = 0.01 h automated
    savings = time_savings(12, 36.0)
    assert savings.manual_hours == pytest.approx(1.0)
    assert savings.automated_hours == pytest.approx(0.01)
    assert savings.hours_saved == pytest.approx(0.99)
    assert savings.percent_saved == pytest.approx(99.0)


def test_metrics_time_savings_zero_resources_req_10_4():
    savings = time_savings(0, 120.0)
    assert savings.manual_hours == 0
    assert savings.hours_saved == 0
    assert savings.percent_saved == 0


def test_metrics_time_savings_never_negative_req_10_4():
    # 1 resource = 5 min manual, automated took 1 h
    savings = time_savings(1, 3600.0)
    assert savings.hours_saved == 0
    assert savings.percent_saved == 0
    assert set(savings.to_dict()) == {
        "manual_hours",
        "automated_hours",
        "hours_saved",
        "percent_saved",
    }


def test_metrics_phase_timings_req_10_1():
    ticks = iter([100.0, 102.5, 102.5, 110.0, 110.0, 111.0])
    timer = PhaseTimer(clock=lambda: next(ticks))
    for name in ("discovery", "collection", "output"):
        with timer.phase(name):
            pass

    phases = timer.to_list()
    assert [p["name"] for p in phases] == ["discovery", "collection", "output"]
    assert [p["duration_seconds"] for p in phases] == [2.5, 7.5, 1.0]
    for phase in phases:
        assert set(phase) == {"name", "started_at", "ended_at", "duration_seconds"}
        assert phase["started_at"].endswith("Z") and phase["ended_at"].endswith("Z")
    assert timer.total_duration_seconds == pytest.approx(11.0)


def test_metrics_phase_recorded_when_body_raises_req_10_1():
    ticks = iter([0.0, 4.0])
    timer = PhaseTimer(clock=lambda: next(ticks))
    with pytest.raises(RuntimeError), timer.phase("collection"):
        raise RuntimeError("boom")
    assert timer.to_list()[0]["duration_seconds"] == 4.0


def test_metrics_run_metrics_fields_req_10_2(tmp_path):
    (tmp_path / "a.json").write_bytes(b"x" * 10)
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.md").write_bytes(b"y" * 5)
    assert files_size([tmp_path / "a.json", tmp_path / "sub" / "b.md"]) == 15

    metrics = RunMetrics(
        resources_discovered=3, specs_collected=2, specs_failed=1, api_calls=9, data_volume_bytes=15
    )
    assert metrics.to_dict() == {
        "resources_discovered": 3,
        "specs_collected": 2,
        "specs_failed": 1,
        "api_calls": 9,
        "data_volume_bytes": 15,
    }
