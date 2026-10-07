"""
MCP Server Module

Provides a safe, controlled interface for AI Agents to query AWS resource
specifications from local cache — no direct AWS API calls are ever made.

Requirements Coverage:
- Requirement 5.1: Expose operations: list-resources, get-resource-spec,
                   analyze-activity-flow, generate-documentation
- Requirement 5.2: Never expose AWS credentials in responses
- Requirement 5.3: Retrieve cached local data only; error if cache missing
- Requirement 5.5: Validate requests against a whitelist of permitted operations
- Requirement 5.6: Log unauthorized attempts and return error responses
- Requirement 5.7: Rate-limit requests to a maximum of 10 per second
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from src.sanitizer import DataSanitizer

logger = logging.getLogger(__name__)

# Operations that AI Agents are permitted to call.
WHITELISTED_OPERATIONS: List[str] = [
    "list-resources",
    "get-resource-spec",
    "analyze-activity-flow",
    "generate-documentation",
]

# Maximum requests allowed within a one-second window.
RATE_LIMIT_MAX_PER_SECOND: int = 10


class MCPServer:
    """
    MCP Server that exposes safe read-only operations over locally cached
    AWS resource specifications.

    Parameters
    ----------
    cache_dir:
        Path to the root of the local spec cache.  Files are expected to be
        organised as ``<cache_dir>/<region>/<resource_type>/<name>.json``.
    """

    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = cache_dir
        self._sanitizer = DataSanitizer()

        # Rate-limiting state: list of monotonic timestamps for each request
        # in the current one-second window.
        self._request_timestamps: List[float] = []

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def handle_request(
        self,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Dispatch an AI Agent request.

        Returns a dict with at minimum a ``status`` key, one of:
        - ``"ok"``           — success; ``data`` contains the result
        - ``"error"``        — permanent failure; ``message`` explains why
        - ``"rate_limited"`` — request rejected because the rate limit was hit
        """
        if params is None:
            params = {}

        # 1. Whitelist check
        if operation not in WHITELISTED_OPERATIONS:
            logger.warning(
                "Unauthorized operation attempted: '%s'", operation
            )
            return {
                "status": "error",
                "message": f"Unauthorized operation: '{operation}'",
            }

        # 2. Rate-limit check
        if self._is_rate_limited():
            return {
                "status": "rate_limited",
                "message": "Rate limit exceeded: max 10 requests per second",
            }

        # 3. Dispatch to the appropriate handler
        try:
            return self._dispatch(operation, params)
        except Exception as exc:  # noqa: BLE001
            logger.error("Error handling operation '%s': %s", operation, exc)
            return {"status": "error", "message": str(exc)}

    # ------------------------------------------------------------------
    # Rate limiting
    # ------------------------------------------------------------------

    def _is_rate_limited(self) -> bool:
        """
        Return True if the caller has exceeded the rate limit.

        Maintains a sliding one-second window: any timestamp older than
        one second is discarded before checking the count.
        """
        now = time.monotonic()
        # Remove timestamps outside the current 1-second window
        self._request_timestamps = [
            ts for ts in self._request_timestamps if now - ts < 1.0
        ]

        if len(self._request_timestamps) >= RATE_LIMIT_MAX_PER_SECOND:
            return True

        # Record this request
        self._request_timestamps.append(now)
        return False

    # ------------------------------------------------------------------
    # Operation dispatch
    # ------------------------------------------------------------------

    def _dispatch(
        self, operation: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        if operation == "list-resources":
            return self._list_resources(params)
        if operation == "get-resource-spec":
            return self._get_resource_spec(params)
        if operation == "analyze-activity-flow":
            return self._analyze_activity_flow(params)
        if operation == "generate-documentation":
            return self._generate_documentation(params)
        # Should never be reached after the whitelist check, but kept for safety
        return {"status": "error", "message": f"Unknown operation: '{operation}'"}

    # ------------------------------------------------------------------
    # Operation handlers
    # ------------------------------------------------------------------

    def _list_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return all cached resources for a given region + resource_type.

        Params
        ------
        region : str  (optional)
        resource_type : str  (optional)

        The cache directory structure is:
            <cache_dir>/<region>/<resource_type>/<name>.json

        If region/resource_type are supplied the search is scoped; otherwise
        all cached resources are returned.
        """
        region = params.get("region")
        resource_type_param = params.get("resource_type")

        # Normalise resource_type: "lambda_function" → "lambda"
        resource_type_dir = self._resource_type_to_dir(resource_type_param)

        resources: List[Dict[str, Any]] = []
        errors: List[str] = []

        # Build the search root
        search_root = self.cache_dir
        if region:
            search_root = os.path.join(search_root, region)
            if resource_type_dir:
                search_root = os.path.join(search_root, resource_type_dir)

        if not os.path.isdir(search_root):
            # Cache directory does not exist → collection has not been run
            return {
                "status": "error",
                "message": (
                    "No cached data found. Run collection first to populate "
                    "the cache before querying."
                ),
            }

        for dirpath, _dirnames, filenames in os.walk(search_root):
            for filename in filenames:
                if not filename.endswith(".json"):
                    continue
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, encoding="utf-8") as fh:
                        data = json.load(fh)
                    # Sanitize to ensure no credentials leak
                    data = self._sanitizer.sanitize(data)
                    resources.append(data)
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(f"{filepath}: {exc}")

        if not resources and not errors:
            return {
                "status": "error",
                "message": (
                    "No cached data found. Run collection first to populate "
                    "the cache before querying."
                ),
            }

        return {"status": "ok", "data": resources}

    def _get_resource_spec(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return the spec for a single resource identified by ARN.

        Params
        ------
        arn : str  (required)
        """
        arn = params.get("arn", "")
        if not arn:
            return {"status": "error", "message": "Parameter 'arn' is required"}

        # Walk the entire cache tree looking for a file whose content has a
        # matching ARN.  This is O(n) but acceptable for a local cache.
        for dirpath, _dirnames, filenames in os.walk(self.cache_dir):
            for filename in filenames:
                if not filename.endswith(".json"):
                    continue
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, encoding="utf-8") as fh:
                        data = json.load(fh)
                    if data.get("arn") == arn:
                        clean = self._sanitizer.sanitize(data)
                        return {"status": "ok", "data": clean}
                except (OSError, json.JSONDecodeError):
                    continue

        return {
            "status": "error",
            "message": (
                f"Resource '{arn}' not found in cache. "
                "Run collection first to populate the cache."
            ),
        }

    def _analyze_activity_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder for activity-flow analysis.

        The actual analysis would delegate to the AnalysisEngine; for now
        returns an empty analysis so that whitelisted callers get a valid
        response rather than an error.
        """
        return {
            "status": "ok",
            "data": {
                "analysis": "Activity flow analysis is not yet implemented.",
                "relationships": [],
            },
        }

    def _generate_documentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder for documentation generation.

        Returns a valid response so that whitelisted callers are not blocked.
        """
        return {
            "status": "ok",
            "data": {
                "documentation": "Documentation generation is not yet implemented.",
            },
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resource_type_to_dir(resource_type: Optional[str]) -> Optional[str]:
        """
        Map a resource_type parameter to a cache sub-directory name.

        The cache uses short service names ("lambda", "ec2", …) while callers
        may pass the longer snake-case form ("lambda_function", "ec2_instance").
        """
        if not resource_type:
            return None
        # Simple mapping: take the first component before the first underscore
        # so "lambda_function" → "lambda", "ec2_instance" → "ec2".
        return resource_type.split("_")[0]
