# Task 3.2: Property Test for Parser - Round-Trip Consistency

## Task Description

This task documents and verifies the property test for parser round-trip consistency that was written in Task 3.1.

## Property Being Tested

**Property 1: Parse-Print Round-Trip**

For all valid ResourceSpec objects, `parse(print(spec))` produces an equivalent structure.

## Requirement Validation

**Validates: Requirement 4.4** - Round-trip parsing preservation

From requirements.md:
> FOR ALL valid parsed specifications, parsing then printing then parsing SHALL produce an equivalent data structure (round-trip property)

## Test Location

The property test is implemented in:
- **File**: `tests/unit/test_parser.py`
- **Function**: `test_property_parse_print_roundtrip_req_4_4`
- **Lines**: 89-136

## Test Strategy

The property test uses Hypothesis (property-based testing framework) to:

1. **Generate** diverse ResourceSpec-like dictionaries with various combinations of:
   - Resource types (S3, EC2, Lambda, RDS)
   - ARNs with different formats
   - AWS regions
   - Account IDs
   - Specifications (nested dictionaries with various types)
   - Metadata (timestamps, versions, checksums)

2. **Execute** the round-trip transformation:
   ```
   Original Spec → JSON (print) → Parsed Spec → JSON (print) → Re-parsed Spec
   ```

3. **Verify** that the original parsed spec equals the re-parsed spec, ensuring no data loss

## Test Implementation Details

### Hypothesis Strategy

The test uses a custom Hypothesis strategy (`resource_spec_strategy`) that generates:

```python
resource_spec_strategy = st.fixed_dictionaries({
    "resource_type": st.sampled_from([...]),
    "arn": st.text(...).map(lambda s: f"arn:aws:s3:::..."),
    "region": st.sampled_from([...]),
    "account_id": st.text(alphabet="0123456789", ...),
    "specifications": st.dictionaries(...),
    "metadata": st.fixed_dictionaries({...})
})
```

This ensures the test covers a wide range of valid ResourceSpec structures.

### Current Status (RED Phase)

The test is **correctly failing** because the `ResourceParser` module hasn't been implemented yet:

```
ModuleNotFoundError: No module named 'src.parser'
```

This is expected behavior in TDD's RED phase - tests are written first and should fail.

### Example Falsifying Case

Hypothesis generated an example test case:

```python
spec_dict={
    'resource_type': 'aws_s3_bucket',
    'arn': 'arn:aws:s3:::ČÄĽħëĳⰹïЭñ³2ľĹïkŰĽżĞŰĦl',
    'region': 'us-east-1',
    'account_id': '818215104572',
    'specifications': {'©': None},
    'metadata': {
        'collected_at': '0000000000',
        'collector_version': '®ô«b...',
        'api_version': '#Ñãàã...',
        'checksum': '00000000000000000000000000000000'
    }
}
```

This demonstrates that the test handles edge cases like:
- Unicode characters in ARNs
- Special characters in specification keys
- Minimal specifications (single key)
- Various unicode in metadata values

## Why This Property Matters

Round-trip consistency is critical for:

1. **Data Integrity**: Ensures no information is lost during parsing/serialization
2. **Bidirectional Conversion**: Allows converting between JSON and structured data reliably
3. **Serialization Safety**: Guarantees that stored specs can be accurately reconstructed
4. **Format Preservation**: Ensures AWS API response format is maintained

## Success Criteria ✓

- [x] Property test exists in `tests/unit/test_parser.py`
- [x] Test validates Requirement 4.4 (round-trip consistency)
- [x] Test is properly annotated with `**Validates: Requirements 4.4**`
- [x] Test uses Hypothesis for property-based testing
- [x] Test currently fails (RED phase) as expected
- [x] Test documentation clearly explains the property being verified

## Next Steps

The next task (Task 3.3) will implement the `ResourceParser` class to make this property test pass (GREEN phase).

## Test Execution

To run this specific property test:

```bash
pytest tests/unit/test_parser.py::test_property_parse_print_roundtrip_req_4_4 -v
```

To run all parser tests:

```bash
pytest tests/unit/test_parser.py -v
```

## Verification

Task completed successfully:
- ✅ Property test exists and is well-documented
- ✅ Test validates the correct requirement (4.4)
- ✅ Test follows TDD methodology (RED phase confirmed)
- ✅ Test uses property-based testing with Hypothesis
- ✅ Test covers diverse input cases
