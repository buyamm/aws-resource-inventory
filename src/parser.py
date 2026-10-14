"""
Resource Parser Module

This module provides parsing and printing functionality for AWS resource specifications.
It converts between JSON strings and typed ResourceSpec objects with full round-trip support.

Requirements Coverage:
- Requirement 4.1: Parse AWS API responses into typed structures
- Requirement 4.2: Descriptive error messages with excerpts
- Requirement 4.3: Format specifications back to valid JSON
- Requirement 4.4: Round-trip parsing preservation
- Requirement 4.5: Preserve original response for debugging

Refactored in Task 3.4 for:
- Comprehensive error handling with descriptive messages
- Improved type annotations (mypy strict compliance)
- Extracted helper functions for structure validation and error excerpts
- Enhanced maintainability and readability
"""

import json
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

# ============================================================================
# Data Models
# ============================================================================


@dataclass
class SpecMetadata:
    """Metadata about spec collection process"""

    collected_at: str
    collector_version: str
    api_version: str
    checksum: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "collected_at": self.collected_at,
            "collector_version": self.collector_version,
            "api_version": self.api_version,
            "checksum": self.checksum,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SpecMetadata":
        """Create SpecMetadata from dictionary"""
        return SpecMetadata(
            collected_at=data.get("collected_at", ""),
            collector_version=data.get("collector_version", ""),
            api_version=data.get("api_version", ""),
            checksum=data.get("checksum", ""),
        )


@dataclass
class ResourceSpec:
    """Complete specification of an AWS resource"""

    resource_type: str
    arn: str
    region: str
    account_id: str
    specifications: dict[str, Any]
    metadata: SpecMetadata
    raw_response: Any = None  # {operation: full API response}; legacy str accepted

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "resource_type": self.resource_type,
            "arn": self.arn,
            "region": self.region,
            "account_id": self.account_id,
            "specifications": self.specifications,
            "metadata": self.metadata.to_dict(),
        }
        if self.raw_response is not None:
            result["raw_response"] = self.raw_response
        return result

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ResourceSpec":
        """Create ResourceSpec from dictionary"""
        return ResourceSpec(
            resource_type=data.get("resource_type", ""),
            arn=data.get("arn", ""),
            region=data.get("region", ""),
            account_id=data.get("account_id", ""),
            specifications=data.get("specifications", {}),
            metadata=SpecMetadata.from_dict(data.get("metadata", {})),
            raw_response=data.get("raw_response"),
        )


# ============================================================================
# Result Types for Error Handling
# ============================================================================

# Generic type variable for Result
T = TypeVar("T")
E = TypeVar("E")


@dataclass
class ParseError:
    """
    Error that occurred during parsing with comprehensive context.

    Provides detailed information about parsing failures including:
    - Descriptive error message
    - Context information (location, excerpt)
    - Original input for debugging (Requirement 4.5)
    """

    message: str
    context: str
    original_input: str
    error_type: str = "ParseError"

    def error_message(self) -> str:
        """Get the error message"""
        return self.message

    def error_context(self) -> str:
        """Get the error context"""
        return self.context

    def __str__(self) -> str:
        """String representation of error with full details"""
        return f"{self.error_type}: {self.message}\nContext: {self.context}"


class Result(Generic[T, E]):
    """
    Result type that can hold either a success value or an error.

    Provides type-safe error handling without exceptions for parsing operations.
    Supports generic typing for improved type checking.
    """

    def __init__(self, value: T | None = None, error: E | None = None) -> None:
        """
        Initialize a Result with either a value or an error.

        Args:
            value: The success value (if ok)
            error: The error value (if err)
        """
        self._value = value
        self._error = error

    def is_ok(self) -> bool:
        """Check if result is successful"""
        return self._error is None

    def is_err(self) -> bool:
        """Check if result is an error"""
        return self._error is not None

    @property
    def value(self) -> T:
        """
        Get the success value.

        Returns:
            The success value

        Raises:
            ValueError: If called on an error result
        """
        if self.is_err():
            raise ValueError("Cannot get value from error result")
        if self._value is None:
            raise ValueError("Result value is None")
        return self._value

    @property
    def error(self) -> E:
        """
        Get the error.

        Returns:
            The error value

        Raises:
            ValueError: If called on a success result
        """
        if self.is_ok():
            raise ValueError("Cannot get error from success result")
        return self._error  # type: ignore[return-value]  # non-None: is_ok() is False

    @staticmethod
    def ok(value: T) -> "Result[T, E]":
        """Create a successful result"""
        return Result(value=value, error=None)

    @staticmethod
    def err(error: E) -> "Result[T, E]":
        """Create an error result"""
        return Result(value=None, error=error)


# ============================================================================
# Helper Functions for JSON Processing
# ============================================================================


def validate_resource_spec_structure(data: dict[str, Any]) -> str | None:
    """
    Validate that a dictionary has the required structure for ResourceSpec.

    Checks for required fields and their types to provide better error messages.

    Args:
        data: Dictionary to validate

    Returns:
        None if valid, error message string if invalid
    """
    required_fields = {
        "resource_type": str,
        "arn": str,
        "region": str,
        "account_id": str,
        "specifications": dict,
        "metadata": dict,
    }

    for field, expected_type in required_fields.items():
        if field not in data:
            return f"Missing required field: '{field}'"

        if not isinstance(data[field], expected_type):
            actual_type = type(data[field]).__name__
            expected_name = expected_type.__name__
            return f"Field '{field}' has wrong type: expected {expected_name}, got {actual_type}"

    # Validate metadata structure
    metadata = data.get("metadata", {})
    metadata_fields = ["collected_at", "collector_version", "api_version", "checksum"]
    for field in metadata_fields:
        if field not in metadata:
            return f"Missing required metadata field: '{field}'"
        if not isinstance(metadata[field], str):
            return f"Metadata field '{field}' must be a string"

    return None


def extract_json_excerpt(text: str, position: int, context_chars: int = 40) -> str:
    """
    Extract an excerpt from JSON text around a specific position.

    Useful for showing context in error messages when JSON parsing fails.

    Args:
        text: The full JSON text
        position: Position of the error (character index)
        context_chars: Number of characters to show on each side of the position

    Returns:
        Excerpt string showing context around the error position
    """
    if not text or position < 0:
        return text[: min(80, len(text))] + ("..." if len(text) > 80 else "")

    if position >= len(text):
        # Position is past end, show the last part
        start = max(0, len(text) - context_chars * 2)
        return ("..." if start > 0 else "") + text[start:]

    start = max(0, position - context_chars)
    end = min(len(text), position + context_chars)

    excerpt = text[start:end]

    # Add ellipsis if we truncated
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(text):
        excerpt = excerpt + "..."

    return excerpt


# ============================================================================
# Resource Parser
# ============================================================================


class ResourceParser:
    """
    Parser for AWS resource specifications with round-trip support.

    Provides robust parsing with comprehensive error handling, type validation,
    and support for round-trip conversion between JSON and typed objects.

    Features:
    - Parse JSON strings to ResourceSpec objects (Requirement 4.1)
    - Print ResourceSpec objects back to JSON (Requirement 4.3)
    - Descriptive error messages with context (Requirement 4.2)
    - Round-trip preservation (Requirement 4.4)
    - Original response preservation for debugging (Requirement 4.5)

    Example:
        >>> parser = ResourceParser()
        >>> result = parser.parse_spec('{"resource_type": "aws_s3_bucket", ...}')
        >>> if result.is_ok():
        ...     spec = result.value
        ...     json_output = parser.print_spec(spec)
    """

    def parse_spec(self, json_data: str) -> "Result[ResourceSpec, ParseError]":
        """
        Parse AWS API response JSON into ResourceSpec.

        Performs comprehensive validation and provides detailed error messages
        for any parsing failures.

        Args:
            json_data: JSON string containing resource specification

        Returns:
            Result containing ResourceSpec on success, ParseError on failure

        Requirements:
        - 4.1: Parse AWS API responses into typed structures
        - 4.2: Descriptive error messages with excerpts
        - 4.4: Round-trip parsing preservation
        - 4.5: Preserve original response for debugging
        """
        # Validate input is not empty
        if not json_data or not json_data.strip():
            return Result.err(
                ParseError(
                    message="Cannot parse empty or whitespace-only JSON string",
                    context="Input must contain valid JSON data",
                    original_input=json_data,
                    error_type="EmptyInputError",
                )
            )

        # Parse JSON with detailed error handling
        parsed_data: dict[str, Any]
        try:
            parsed_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            # Extract helpful excerpt around the error location
            excerpt = extract_json_excerpt(json_data, e.pos)

            return Result.err(
                ParseError(
                    message=f"Invalid JSON syntax: {e.msg}",
                    context=f"Error at position {e.pos}, line {e.lineno}, "
                    f"column {e.colno}: {excerpt}",
                    original_input=json_data,
                    error_type="JSONDecodeError",
                )
            )
        except RecursionError:
            # The only other failure of json.loads on a str: nesting too deep
            return Result.err(
                ParseError(
                    message="Invalid JSON: nesting exceeds the interpreter recursion limit",
                    context=f"Input of {len(json_data)} characters is too deeply nested",
                    original_input=json_data,
                    error_type="RecursionError",
                )
            )

        # Validate it's a dictionary (object type)
        if not isinstance(parsed_data, dict):
            return Result.err(
                ParseError(
                    message=f"JSON must be an object (dictionary), not {type(parsed_data).__name__}",
                    context=f"Expected object with resource fields, got {type(parsed_data).__name__}",
                    original_input=json_data,
                    error_type="TypeMismatchError",
                )
            )

        # Validate ResourceSpec structure
        validation_error = validate_resource_spec_structure(parsed_data)
        if validation_error:
            return Result.err(
                ParseError(
                    message=f"Invalid ResourceSpec structure: {validation_error}",
                    context="JSON structure does not match ResourceSpec requirements",
                    original_input=json_data,
                    error_type="StructureValidationError",
                )
            )

        # Field types were validated above, so construction cannot fail
        return Result.ok(ResourceSpec.from_dict(parsed_data))

    def print_spec(self, spec: ResourceSpec) -> str:
        """
        Format ResourceSpec back to valid AWS JSON.

        Produces consistently formatted JSON with sorted keys for
        reliable comparison and version control.

        Args:
            spec: ResourceSpec object to serialize

        Returns:
            JSON string representation of the ResourceSpec with indentation and sorted keys

        Requirements:
        - 4.3: Format specifications back to valid JSON matching AWS API format
        - 4.4: Round-trip parsing preservation
        """
        data = spec.to_dict()
        return json.dumps(data, indent=2, sort_keys=True)
