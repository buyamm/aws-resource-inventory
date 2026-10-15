"""
Inventory collection: turns discovered resources into ResourceSpecs.

Requirements Coverage:
- Requirement 2.1: One Resource_Spec per discovered resource
- Requirement 3.3: region and account_id set from discovery / STS
- Requirement 10.2: api_calls across all collectors
- Requirement 12.2: Failed resources become CollectionErrors; collection continues
- Requirement 12.4: Every attempted operation is reported
- Requirement 13.3: Dependency closure: resources referenced by collected specs are
  collected too, until no new resource appears
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

from src.collector import CallStatus, OperationRecord, RetryConfig, SpecCollector
from src.discovery import DiscoveredResource
from src.parser import ResourceSpec
from src.resource_types import GLOBAL_REGION, REGISTRY
from src.scope import extract_references

GLOBAL_CLIENT_REGION = "us-east-1"


@dataclass
class CollectionError:
    """A failed or denied operation (Req 12.2)."""

    resource_arn: str
    operation: str
    error_type: str
    error_message: str
    timestamp: str
    retry_count: int


@dataclass
class CollectionResult:
    specs: list[ResourceSpec] = field(default_factory=list)
    errors: list[CollectionError] = field(default_factory=list)
    operations: list[OperationRecord] = field(default_factory=list)
    api_calls: int = 0
    # Resources added by the dependency closure, with their referenced_by (Req 13.3).
    referenced: list[DiscoveredResource] = field(default_factory=list)

    @property
    def attempted(self) -> int:
        """Resources whose collection was attempted (seeds + closure)."""
        return len({op.resource_arn for op in self.operations} | {s.arn for s in self.specs})


def _identity(resource: DiscoveredResource) -> tuple[str, str, str]:
    return resource.resource_type, resource.region, resource.resource_id


class InventoryCollector:
    """Collects specs for discovered resources, one SpecCollector per (service, region)."""

    def __init__(
        self,
        session: Any,
        account_id: str,
        retry_config: RetryConfig | None = None,
        max_workers: int = 10,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> None:
        self.session = session
        self.account_id = account_id
        self.retry_config = retry_config
        self.max_workers = max_workers
        self.progress_callback = progress_callback

    def collect_all(
        self, resources: list[DiscoveredResource], follow_references: bool = True
    ) -> CollectionResult:
        """Collect ``resources``; with ``follow_references`` also everything they reference."""
        collectors: dict[tuple[str, str], SpecCollector] = {}
        specs: list[ResourceSpec] = []
        referenced: list[DiscoveredResource] = []
        # Identity, not ARN: discovery may build EC2 ARNs without the account id.
        known = {_identity(r) for r in resources}
        wave = list(resources)
        while wave:
            collected = self._collect_wave(wave, collectors)
            specs += collected
            if not follow_references:
                break
            pending: dict[tuple[str, str, str], DiscoveredResource] = {}
            for spec in collected:
                for target in extract_references(spec, self.account_id):
                    key = _identity(target)
                    if key in known:
                        continue
                    if key in pending:
                        pending[key].referenced_by += target.referenced_by
                    else:
                        pending[key] = target
            wave = sorted(pending.values(), key=lambda r: r.arn)
            known.update(pending)
            referenced += wave
        return self._result(specs, referenced, collectors)

    def _collect_wave(
        self,
        resources: list[DiscoveredResource],
        collectors: dict[tuple[str, str], SpecCollector],
    ) -> list[ResourceSpec]:
        jobs: list[tuple[SpecCollector, DiscoveredResource]] = []
        for resource in resources:
            info = REGISTRY.get(resource.resource_type)
            if info is None:
                continue
            client_region = (
                GLOBAL_CLIENT_REGION if resource.region == GLOBAL_REGION else resource.region
            )
            key = (info.service, client_region)
            if key not in collectors:
                client = self.session.client(info.service, region_name=client_region)
                collectors[key] = SpecCollector(client, self.retry_config)
            jobs.append((collectors[key], resource))

        specs: list[ResourceSpec | None] = [None] * len(jobs)
        done = 0
        lock = threading.Lock()

        def run(index: int) -> None:
            nonlocal done
            collector, resource = jobs[index]
            result = collector.collect_resource(
                resource.resource_type,
                resource.resource_id,
                resource.arn,
                resource.region,
                self.account_id,
            )
            if result.is_ok():
                specs[index] = result.value
            with lock:
                done += 1
                if self.progress_callback is not None:
                    self.progress_callback(done, len(jobs))

        with ThreadPoolExecutor(max_workers=max(1, self.max_workers)) as executor:
            list(executor.map(run, range(len(jobs))))
        return [s for s in specs if s is not None]

    def _result(
        self,
        specs: list[ResourceSpec],
        referenced: list[DiscoveredResource],
        collectors: dict[tuple[str, str], SpecCollector],
    ) -> CollectionResult:
        result = CollectionResult(specs=specs, referenced=referenced)
        for collector in collectors.values():
            result.api_calls += collector.api_calls
            result.operations.extend(collector.operations)
        result.operations.sort(key=lambda op: (op.resource_arn, op.timestamp))
        result.errors = [
            CollectionError(
                resource_arn=op.resource_arn,
                operation=op.operation,
                error_type=op.error_type,
                error_message=op.detail,
                timestamp=op.timestamp,
                retry_count=max(0, op.attempts - 1),
            )
            for op in result.operations
            if op.status in (CallStatus.DENIED, CallStatus.FAILED)
        ]
        return result
