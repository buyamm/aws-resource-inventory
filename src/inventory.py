"""
Inventory collection: turns discovered resources into ResourceSpecs.

Requirements Coverage:
- Requirement 2.1: One Resource_Spec per discovered resource
- Requirement 3.3: region and account_id set from discovery / STS
- Requirement 10.2: api_calls across all collectors
- Requirement 12.2: Failed resources become CollectionErrors; collection continues
- Requirement 12.4: Every attempted operation is reported
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

    def collect_all(self, resources: list[DiscoveredResource]) -> CollectionResult:
        collectors: dict[tuple[str, str], SpecCollector] = {}
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

        result = CollectionResult(specs=[s for s in specs if s is not None])
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
