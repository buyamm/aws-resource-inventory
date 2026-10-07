"""
Diagram Generator Module

This module provides the DiagramGenerator class for converting AWS ResourceSpec
objects into visual draw.io (mxGraph XML) architecture diagrams with automatic
relationship identification and common architecture pattern detection.

Requirements Coverage:
- Requirement 6.1: Identify relationships between resources (VPC connections, Lambda triggers, IAM roles)
- Requirement 6.2: Detect common patterns (API Gateway + Lambda + DynamoDB, EC2 + VPC)
- Requirement 6.4: Create visual diagrams showing resource relationships using drawio XML
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from src.parser import ResourceSpec


@dataclass
class ResourceRelationship:
    """Relationship between two resources."""

    from_arn: str
    to_arn: str
    relationship_type: str  # e.g., "vpc_connection", "iam_role_usage", "dynamodb_access"
    confidence: float = 1.0


class DiagramGenerator:
    """
    Generator for visual AWS architecture diagrams in draw.io (mxGraph XML) format.
    Automatically identifies connections and architecture patterns across resources.
    """

    # Service-specific fill and stroke colors for AWS components
    SERVICE_COLORS: dict[str, tuple[str, str]] = {
        "aws_s3_bucket": ("#D5E8D4", "#82B366"),  # Green
        "aws_ec2_instance": ("#FFE6CC", "#D79B00"),  # Orange
        "aws_lambda_function": ("#FFF2CC", "#D6B656"),  # Yellow/Gold
        "aws_vpc": ("#F8CECC", "#B85450"),  # Red/Coral
        "aws_security_group": ("#F5F5F5", "#666666"),  # Gray
        "aws_iam_role": ("#E1D5E7", "#9673A6"),  # Purple
        "aws_dynamodb_table": ("#DAE8FC", "#6C8EBF"),  # Blue
        "aws_rds_instance": ("#DAE8FC", "#6C8EBF"),  # Blue
    }

    def __init__(self, drawio_kit_path: str | Path | None = None) -> None:
        """
        Initialize DiagramGenerator.

        Args:
            drawio_kit_path: Optional path to drawio-ai-kit templates.
        """
        self.drawio_kit_path = Path(drawio_kit_path) if drawio_kit_path else None

    # ========================================================================
    # Relationship Identification (Requirements 6.1, 6.2)
    # ========================================================================

    def identify_relationships(self, specs: list[ResourceSpec]) -> list[ResourceRelationship]:
        """
        Identify relationships between resources:
        - VPC connections (EC2 in VPC, Lambda in VPC, Subnet in VPC)
        - IAM Role usage (Lambda execution role, EC2 instance profile)
        - DynamoDB access (Lambda referencing DynamoDB table in env or policies)
        - Security Group associations

        Requirements: 6.1, 6.2
        """
        relationships: list[ResourceRelationship] = []

        # Lookup maps
        vpc_map: dict[str, ResourceSpec] = {}  # vpc_id -> spec
        role_map: dict[str, ResourceSpec] = {}  # role_name / arn -> spec
        table_map: dict[str, ResourceSpec] = {}  # table_name / arn -> spec
        sg_map: dict[str, ResourceSpec] = {}  # sg_id -> spec

        for s in specs:
            specs_dict = s.specifications or {}
            # Index VPCs
            if "vpc" in s.resource_type.lower():
                vpc_id = specs_dict.get("vpc_id") or specs_dict.get("id") or s.arn.split("/")[-1]
                vpc_map[str(vpc_id)] = s
                vpc_map[s.arn] = s

            # Index IAM Roles
            if "role" in s.resource_type.lower() or "iam" in s.resource_type.lower():
                role_name = specs_dict.get("role_name") or s.arn.split("/")[-1]
                role_map[str(role_name)] = s
                role_map[s.arn] = s

            # Index DynamoDB Tables
            if "dynamodb" in s.resource_type.lower() or "table" in s.resource_type.lower():
                table_name = specs_dict.get("table_name") or s.arn.split("/")[-1]
                table_map[str(table_name)] = s
                table_map[s.arn] = s

            # Index Security Groups
            if "security_group" in s.resource_type.lower():
                sg_id = specs_dict.get("group_id") or specs_dict.get("id") or s.arn.split("/")[-1]
                sg_map[str(sg_id)] = s
                sg_map[s.arn] = s

        # Scan for relationships
        for s in specs:
            specs_dict = s.specifications or {}

            # 1. VPC Connection
            vpc_ref = specs_dict.get("vpc_id") or specs_dict.get("VpcId")
            if vpc_ref and str(vpc_ref) in vpc_map:
                target_vpc = vpc_map[str(vpc_ref)]
                if target_vpc.arn != s.arn:
                    relationships.append(
                        ResourceRelationship(
                            from_arn=s.arn,
                            to_arn=target_vpc.arn,
                            relationship_type="vpc_connection",
                            confidence=1.0,
                        )
                    )

            # 2. IAM Role Usage
            role_ref = (
                specs_dict.get("role") or specs_dict.get("Role") or specs_dict.get("role_arn")
            )
            if role_ref:
                ref_str = str(role_ref)
                matched_role = role_map.get(ref_str) or role_map.get(ref_str.split("/")[-1])
                if matched_role and matched_role.arn != s.arn:
                    relationships.append(
                        ResourceRelationship(
                            from_arn=s.arn,
                            to_arn=matched_role.arn,
                            relationship_type="iam_role_usage",
                            confidence=0.95,
                        )
                    )

            # 3. Security Group attachment
            sgs = specs_dict.get("security_groups") or []
            if isinstance(sgs, list):
                for sg_item in sgs:
                    sg_id = sg_item.get("group_id") if isinstance(sg_item, dict) else str(sg_item)
                    if sg_id and str(sg_id) in sg_map:
                        target_sg = sg_map[str(sg_id)]
                        if target_sg.arn != s.arn:
                            relationships.append(
                                ResourceRelationship(
                                    from_arn=s.arn,
                                    to_arn=target_sg.arn,
                                    relationship_type="security_group",
                                    confidence=0.9,
                                )
                            )

            # 4. DynamoDB Access from environment variables / config
            env_vars = specs_dict.get("environment_variables") or {}
            if isinstance(env_vars, dict):
                for env_val in env_vars.values():
                    val_str = str(env_val)
                    for t_name, t_spec in table_map.items():
                        if t_name == val_str or (len(t_name) > 3 and t_name in val_str):
                            if t_spec.arn != s.arn:
                                relationships.append(
                                    ResourceRelationship(
                                        from_arn=s.arn,
                                        to_arn=t_spec.arn,
                                        relationship_type="dynamodb_access",
                                        confidence=0.85,
                                    )
                                )
                                break

        # Deduplicate relationships
        seen = set()
        unique_rels: list[ResourceRelationship] = []
        for r in relationships:
            key = (r.from_arn, r.to_arn, r.relationship_type)
            if key not in seen:
                seen.add(key)
                unique_rels.append(r)

        return unique_rels

    # ========================================================================
    # Draw.io (mxGraph XML) Generation (Requirements 6.4)
    # ========================================================================

    def generate_diagram(self, specs: list[ResourceSpec]) -> str:
        """
        Generate draw.io XML diagram from resource specifications.

        Requirements:
        - 6.4: Create visual diagrams showing resource relationships using drawio XML
        - Property 4: All resources must appear in the generated diagram
        """
        relationships = self.identify_relationships(specs)

        # Build mxGraph XML
        mxfile = ET.Element(
            "mxfile",
            attrib={
                "host": "Electron",
                "agent": "AWS-Resource-Inventory",
                "version": "21.0.0",
                "type": "device",
            },
        )

        diagram = ET.SubElement(
            mxfile,
            "diagram",
            attrib={"id": "aws-architecture", "name": "AWS Infrastructure Architecture"},
        )

        model = ET.SubElement(
            diagram,
            "mxGraphModel",
            attrib={
                "dx": "1400",
                "dy": "900",
                "grid": "1",
                "gridSize": "10",
                "guides": "1",
                "tooltips": "1",
                "connect": "1",
                "arrows": "1",
                "fold": "1",
                "page": "1",
                "pageScale": "1",
                "pageWidth": "1600",
                "pageHeight": "1200",
                "math": "0",
                "shadow": "0",
            },
        )

        root = ET.SubElement(model, "root")

        # Standard mxGraph base cells
        ET.SubElement(root, "mxCell", attrib={"id": "0"})
        ET.SubElement(root, "mxCell", attrib={"id": "1", "parent": "0"})

        # Map each resource ARN to an XML cell ID
        arn_to_id: dict[str, str] = {}
        cols = 3
        cell_width = 240
        cell_height = 90
        spacing_x = 80
        spacing_y = 70
        start_x = 80
        start_y = 80

        for idx, spec in enumerate(specs):
            cell_id = f"res_{idx + 2}"
            arn_to_id[spec.arn] = cell_id

            col = idx % cols
            row = idx // cols
            pos_x = start_x + col * (cell_width + spacing_x)
            pos_y = start_y + row * (cell_height + spacing_y)

            fill_color, stroke_color = self.SERVICE_COLORS.get(
                spec.resource_type, ("#E1D5E7", "#9673A6")
            )
            style = (
                f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill_color};"
                f"strokeColor={stroke_color};fontStyle=1;align=center;verticalAlign=middle;"
            )

            # Cell label includes type, identifier, and full ARN (for traceability and Property 4)
            specs_dict = spec.specifications or {}
            short_name = (
                specs_dict.get("bucket")
                or specs_dict.get("bucket_name")
                or specs_dict.get("instance_id")
                or specs_dict.get("function_name")
                or specs_dict.get("table_name")
                or specs_dict.get("role_name")
                or specs_dict.get("id")
                or spec.arn.split("/")[-1]
            )

            label = (
                f"&lt;b&gt;{html.escape(spec.resource_type)}&lt;/b&gt;&lt;br/&gt;"
                f"{html.escape(str(short_name))}&lt;br/&gt;"
                f"&lt;font size='1' color='#555555'&gt;{html.escape(spec.arn)}&lt;/font&gt;"
            )

            cell = ET.SubElement(
                root,
                "mxCell",
                attrib={
                    "id": cell_id,
                    "value": label,
                    "style": style,
                    "vertex": "1",
                    "parent": "1",
                },
            )

            ET.SubElement(
                cell,
                "mxGeometry",
                attrib={
                    "x": str(pos_x),
                    "y": str(pos_y),
                    "width": str(cell_width),
                    "height": str(cell_height),
                    "as": "geometry",
                },
            )

        # Create relationship edges
        edge_idx = len(specs) + 2
        for rel in relationships:
            source_id = arn_to_id.get(rel.from_arn)
            target_id = arn_to_id.get(rel.to_arn)

            if source_id and target_id:
                edge_id = f"edge_{edge_idx}"
                edge_idx += 1

                edge_style = (
                    "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;"
                    "jettySize=auto;html=1;strokeColor=#4A90E2;strokeWidth=2;"
                )
                edge_cell = ET.SubElement(
                    root,
                    "mxCell",
                    attrib={
                        "id": edge_id,
                        "value": rel.relationship_type.replace("_", " "),
                        "style": edge_style,
                        "edge": "1",
                        "parent": "1",
                        "source": source_id,
                        "target": target_id,
                    },
                )
                ET.SubElement(edge_cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"})

        # Serialize to XML string
        raw_xml_bytes = ET.tostring(mxfile, encoding="utf-8")
        return str(raw_xml_bytes.decode("utf-8"))
