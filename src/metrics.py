"""
Run metrics for the online CLI commands.

Requirements Coverage:
- Requirement 10.1: Start/end time and duration of the discovery, collection and output phases
- Requirement 10.2: resources_discovered, specs_collected, specs_failed, api_calls, data_volume_bytes
- Requirement 10.4: Time-savings formulas (5 minutes of manual work per resource)
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MANUAL_MINUTES_PER_RESOURCE = 5


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@dataclass
class PhaseTiming:
    name: str
    started_at: str
    ended_at: str
    duration_seconds: float


class PhaseTimer:
    """Records the timing of named phases (Req 10.1)."""

    def __init__(
        self,
        clock: Callable[[], float] = time.perf_counter,
        now: Callable[[], str] = _utc_now,
    ) -> None:
        self._clock = clock
        self._now = now
        self.phases: list[PhaseTiming] = []

    @contextmanager
    def phase(self, name: str) -> Iterator[None]:
        started_at = self._now()
        start = self._clock()
        try:
            yield
        finally:
            duration = self._clock() - start
            self.phases.append(PhaseTiming(name, started_at, self._now(), round(duration, 6)))

    @property
    def total_duration_seconds(self) -> float:
        return sum(p.duration_seconds for p in self.phases)

    def to_list(self) -> list[dict[str, Any]]:
        return [asdict(p) for p in self.phases]


@dataclass
class RunMetrics:
    """Counters of one collection run (Req 10.2)."""

    resources_discovered: int = 0
    specs_collected: int = 0
    specs_failed: int = 0
    api_calls: int = 0
    data_volume_bytes: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass
class TimeSavings:
    manual_hours: float
    automated_hours: float
    hours_saved: float
    percent_saved: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def time_savings(resources: int, duration_seconds: float) -> TimeSavings:
    """Manual vs automated effort (Req 10.4)."""
    manual_hours = resources * MANUAL_MINUTES_PER_RESOURCE / 60
    automated_hours = duration_seconds / 3600
    hours_saved = max(0.0, manual_hours - automated_hours)
    percent_saved = hours_saved / manual_hours * 100 if manual_hours > 0 else 0.0
    return TimeSavings(manual_hours, automated_hours, hours_saved, percent_saved)


def files_size(paths: Iterable[Path]) -> int:
    """Total size in bytes of the given files (missing files count as 0)."""
    return sum(path.stat().st_size for path in set(paths) if path.is_file())
