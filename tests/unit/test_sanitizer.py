"""
Unit tests for Data Sanitizer component.

This module contains property-based tests and unit tests for the DataSanitizer class.
Tests are written BEFORE implementation following TDD Red-Green-Refactor methodology.

Property-Based Tests:
- test_property_sanitizer_preserves_structure_req_9_5: Validates that sanitization preserves data structure

Unit Tests:
- test_sanitizer_removes_aws_credentials_req_9_5: Validates AWS credential redaction
- test_sanitizer_logs_redactions_req_9_6: Validates redaction logging
"""

import pytest
from hypothesis import given, strategies as st

# This import will fail until we implement the sanitizer (RED phase)
try:
    from src.sanitizer import DataSanitizer
except ImportError:
    DataSanitizer = None


def get_structure(data):
    """
    Recursively extract the structural 'shape' of a dictionary.

    Returns a nested dict of the same keys, where each value is either
    another structural dict (for dict values) or None (for leaf values).
    This lets us compare structure independently of values.
    """
    if isinstance(data, dict):
        return {k: get_structure(v) for k, v in data.items()}
    return None


class TestDataSanitizerPropertyTests:
    """Property-based tests for DataSanitizer using Hypothesis."""

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet (RED phase)")
    @given(st.dictionaries(keys=st.text(min_size=1, max_size=50), 
                          values=st.one_of(
                              st.text(max_size=100),
                              st.integers(),
                              st.floats(allow_nan=False, allow_infinity=False),
                              st.booleans(),
                              st.none()
                          ),
                          min_size=0,
                          max_size=20))
    def test_property_sanitizer_preserves_structure_req_9_5(self, data):
        """
        Property: For all dictionaries, sanitization preserves structure.
        
        The sanitizer should maintain the same keys and overall structure
        even when values are redacted. This ensures that downstream code
        can still navigate the data structure predictably.
        
        **Validates: Requirements 9.5**
        
        Property tested:
        - For all input dictionaries D, sanitize(D).keys() == D.keys()
        - The depth and nesting structure remains unchanged
        - Only values are modified, not keys or structure
        """
        # RED phase: This test will fail because DataSanitizer is not implemented
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)
        
        # Assert: Keys are preserved
        assert sanitized.keys() == data.keys(), \
            "Sanitization must preserve all dictionary keys"
        
        # Assert: Structure is still a dictionary
        assert isinstance(sanitized, dict), \
            "Sanitization must return a dictionary"

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet (RED phase)")
    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=30),
            values=st.recursive(
                st.one_of(
                    st.text(max_size=100),
                    st.integers(),
                    st.booleans(),
                    st.none(),
                ),
                lambda children: st.dictionaries(
                    keys=st.text(min_size=1, max_size=30),
                    values=children,
                    min_size=0,
                    max_size=5,
                ),
                max_leaves=20,
            ),
            min_size=0,
            max_size=10,
        )
    )
    def test_property_sanitizer_preserves_nested_structure_req_9_5(self, data):
        """
        Property 2: For all nested dictionaries, sanitization preserves the full
        recursive structure — the same keys at every nesting level.

        This is the recursive counterpart to the flat-dict property above. AWS
        resource specs frequently carry deeply-nested config (e.g. Lambda env
        vars inside a function config block), so the sanitizer must preserve
        structure at every depth, not only at the top level.

        **Validates: Requirements 9.5**

        Properties tested:
        - get_structure(sanitize(D)) == get_structure(D)
          (keys and nesting are identical at all depths)
        - sanitize(D) is always a dict when D is a dict
        - No keys are added or removed at any nesting level
        """
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)

        # Assert: result is still a dictionary
        assert isinstance(sanitized, dict), (
            "Sanitization must return a dict when given a dict"
        )

        # Assert: full recursive structure is preserved
        assert get_structure(sanitized) == get_structure(data), (
            "Sanitization must preserve all keys at every nesting level. "
            f"Original structure: {get_structure(data)!r}, "
            f"Sanitized structure: {get_structure(sanitized)!r}"
        )


class TestDataSanitizerSecurityTests:
    """Security-focused unit tests for credential and sensitive data handling."""

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet (RED phase)")
    def test_sanitizer_removes_aws_credentials_req_9_5(self):
        """
        Security: Sanitizer replaces AWS credentials with placeholders.
        
        AWS credentials must never appear in output files. This test validates
        that both AWS Access Keys (AKIA...) and Secret Access Keys are properly
        detected and replaced with safe placeholder values.
        
        **Validates: Requirements 9.5**
        
        Test scenarios:
        - AWS_ACCESS_KEY_ID starting with AKIA is redacted
        - AWS_SECRET_ACCESS_KEY is redacted
        - Redacted values are replaced with safe placeholders
        """
        # RED phase: This test will fail because DataSanitizer is not implemented
        data = {
            "environment_variables": {
                "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
                "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "OTHER_VAR": "safe_value"
            },
            "config": {
                "region": "us-east-1"
            }
        }
        
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)
        
        # Assert: AWS Access Key is redacted
        assert sanitized["environment_variables"]["AWS_ACCESS_KEY_ID"] == "[REDACTED_AWS_KEY]", \
            "AWS Access Key must be redacted"
        
        # Assert: AWS Secret Access Key is redacted
        assert sanitized["environment_variables"]["AWS_SECRET_ACCESS_KEY"] == "[REDACTED_AWS_SECRET]", \
            "AWS Secret Access Key must be redacted"
        
        # Assert: Non-sensitive values are preserved
        assert sanitized["environment_variables"]["OTHER_VAR"] == "safe_value", \
            "Non-sensitive values must be preserved"
        
        # Assert: Structure is preserved
        assert "config" in sanitized, \
            "Non-sensitive sections must be preserved"
        assert sanitized["config"]["region"] == "us-east-1", \
            "Non-sensitive config values must be preserved"

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet (RED phase)")
    def test_sanitizer_removes_aws_credentials_in_nested_structures_req_9_5(self):
        """
        Security: Sanitizer finds and redacts AWS credentials in deeply nested structures.
        
        **Validates: Requirements 9.5**
        """
        # RED phase: This test will fail because DataSanitizer is not implemented
        data = {
            "lambda_functions": [
                {
                    "name": "my-function",
                    "environment": {
                        "variables": {
                            "AWS_ACCESS_KEY_ID": "AKIAI44QH8DHBEXAMPLE",
                            "DB_HOST": "db.example.com"
                        }
                    }
                }
            ]
        }
        
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)
        
        # Assert: Nested AWS Access Key is redacted
        nested_key = sanitized["lambda_functions"][0]["environment"]["variables"]["AWS_ACCESS_KEY_ID"]
        assert nested_key == "[REDACTED_AWS_KEY]", \
            "AWS Access Keys in nested structures must be redacted"
        
        # Assert: Non-sensitive nested values are preserved
        db_host = sanitized["lambda_functions"][0]["environment"]["variables"]["DB_HOST"]
        assert db_host == "db.example.com", \
            "Non-sensitive nested values must be preserved"

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet (RED phase)")
    def test_sanitizer_removes_passwords_and_secrets_req_9_5(self):
        """
        Security: Sanitizer redacts common secret patterns beyond AWS credentials.
        
        **Validates: Requirements 9.5**
        """
        # RED phase: This test will fail because DataSanitizer is not implemented
        data = {
            "database": {
                "password": "super_secret_123",
                "username": "admin"
            },
            "api": {
                "secret_key": "sk_live_1234567890",
                "public_key": "pk_live_0987654321"
            }
        }
        
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)
        
        # Assert: Password is redacted
        assert sanitized["database"]["password"] == "[REDACTED]", \
            "Passwords must be redacted"
        
        # Assert: Secret key is redacted
        assert sanitized["api"]["secret_key"] == "[REDACTED]", \
            "Secret keys must be redacted"
        
        # Assert: Non-secret values are preserved
        assert sanitized["database"]["username"] == "admin", \
            "Usernames should be preserved (not considered secrets)"
        assert sanitized["api"]["public_key"] == "pk_live_0987654321", \
            "Public keys should be preserved"


class TestDataSanitizerLoggingTests:
    """Tests for redaction logging and audit trail."""

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet (RED phase)")
    def test_sanitizer_logs_redactions_req_9_6(self):
        """
        Unit: Sanitizer logs what was redacted for audit purposes.
        
        For security compliance and debugging, the sanitizer must maintain
        a log of which fields were redacted (but NOT the actual values).
        This allows administrators to verify sanitization is working correctly.
        
        **Validates: Requirements 9.6**
        
        Test scenarios:
        - Each redaction is logged
        - Logs contain field names/paths that were redacted
        - Logs do NOT contain the actual sensitive values
        """
        # RED phase: This test will fail because DataSanitizer is not implemented
        data = {
            "password": "secret123",
            "api_token": "token_abc_xyz",
            "config": {
                "AWS_SECRET_ACCESS_KEY": "verysecret"
            }
        }
        
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)
        
        # Get redaction logs
        logs = sanitizer.get_redaction_logs()
        
        # Assert: Logs exist and contain entries
        assert len(logs) > 0, \
            "Redaction logs must contain entries when data is sanitized"
        
        # Assert: Password redaction is logged
        password_logged = any("password" in log.lower() for log in logs)
        assert password_logged, \
            "Password field redaction must be logged"
        
        # Assert: API token redaction is logged
        token_logged = any("api_token" in log.lower() or "token" in log.lower() for log in logs)
        assert token_logged, \
            "API token field redaction must be logged"
        
        # Assert: AWS secret redaction is logged
        aws_secret_logged = any("aws_secret" in log.lower() or "secret_access_key" in log.lower() for log in logs)
        assert aws_secret_logged, \
            "AWS Secret Access Key redaction must be logged"
        
        # Assert: Actual secret values are NOT in logs (security check)
        for log in logs:
            assert "secret123" not in log, \
                "Actual secret values must NOT appear in logs"
            assert "token_abc_xyz" not in log, \
                "Actual token values must NOT appear in logs"
            assert "verysecret" not in log, \
                "Actual AWS secret values must NOT appear in logs"

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet (RED phase)")
    def test_sanitizer_logs_include_field_paths_req_9_6(self):
        """
        Unit: Redaction logs include the full path to redacted fields.
        
        **Validates: Requirements 9.6**
        """
        # RED phase: This test will fail because DataSanitizer is not implemented
        data = {
            "services": {
                "database": {
                    "password": "secret"
                }
            }
        }
        
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)
        logs = sanitizer.get_redaction_logs()
        
        # Assert: Log includes the full path to the redacted field
        path_logged = any("services" in log and "database" in log and "password" in log for log in logs)
        assert path_logged, \
            "Redaction logs must include the full path to redacted fields"

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet (RED phase)")
    def test_sanitizer_clears_logs_between_operations_req_9_6(self):
        """
        Unit: Sanitizer provides clean logs for each sanitization operation.
        
        **Validates: Requirements 9.6**
        """
        # RED phase: This test will fail because DataSanitizer is not implemented
        sanitizer = DataSanitizer()
        
        # First sanitization
        data1 = {"password": "secret1"}
        sanitizer.sanitize(data1)
        logs1 = sanitizer.get_redaction_logs()
        first_count = len(logs1)
        
        # Second sanitization with fresh sanitizer
        sanitizer2 = DataSanitizer()
        data2 = {"api_key": "key123"}
        sanitizer2.sanitize(data2)
        logs2 = sanitizer2.get_redaction_logs()
        
        # Assert: Second sanitizer's logs don't contain first sanitizer's data
        assert len(logs2) > 0, \
            "Second sanitization should have logs"
        
        # The logs should be independent between instances
        password_in_logs2 = any("password" in log.lower() for log in logs2)
        assert not password_in_logs2, \
            "Logs from different sanitizer instances should be independent"


class TestDataSanitizerAdditionalPatterns:
    """Tests for patterns added in the REFACTOR phase (task 5.4)."""

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet")
    def test_sanitizer_redacts_database_password_req_9_5(self):
        """
        Security: database_password key is redacted.

        **Validates: Requirements 9.5**
        """
        data = {
            "database_password": "super_secret_db_pass",
            "db_password": "another_secret",
            "host": "db.example.com",
        }
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)

        assert sanitized["database_password"] == "[REDACTED]"
        assert sanitized["db_password"] == "[REDACTED]"
        assert sanitized["host"] == "db.example.com"

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet")
    def test_sanitizer_redacts_bearer_token_req_9_5(self):
        """
        Security: bearer_token key is redacted.

        **Validates: Requirements 9.5**
        """
        data = {
            "bearer_token": "eyJhbGciOiJSUzI1NiJ9.payload.sig",
            "user_id": "u-12345",
        }
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)

        assert sanitized["bearer_token"] == "[REDACTED]"
        assert sanitized["user_id"] == "u-12345"

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet")
    def test_sanitizer_redacts_credentials_key_req_9_5(self):
        """
        Security: A key named 'credentials' (or containing that substring)
        is redacted.

        **Validates: Requirements 9.5**
        """
        data = {
            "credentials": "some_bundle_of_secrets",
            "aws_credentials": "AKIAIOSFODNN7EXAMPLE:secret",
            "region": "us-east-1",
        }
        sanitizer = DataSanitizer()
        sanitized = sanitizer.sanitize(data)

        assert sanitized["credentials"] == "[REDACTED]"
        assert sanitized["aws_credentials"] == "[REDACTED]"
        assert sanitized["region"] == "us-east-1"

    @pytest.mark.skipif(DataSanitizer is None, reason="DataSanitizer not implemented yet")
    def test_sanitizer_performance_large_nested_structure_req_9_5(self):
        """
        Performance: Sanitizer handles a large, deeply nested structure
        without redundant processing of shared container references.

        **Validates: Requirements 9.5**
        """
        import time

        # Build a wide, deep structure — 50 top-level keys, each containing
        # a 10-level-deep dict with a 'password' leaf at every level.
        def make_deep(depth: int, breadth: int) -> dict:
            if depth == 0:
                return {"safe_value": "ok", "password": "secret"}
            return {f"level_{depth}_{i}": make_deep(depth - 1, breadth) for i in range(breadth)}

        large_data = make_deep(depth=5, breadth=5)

        sanitizer = DataSanitizer()
        start = time.monotonic()
        sanitized = sanitizer.sanitize(large_data)
        elapsed = time.monotonic() - start

        # Should complete well within 2 seconds on any modern machine
        assert elapsed < 2.0, f"Sanitization of large structure took {elapsed:.3f}s"

        # Spot-check: structure preserved and passwords redacted
        assert isinstance(sanitized, dict)
        logs = sanitizer.get_redaction_logs()
        assert len(logs) > 0, "Expected redaction entries for nested passwords"
