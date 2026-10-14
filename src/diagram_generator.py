"""
Diagram Generator Module

Generates draw.io (mxGraph XML) architecture diagrams from collected specs and the
relationships found by the Analysis_Engine. Vertices use the native
``mxgraph.aws4.*`` stencils (the catalog used by drawio-ai-kit); validation with
the drawio-ai-kit CLI is optional.

Requirements Coverage:
- Requirement 6.1: Relationships are drawn as edges
- Requirement 6.4: Valid .drawio file, one vertex per resource (UserObject with
  ``arn`` and ``tooltip`` = ARN), aws4 stencil styles
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from src.analysis_engine import AnalysisEngine, ResourceRelationship
from src.parser import ResourceSpec
from src.resource_types import GLOBAL_REGION, REGISTRY, canonical_type, resource_id

__all__ = ["DiagramGenerator", "ResourceRelationship", "validate_with_drawio_ai"]

FALLBACK_STYLE = "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#666666;"
EDGE_STYLE = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;fontSize=10;"
REGION_LABEL_STYLE = "text;html=1;fontSize=14;fontStyle=1;align=left;verticalAlign=middle;"

ICON_SIZE = 60
COLUMN_WIDTH = 260
ROW_HEIGHT = 130
MARGIN = 40
TYPE_ORDER = {type_id: index for index, type_id in enumerate(REGISTRY)}


def _cell_id(prefix: str, *parts: str) -> str:
    return (
        f"{prefix}-"
        + hashlib.sha1("|".join(parts).encode("utf-8"), usedforsecurity=False).hexdigest()[:12]
    )


class DiagramGenerator:
    """Builds deterministic draw.io diagrams."""

    def __init__(self, drawio_kit_path: str | Path | None = None) -> None:
        # Kept for API compatibility; styles come from the resource type registry.
        self.drawio_kit_path = Path(drawio_kit_path) if drawio_kit_path else None

    def identify_relationships(self, specs: list[ResourceSpec]) -> list[ResourceRelationship]:
        """Relationships drawn as edges (delegates to the Analysis_Engine rules)."""
        return AnalysisEngine().identify_relationships(specs)

    def generate_diagram(
        self,
        specs: list[ResourceSpec],
        relationships: list[ResourceRelationship] | None = None,
    ) -> str:
        """Return the .drawio XML for ``specs``; relationships are computed when omitted."""
        unique: dict[str, ResourceSpec] = {}
        for spec in specs:
            unique.setdefault(spec.arn, spec)
        ordered = sorted(
            unique.values(),
            key=lambda s: (
                s.region != GLOBAL_REGION,
                s.region or GLOBAL_REGION,
                TYPE_ORDER.get(canonical_type(s.resource_type) or "", len(TYPE_ORDER)),
                s.resource_type,
                s.arn,
            ),
        )
        if relationships is None:
            relationships = self.identify_relationships(ordered)

        mxfile = ET.Element("mxfile", host="aws-resource-inventory", type="device")
        diagram = ET.SubElement(mxfile, "diagram", id="architecture", name="AWS Architecture")
        model = ET.SubElement(
            diagram,
            "mxGraphModel",
            grid="1",
            gridSize="10",
            page="1",
            pageWidth="1600",
            pageHeight="1200",
            math="0",
            shadow="0",
        )
        root = ET.SubElement(model, "root")
        _sub(root, "mxCell", id="0")
        _sub(root, "mxCell", id="1", parent="0")

        regions = list(dict.fromkeys(s.region or GLOBAL_REGION for s in ordered))
        vertex_ids: dict[str, str] = {}
        for column, region in enumerate(regions):
            x = MARGIN + column * COLUMN_WIDTH
            label = _sub(
                root,
                "mxCell",
                id=_cell_id("region", region),
                value=region,
                style=REGION_LABEL_STYLE,
                vertex="1",
                parent="1",
            )
            _sub(
                label,
                "mxGeometry",
                x=str(x),
                y=str(MARGIN),
                width="200",
                height="30",
                **{"as": "geometry"},
            )
            in_region = [s for s in ordered if (s.region or GLOBAL_REGION) == region]
            for row, spec in enumerate(in_region):
                vertex_id = _cell_id("res", spec.arn)
                vertex_ids[spec.arn] = vertex_id
                info = REGISTRY.get(canonical_type(spec.resource_type) or "")
                obj = _sub(
                    root,
                    "UserObject",
                    id=vertex_id,
                    label=f"<b>{_escape(spec.resource_type)}</b><br/>{_escape(resource_id(spec))}",
                    tooltip=spec.arn,
                    arn=spec.arn,
                )
                cell = _sub(
                    obj,
                    "mxCell",
                    style=info.drawio_style if info else FALLBACK_STYLE,
                    vertex="1",
                    parent="1",
                )
                _sub(
                    cell,
                    "mxGeometry",
                    x=str(x + 70),
                    y=str(MARGIN + 50 + row * ROW_HEIGHT),
                    width=str(ICON_SIZE),
                    height=str(ICON_SIZE),
                    **{"as": "geometry"},
                )

        for rel in sorted(relationships, key=lambda r: (r.from_arn, r.to_arn, r.relationship_type)):
            source, target = vertex_ids.get(rel.from_arn), vertex_ids.get(rel.to_arn)
            if source is None or target is None:
                continue
            edge = _sub(
                root,
                "mxCell",
                id=_cell_id("edge", rel.from_arn, rel.to_arn, rel.relationship_type),
                value=rel.relationship_type,
                style=EDGE_STYLE,
                edge="1",
                parent="1",
                source=source,
                target=target,
            )
            _sub(edge, "mxGeometry", relative="1", **{"as": "geometry"})

        ET.indent(mxfile)
        return ET.tostring(mxfile, encoding="unicode")

    def write_diagram(
        self,
        specs: list[ResourceSpec],
        path: str | Path,
        relationships: list[ResourceRelationship] | None = None,
    ) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.generate_diagram(specs, relationships), encoding="utf-8")
        return target


def _sub(element: ET.Element, tag: str, **attributes: str) -> ET.Element:
    """SubElement with attributes given as a dict (attribute names like 'parent' or 'as')."""
    return ET.SubElement(element, tag, attributes)


def _escape(text: str) -> str:
    # ElementTree escapes attribute values; only the HTML label markup needs care.
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def validate_with_drawio_ai(path: str | Path) -> tuple[bool | None, str]:
    """
    Validate a diagram with the drawio-ai-kit CLI (``drawio-ai validate``).

    Returns (None, message) when the CLI is not installed, otherwise (passed, output).
    """
    executable = shutil.which("drawio-ai")
    if executable is None:
        return None, "drawio-ai CLI not found on PATH; validation skipped"
    result = subprocess.run(  # noqa: S603 - fixed executable and arguments
        [executable, "validate", str(path)], capture_output=True, text=True, check=False
    )
    output = f"{result.stdout}{result.stderr}".strip()
    return result.returncode == 0, output
