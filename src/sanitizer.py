"""
Data Sanitizer Module

This module provides sensitive data detection and redaction for AWS resource specifications.
It ensures that credentials, secrets, and other sensitive values are replaced with
placeholder text before data is written to output files.

Requirements Coverage:
- Requirement 9.5: Sanitize sensitive data (secrets, passwords, private keys) from outputs
- Requirement 9.6: Replace detected sensitive values with placeholder text and log sanitization

Design:
- Sensitive keys are matched case-insensitively by name (e.g. "password", "aws_access_key_id")
- Sensitive values are matched by regex pattern (e.g. AKIA... AWS access keys)
- Both key-name matching and value-pattern matching are applied
- Redaction logs record the full path to each redacted field without exposing the value
- All nested structures (dicts, lists) are recursively traversed
- Performance: compiled regex patterns are cached at class construction; a shared
  object-identity set prevents duplicate work when the same container is referenced
  from multiple places in a large structure
"""

import re
from typing import Any, Dict, List, Optional, Set  # noqa: UP035 — py3.9 compat


# ============================================================================
# Sensitive Pattern Definitions
# ============================================================================

# Regex patterns applied to VALUES regardless of key name.
# Each entry is (pattern, replacement_label).
SENSITIVE_VALUE_PATTERNS: List[tuple[str, str]] = [
    # AWS Access Key IDs start with AKIA, ASIA, AROA, AIDA, ANPA, ANVA
    (r'(?:AKIA|ASIA|AROA|AIDA|ANPA|ANVA)[0-9A-Z]{16}', "[REDACTED_AWS_KEY]"),
]

# Key names (case-insensitive, substring match) that indicate sensitive values.
# The order matters: more specific matches must come before general ones so
# that "aws_access_key_id" is caught before the broader "key" pattern.
SENSITIVE_KEY_PATTERNS: List[tuple[str, str]] = [
    # AWS-specific credential keys → specific redaction labels
    ("aws_access_key_id",      "[REDACTED_AWS_KEY]"),
    ("aws_secret_access_key",  "[REDACTED_AWS_SECRET]"),
    # Generic sensitive key names → generic redaction label
    ("secret_access_key",      "[REDACTED_AWS_SECRET]"),
    # Database / service passwords (explicit entries placed before "password"
    # so the more descriptive label could be applied in future if needed)
    ("database_password",      "[REDACTED]"),
    ("db_password",            "[REDACTED]"),
    ("password",               "[REDACTED]"),
    ("passwd",                 "[REDACTED]"),
    # Key / secret variants
    ("private_key",            "[REDACTED]"),
    ("secret_key",             "[REDACTED]"),
    ("secret",                 "[REDACTED]"),
    # Token variants (bearer_token, auth_token, api_token, access_token, token)
    ("bearer_token",           "[REDACTED]"),
    ("api_token",              "[REDACTED]"),
    ("api_key",                "[REDACTED]"),
    ("access_token",           "[REDACTED]"),
    ("auth_token",             "[REDACTED]"),
    ("token",                  "[REDACTED]"),
    # Credential bundles
    ("credentials",            "[REDACTED]"),
    # Generic key catch-all (must stay last so specific entries win)
    ("key",                    "[REDACTED]"),
]

# Keys that should NOT be redacted even if they substring-match a sensitive pattern.
# e.g. "public_key" contains "key" but is safe to expose.
SAFE_KEY_ALLOWLIST: List[str] = [
    "public_key",
    "public",
]


# ============================================================================
# DataSanitizer
# ============================================================================

class DataSanitizer:
    """
    Sanitizer that removes sensitive values from nested data structures.

    Usage::

        sanitizer = DataSanitizer()
        clean = sanitizer.sanitize(data)
        logs  = sanitizer.get_redaction_logs()

    Each ``DataSanitizer`` instance maintains its own redaction log so that
    logs from different sanitization operations stay independent.

    Performance notes:
    - Value-pattern regexes are compiled once at construction time.
    - A combined single-regex is built from all value patterns so each string
      value is scanned in one pass instead of N separate regex searches.
    - An object-identity visited set prevents duplicate traversal of containers
      that are referenced from multiple places in a large structure.
    """

    def __init__(self) -> None:
        self._redaction_logs: List[str] = []

        # Pre-compile individual patterns (kept for the replacement label lookup)
        self._compiled_value_patterns = [
            (re.compile(pattern), replacement)
            for pattern, replacement in SENSITIVE_VALUE_PATTERNS
        ]

        # Build a combined pattern so a single regex search determines whether
        # *any* sensitive value pattern is present in a string — avoids
        # iterating the list for every leaf string value in large structures.
        combined = "|".join(
            f"(?P<g{i}>{pattern})"
            for i, (pattern, _) in enumerate(SENSITIVE_VALUE_PATTERNS)
        )
        self._combined_value_pattern: Optional[re.Pattern] = (
            re.compile(combined) if combined else None
        )

        # Internal: set of container object ids seen during the current
        # top-level sanitize() call, used to skip already-processed nodes.
        self._visited: Set[int] = set()

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def sanitize(self, data: Any, _path: Optional[str] = None) -> Any:
        """
        Recursively sanitize a data structure, replacing sensitive values.

        The structure (keys, nesting, types) is preserved; only leaf string
        values that match sensitive patterns are replaced.

        Args:
            data: Any Python object (dict, list, str, int, …)

        Returns:
            A new object of the same type with sensitive values redacted.
        """
        # Reset state on every top-level call (i.e. when called without _path)
        if _path is None:
            self._redaction_logs = []
            self._visited = set()

        if isinstance(data, dict):
            return self._sanitize_dict(data, _path or "")
        if isinstance(data, list):
            return self._sanitize_list(data, _path or "")
        if isinstance(data, str):
            return self._sanitize_string_value(data, _path or "")
        # Non-string scalars (int, float, bool, None) are never sensitive
        return data

    def get_redaction_logs(self) -> List[str]:
        """Return a copy of all redaction log entries accumulated so far."""
        return list(self._redaction_logs)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _sanitize_dict(self, data: Dict[str, Any], path: str) -> Dict[str, Any]:
        """Sanitize every value in a dictionary, preserving all keys.

        Skips re-processing if this exact container object has already been
        visited during the current sanitize() call (handles shared references
        in large structures without redundant work).
        """
        obj_id = id(data)
        if obj_id in self._visited:
            # Already processed — return a shallow copy to avoid mutation
            return dict(data)
        self._visited.add(obj_id)

        result: Dict[str, Any] = {}
        for key, value in data.items():
            child_path = f"{path}.{key}" if path else key
            redaction_label = self._sensitive_key_redaction(key)
            if redaction_label is not None and isinstance(value, str):
                # Key name itself marks this as sensitive — redact directly
                result[key] = redaction_label
                self._log_redaction(child_path, redaction_label)
            else:
                # Recurse so nested dicts/lists are also sanitized
                result[key] = self.sanitize(value, child_path)
        return result

    def _sanitize_list(self, data: list, path: str) -> list:
        """Sanitize every element in a list.

        Uses the same visited-set guard as ``_sanitize_dict`` to avoid
        re-traversing the same list when it is referenced multiple times.
        """
        obj_id = id(data)
        if obj_id in self._visited:
            return list(data)
        self._visited.add(obj_id)

        return [
            self.sanitize(item, f"{path}[{idx}]")
            for idx, item in enumerate(data)
        ]

    def _sanitize_string_value(self, value: str, path: str) -> str:
        """
        Apply value-based regex patterns to a string.

        Uses a pre-built combined pattern for a single-pass scan, then
        looks up the replacement label from the individual pattern list.

        Key-name-based redaction is handled by ``_sanitize_dict``; this
        method only performs regex matching on the *content* of a string.
        """
        if self._combined_value_pattern is None:
            return value

        # Fast path: combined pattern tells us if *any* sensitive value is present
        if not self._combined_value_pattern.search(value):
            return value

        # Determine the correct replacement label by checking individual patterns
        for compiled_pattern, replacement in self._compiled_value_patterns:
            if compiled_pattern.search(value):
                self._log_redaction(path, replacement)
                return replacement

        return value  # pragma: no cover — combined match guarantees one hit

    def _sensitive_key_redaction(self, key: str) -> Optional[str]:
        """
        Return the appropriate redaction label if ``key`` is sensitive,
        or ``None`` if it is safe.

        Matching is case-insensitive substring match.  A key is considered
        safe if it appears in SAFE_KEY_ALLOWLIST (also case-insensitive).
        """
        lower_key = key.lower()

        # Check allowlist first
        for safe in SAFE_KEY_ALLOWLIST:
            if safe in lower_key:
                return None

        # Check sensitive key patterns (most-specific first)
        for pattern, replacement in SENSITIVE_KEY_PATTERNS:
            if pattern in lower_key:
                return replacement

        return None

    def _log_redaction(self, path: str, replacement: str) -> None:
        """Append a redaction log entry (path + label, never the actual value)."""
        entry = f"Redacted field '{path}' → {replacement}"
        self._redaction_logs.append(entry)
