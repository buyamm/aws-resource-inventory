"""
Unit and Property tests for DiagramGenerator (TDD RED and GREEN phases).

Requirements Coverage:
- Requirement 6.1: Identify relationships between resources
- Requirement 6.2: Detect common patterns (API Gateway + Lambda + DynamoDB, EC2 + VPC, etc.)
- Requirement 6.4: Create visual diagrams showing resource relationships using drawio XML
"""

import xml.etree.ElementTree as ET

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.diagram_generator import DiagramGenerator
from src.parser import ResourceSpec, SpecMetadata

# ============================================================================
# Hypothesis Strategies for Property 4
# ============================================================================

resource_types = [
    "aws_s3_bucket",
    "aws_ec2_instance",
    "aws_lambda_function",
    "aws_vpc",
    "aws_security_group",
    "aws_iam_role",
    "aws_dynamodb_table",
]

spec_metadata = SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "v1", "chk")

resource_spec_strategy = st.builds(
    ResourceSpec,
    resource_type=st.sampled_from(resource_types),
    arn=st.from_regex(r"arn:aws:[a-z0-9-]+:[a-z0-9-]+:123456789012:[a-z0-9_-]+", fullmatch=True),
    region=st.sampled_from(["us-east-1", "us-west-2", "eu-central-1"]),
    account_id=st.just("123456789012"),
    specifications=st.dictionaries(
        st.text(min_size=1, max_size=10), st.text(max_size=10), max_size=3
    ),
    metadata=st.just(spec_metadata),
    raw_response=st.none(),
)


# ============================================================================
# Helpers
# ============================================================================


def is_valid_drawio_xml(xml_content: str) -> bool:
    """Validate that XML string is well-formed draw.io XML."""
    if not xml_content.strip().startswith("<mxfile"):
        return False
    try:
        root = ET.fromstring(xml_content)
        return root.tag == "mxfile" and root.find(".//mxGraphModel") is not None
    except ET.ParseError:
        return False


def resource_appears_in_diagram(xml_content: str, arn_or_name: str) -> bool:
    """Check if a resource identifier appears in an mxCell vertex in the diagram."""
    root = ET.fromstring(xml_content)
    for cell in root.iter("mxCell"):
        value = cell.get("value", "")
        if arn_or_name in value:
            return True
    return False


# ============================================================================
# Property 4: Diagram Includes All Resources (Task 12.1 & 12.2)
# ============================================================================


class TestDiagramGeneratorPropertyTests:
    """Property tests for DiagramGenerator (Requirement 6.4)."""

    @given(st.lists(resource_spec_strategy, min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_property_diagram_includes_all_resources_req_6_4(
        self, specs: list[ResourceSpec]
    ) -> None:
        """
        Property 4: Diagram Includes All Resources (Requirement 6.4).

        For all non-empty lists of ResourceSpec objects, the generated diagram
        SHALL include every resource (by ARN or name).
        """
        generator = DiagramGenerator()
        xml_diagram = generator.generate_diagram(specs)

        assert is_valid_drawio_xml(xml_diagram)

        # Every resource must appear in the diagram
        for spec in specs:
            assert resource_appears_in_diagram(
                xml_diagram, spec.arn
            ), f"Resource {spec.arn} does not appear in generated diagram"


# ============================================================================
# Unit Tests (Task 12.1 & 12.3)
# ============================================================================


class TestDiagramGeneratorUnitTests:
    """Unit tests for diagram generator and relationship identification."""

    @pytest.fixture
    def vpc_and_ec2_specs(self) -> list[ResourceSpec]:
        """Provide VPC and EC2 instance specs connected by VPC ID."""
        vpc = ResourceSpec(
            resource_type="aws_vpc",
            arn="arn:aws:ec2:us-east-1:123456789012:vpc/vpc-12345678",
            region="us-east-1",
            account_id="123456789012",
            specifications={"vpc_id": "vpc-12345678", "cidr_block": "10.0.0.0/16"},
            metadata=spec_metadata,
        )
        ec2 = ResourceSpec(
            resource_type="aws_ec2_instance",
            arn="arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0",
            region="us-east-1",
            account_id="123456789012",
            specifications={
                "instance_id": "i-1234567890abcdef0",
                "vpc_id": "vpc-12345678",
                "instance_type": "t3.micro",
            },
            metadata=spec_metadata,
        )
        return [vpc, ec2]

    @pytest.fixture
    def serverless_specs(self) -> list[ResourceSpec]:
        """Provide Lambda and DynamoDB specs connected by role/table."""
        role = ResourceSpec(
            resource_type="aws_iam_role",
            arn="arn:aws:iam::123456789012:role/OrderProcessorRole",
            region="global",
            account_id="123456789012",
            specifications={"role_name": "OrderProcessorRole"},
            metadata=spec_metadata,
        )
        dynamo = ResourceSpec(
            resource_type="aws_dynamodb_table",
            arn="arn:aws:dynamodb:us-east-1:123456789012:table/Orders",
            region="us-east-1",
            account_id="123456789012",
            specifications={"table_name": "Orders"},
            metadata=spec_metadata,
        )
        lambda_fn = ResourceSpec(
            resource_type="aws_lambda_function",
            arn="arn:aws:lambda:us-east-1:123456789012:function:OrderProcessor",
            region="us-east-1",
            account_id="123456789012",
            specifications={
                "function_name": "OrderProcessor",
                "role": "arn:aws:iam::123456789012:role/OrderProcessorRole",
                "environment_variables": {"ORDERS_TABLE": "Orders"},
            },
            metadata=spec_metadata,
        )
        return [role, dynamo, lambda_fn]

    def test_diagram_generator_creates_valid_drawio_xml_req_6_4(
        self, vpc_and_ec2_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 6.4: Generator outputs valid drawio XML format."""
        generator = DiagramGenerator()
        xml_output = generator.generate_diagram(vpc_and_ec2_specs)

        assert is_valid_drawio_xml(xml_output)
        assert "<mxfile" in xml_output
        assert "</mxfile>" in xml_output

    def test_diagram_generator_shows_relationships_req_6_1(
        self, vpc_and_ec2_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 6.1: Diagram includes resource relationships."""
        generator = DiagramGenerator()
        relationships = generator.identify_relationships(vpc_and_ec2_specs)

        assert len(relationships) >= 1
        rel = relationships[0]
        assert "vpc" in rel.relationship_type.lower()
        assert rel.from_arn == vpc_and_ec2_specs[1].arn or rel.to_arn == vpc_and_ec2_specs[1].arn

        # Verify edge in generated diagram XML
        xml_output = generator.generate_diagram(vpc_and_ec2_specs)
        root = ET.fromstring(xml_output)
        edges = [cell for cell in root.iter("mxCell") if cell.get("edge") == "1"]
        assert len(edges) >= 1

    def test_diagram_generator_detects_common_patterns_req_6_2(
        self, serverless_specs: list[ResourceSpec]
    ) -> None:
        """Requirement 6.2: Detect common patterns (Lambda + DynamoDB + IAM Role)."""
        generator = DiagramGenerator()
        relationships = generator.identify_relationships(serverless_specs)

        rel_types = [r.relationship_type for r in relationships]
        # Should detect iam_role_usage and dynamodb_access
        assert any("role" in t.lower() for t in rel_types)
        assert any("dynamo" in t.lower() or "table" in t.lower() for t in rel_types)

    def test_diagram_generator_empty_specs(self) -> None:
        """Handles empty list gracefully."""
        generator = DiagramGenerator()
        xml_output = generator.generate_diagram([])
        assert is_valid_drawio_xml(xml_output)
