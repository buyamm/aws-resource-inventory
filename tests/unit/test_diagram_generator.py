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
    "aws_instance",
    "aws_ec2_instance",
    "not_a_registered_type",
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


def resource_appears_in_diagram(xml_content: str, arn: str) -> bool:
    """A resource appears as a UserObject vertex whose arn/tooltip attributes are the ARN."""
    root = ET.fromstring(xml_content)
    for obj in root.iter("UserObject"):
        cell = obj.find("mxCell")
        if obj.get("arn") == arn and obj.get("tooltip") == arn and cell is not None:
            if cell.get("vertex") == "1":
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
            specifications={"VpcId": "vpc-12345678", "CidrBlock": "10.0.0.0/16"},
            metadata=spec_metadata,
        )
        ec2 = ResourceSpec(
            resource_type="aws_instance",
            arn="arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0",
            region="us-east-1",
            account_id="123456789012",
            specifications={
                "InstanceId": "i-1234567890abcdef0",
                "VpcId": "vpc-12345678",
                "InstanceType": "t3.micro",
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
            specifications={
                "RoleName": "OrderProcessorRole",
                "Arn": "arn:aws:iam::123456789012:role/OrderProcessorRole",
            },
            metadata=spec_metadata,
        )
        dynamo = ResourceSpec(
            resource_type="aws_dynamodb_table",
            arn="arn:aws:dynamodb:us-east-1:123456789012:table/Orders",
            region="us-east-1",
            account_id="123456789012",
            specifications={"TableName": "Orders"},
            metadata=spec_metadata,
        )
        lambda_fn = ResourceSpec(
            resource_type="aws_lambda_function",
            arn="arn:aws:lambda:us-east-1:123456789012:function:OrderProcessor",
            region="us-east-1",
            account_id="123456789012",
            specifications={
                "FunctionName": "OrderProcessor",
                "Role": "arn:aws:iam::123456789012:role/OrderProcessorRole",
                "Environment": {"Variables": {"ORDERS_TABLE": "Orders"}},
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


# ============================================================================
# Task 17: stencils, edges, determinism, drawio-ai validation
# ============================================================================


def _vertex_styles(xml_content: str) -> dict[str, str]:
    root = ET.fromstring(xml_content)
    return {obj.get("arn"): obj.find("mxCell").get("style") for obj in root.iter("UserObject")}


class TestDiagramGeneratorStyles:
    vpc_and_ec2_specs = TestDiagramGeneratorUnitTests.vpc_and_ec2_specs
    serverless_specs = TestDiagramGeneratorUnitTests.serverless_specs

    def test_diagram_uses_aws4_stencils_req_6_4(self, vpc_and_ec2_specs):
        styles = _vertex_styles(DiagramGenerator().generate_diagram(vpc_and_ec2_specs))
        assert "resIcon=mxgraph.aws4.vpc" in styles[vpc_and_ec2_specs[0].arn]
        assert "resIcon=mxgraph.aws4.ec2" in styles[vpc_and_ec2_specs[1].arn]

    def test_diagram_edges_connect_vertices_req_6_4(self, serverless_specs):
        xml_output = DiagramGenerator().generate_diagram(serverless_specs)
        root = ET.fromstring(xml_output)
        ids = {obj.get("id"): obj.get("arn") for obj in root.iter("UserObject")}
        edges = [c for c in root.iter("mxCell") if c.get("edge") == "1"]
        assert {e.get("value") for e in edges} == {"iam_role_usage", "dynamodb_access"}
        for edge in edges:
            assert edge.get("source") in ids and edge.get("target") in ids
        all_ids = [e.get("id") for e in root.iter() if e.get("id")]
        assert len(all_ids) == len(set(all_ids)), "cell ids must be unique"

    def test_diagram_is_deterministic_req_6_4(self, serverless_specs):
        generator = DiagramGenerator()
        assert generator.generate_diagram(serverless_specs) == generator.generate_diagram(
            list(reversed(serverless_specs))
        )

    def test_diagram_validate_with_drawio_ai_skipped_when_missing_req_6_4(
        self, tmp_path, monkeypatch
    ):
        from src import diagram_generator as module

        monkeypatch.setattr(module.shutil, "which", lambda name: None)
        ok, message = module.validate_with_drawio_ai(tmp_path / "x.drawio")
        assert ok is None and "skipped" in message

    def test_diagram_validate_with_drawio_ai_runs_cli_req_6_4(self, tmp_path, monkeypatch):
        from unittest.mock import Mock

        from src import diagram_generator as module

        monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/local/bin/drawio-ai")
        run = Mock(return_value=Mock(returncode=0, stdout="valid", stderr=""))
        monkeypatch.setattr(module.subprocess, "run", run)
        ok, message = module.validate_with_drawio_ai(tmp_path / "x.drawio")
        assert ok is True and "valid" in message
        assert run.call_args.args[0] == [
            "/usr/local/bin/drawio-ai",
            "validate",
            str(tmp_path / "x.drawio"),
        ]
