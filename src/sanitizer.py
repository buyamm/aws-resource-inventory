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
- ``{"name": <sensitive name>, "value": ...}`` pairs (ECS container environments) are
  treated like a key/value entry: the ``value`` is redacted
- EC2 launch template ``UserData`` is base64 and cannot be scanned, so it is always redacted
- Sensitive values are matched by regex pattern (e.g. AKIA... AWS access keys)
- Both key-name matching and value-pattern matching are applied
- Redaction logs record the full path to each redacted field without exposing the value
- All nested structures (dicts, lists) are recursively traversed
- Performance: compiled regex patterns are cached at class construction; an
  object-identity memo sanitizes a container referenced from several places once
  and reuses the sanitized copy (which also makes self-referencing input safe)
"""

import re
from typing import Any  # noqa: UP035

# ============================================================================
# Sensitive Pattern Definitions
# ============================================================================

# Regex patterns applied to VALUES regardless of key name.
# Each entry is (pattern, replacement_label). Only real credentials are matched:
# AKIA (long-term) and ASIA (temporary) access key IDs, and PEM private keys.
# Unique-ID prefixes such as AROA/AIDA identify principals and are not secrets.
SENSITIVE_VALUE_PATTERNS: list[tuple[str, str]] = [
    (r"(?:AKIA|ASIA)[0-9A-Z]{16}", "[REDACTED_AWS_KEY]"),
    (r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]"),
]

# Key names (case-insensitive, substring match) whose STRING values are sensitive.
# Order matters: the first matching entry decides the placeholder.
SENSITIVE_KEY_PATTERNS: list[tuple[str, str]] = [
    ("access_key_id", "[REDACTED_AWS_KEY]"),
    ("secret_access_key", "[REDACTED_AWS_SECRET]"),
    ("password", "[REDACTED]"),
    ("passwd", "[REDACTED]"),
    ("private_key", "[REDACTED]"),
    ("secret", "[REDACTED]"),
    ("token", "[REDACTED]"),
    ("api_key", "[REDACTED]"),
    ("credential", "[REDACTED]"),
    ("userdata", "[REDACTED]"),
]

# {"name": ..., "value": ...} entries: the name decides whether the value is sensitive.
NAME_VALUE_KEYS = ("name", "value")

# Keys that should NOT be redacted even if they substring-match a sensitive pattern.
SAFE_KEY_ALLOWLIST: list[str] = [
    "public",
]

# Placeholders produced by this module; values already equal to one are left as-is,
# which makes sanitize() idempotent (Requirement 9.6).
PLACEHOLDERS = frozenset(label for _, label in SENSITIVE_VALUE_PATTERNS + SENSITIVE_KEY_PATTERNS)


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
    - An object-identity memo sanitizes a container referenced from multiple
      places once; every reference then points at the same sanitized copy.
    """

    def __init__(self) -> None:
        self._redaction_logs: list[str] = []

        # Pre-compile individual patterns (kept for the replacement label lookup)
        self._compiled_value_patterns = [
            (re.compile(pattern), replacement) for pattern, replacement in SENSITIVE_VALUE_PATTERNS
        ]

        # Build a combined pattern so a single regex search determines whether
        # *any* sensitive value pattern is present in a string — avoids
        # iterating the list for every leaf string value in large structures.
        combined = "|".join(
            f"(?P<g{i}>{pattern})" for i, (pattern, _) in enumerate(SENSITIVE_VALUE_PATTERNS)
        )
        self._combined_value_pattern = re.compile(combined)

        # Internal: container id -> sanitized copy for the current top-level
        # sanitize() call. The input is kept alive by the caller, so ids stay unique.
        self._memo: dict[int, Any] = {}

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def sanitize(self, data: Any, _path: str | None = None) -> Any:
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
            self._memo = {}

        if isinstance(data, dict):
            return self._sanitize_dict(data, _path or "")
        if isinstance(data, list):
            return self._sanitize_list(data, _path or "")
        if isinstance(data, str):
            return self._sanitize_string_value(data, _path or "")
        # Non-string scalars (int, float, bool, None) are never sensitive
        return data

    def get_redaction_logs(self) -> list[str]:
        """Return a copy of all redaction log entries accumulated so far."""
        return list(self._redaction_logs)

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _sanitize_dict(self, data: dict[str, Any], path: str) -> dict[str, Any]:
        """Sanitize every value in a dictionary, preserving all keys.

        A dictionary reached again (shared or cyclic reference) returns the
        sanitized copy made on first visit, never the raw input.
        """
        if id(data) in self._memo:
            return self._memo[id(data)]  # type: ignore[no-any-return]
        result: dict[str, Any] = {}
        self._memo[id(data)] = result
        pair_label = self._name_value_redaction(data)
        for key, value in data.items():
            child_path = f"{path}.{key}" if path else key
            redaction_label = self._sensitive_key_redaction(key)
            if pair_label is not None and key.lower() == NAME_VALUE_KEYS[1]:
                redaction_label = pair_label
            if redaction_label is not None and isinstance(value, str) and value not in PLACEHOLDERS:
                # Key name itself marks this as sensitive — redact directly
                result[key] = redaction_label
                self._log_redaction(child_path, redaction_label)
            else:
                # Recurse so nested dicts/lists are also sanitized
                result[key] = self.sanitize(value, child_path)
        return result

    def _sanitize_list(self, data: list, path: str) -> list:
        """Sanitize every element in a list.

        Uses the same memo as ``_sanitize_dict``, so a list referenced several
        times is sanitized once and every reference gets the sanitized copy.
        """
        if id(data) in self._memo:
            return self._memo[id(data)]  # type: ignore[no-any-return]
        result: list = []
        self._memo[id(data)] = result
        result.extend(self.sanitize(item, f"{path}[{idx}]") for idx, item in enumerate(data))
        return result

    def _sanitize_string_value(self, value: str, path: str) -> str:
        """
        Apply value-based regex patterns to a string.

        Uses a pre-built combined pattern for a single-pass scan, then
        looks up the replacement label from the individual pattern list.

        Key-name-based redaction is handled by ``_sanitize_dict``; this
        method only performs regex matching on the *content* of a string.
        """
        # Fast path: combined pattern tells us if *any* sensitive value is present
        if not self._combined_value_pattern.search(value):
            return value

        # Determine the correct replacement label by checking individual patterns
        for compiled_pattern, replacement in self._compiled_value_patterns:
            if compiled_pattern.search(value):
                self._log_redaction(path, replacement)
                return replacement

        return value  # pragma: no cover — combined match guarantees one hit

    def _name_value_redaction(self, data: dict[str, Any]) -> str | None:
        """Label for the ``value`` of a ``{"name": ..., "value": ...}`` entry, if sensitive."""
        lowered = {str(k).lower(): v for k, v in data.items()}
        name = lowered.get(NAME_VALUE_KEYS[0])
        if not isinstance(name, str) or NAME_VALUE_KEYS[1] not in lowered:
            return None
        return self._sensitive_key_redaction(name)

    def _sensitive_key_redaction(self, key: str) -> str | None:
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
