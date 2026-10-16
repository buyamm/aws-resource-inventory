"""
Diagram Generator Module

Generates draw.io (mxGraph XML) architecture diagrams from collected specs and the
relationships found by the Analysis_Engine, following the vendored
``aws-architecture-diagram`` and ``drawio`` skills deterministically: nested
AWS Cloud -> Region -> VPC -> Availability Zone -> subnet containers, a left-to-right
data flow, verified ``mxgraph.aws4.*`` stencils, a title block and a background.

Nothing is guessed: containers come from subnet/VPC specs, placement from
``subnet_placement`` relationships, edges from relationships (each edge keeps the
relationship types and citations it was drawn from), labels from Name tags or spec
fields.

Requirements Coverage:
- Requirement 6.4: Valid .drawio file, every resource present (``arns`` metadata),
  aws4 stencil styles
- Requirement 15.1: Containers, placement in the subnet named by the spec, edge
  services left of the VPC
- Requirement 15.2: Data-flow edges only
- Requirement 15.3: Grouping of identical resources, supporting resources panel,
  human labels
- Requirement 15.4: Overview and Network detail pages, deterministic layout, PNG export
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.analysis_engine import AnalysisEngine, ResourceRelationship
from src.integrity import resolve_property_path
from src.parser import ResourceSpec
from src.resource_types import GLOBAL_REGION, REGISTRY, canonical_type, resource_id

__all__ = ["DiagramGenerator", "ResourceRelationship", "export_png", "validate_with_drawio_ai"]

OVERVIEW_PAGE = "Overview"
NETWORK_PAGE = "Network detail"

# Layout grid (aws-architecture-diagram skill: 78px icons, >= 220px between icon centers).
ICON = 78
SLOT_W = 160
SLOT_H = 130
GAP = 60
GROUP_PAD = (50, 30, 30, 30)  # top (label), right, bottom, left
MARGIN = 40
TITLE_H = 70
SUPPORT_COLUMNS = 8
MAX_LABEL = 30

# Group styles from the skill's verified group table (container=1 for nesting).
_GROUP_BASE = (
    "points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],"
    "[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;"
    "gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;container=1;dropTarget=1;"
    "pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;"
    "fillColor=none;verticalAlign=top;align=left;spacingLeft=30;"
)


def _group_style(gr_icon: str, stroke: str, font: str, dashed: bool, bold: bool) -> str:
    return (
        f"{_GROUP_BASE}grIcon=mxgraph.aws4.{gr_icon};strokeColor={stroke};fontColor={font};"
        f"dashed={int(dashed)};fontStyle={int(bold)};"
    )


CLOUD_STYLE = _group_style("group_aws_cloud_alt", "#232F3E", "#232F3E", False, True)
REGION_STYLE = _group_style("group_region", "#00A4A6", "#147EBA", True, True)
VPC_STYLE = _group_style("group_vpc", "#8C4FFF", "#8C4FFF", False, True)
PUBLIC_SUBNET_STYLE = _group_style("group_security_group", "#7AA116", "#248814", False, False)
PRIVATE_SUBNET_STYLE = _group_style("group_security_group", "#147EBA", "#147EBA", False, False)
AZ_STYLE = (
    "fillColor=none;strokeColor=#007FAA;dashed=1;verticalAlign=top;align=center;fontStyle=1;"
    "fontColor=#007FAA;whiteSpace=wrap;html=1;container=1;dropTarget=1;collapsible=0;"
    "recursiveResize=0;"
)
PANEL_STYLE = (
    "fillColor=none;strokeColor=#5A6C86;dashed=1;verticalAlign=top;align=left;spacingLeft=10;"
    "fontStyle=0;fontColor=#5A6C86;whiteSpace=wrap;html=1;container=1;dropTarget=1;"
    "collapsible=0;recursiveResize=0;"
)
USERS_STYLE = (
    "sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor=#232F3D;"
    "strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;"
    "html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.users;"
)
FALLBACK_STYLE = (
    "sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor=#232F3E;strokeColor=#ffffff;"
    "dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;"
    "fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;"
    "resIcon=mxgraph.aws4.general_AWScloud;"
)
BACKGROUND_STYLE = "rounded=0;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=none;"
TITLE_STYLE = (
    "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=14;spacing=8;"
)
EDGE_BASE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
    "strokeWidth=2;strokeColor=#545B64;endArrow=block;endFill=1;"
)

DISPLAY_NAMES = {
    "aws_instance": "EC2 instance",
    "aws_vpc": "VPC",
    "aws_security_group": "Security group",
    "aws_lambda_function": "Lambda function",
    "aws_db_instance": "RDS instance",
    "aws_cloudwatch_log_group": "Log group",
    "aws_sfn_state_machine": "Step Functions",
    "aws_dynamodb_table": "DynamoDB table",
    "aws_s3_bucket": "S3 bucket",
    "aws_iam_role": "IAM role",
    "aws_subnet": "Subnet",
    "aws_route_table": "Route table",
    "aws_internet_gateway": "Internet gateway",
    "aws_nat_gateway": "NAT gateway",
    "aws_vpc_endpoint": "VPC endpoint",
    "aws_cloudfront_distribution": "CloudFront",
    "aws_lb": "Load balancer",
    "aws_lb_listener": "Listener",
    "aws_lb_target_group": "Target group",
    "aws_route53_zone": "Route 53 zone",
    "aws_acm_certificate": "ACM certificate",
    "aws_wafv2_web_acl": "WAF web ACL",
    "aws_ecs_cluster": "ECS cluster",
    "aws_ecs_service": "ECS service",
    "aws_ecs_task_definition": "Task definition",
    "aws_ecr_repository": "ECR repository",
    "aws_autoscaling_group": "Auto Scaling group",
    "aws_launch_template": "Launch template",
    "aws_elasticache_replication_group": "ElastiCache",
    "aws_sqs_queue": "SQS queue",
    "aws_sns_topic": "SNS topic",
    "aws_cloudwatch_event_rule": "EventBridge rule",
    "aws_scheduler_schedule": "Schedule",
}

# Spec fields naming a resource when it has no Name tag (dotted path, list index allowed).
NAME_FIELDS = {
    "aws_lb": "LoadBalancerName",
    "aws_lb_target_group": "TargetGroupName",
    "aws_ecs_service": "serviceName",
    "aws_route53_zone": "Name",
    "aws_cloudfront_distribution": "DistributionConfig.Aliases.Items[0]",
    "aws_wafv2_web_acl": "Name",
    "aws_security_group": "GroupName",
    "aws_acm_certificate": "DomainName",
}

# Overview: resources that support the flow but are not part of it (one icon per type).
SUPPORT_TYPES = (
    "aws_iam_role",
    "aws_cloudwatch_log_group",
    "aws_security_group",
    "aws_route_table",
    "aws_lb_listener",
    "aws_lb_target_group",
    "aws_acm_certificate",
    "aws_ecs_cluster",
    "aws_ecs_task_definition",
    "aws_ecr_repository",
    "aws_launch_template",
)
EDGE_TYPES = ("aws_route53_zone", "aws_wafv2_web_acl", "aws_cloudfront_distribution")
CONTAINER_TYPES = ("aws_vpc", "aws_subnet")
NETWORK_TYPES = (
    "aws_internet_gateway",
    "aws_nat_gateway",
    "aws_vpc_endpoint",
    "aws_route_table",
    "aws_security_group",
)

# Left-to-right order: triggers, entry, compute, messaging, data.
LAYERS = {
    "aws_cloudwatch_event_rule": 0,
    "aws_scheduler_schedule": 0,
    "aws_lb": 1,
    "aws_nat_gateway": 1,
    "aws_internet_gateway": 1,
    "aws_instance": 2,
    "aws_autoscaling_group": 2,
    "aws_ecs_service": 2,
    "aws_lambda_function": 2,
    "aws_sfn_state_machine": 2,
    "aws_sns_topic": 3,
    "aws_sqs_queue": 3,
    "aws_vpc_endpoint": 3,
    "aws_db_instance": 4,
    "aws_elasticache_replication_group": 4,
    "aws_dynamodb_table": 4,
    "aws_s3_bucket": 4,
}
DEFAULT_LAYER = 2

# Relationship type -> (edge label, dashed, arrow). Only these are drawn (data flow).
FLOW_EDGES: dict[str, tuple[str, bool, bool]] = {
    "dns_alias": ("DNS", True, True),
    "waf_protection": ("WAF", True, False),
    "cdn_origin": ("", False, True),
    "network_access": ("", False, True),
    "dynamodb_access": ("", False, True),
    "event_target": ("", True, True),
    "subscription": ("", True, True),
}
NETWORK_EDGES: dict[str, tuple[str, bool, bool]] = {
    "route_target": ("", False, True),
    "route_table_association": ("", True, False),
}

DRAWIO_APP_PATHS: tuple[str, ...] = ("/Applications/draw.io.app/Contents/MacOS/draw.io",)


# ============================================================================
# Model
# ============================================================================


@dataclass
class _Box:
    """A layout box: a drawn container/icon (``cell_id`` set) or an invisible frame."""

    cell_id: str | None = None
    value: str = ""
    style: str = ""
    attrs: dict[str, str] | None = None  # UserObject attributes (resources)
    direction: str = "row"  # row | column | grid
    children: list[_Box] = field(default_factory=list)
    icon: bool = False
    pad: tuple[int, int, int, int] = (0, 0, 0, 0)
    gap: int = GAP
    columns: int = 0
    align_rows: bool = False  # column of rows whose i-th children share a width
    min_w: float = 0
    min_h: float = 0
    x: float = 0
    y: float = 0
    w: float = 0
    h: float = 0


@dataclass
class _Node:
    """One icon: a single resource or a group of identical ones."""

    key: tuple[str, ...]
    type_id: str
    name: str
    arns: list[str]
    layer: int


@dataclass
class _Context:
    specs: dict[str, ResourceSpec]
    relationships: list[ResourceRelationship]
    subnets: dict[str, ResourceSpec]  # subnet id -> spec
    public: dict[str, bool]  # subnet id -> public
    placement: dict[str, list[str]]  # resource ARN -> subnet ids
    vpc_of: dict[str, str]  # resource ARN -> VPC id
    vpcs: dict[str, ResourceSpec]  # VPC id -> spec
    members: dict[str, str]  # instance ARN -> Auto Scaling group ARN


# ============================================================================
# Helpers
# ============================================================================


def _cell_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8"), usedforsecurity=False)
    return f"{prefix}-{digest.hexdigest()[:12]}"


# Characters XML 1.0 cannot carry (control characters, surrogates, U+FFFE/U+FFFF).
_XML_INVALID = re.compile("[^\t\n\r\x20-\ud7ff\ue000-\ufffd\U00010000-\U0010ffff]")


def _escape(text: str) -> str:
    # ElementTree escapes attribute values; only the HTML label markup needs care.
    text = _XML_INVALID.sub("\ufffd", text)
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _type(spec: ResourceSpec) -> str:
    return canonical_type(spec.resource_type) or spec.resource_type


def _tag(specs: dict[str, Any], key: str) -> str | None:
    tags = specs.get("Tags", specs.get("tags"))
    if isinstance(tags, dict):
        value = tags.get(key)
        return value if isinstance(value, str) else None
    for tag in tags if isinstance(tags, list) else []:
        if isinstance(tag, dict) and (tag.get("Key") or tag.get("key")) == key:
            value = tag.get("Value", tag.get("value"))
            return value if isinstance(value, str) else None
    return None


def _field(specs: dict[str, Any], path: str) -> Any:
    try:
        return resolve_property_path({"specifications": specs}, f"specifications.{path}")
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def _name(spec: ResourceSpec) -> str:
    specs = spec.specifications or {}
    kind = _type(spec)
    name = _tag(specs, "Name")
    if not name and kind == "aws_lb_listener" and specs.get("Protocol") and specs.get("Port"):
        name = f"{specs['Protocol']}:{specs['Port']}"
    if not name and kind in NAME_FIELDS:
        value = _field(specs, NAME_FIELDS[kind])
        name = value if isinstance(value, str) else None
    name = (name or resource_id(spec)).rstrip(".") or spec.arn
    return name if len(name) <= MAX_LABEL else name[: MAX_LABEL - 1] + "…"


def _style(type_id: str) -> str:
    info = REGISTRY.get(type_id)
    return info.drawio_style if info else FALLBACK_STYLE


def _display(type_id: str) -> str:
    return DISPLAY_NAMES.get(type_id, type_id)


def _icon_label(name: str, type_id: str, count: int, members: int = 0) -> str:
    title = f"{name} ×{count}" if count > 1 else name
    kind = _display(type_id)
    if members:
        kind += f" ({members} instance{'s' if members > 1 else ''})"
    return f"<b>{_escape(title)}</b><br>{_escape(kind)}"


# ============================================================================
# Facts derived from specs and relationships
# ============================================================================


def _context(specs: list[ResourceSpec], relationships: list[ResourceRelationship]) -> _Context:
    by_arn = {s.arn: s for s in specs}
    subnets = {
        str(s.specifications.get("SubnetId")): s
        for s in specs
        if _type(s) == "aws_subnet" and isinstance((s.specifications or {}).get("SubnetId"), str)
    }
    vpcs = {
        str(s.specifications.get("VpcId")): s
        for s in specs
        if _type(s) == "aws_vpc" and isinstance((s.specifications or {}).get("VpcId"), str)
    }
    subnet_by_arn = {s.arn: subnet_id for subnet_id, s in subnets.items()}
    vpc_by_arn = {s.arn: vpc_id for vpc_id, s in vpcs.items()}

    placement: dict[str, list[str]] = {}
    vpc_of: dict[str, str] = {}
    for rel in relationships:
        if rel.relationship_type == "subnet_placement" and rel.to_arn in subnet_by_arn:
            placement.setdefault(rel.from_arn, []).append(subnet_by_arn[rel.to_arn])
        elif rel.relationship_type == "vpc_connection" and rel.to_arn in vpc_by_arn:
            vpc_of[rel.from_arn] = vpc_by_arn[rel.to_arn]
    for spec in subnets.values():
        vpc_id = spec.specifications.get("VpcId")
        if isinstance(vpc_id, str):
            vpc_of[spec.arn] = vpc_id
    public = {subnet_id: _is_public(subnet_id, specs) for subnet_id in subnets}
    for arn, ids in placement.items():
        placement[arn] = sorted(set(ids), key=lambda i: (_az(subnets[i]), not public[i], i))
        vpc_of.setdefault(arn, str(subnets[placement[arn][0]].specifications.get("VpcId")))

    # EC2 instances launched by a collected Auto Scaling group join the group's icon.
    groups = {
        str(s.specifications.get("AutoScalingGroupName")): s.arn
        for s in specs
        if _type(s) == "aws_autoscaling_group"
    }
    members = {
        s.arn: groups[group]
        for s in specs
        if _type(s) == "aws_instance"
        and (group := _tag(s.specifications or {}, "aws:autoscaling:groupName")) in groups
    }
    return _Context(by_arn, relationships, subnets, public, placement, vpc_of, vpcs, members)


def _az(subnet: ResourceSpec) -> str:
    return str((subnet.specifications or {}).get("AvailabilityZone") or "")


def _is_public(subnet_id: str, specs: list[ResourceSpec]) -> bool:
    """Public = the subnet's route table (explicit, else the VPC's main) routes to an IGW."""
    tables = [s.specifications or {} for s in specs if _type(s) == "aws_route_table"]
    subnet_vpc = next(
        (
            (s.specifications or {}).get("VpcId")
            for s in specs
            if _type(s) == "aws_subnet" and (s.specifications or {}).get("SubnetId") == subnet_id
        ),
        None,
    )

    def associated(table: dict[str, Any], main: bool) -> bool:
        for association in table.get("Associations") or []:
            if not isinstance(association, dict):
                continue
            if main and association.get("Main") and table.get("VpcId") == subnet_vpc:
                return True
            if not main and association.get("SubnetId") == subnet_id:
                return True
        return False

    table = next((t for t in tables if associated(t, False)), None)
    if table is None:
        table = next((t for t in tables if associated(t, True)), None)
    if table is None:
        return False
    return any(
        isinstance(route, dict) and str(route.get("GatewayId") or "").startswith("igw-")
        for route in table.get("Routes") or []
    )


# ============================================================================
# Layout
# ============================================================================


def _measure(box: _Box) -> None:
    if box.icon:
        box.w, box.h = SLOT_W, SLOT_H
        return
    for child in box.children:
        _measure(child)
    if box.align_rows:
        _align_rows(box)
    top, right, bottom, left = box.pad
    children = box.children
    if box.direction == "grid" and children:
        columns = max(1, box.columns)
        widths = [0.0] * min(columns, len(children))
        heights = [0.0] * ((len(children) + columns - 1) // columns)
        for index, child in enumerate(children):
            widths[index % columns] = max(widths[index % columns], child.w)
            heights[index // columns] = max(heights[index // columns], child.h)
        for index, child in enumerate(children):
            child.x = left + sum(widths[: index % columns]) + box.gap * (index % columns)
            child.y = top + sum(heights[: index // columns]) + box.gap * (index // columns)
        content_w = sum(widths) + box.gap * (len(widths) - 1)
        content_h = sum(heights) + box.gap * (len(heights) - 1)
    elif box.direction == "row":
        offset = float(left)
        for child in children:
            child.x, child.y = offset, top
            offset += child.w + box.gap
        content_w = sum(c.w for c in children) + box.gap * max(0, len(children) - 1)
        content_h = max((c.h for c in children), default=0)
    else:
        offset = float(top)
        for child in children:
            child.x, child.y = left, offset
            offset += child.h + box.gap
        content_w = max((c.w for c in children), default=0)
        content_h = sum(c.h for c in children) + box.gap * max(0, len(children) - 1)
    box.w = max(box.min_w, left + content_w + right)
    box.h = max(box.min_h, top + content_h + bottom)


def _align_rows(box: _Box) -> None:
    """Give the i-th child of every row the same width, and every row the same width."""
    rows = box.children
    widest = max((len(r.children) for r in rows), default=0)
    for index in range(widest):
        width = max(r.children[index].w for r in rows if len(r.children) > index)
        for row in rows:
            if len(row.children) > index:
                row.children[index].min_w = width
    for row in rows:
        _measure(row)
    width = max((r.w for r in rows), default=0)
    for row in rows:
        row.min_w = width
        _measure(row)


@dataclass
class _Emitted:
    root: ET.Element
    rects: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)
    parents: dict[str, str] = field(default_factory=dict)


def _emit(
    box: _Box, out: _Emitted, parent: str, ox: float, oy: float, ax: float, ay: float
) -> None:
    """Write ``box``; (ox, oy) offset inside the parent cell, (ax, ay) absolute origin."""
    x, y = ox + box.x, oy + box.y
    if box.cell_id is None:
        for child in box.children:
            _emit(child, out, parent, x, y, ax + box.x, ay + box.y)
        return
    gx: float
    gy: float
    gw: float
    gh: float
    if box.icon:
        gx, gy, gw, gh = x + (SLOT_W - ICON) / 2, y, ICON, ICON
    else:
        gx, gy, gw, gh = x, y, box.w, box.h
    if box.attrs is not None:
        element = ET.SubElement(
            out.root, "UserObject", {"id": box.cell_id, "label": box.value, **box.attrs}
        )
        cell = ET.SubElement(
            element, "mxCell", {"style": box.style, "vertex": "1", "parent": parent}
        )
    else:
        cell = ET.SubElement(
            out.root,
            "mxCell",
            {
                "id": box.cell_id,
                "value": box.value,
                "style": box.style,
                "vertex": "1",
                "parent": parent,
            },
        )
    ET.SubElement(
        cell,
        "mxGeometry",
        {"x": _num(gx), "y": _num(gy), "width": _num(gw), "height": _num(gh), "as": "geometry"},
    )
    abs_x, abs_y = ax + (gx - ox) + 0, ay + (gy - oy)
    out.rects[box.cell_id] = (abs_x, abs_y, gw, gh)
    out.parents[box.cell_id] = parent
    for child in box.children:
        _emit(child, out, box.cell_id, 0, 0, ax + box.x, ay + box.y)


def _num(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


# ============================================================================
# Page builders
# ============================================================================


class _PageBuilder:
    """Builds one page: boxes, then edges between the drawn cells."""

    def __init__(self, page: str, ctx: _Context) -> None:
        self.page = page
        self.ctx = ctx
        self.cell_of: dict[str, str] = {}  # ARN -> cell id

    # -- boxes -----------------------------------------------------------

    def icon(self, node: _Node) -> _Box:
        cell_id = _cell_id(f"{self.page[:3].lower()}-res", *node.key)
        for arn in node.arns:
            self.cell_of[arn] = cell_id
        joined = "\n".join(node.arns)
        return _Box(
            cell_id=cell_id,
            value=_icon_label(
                node.name,
                node.type_id,
                sum(1 for a in node.arns if a not in self.ctx.members),
                sum(1 for a in node.arns if a in self.ctx.members),
            ),
            style=_style(node.type_id),
            attrs={"tooltip": joined, "arns": joined, "resource_type": node.type_id},
            icon=True,
        )

    def resource_group(self, spec: ResourceSpec, value: str, style: str, **extra: str) -> _Box:
        cell_id = _cell_id(f"{self.page[:3].lower()}-grp", spec.arn)
        self.cell_of[spec.arn] = cell_id
        attrs = {"tooltip": spec.arn, "arns": spec.arn, "resource_type": _type(spec), **extra}
        return _Box(cell_id=cell_id, value=value, style=style, attrs=attrs, pad=GROUP_PAD)

    def plain_group(self, key: str, value: str, style: str) -> _Box:
        return _Box(
            cell_id=_cell_id(f"{self.page[:3].lower()}-box", key),
            value=value,
            style=style,
            pad=GROUP_PAD,
        )

    def column(self, children: list[_Box], gap: int = GAP) -> _Box:
        return _Box(direction="column", children=children, gap=gap)

    def row(self, children: list[_Box], gap: int = GAP) -> _Box:
        return _Box(direction="row", children=children, gap=gap)

    def vpc_box(
        self,
        vpc_id: str,
        subnet_nodes: dict[str, list[_Node]],
        sides: tuple[list[_Node], list[_Node]],
        extra_rows: list[_Box],
    ) -> _Box:
        ctx = self.ctx
        vpc = ctx.vpcs[vpc_id]
        specs = vpc.specifications or {}
        cidr = specs.get("CidrBlock")
        label = f"{_name(vpc)} ({cidr})" if isinstance(cidr, str) else _name(vpc)
        box = self.resource_group(vpc, _escape(label), VPC_STYLE)
        zones: dict[str, list[str]] = {}
        for subnet_id, subnet in ctx.subnets.items():
            if subnet.specifications.get("VpcId") == vpc_id:
                zones.setdefault(_az(subnet), []).append(subnet_id)
        az_rows = []
        for zone in sorted(zones):
            ordered = sorted(
                zones[zone],
                key=lambda i: (not ctx.public[i], _name(ctx.subnets[i]), i),
            )
            az = self.plain_group(f"{vpc_id}|{zone}", _escape(zone or "unknown AZ"), AZ_STYLE)
            for subnet_id in ordered:
                subnet = ctx.subnets[subnet_id]
                public = ctx.public[subnet_id]
                cidr = subnet.specifications.get("CidrBlock")
                label = _escape(_name(subnet))
                if isinstance(cidr, str):
                    label += f"<br>{_escape(cidr)}"
                group = self.resource_group(
                    subnet,
                    label,
                    PUBLIC_SUBNET_STYLE if public else PRIVATE_SUBNET_STYLE,
                    subnet_type="public" if public else "private",
                )
                group.children = [self.icon(n) for n in subnet_nodes.get(subnet_id, [])]
                group.min_w, group.min_h = (
                    SLOT_W + GROUP_PAD[1] + GROUP_PAD[3],
                    SLOT_H + GROUP_PAD[0] + GROUP_PAD[2],
                )
                az.children.append(group)
            az_rows.append(az)
        azs = _Box(direction="column", children=az_rows, align_rows=True)
        left, right = sides
        main = [self.column([self.icon(n) for n in left])] if left else []
        main.append(azs)
        if right:
            main.append(self.column([self.icon(n) for n in right]))
        box.direction = "column"
        box.children = [self.row(main), *extra_rows]
        return box

    # -- edges -----------------------------------------------------------

    def edges(
        self,
        out: _Emitted,
        drawn: list[tuple[str, str, str, list[str], list[str], tuple[bool, bool]]],
    ) -> None:
        """drawn: (source cell, target cell, label, relationship types, evidence, (dashed, arrow))."""
        merged: dict[tuple[str, str], dict[str, Any]] = {}
        for source, target, label, kinds, evidence, (dashed, arrow) in drawn:
            if source == target:
                continue
            entry = merged.setdefault(
                (source, target),
                {
                    "labels": set(),
                    "kinds": set(),
                    "evidence": set(),
                    "dashed": dashed,
                    "arrow": arrow,
                },
            )
            if label:
                entry["labels"].add(label)
            entry["kinds"].update(kinds)
            entry["evidence"].update(evidence)
        for (source, target), entry in sorted(merged.items()):
            label = ", ".join(sorted(entry["labels"]))
            style = EDGE_BASE + _ports(out.rects[source], out.rects[target])
            if entry["dashed"]:
                style += "dashed=1;"
            if not entry["arrow"]:
                style += "endArrow=none;"
            if label:
                style += "labelBackgroundColor=#F5F5F5;fontSize=11;"
            relationship_types = ",".join(sorted(entry["kinds"]))
            element = ET.SubElement(
                out.root,
                "UserObject",
                {
                    "id": _cell_id(f"{self.page[:3].lower()}-edge", source, target),
                    "label": label,
                    "relationships": relationship_types,
                    "evidence": "\n".join(sorted(entry["evidence"])),
                },
            )
            cell = ET.SubElement(
                element,
                "mxCell",
                {
                    "style": style,
                    "edge": "1",
                    "parent": _common_parent(out.parents, source, target),
                    "source": source,
                    "target": target,
                },
            )
            ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})


def _ports(source: tuple[float, ...], target: tuple[float, ...]) -> str:
    sx, sy = source[0] + source[2] / 2, source[1] + source[3] / 2
    tx, ty = target[0] + target[2] / 2, target[1] + target[3] / 2
    dx, dy = tx - sx, ty - sy
    if abs(dx) >= abs(dy):
        exit_x, entry_x = (1, 0) if dx >= 0 else (0, 1)
        return (
            f"exitX={exit_x};exitY=0.5;exitDx=0;exitDy=0;"
            f"entryX={entry_x};entryY=0.5;entryDx=0;entryDy=0;"
        )
    exit_y, entry_y = (1, 0) if dy > 0 else (0, 1)
    return (
        f"exitX=0.5;exitY={exit_y};exitDx=0;exitDy=0;"
        f"entryX=0.5;entryY={entry_y};entryDx=0;entryDy=0;"
    )


def _common_parent(parents: dict[str, str], source: str, target: str) -> str:
    def chain(cell: str) -> list[str]:
        result = []
        while cell in parents:
            cell = parents[cell]
            result.append(cell)
        return result

    target_chain = set(chain(target))
    return next((c for c in chain(source) if c in target_chain), "1")


def _evidence(relationships: Iterable[ResourceRelationship]) -> list[str]:
    return [f"{c.resource_arn}#{c.property_path}" for r in relationships for c in r.citations]


# ============================================================================
# Generator
# ============================================================================


class DiagramGenerator:
    """Builds deterministic draw.io diagrams (Overview and Network detail pages)."""

    def __init__(self, drawio_kit_path: str | Path | None = None) -> None:
        # Kept for API compatibility; styles come from the resource type registry.
        self.drawio_kit_path = Path(drawio_kit_path) if drawio_kit_path else None

    def identify_relationships(self, specs: list[ResourceSpec]) -> list[ResourceRelationship]:
        """Relationships the diagram is drawn from (delegates to the Analysis_Engine rules)."""
        return AnalysisEngine().identify_relationships(specs)

    def generate_diagram(
        self,
        specs: list[ResourceSpec],
        relationships: list[ResourceRelationship] | None = None,
    ) -> str:
        """Return the .drawio XML for ``specs``; relationships are computed when omitted."""
        unique: dict[str, ResourceSpec] = {}
        for spec in sorted(specs, key=lambda s: s.arn):
            unique.setdefault(spec.arn, spec)
        ordered = list(unique.values())
        if relationships is None:
            relationships = self.identify_relationships(ordered)
        relationships = sorted(
            (r for r in relationships if r.from_arn in unique and r.to_arn in unique),
            key=lambda r: (r.from_arn, r.to_arn, r.relationship_type),
        )
        ctx = _context(ordered, relationships)
        title = _title(ordered)

        mxfile = ET.Element("mxfile", host="aws-resource-inventory", type="device")
        _overview_page(mxfile, ctx, title)
        _network_page(mxfile, ctx, title)
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


def _title(specs: list[ResourceSpec]) -> str:
    accounts = sorted({s.account_id for s in specs if s.account_id}) or ["unknown"]
    regions = sorted({s.region for s in specs if s.region and s.region != GLOBAL_REGION})
    collected = max((s.metadata.collected_at for s in specs if s.metadata), default="")
    parts = [
        f"account {', '.join(accounts)}",
        f"regions {', '.join(regions) or '-'}",
        f"collected {collected[:10] or '-'}",
        "aws-resource-inventory",
    ]
    return f"<b>AWS architecture</b><br>{_escape(' | '.join(parts))}"


def _page(mxfile: ET.Element, page: str, content: _Box, title: str) -> _Emitted:
    diagram = ET.SubElement(mxfile, "diagram", id=page.lower().replace(" ", "-"), name=page)
    _measure(content)
    content.x, content.y = MARGIN, MARGIN + TITLE_H
    width = int(max(content.w + 2 * MARGIN, 640))
    height = int(content.h + 2 * MARGIN + TITLE_H)
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": str(width + 400),
            "dy": str(height + 200),
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(width),
            "pageHeight": str(height),
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    prefix = page[:3].lower()
    for cell_id, value, style, geometry in (
        (f"{prefix}-background", "", BACKGROUND_STYLE, (0, 0, width, height)),
        (f"{prefix}-title", title, TITLE_STYLE, (MARGIN, 20, 620, TITLE_H - 10)),
    ):
        cell = ET.SubElement(
            root,
            "mxCell",
            {"id": cell_id, "value": value, "style": style, "vertex": "1", "parent": "1"},
        )
        x, y, w, h = geometry
        ET.SubElement(
            cell,
            "mxGeometry",
            {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"},
        )
    out = _Emitted(root)
    _emit(content, out, "1", 0, 0, 0, 0)
    return out


def _group_nodes(items: list[tuple[tuple[str, ...], ResourceSpec]], ctx: _Context) -> list[_Node]:
    """One node per (container key, type, name); Auto Scaling members join their group."""
    nodes: dict[tuple[str, ...], _Node] = {}
    for container, spec in items:
        kind = _type(spec)
        name = _name(spec)
        key = (*container, kind, name)
        node = nodes.get(key)
        if node is None:
            node = nodes[key] = _Node(key, kind, name, [], LAYERS.get(kind, DEFAULT_LAYER))
        node.arns.append(spec.arn)
        node.arns.extend(m for m, group in sorted(ctx.members.items()) if group == spec.arn)
    return sorted(nodes.values(), key=lambda n: (n.layer, n.type_id, n.name, n.arns[0]))


def _overview_page(mxfile: ET.Element, ctx: _Context, title: str) -> None:
    builder = _PageBuilder(OVERVIEW_PAGE, ctx)
    placed: dict[str, list[tuple[tuple[str, ...], ResourceSpec]]] = {}

    def put(area: str, container: tuple[str, ...], spec: ResourceSpec) -> None:
        placed.setdefault(area, []).append((container, spec))

    for arn, spec in ctx.specs.items():
        kind = _type(spec)
        if kind in CONTAINER_TYPES and _container_drawn(spec, ctx):
            continue
        if arn in ctx.members:
            continue  # drawn inside its Auto Scaling group's icon
        if kind in SUPPORT_TYPES:
            put("support", ("support",), spec)
        elif kind in EDGE_TYPES and (spec.region == GLOBAL_REGION or kind != "aws_wafv2_web_acl"):
            put("edge", ("edge", "1" if kind == "aws_route53_zone" else "2"), spec)
        elif ctx.placement.get(arn):
            put("subnet:" + ctx.placement[arn][0], ("subnet", ctx.placement[arn][0]), spec)
        elif ctx.vpc_of.get(arn) in ctx.vpcs and kind in (
            "aws_internet_gateway",
            "aws_vpc_endpoint",
        ):
            side = "left" if kind == "aws_internet_gateway" else "right"
            put(f"vpc:{ctx.vpc_of[arn]}:{side}", ("vpc", ctx.vpc_of[arn], side), spec)
        elif spec.region == GLOBAL_REGION or not spec.region:
            put("global", ("global",), spec)
        else:
            put(f"region:{spec.region}", ("region", spec.region), spec)

    def nodes(area: str) -> list[_Node]:
        return _group_nodes(placed.get(area, []), ctx)

    # Support panel: one icon per type.
    support_nodes: list[_Node] = []
    by_type: dict[str, list[str]] = {}
    for _, spec in placed.get("support", []):
        by_type.setdefault(_type(spec), []).append(spec.arn)
    for kind in SUPPORT_TYPES:
        if kind in by_type:
            arns = sorted(by_type[kind])
            name = _name(ctx.specs[arns[0]]) if len(arns) == 1 else _display(kind)
            support_nodes.append(_Node(("support", kind), kind, name, arns, 0))

    regions = sorted(
        {s.region for s in ctx.specs.values() if s.region and s.region != GLOBAL_REGION}
        | {str(s.region) for s in ctx.vpcs.values() if s.region}
    )
    region_boxes = []
    for region in regions:
        children: list[_Box] = []
        vpc_boxes = []
        for vpc_id in sorted(v for v, s in ctx.vpcs.items() if s.region == region):
            subnet_nodes = {
                subnet_id: nodes(f"subnet:{subnet_id}")
                for subnet_id, subnet in ctx.subnets.items()
                if subnet.specifications.get("VpcId") == vpc_id
            }
            sides = (nodes(f"vpc:{vpc_id}:left"), nodes(f"vpc:{vpc_id}:right"))
            vpc_boxes.append(builder.vpc_box(vpc_id, subnet_nodes, sides, []))
        if vpc_boxes:
            children.append(builder.column(vpc_boxes))
        services = nodes(f"region:{region}")
        layers = sorted({n.layer for n in services})
        if services:
            children.append(
                builder.row(
                    [
                        builder.column([builder.icon(n) for n in services if n.layer == layer])
                        for layer in layers
                    ]
                )
            )
        # Subnets of VPCs that were not collected cannot be drawn as containers; their
        # resources are kept in the region area.
        orphans = [
            n
            for area in sorted(placed)
            if area.startswith("subnet:") and _orphan_subnet(area[7:], ctx, region)
            for n in nodes(area)
        ]
        if orphans:
            children.append(builder.column([builder.icon(n) for n in orphans]))
        if not children:
            continue
        box = builder.plain_group(f"region|{region}", _escape(region), REGION_STYLE)
        box.children = children
        region_boxes.append(box)

    edge_nodes = nodes("edge")
    edge_columns = [
        builder.column([builder.icon(n) for n in edge_nodes if n.key[1] == column])
        for column in ("1", "2")
        if any(n.key[1] == column for n in edge_nodes)
    ]
    top_row: list[_Box] = []
    if edge_columns:
        top_row.append(builder.row(edge_columns))
    if region_boxes:
        top_row.append(builder.column(region_boxes))
    global_nodes = nodes("global")
    if global_nodes:
        top_row.append(builder.column([builder.icon(n) for n in global_nodes]))
    accounts = sorted({s.account_id for s in ctx.specs.values() if s.account_id})
    cloud = builder.plain_group(
        "cloud",
        _escape("AWS Cloud" + (f" (account {', '.join(accounts)})" if accounts else "")),
        CLOUD_STYLE,
    )
    cloud.direction = "column"
    cloud.children = [builder.row(top_row)] if top_row else []
    if support_nodes:
        panel = builder.plain_group("support", "Supporting resources", PANEL_STYLE)
        panel.direction, panel.columns = "grid", SUPPORT_COLUMNS
        panel.pad = (40, 20, 20, 20)
        panel.children = [builder.icon(n) for n in support_nodes]
        cloud.children.append(panel)
    cloud.min_w, cloud.min_h = 400, 200

    page_children = []
    users = _entry_points(ctx)
    users_box = None
    if users:
        users_box = _Box(cell_id="ove-users", value="Users", style=USERS_STYLE, icon=True)
        page_children.append(
            _Box(direction="column", children=[users_box], pad=(GROUP_PAD[0], 0, 0, 0))
        )
    page_children.append(cloud)
    out = _page(mxfile, OVERVIEW_PAGE, _Box(direction="row", children=page_children), title)

    cell = builder.cell_of
    drawn: list[tuple[str, str, str, list[str], list[str], tuple[bool, bool]]] = []
    for arn in users:
        if arn in cell and users_box is not None and users_box.cell_id:
            drawn.append((users_box.cell_id, cell[arn], "", ["entry_point"], [arn], (False, True)))
    for rel in ctx.relationships:
        style = FLOW_EDGES.get(rel.relationship_type)
        if style is None or rel.from_arn not in cell or rel.to_arn not in cell:
            continue
        label = _network_port(rel, ctx) if rel.relationship_type == "network_access" else style[0]
        drawn.append(
            (
                cell[rel.from_arn],
                cell[rel.to_arn],
                label,
                [rel.relationship_type],
                _evidence([rel]),
                style[1:],
            )
        )
    drawn.extend(_load_balancer_edges(ctx, cell))
    builder.edges(out, drawn)


def _container_drawn(spec: ResourceSpec, ctx: _Context) -> bool:
    """VPCs and subnets are drawn as containers when their VPC is collected."""
    specs = spec.specifications or {}
    if _type(spec) == "aws_vpc":
        return ctx.vpcs.get(str(specs.get("VpcId"))) is spec
    return (
        ctx.subnets.get(str(specs.get("SubnetId"))) is spec and str(specs.get("VpcId")) in ctx.vpcs
    )


def _orphan_subnet(subnet_id: str, ctx: _Context, region: str) -> bool:
    subnet = ctx.subnets.get(subnet_id)
    return (
        subnet is not None
        and subnet.region == region
        and subnet.specifications.get("VpcId") not in ctx.vpcs
    )


def _entry_points(ctx: _Context) -> list[str]:
    """CloudFront distributions and internet-facing load balancers no distribution fronts."""
    fronted = {r.to_arn for r in ctx.relationships if r.relationship_type == "cdn_origin"}
    entries = []
    for arn, spec in ctx.specs.items():
        kind = _type(spec)
        if kind == "aws_cloudfront_distribution":
            entries.append(arn)
        elif (
            kind == "aws_lb"
            and (spec.specifications or {}).get("Scheme") == "internet-facing"
            and arn not in fronted
        ):
            entries.append(arn)
    return sorted(entries)


def _network_port(rel: ResourceRelationship, ctx: _Context) -> str:
    """Port of the security group rule cited first by a network_access relationship."""
    citation = rel.citations[0]
    match = re.match(r"specifications\.IpPermissions\[(\d+)\]", citation.property_path)
    group = ctx.specs.get(citation.resource_arn)
    if match is None or group is None:
        return ""
    rules = (group.specifications or {}).get("IpPermissions") or []
    rule = rules[int(match.group(1))] if int(match.group(1)) < len(rules) else {}
    low, high = rule.get("FromPort"), rule.get("ToPort")
    if low is None or low == -1:
        return "all"
    return str(low) if low == high else f"{low}-{high}"


def _load_balancer_edges(
    ctx: _Context, cell: dict[str, str]
) -> list[tuple[str, str, str, list[str], list[str], tuple[bool, bool]]]:
    """Load balancer -> ECS service / Auto Scaling group through listener and target group."""
    by_type: dict[str, list[ResourceRelationship]] = {}
    for rel in ctx.relationships:
        by_type.setdefault(rel.relationship_type, []).append(rel)
    edges = []
    for listener in by_type.get("lb_listener", []):
        spec = ctx.specs[listener.from_arn].specifications or {}
        protocol, port = spec.get("Protocol"), spec.get("Port")
        label = f"{protocol}:{port}" if protocol and port else ""
        for forward in by_type.get("forwards_to", []):
            if forward.from_arn != listener.from_arn:
                continue
            for target in by_type.get("lb_target", []):
                if target.from_arn != forward.to_arn:
                    continue
                if listener.to_arn in cell and target.to_arn in cell:
                    edges.append(
                        (
                            cell[listener.to_arn],
                            cell[target.to_arn],
                            label,
                            ["lb_listener", "forwards_to", "lb_target"],
                            _evidence([listener, forward, target]),
                            (False, True),
                        )
                    )
    return edges


def _network_page(mxfile: ET.Element, ctx: _Context, title: str) -> None:
    builder = _PageBuilder(NETWORK_PAGE, ctx)
    placed: dict[str, list[tuple[tuple[str, ...], ResourceSpec]]] = {}
    for arn, spec in ctx.specs.items():
        kind = _type(spec)
        vpc_id = ctx.vpc_of.get(arn)
        area: str
        container: tuple[str, ...]
        if kind not in NETWORK_TYPES or vpc_id not in ctx.vpcs:
            continue
        if kind in ("aws_nat_gateway", "aws_vpc_endpoint") and ctx.placement.get(arn):
            area, container = f"subnet:{ctx.placement[arn][0]}", ("subnet", ctx.placement[arn][0])
        elif kind == "aws_internet_gateway":
            area, container = f"vpc:{vpc_id}:left", ("vpc", str(vpc_id), "left")
        elif kind == "aws_security_group":
            area, container = f"vpc:{vpc_id}:sg", ("vpc", str(vpc_id), "sg")
        else:
            area, container = f"vpc:{vpc_id}:right", ("vpc", str(vpc_id), "right")
        placed.setdefault(area, []).append((container, spec))

    def nodes(area: str) -> list[_Node]:
        return _group_nodes(placed.get(area, []), ctx)

    region_boxes = []
    for region in sorted({str(s.region) for s in ctx.vpcs.values()}):
        vpc_boxes = []
        for vpc_id in sorted(v for v, s in ctx.vpcs.items() if s.region == region):
            subnet_nodes = {
                subnet_id: nodes(f"subnet:{subnet_id}")
                for subnet_id, subnet in ctx.subnets.items()
                if subnet.specifications.get("VpcId") == vpc_id
            }
            groups = nodes(f"vpc:{vpc_id}:sg")
            extra = [builder.row([builder.icon(n) for n in groups])] if groups else []
            sides = (nodes(f"vpc:{vpc_id}:left"), nodes(f"vpc:{vpc_id}:right"))
            vpc_boxes.append(builder.vpc_box(vpc_id, subnet_nodes, sides, extra))
        box = builder.plain_group(f"region|{region}", _escape(region), REGION_STYLE)
        box.children = [builder.column(vpc_boxes)]
        region_boxes.append(box)
    if region_boxes:
        content = builder.plain_group("cloud", "AWS Cloud", CLOUD_STYLE)
        content.direction = "column"
        content.children = region_boxes
    else:
        content = _Box(
            cell_id="net-empty",
            value="No VPC collected",
            style="text;html=1;align=left;verticalAlign=top;fontSize=12;",
            min_w=300,
            min_h=40,
        )
    out = _page(mxfile, NETWORK_PAGE, _Box(direction="row", children=[content]), title)

    cell = builder.cell_of
    drawn = []
    for rel in ctx.relationships:
        style = NETWORK_EDGES.get(rel.relationship_type)
        if style is None or rel.from_arn not in cell or rel.to_arn not in cell:
            continue
        label = _route_destination(rel, ctx) if rel.relationship_type == "route_target" else ""
        drawn.append(
            (
                cell[rel.from_arn],
                cell[rel.to_arn],
                label,
                [rel.relationship_type],
                _evidence([rel]),
                style[1:],
            )
        )
    builder.edges(out, drawn)


def _route_destination(rel: ResourceRelationship, ctx: _Context) -> str:
    """Destination of the route a route_target relationship cites."""
    citation = rel.citations[0]
    match = re.match(r"specifications\.Routes\[(\d+)\]", citation.property_path)
    table = ctx.specs.get(citation.resource_arn)
    if match is None or table is None:
        return ""
    routes = (table.specifications or {}).get("Routes") or []
    route = routes[int(match.group(1))] if int(match.group(1)) < len(routes) else {}
    for key in ("DestinationCidrBlock", "DestinationIpv6CidrBlock", "DestinationPrefixListId"):
        if isinstance(route.get(key), str):
            return str(route[key])
    return ""


# ============================================================================
# External CLIs
# ============================================================================


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


def _drawio_cli() -> str | None:
    for name in ("drawio", "draw.io"):
        found = shutil.which(name)
        if found:
            return found
    return next((p for p in DRAWIO_APP_PATHS if Path(p).is_file()), None)


def export_png(path: str | Path) -> tuple[bool | None, str]:
    """
    Export the first page of ``path`` to ``<path>.png`` with the draw.io desktop CLI
    (diagram XML embedded, so the PNG stays editable).

    Returns (None, message) when the CLI is not installed, otherwise (passed, message).
    """
    executable = _drawio_cli()
    if executable is None:
        return None, "draw.io desktop CLI not found; PNG export skipped"
    source = Path(path)
    target = source.with_name(source.name + ".png")
    result = subprocess.run(  # noqa: S603 - fixed executable and arguments
        [executable, "-x", "-f", "png", "-e", "-b", "10", "-o", str(target), str(source)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False, f"{result.stdout}{result.stderr}".strip() or "draw.io export failed"
    return True, f"PNG: {target}"
