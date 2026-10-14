"""
MCP Server Module

Safe, read-only interface for AI Agents over the spec files of an Output_Dir
(``<cache_dir>/<canonical_type>/<region>/<file_id>.json``). No AWS API is ever
called and this module must not import boto3/botocore.

Processing order of ``handle_request``: whitelist → parameter validation →
rate limit → dispatch → sanitize the whole response (single exit point).

Requirements Coverage:
- Requirement 5.1: Tools list-resources, get-resource-spec, analyze-activity-flow,
                   generate-documentation with the parameters of design.md
- Requirement 5.2: Every response passes through the Data_Sanitizer
- Requirement 5.3 / 5.4: Cached spec files only; cache misses are errors
- Requirement 5.5 / 5.6: Whitelist and parameter validation with a security log
- Requirement 5.7: At most 10 accepted requests in any sliding 1-second window
- Requirement 8.6: Unknown ARNs are rejected
"""

from __future__ import annotations

import json
import logging
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

from src.analysis_engine import AnalysisEngine
from src.documentation import document_citations, generate_infrastructure_doc
from src.parser import ResourceSpec
from src.resource_types import REGISTRY, canonical_type, resource_id
from src.sanitizer import DataSanitizer

logger = logging.getLogger(__name__)

# Tool name → {parameter: (type, required)} (design.md §"MCP Server").
TOOL_PARAMETERS: dict[str, dict[str, tuple[type, bool]]] = {
    "list-resources": {"region": (str, False), "resource_type": (str, False)},
    "get-resource-spec": {"arn": (str, True)},
    "analyze-activity-flow": {"arn": (str, False)},
    "generate-documentation": {},
}
WHITELISTED_OPERATIONS: list[str] = list(TOOL_PARAMETERS)

RATE_LIMIT_MAX_PER_SECOND = 10
RATE_LIMIT_WINDOW_SECONDS = 1.0
RATE_LIMIT_MESSAGE = "Rate limit exceeded: max 10 requests per second"
SECURITY_LOG_MAX_ENTRIES = 1000

EMPTY_CACHE_MESSAGE = (
    "The cache directory has no spec files, so the requested data is not in the "
    "collected data. Run `aws-inventory collect` first."
)


class SecurityLogEntry(TypedDict):
    timestamp: str
    operation: str
    reason: str


@dataclass(frozen=True)
class CachedSpec:
    """One per-resource spec file of the cache."""

    spec_file: str  # relative to cache_dir, posix separators
    document: dict[str, Any]  # sanitized file content
    spec: ResourceSpec


class _InvalidParameters(Exception):
    pass


def _not_collected(arn: str) -> str:
    return (
        f"Resource '{arn}' not found: it is not in the collected data. "
        "Run `aws-inventory collect` to collect it first."
    )


class MCPServer:
    """
    Request handler behind the MCP stdio transport.

    Parameters
    ----------
    cache_dir:
        Output_Dir written by ``aws-inventory collect``.
    clock:
        Monotonic clock in seconds, used only for rate limiting.
    """

    def __init__(self, cache_dir: str, clock: Callable[[], float] = time.monotonic) -> None:
        self.cache_dir = Path(cache_dir)
        self._clock = clock
        self._sanitizer = DataSanitizer()
        self._accepted: deque[float] = deque()
        self._security_log: deque[SecurityLogEntry] = deque(maxlen=SECURITY_LOG_MAX_ENTRIES)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_request(self, operation: str, params: Any = None) -> dict[str, Any]:
        """
        Handle one tool request. Returns ``{"status": "ok", "data": ...}``,
        ``{"status": "error", "message": ...}`` or ``{"status": "rate_limited", ...}``.
        """
        if operation not in TOOL_PARAMETERS:
            reason = f"Unauthorized operation: '{operation}'"
            self._reject(operation, reason)
            return self._respond({"status": "error", "message": reason})

        try:
            clean_params = self._validate(operation, params)
        except _InvalidParameters as exc:
            reason = f"Invalid parameters for '{operation}': {exc}"
            self._reject(operation, reason)
            return self._respond({"status": "error", "message": reason})

        if not self._admit():
            return self._respond({"status": "rate_limited", "message": RATE_LIMIT_MESSAGE})

        try:
            response = self._dispatch(operation, clean_params)
        except Exception as exc:  # noqa: BLE001 - every failure becomes an error response
            logger.error("Error handling operation '%s': %s", operation, type(exc).__name__)
            response = {"status": "error", "message": f"{type(exc).__name__}: {exc}"}
        return self._respond(response)

    def get_security_logs(self) -> list[SecurityLogEntry]:
        """Rejected requests, oldest first (Req 5.6)."""
        return [SecurityLogEntry(**entry) for entry in self._security_log]

    # ------------------------------------------------------------------
    # Validation, security log, rate limit, response exit point
    # ------------------------------------------------------------------

    @staticmethod
    def _validate(operation: str, params: Any) -> dict[str, Any]:
        if params is None:
            params = {}
        if not isinstance(params, dict):
            raise _InvalidParameters("parameters must be an object")
        schema = TOOL_PARAMETERS[operation]
        unknown = sorted(str(name) for name in params if name not in schema)
        if unknown:
            raise _InvalidParameters(f"unknown parameter(s) {', '.join(map(repr, unknown))}")
        clean: dict[str, Any] = {}
        for name, (expected, required) in schema.items():
            value = params.get(name)
            if value is None:
                if required:
                    raise _InvalidParameters(f"missing required parameter '{name}'")
                continue
            if not isinstance(value, expected):
                raise _InvalidParameters(f"parameter '{name}' must be a {expected.__name__}")
            clean[name] = value
        if "resource_type" in clean:
            resolved = canonical_type(clean["resource_type"])
            if resolved is None:
                raise _InvalidParameters(
                    f"unknown resource_type '{clean['resource_type']}' "
                    f"(supported: {', '.join(sorted(REGISTRY))})"
                )
            clean["resource_type"] = resolved
        return clean

    def _reject(self, operation: str, reason: str) -> None:
        entry = SecurityLogEntry(
            timestamp=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            operation=self._sanitizer.sanitize(str(operation)),
            reason=self._sanitizer.sanitize(reason),
        )
        self._security_log.append(entry)
        logger.warning("Rejected MCP request '%s': %s", entry["operation"], entry["reason"])

    def _admit(self) -> bool:
        """Sliding-window limiter; only accepted requests are recorded (Req 5.7)."""
        now = self._clock()
        while self._accepted and now - self._accepted[0] >= RATE_LIMIT_WINDOW_SECONDS:
            self._accepted.popleft()
        if len(self._accepted) >= RATE_LIMIT_MAX_PER_SECOND:
            return False
        self._accepted.append(now)
        return True

    def _respond(self, response: dict[str, Any]) -> dict[str, Any]:
        """Single exit point: every response is sanitized (Req 5.2)."""
        sanitized: dict[str, Any] = self._sanitizer.sanitize(response)
        return sanitized

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------

    def load_cache(self) -> list[CachedSpec]:
        """
        Read ``<type>/<region>/*.json`` for the registry's types only, so other
        output directories are never mistaken for specs. Sorted by spec_file.
        """
        entries: list[CachedSpec] = []
        for type_id in sorted(REGISTRY):
            for path in sorted((self.cache_dir / type_id).glob("*/*.json")):
                rel = path.relative_to(self.cache_dir).as_posix()
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if not isinstance(data, dict) or not isinstance(data.get("arn"), str):
                        raise ValueError("not a resource spec document")
                except (OSError, ValueError) as exc:
                    logger.warning("Skipping unreadable spec file %s: %s", rel, exc)
                    continue
                document = self._sanitizer.sanitize(data)
                entries.append(CachedSpec(rel, document, ResourceSpec.from_dict(document)))
        return entries

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def _dispatch(self, operation: str, params: dict[str, Any]) -> dict[str, Any]:
        cache = self.load_cache()
        if not cache:
            return {"status": "error", "message": EMPTY_CACHE_MESSAGE}
        arn = params.get("arn")
        if arn is not None and not any(entry.spec.arn == arn for entry in cache):
            return {"status": "error", "message": _not_collected(arn)}

        handlers: dict[str, Callable[[list[CachedSpec], dict[str, Any]], Any]] = {
            "list-resources": self._list_resources,
            "get-resource-spec": self._get_resource_spec,
            "analyze-activity-flow": self._analyze_activity_flow,
            "generate-documentation": self._generate_documentation,
        }
        return {"status": "ok", "data": handlers[operation](cache, params)}

    @staticmethod
    def _list_resources(cache: list[CachedSpec], params: dict[str, Any]) -> list[dict[str, Any]]:
        region = params.get("region")
        wanted_type = params.get("resource_type")
        result = []
        for entry in cache:
            spec = entry.spec
            kind = canonical_type(spec.resource_type) or spec.resource_type
            if region is not None and spec.region != region:
                continue
            if wanted_type is not None and kind != wanted_type:
                continue
            result.append(
                {
                    "arn": spec.arn,
                    "resource_type": kind,
                    "region": spec.region,
                    "account_id": spec.account_id,
                    "resource_id": resource_id(spec),
                    "spec_file": entry.spec_file,
                    "checksum": spec.metadata.checksum,
                }
            )
        return result

    @staticmethod
    def _get_resource_spec(cache: list[CachedSpec], params: dict[str, Any]) -> dict[str, Any]:
        entry = next(e for e in cache if e.spec.arn == params["arn"])
        return {**entry.document, "spec_file": entry.spec_file}

    @staticmethod
    def _analyze_activity_flow(cache: list[CachedSpec], params: dict[str, Any]) -> dict[str, Any]:
        data = AnalysisEngine().analyze([entry.spec for entry in cache]).to_dict()
        arn = params.get("arn")
        if arn is not None:
            data["relationships"] = [
                r for r in data["relationships"] if arn in (r["from_arn"], r["to_arn"])
            ]
            data["patterns"] = [p for p in data["patterns"] if arn in p["participating_resources"]]
            data["security_findings"] = [
                f for f in data["security_findings"] if f["resource_arn"] == arn
            ]
        return data

    @staticmethod
    def _generate_documentation(cache: list[CachedSpec], params: dict[str, Any]) -> dict[str, Any]:
        specs = [entry.spec for entry in cache]
        report = AnalysisEngine().analyze(specs)
        return {
            "markdown": generate_infrastructure_doc(report, specs),
            "citations": document_citations(report, specs),
        }
