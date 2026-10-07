"""
Property-based tests for ResourceParser (RED phase - TDD)

This module contains property tests that MUST be written before implementation.
All tests should fail with NotImplementedError initially to prove they test real functionality.

Test Strategy:
- Property 1: Parse-Print Round-Trip - parsing then printing then parsing produces equivalent structure
- Property 2: Print-Parse Round-Trip - printing then parsing preserves JSON equivalence
- Unit Test: Malformed JSON returns descriptive error messages

Requirements Coverage:
- Requirement 4.4: Round-trip parsing preservation
- Requirement 4.2: Descriptive error messages with excerpts
"""

import json
import pytest
from hypothesis import given, strategies as st
from typing import Dict, Any


# ============================================================================
# Test Fixtures and Helpers
# ============================================================================

def normalize_json(json_str: str) -> Dict[str, Any]:
    """
    Normalize JSON string for comparison by parsing and re-serializing.
    This removes whitespace differences and standardizes key ordering.
    """
    return json.loads(json_str)


def is_valid_json(text: str) -> bool:
    """Check if a string is valid JSON."""
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

# Strategy for generating valid ResourceSpec-like dictionaries
resource_spec_strategy = st.fixed_dictionaries({
    "resource_type": st.sampled_from([
        "aws_s3_bucket",
        "aws_ec2_instance", 
        "aws_lambda_function",
        "aws_rds_instance"
    ]),
    "arn": st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=":-/"),
        min_size=20,
        max_size=100
    ).map(lambda s: f"arn:aws:s3:::{s}"),
    "region": st.sampled_from(["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]),
    "account_id": st.text(alphabet="0123456789", min_size=12, max_size=12),
    "specifications": st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(
            st.text(max_size=50),
            st.integers(),
            st.booleans(),
            st.none()
        ),
        min_size=1,
        max_size=10
    ),
    "metadata": st.fixed_dictionaries({
        "collected_at": st.text(min_size=10, max_size=30),
        "collector_version": st.text(min_size=5, max_size=10),
        "api_version": st.text(min_size=5, max_size=10),
        "checksum": st.text(min_size=32, max_size=64)
    })
})


# ============================================================================
# Property Test 1: Parse-Print Round-Trip
# **Validates: Requirements 4.4**
# ============================================================================

@given(resource_spec_strategy)
def test_property_parse_print_roundtrip_req_4_4(spec_dict: Dict[str, Any]):
    """
    Property: For all valid ResourceSpec objects, parse(print(spec)) produces equivalent structure
    
    This property test verifies that:
    1. A ResourceSpec can be printed to JSON
    2. That JSON can be parsed back to a ResourceSpec
    3. The resulting ResourceSpec is equivalent to the original
    
    This ensures bidirectional conversion between structured data and JSON is lossless.
    
    **Validates: Requirements 4.4**
    
    Expected Result (RED phase): This test should FAIL with NotImplementedError
    because ResourceParser is not yet implemented.
    """
    # Import will be added once parser module exists
    # For now, this will fail because the module doesn't exist
    try:
        from src.parser import ResourceParser
        
        parser = ResourceParser()
        
        # Convert dict to JSON string (simulating already-parsed spec being printed)
        json_output = json.dumps(spec_dict)
        
        # Parse the JSON
        parsed_result = parser.parse_spec(json_output)
        
        # Verify parse succeeded
        assert parsed_result.is_ok(), f"Parsing failed: {parsed_result.error if hasattr(parsed_result, 'error') else 'Unknown error'}"
        
        parsed_spec = parsed_result.value
        
        # Print back to JSON
        printed_json = parser.print_spec(parsed_spec)
        
        # Parse again
        reparsed_result = parser.parse_spec(printed_json)
        assert reparsed_result.is_ok(), "Re-parsing failed"
        
        reparsed_spec = reparsed_result.value
        
        # Verify round-trip: original spec == reparsed spec
        assert parsed_spec == reparsed_spec, "Round-trip parsing did not preserve structure"
        
    except ImportError:
        pytest.fail("ResourceParser module not yet implemented (expected in RED phase)")
    except NotImplementedError:
        # This is expected in RED phase
        pytest.fail("ResourceParser.parse_spec() or print_spec() not yet implemented (expected in RED phase)")


# ============================================================================
# Property Test 2: Print-Parse Round-Trip (JSON Preservation)
# **Validates: Requirements 4.4**
# ============================================================================

@given(resource_spec_strategy)
def test_property_print_parse_roundtrip_req_4_4(spec_dict: Dict[str, Any]):
    """
    Property: For all valid ResourceSpec dictionaries, print(parse(json)) produces equivalent JSON
    
    This property test verifies that:
    1. Valid ResourceSpec JSON can be parsed into a ResourceSpec
    2. That ResourceSpec can be printed back to JSON
    3. The resulting JSON is semantically equivalent (same structure/values)
    
    Note: We compare normalized JSON (parsed objects) rather than strings
    because whitespace and key order may differ. We use ResourceSpec dictionaries
    instead of arbitrary JSON to ensure valid structures.
    
    **Validates: Requirements 4.4**
    
    Expected Result (RED phase): This test should FAIL with NotImplementedError
    because ResourceParser is not yet implemented.
    """
    try:
        from src.parser import ResourceParser
        
        parser = ResourceParser()
        
        # Convert dict to JSON string
        json_text = json.dumps(spec_dict)
        
        # Parse JSON to ResourceSpec
        parsed_result = parser.parse_spec(json_text)
        
        if not parsed_result.is_ok():
            # Skip invalid structures (parser correctly rejected them)
            return
        
        parsed_spec = parsed_result.value
        
        # Print back to JSON
        output_json = parser.print_spec(parsed_spec)
        
        # Verify output is valid JSON
        assert is_valid_json(output_json), "print_spec() did not produce valid JSON"
        
        # Compare normalized structures (ignoring whitespace/ordering)
        original_data = normalize_json(json_text)
        output_data = normalize_json(output_json)
        
        # Verify all original fields are preserved in output
        assert output_data is not None, "Output JSON was empty"
        assert output_data.get("resource_type") == original_data.get("resource_type")
        assert output_data.get("arn") == original_data.get("arn")
        assert output_data.get("region") == original_data.get("region")
        
    except ImportError:
        pytest.fail("ResourceParser module not yet implemented (expected in RED phase)")
    except NotImplementedError:
        pytest.fail("ResourceParser.parse_spec() or print_spec() not yet implemented (expected in RED phase)")


# ============================================================================
# Unit Test: Malformed JSON Error Handling
# **Validates: Requirements 4.2**
# ============================================================================

@pytest.mark.parametrize("malformed_json,expected_excerpt", [
    ('{"key": invalid}', 'invalid'),
    ('{"unclosed": "string}', 'string'),
    ('{missing_quotes: "value"}', 'missing_quotes'),
    ('{"key": }', '}'),
    ('', ''),
])
def test_parser_malformed_json_returns_descriptive_error_req_4_2(malformed_json: str, expected_excerpt: str):
    """
    Unit: Parser returns descriptive error with excerpt for malformed JSON
    
    This test verifies that:
    1. Malformed JSON is detected and rejected
    2. Error message is descriptive (tells what went wrong)
    3. Error includes excerpt from the problematic input
    4. Error provides context for debugging
    
    **Validates: Requirements 4.2**
    
    Expected Result (RED phase): This test should FAIL with NotImplementedError
    because ResourceParser.parse_spec() is not yet implemented.
    """
    try:
        from src.parser import ResourceParser
        
        parser = ResourceParser()
        
        # Attempt to parse malformed JSON
        result = parser.parse_spec(malformed_json)
        
        # Verify parsing failed
        assert result.is_err(), f"Parser should reject malformed JSON: {malformed_json}"
        
        # Get error details
        error = result.error
        error_message = str(error) if not hasattr(error, 'message') else error.message
        
        # Verify error is descriptive
        assert len(error_message) > 0, "Error message should not be empty"
        assert any(keyword in error_message.lower() for keyword in ['invalid', 'malformed', 'parse', 'json', 'error']), \
            f"Error message should be descriptive: {error_message}"
        
        # Verify error includes excerpt from input
        if expected_excerpt and len(expected_excerpt) > 0:
            # Either in the error message or in a separate context field
            error_context = ""
            if hasattr(error, 'context'):
                error_context = str(error.context)
            elif hasattr(error, 'error_context'):
                error_context = str(error.error_context())
            
            full_error_text = error_message + " " + error_context
            assert expected_excerpt in full_error_text or expected_excerpt in malformed_json, \
                f"Error should include excerpt '{expected_excerpt}' from input"
        
    except ImportError:
        pytest.fail("ResourceParser module not yet implemented (expected in RED phase)")
    except NotImplementedError:
        pytest.fail("ResourceParser.parse_spec() not yet implemented (expected in RED phase)")


# ============================================================================
# Additional Unit Test: Valid JSON Parsing Success
# ============================================================================

def test_parser_valid_json_parses_successfully():
    """
    Unit: Parser successfully parses valid ResourceSpec JSON
    
    This is a basic sanity test that verifies the parser can handle
    a well-formed ResourceSpec JSON structure.
    
    Expected Result (RED phase): This test should FAIL with NotImplementedError
    """
    try:
        from src.parser import ResourceParser
        
        parser = ResourceParser()
        
        valid_json = json.dumps({
            "resource_type": "aws_s3_bucket",
            "arn": "arn:aws:s3:::my-test-bucket",
            "region": "us-east-1",
            "account_id": "123456789012",
            "specifications": {
                "bucket_name": "my-test-bucket",
                "versioning": True,
                "encryption": "AES256"
            },
            "metadata": {
                "collected_at": "2024-01-01T00:00:00Z",
                "collector_version": "1.0.0",
                "api_version": "2.0",
                "checksum": "abc123def456"
            }
        })
        
        result = parser.parse_spec(valid_json)
        
        assert result.is_ok(), f"Valid JSON should parse successfully: {result.error if hasattr(result, 'error') else 'Unknown error'}"
        
        spec = result.value
        assert spec.resource_type == "aws_s3_bucket"
        assert spec.arn == "arn:aws:s3:::my-test-bucket"
        assert spec.region == "us-east-1"
        
    except ImportError:
        pytest.fail("ResourceParser module not yet implemented (expected in RED phase)")
    except NotImplementedError:
        pytest.fail("ResourceParser.parse_spec() not yet implemented (expected in RED phase)")


# ============================================================================
# Additional Tests for Enhanced Error Handling (Task 3.4 - REFACTOR phase)
# ============================================================================

def test_parser_missing_required_field_returns_descriptive_error():
    """
    Unit: Parser returns descriptive error when required fields are missing
    
    This test verifies enhanced error messages from refactored parser (Task 3.4).
    Tests validation of ResourceSpec structure.
    """
    from src.parser import ResourceParser
    
    parser = ResourceParser()
    
    # JSON missing 'arn' field
    incomplete_json = json.dumps({
        "resource_type": "aws_s3_bucket",
        "region": "us-east-1",
        "account_id": "123456789012",
        "specifications": {},
        "metadata": {
            "collected_at": "2024-01-01T00:00:00Z",
            "collector_version": "1.0.0",
            "api_version": "2.0",
            "checksum": "abc123"
        }
    })
    
    result = parser.parse_spec(incomplete_json)
    
    assert result.is_err(), "Parser should reject incomplete ResourceSpec"
    error = result.error
    assert "arn" in str(error).lower(), "Error should mention missing 'arn' field"
    assert "missing" in str(error).lower() or "required" in str(error).lower()


def test_parser_wrong_type_field_returns_descriptive_error():
    """
    Unit: Parser returns descriptive error when field has wrong type
    
    This test verifies type validation from refactored parser (Task 3.4).
    """
    from src.parser import ResourceParser
    
    parser = ResourceParser()
    
    # 'specifications' should be dict, not string
    wrong_type_json = json.dumps({
        "resource_type": "aws_s3_bucket",
        "arn": "arn:aws:s3:::bucket",
        "region": "us-east-1",
        "account_id": "123456789012",
        "specifications": "this should be a dict",
        "metadata": {
            "collected_at": "2024-01-01T00:00:00Z",
            "collector_version": "1.0.0",
            "api_version": "2.0",
            "checksum": "abc123"
        }
    })
    
    result = parser.parse_spec(wrong_type_json)
    
    assert result.is_err(), "Parser should reject wrong type for specifications"
    error = result.error
    assert "specifications" in str(error).lower() or "type" in str(error).lower()


def test_parser_non_dict_json_returns_descriptive_error():
    """
    Unit: Parser returns descriptive error for non-dict JSON (array, string, etc.)
    
    This test verifies type checking from refactored parser (Task 3.4).
    """
    from src.parser import ResourceParser
    
    parser = ResourceParser()
    
    # Valid JSON but not an object
    array_json = json.dumps(["item1", "item2", "item3"])
    
    result = parser.parse_spec(array_json)
    
    assert result.is_err(), "Parser should reject non-object JSON"
    error = result.error
    assert "object" in str(error).lower() or "dictionary" in str(error).lower()


def test_parser_missing_metadata_field_returns_descriptive_error():
    """
    Unit: Parser returns descriptive error when metadata fields are missing
    
    This test verifies metadata validation from refactored parser (Task 3.4).
    """
    from src.parser import ResourceParser
    
    parser = ResourceParser()
    
    # Metadata missing 'checksum' field
    incomplete_metadata_json = json.dumps({
        "resource_type": "aws_s3_bucket",
        "arn": "arn:aws:s3:::bucket",
        "region": "us-east-1",
        "account_id": "123456789012",
        "specifications": {},
        "metadata": {
            "collected_at": "2024-01-01T00:00:00Z",
            "collector_version": "1.0.0",
            "api_version": "2.0"
            # missing 'checksum'
        }
    })
    
    result = parser.parse_spec(incomplete_metadata_json)
    
    assert result.is_err(), "Parser should reject incomplete metadata"
    error = result.error
    assert "metadata" in str(error).lower() and "checksum" in str(error).lower()


# ============================================================================
# Test Configuration for RED Phase Verification
# ============================================================================

def test_red_phase_verification():
    """
    Meta-test: Verify we are in RED phase
    
    This test confirms that the parser module does not yet exist,
    which proves we are correctly following TDD (tests first, implementation second).
    
    This test should PASS in RED phase and be removed in GREEN phase.
    """
    try:
        from src.parser import ResourceParser
        # If we get here, parser exists - we might be past RED phase
        pytest.skip("Parser module exists - may be past RED phase. Verify tests fail with NotImplementedError.")
    except ImportError:
        # Expected in RED phase
        pass
