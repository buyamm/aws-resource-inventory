"""
Unit and property tests for DiagramGenerator.

Requirements Coverage:
- Requirement 6.1: Relationships identified for the diagram
- Requirement 6.4: Valid .drawio file, every collected resource present, aws4 stencils
- Requirement 15.1: Nested AWS Cloud -> Region -> VPC -> AZ -> subnet containers,
  resources in the subnet named by their spec, edge services left of the VPC
- Requirement 15.2: Data-flow edges only, each traceable to relationships/citations
- Requirement 15.3: Identical resources grouped, supporting resources panel, human
  labels, verified stencil names only
- Requirement 15.4: Overview and Network detail pages, title block and background,
  deterministic output (golden file), optional PNG export
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.analysis_engine import AnalysisEngine
from src.diagram_generator import DiagramGenerator
from src.output_generator import OutputGenerator
from src.parser import ResourceSpec, SpecMetadata
from src.resource_types import REGISTRY

ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = ROOT / ".claude" / "skills" / "aws-architecture-diagram"
EXAMPLE_DIR = ROOT / "examples" / "output"

ACCOUNT = "123456789012"
EC2 = f"arn:aws:ec2:us-east-1:{ACCOUNT}"
LB_ARN = f"arn:aws:elasticloadbalancing:us-east-1:{ACCOUNT}:loadbalancer/app/web/abc"
LISTENER_ARN = f"arn:aws:elasticloadbalancing:us-east-1:{ACCOUNT}:listener/app/web/abc/l1"
TG_ARN = f"arn:aws:elasticloadbalancing:us-east-1:{ACCOUNT}:targetgroup/web/def"
SERVICE_ARN = f"arn:aws:ecs:us-east-1:{ACCOUNT}:service/shop/web"
DB_ARN = f"arn:aws:rds:us-east-1:{ACCOUNT}:db:orders"
CF_ARN = f"arn:aws:cloudfront::{ACCOUNT}:distribution/E1"
WAF_ARN = f"arn:aws:wafv2:us-east-1:{ACCOUNT}:global/webacl/shop/w1"
ZONE_ARN = "arn:aws:route53:::hostedzone/Z1"
BUCKET_ARN = "arn:aws:s3:::shop-static"
ROLE_A = f"arn:aws:iam::{ACCOUNT}:role/task"
ROLE_B = f"arn:aws:iam::{ACCOUNT}:role/exec"
LOG_ARN = f"arn:aws:logs:us-east-1:{ACCOUNT}:log-group:/ecs/web"
INSTANCE_1 = f"{EC2}:instance/i-1"
INSTANCE_2 = f"{EC2}:instance/i-2"
LB_DNS = "web-1.us-east-1.elb.amazonaws.com"
CF_DNS = "d1.cloudfront.net"

spec_metadata = SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "v1", "chk")


def _spec(resource_type: str, arn: str, specifications: dict, region: str = "us-east-1"):
    return ResourceSpec(
        resource_type=resource_type,
        arn=arn,
        region=region,
        account_id=ACCOUNT,
        specifications=specifications,
        metadata=spec_metadata,
    )


def _name(value: str) -> list[dict[str, str]]:
    return [{"Key": "Name", "Value": value}]


@pytest.fixture
def shop_specs() -> list[ResourceSpec]:
    """Route 53 -> CloudFront (WAF) -> ALB (public) -> ECS (private) -> RDS, plus extras."""
    return [
        _spec(
            "aws_vpc",
            f"{EC2}:vpc/vpc-1",
            {"VpcId": "vpc-1", "CidrBlock": "10.0.0.0/16", "Tags": _name("shop-vpc")},
        ),
        _spec(
            "aws_subnet",
            f"{EC2}:subnet/subnet-pub",
            {
                "SubnetId": "subnet-pub",
                "VpcId": "vpc-1",
                "AvailabilityZone": "us-east-1a",
                "CidrBlock": "10.0.1.0/24",
                "Tags": _name("shop-public-a"),
            },
        ),
        _spec(
            "aws_subnet",
            f"{EC2}:subnet/subnet-priv",
            {
                "SubnetId": "subnet-priv",
                "VpcId": "vpc-1",
                "AvailabilityZone": "us-east-1a",
                "CidrBlock": "10.0.2.0/24",
                "Tags": _name("shop-private-a"),
            },
        ),
        _spec(
            "aws_route_table",
            f"{EC2}:route-table/rtb-pub",
            {
                "RouteTableId": "rtb-pub",
                "VpcId": "vpc-1",
                "Routes": [
                    {"DestinationCidrBlock": "10.0.0.0/16", "GatewayId": "local"},
                    {"DestinationCidrBlock": "0.0.0.0/0", "GatewayId": "igw-1"},
                ],
                "Associations": [{"Main": False, "SubnetId": "subnet-pub"}],
            },
        ),
        _spec(
            "aws_internet_gateway",
            f"{EC2}:internet-gateway/igw-1",
            {"InternetGatewayId": "igw-1", "Attachments": [{"VpcId": "vpc-1"}]},
        ),
        _spec(
            "aws_security_group",
            f"{EC2}:security-group/sg-app",
            {"GroupId": "sg-app", "GroupName": "app", "VpcId": "vpc-1", "IpPermissions": []},
        ),
        _spec(
            "aws_security_group",
            f"{EC2}:security-group/sg-db",
            {
                "GroupId": "sg-db",
                "GroupName": "db",
                "VpcId": "vpc-1",
                "IpPermissions": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 5432,
                        "ToPort": 5432,
                        "UserIdGroupPairs": [{"GroupId": "sg-app"}],
                    }
                ],
            },
        ),
        _spec(
            "aws_lb",
            LB_ARN,
            {
                "LoadBalancerArn": LB_ARN,
                "LoadBalancerName": "web",
                "DNSName": LB_DNS,
                "Scheme": "internet-facing",
                "VpcId": "vpc-1",
                "AvailabilityZones": [{"SubnetId": "subnet-pub", "ZoneName": "us-east-1a"}],
            },
        ),
        _spec(
            "aws_lb_listener",
            LISTENER_ARN,
            {
                "ListenerArn": LISTENER_ARN,
                "LoadBalancerArn": LB_ARN,
                "Protocol": "HTTPS",
                "Port": 443,
                "DefaultActions": [{"Type": "forward", "TargetGroupArn": TG_ARN}],
            },
        ),
        _spec("aws_lb_target_group", TG_ARN, {"TargetGroupArn": TG_ARN, "VpcId": "vpc-1"}),
        _spec(
            "aws_ecs_service",
            SERVICE_ARN,
            {
                "serviceArn": SERVICE_ARN,
                "serviceName": "web",
                "loadBalancers": [{"targetGroupArn": TG_ARN}],
                "networkConfiguration": {
                    "awsvpcConfiguration": {
                        "subnets": ["subnet-priv"],
                        "securityGroups": ["sg-app"],
                    }
                },
            },
        ),
        _spec(
            "aws_db_instance",
            DB_ARN,
            {
                "DBInstanceIdentifier": "orders",
                "VpcSecurityGroups": [{"VpcSecurityGroupId": "sg-db"}],
                "DBSubnetGroup": {
                    "VpcId": "vpc-1",
                    "Subnets": [{"SubnetIdentifier": "subnet-priv"}],
                },
            },
        ),
        _spec(
            "aws_instance",
            INSTANCE_1,
            {"InstanceId": "i-1", "SubnetId": "subnet-priv", "Tags": _name("batch")},
        ),
        _spec(
            "aws_instance",
            INSTANCE_2,
            {"InstanceId": "i-2", "SubnetId": "subnet-priv", "Tags": _name("batch")},
        ),
        _spec("aws_iam_role", ROLE_A, {"RoleName": "task", "Arn": ROLE_A}, "global"),
        _spec("aws_iam_role", ROLE_B, {"RoleName": "exec", "Arn": ROLE_B}, "global"),
        _spec("aws_cloudwatch_log_group", LOG_ARN, {"logGroupName": "/ecs/web"}),
        _spec("aws_wafv2_web_acl", WAF_ARN, {"ARN": WAF_ARN, "Name": "shop"}, "global"),
        _spec("aws_s3_bucket", BUCKET_ARN, {"Name": "shop-static"}, "global"),
        _spec(
            "aws_cloudfront_distribution",
            CF_ARN,
            {
                "Id": "E1",
                "DomainName": CF_DNS,
                "DistributionConfig": {
                    "Aliases": {"Quantity": 1, "Items": ["shop.example.com"]},
                    "Origins": {
                        "Items": [
                            {"Id": "s3", "DomainName": "shop-static.s3.amazonaws.com"},
                            {"Id": "alb", "DomainName": LB_DNS},
                        ]
                    },
                    "WebACLId": WAF_ARN,
                },
            },
            "global",
        ),
        _spec(
            "aws_route53_zone",
            ZONE_ARN,
            {
                "Id": "/hostedzone/Z1",
                "Name": "example.com.",
                "ResourceRecordSets": [
                    {"Name": "shop.example.com.", "AliasTarget": {"DNSName": CF_DNS + "."}}
                ],
            },
            "global",
        ),
    ]


# ============================================================================
# Helpers
# ============================================================================


class Page:
    """Cells of one diagram page, keyed by id (UserObject attributes merged in)."""

    def __init__(self, diagram: ET.Element) -> None:
        self.name = diagram.get("name")
        self.cells: dict[str, dict] = {}
        root = diagram.find("mxGraphModel/root")
        assert root is not None
        for element in root:
            if element.tag == "UserObject":
                cell = element.find("mxCell")
                attrs = dict(element.attrib)
            else:
                cell, attrs = element, dict(element.attrib)
            assert cell is not None
            attrs.update({k: v for k, v in cell.attrib.items() if k != "id"})
            attrs["geometry"] = cell.find("mxGeometry")
            self.cells[attrs["id"]] = attrs

    def vertices(self) -> list[dict]:
        return [c for c in self.cells.values() if c.get("vertex") == "1"]

    def edges(self) -> list[dict]:
        return [c for c in self.cells.values() if c.get("edge") == "1"]

    def by_arn(self, arn: str) -> dict:
        (cell,) = [c for c in self.vertices() if arn in c.get("arns", "").split("\n")]
        return cell

    def ancestors(self, cell_id: str) -> list[str]:
        chain = []
        parent = self.cells[cell_id].get("parent")
        while parent in self.cells:
            chain.append(parent)
            parent = self.cells[parent].get("parent")
        return chain

    def absolute(self, cell_id: str) -> tuple[float, float, float, float]:
        x = y = 0.0
        current: str | None = cell_id
        while current in self.cells:
            geometry = self.cells[current]["geometry"]
            if geometry is not None and geometry.get("relative") != "1":
                x += float(geometry.get("x", 0))
                y += float(geometry.get("y", 0))
            current = self.cells[current].get("parent")
        geometry = self.cells[cell_id]["geometry"]
        return x, y, float(geometry.get("width", 0)), float(geometry.get("height", 0))


def _pages(xml_content: str) -> dict[str, Page]:
    root = ET.fromstring(xml_content)
    assert root.tag == "mxfile"
    return {d.get("name"): Page(d) for d in root.findall("diagram")}


def _overview(specs: list[ResourceSpec]) -> Page:
    return _pages(DiagramGenerator().generate_diagram(specs))["Overview"]


def _verified_stencils() -> set[str]:
    """Stencil names listed in the vendored aws-architecture-diagram skill."""
    names: set[str] = set()
    for path in [SKILL_DIR / "SKILL.md", *sorted((SKILL_DIR / "references").glob("*.md"))]:
        if "3d" in path.name or "allied" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        names.update(re.findall(r"`([a-z0-9_]+)`", text))
        names.update(re.findall(r"mxgraph\.aws4\.([A-Za-z0-9_]+)", text))
    return names


def _stencils(style: str) -> list[str]:
    return re.findall(r"(?:resIcon|grIcon|shape)=mxgraph\.aws4\.([A-Za-z0-9_]+)", style)


# ============================================================================
# Property 4: every collected resource appears in the diagram (Req 6.4)
# ============================================================================

resource_types = [
    "aws_s3_bucket",
    "aws_instance",
    "aws_ec2_instance",
    "not_a_registered_type",
    "aws_lambda_function",
    "aws_vpc",
    "aws_subnet",
    "aws_security_group",
    "aws_iam_role",
    "aws_dynamodb_table",
    "aws_lb",
    "aws_cloudfront_distribution",
]

resource_spec_strategy = st.builds(
    ResourceSpec,
    resource_type=st.sampled_from(resource_types),
    arn=st.from_regex(r"arn:aws:[a-z0-9-]+:[a-z0-9-]+:123456789012:[a-z0-9_-]+", fullmatch=True),
    region=st.sampled_from(["us-east-1", "us-west-2", "global"]),
    account_id=st.just(ACCOUNT),
    specifications=st.fixed_dictionaries(
        {},
        optional={
            "Tags": st.lists(
                st.fixed_dictionaries({"Key": st.just("Name"), "Value": st.text(max_size=8)}),
                max_size=1,
            ),
            "VpcId": st.sampled_from(["vpc-1", "vpc-2"]),
            "AvailabilityZone": st.sampled_from(["us-east-1a", "us-east-1b"]),
        },
    ),
    metadata=st.just(spec_metadata),
    raw_response=st.none(),
)


@given(st.lists(resource_spec_strategy, min_size=1, max_size=10))
@settings(max_examples=100)
def test_property_diagram_includes_all_resources_req_6_4(specs: list[ResourceSpec]) -> None:
    pages = _pages(DiagramGenerator().generate_diagram(specs))
    overview = pages["Overview"]
    drawn = {arn for c in overview.vertices() for arn in c.get("arns", "").split("\n") if arn}
    assert {s.arn for s in specs} <= drawn
    for page in pages.values():
        ids = list(page.cells)
        assert len(ids) == len(set(ids))
        for edge in page.edges():
            assert edge["source"] in page.cells and edge["target"] in page.cells


# ============================================================================
# Containers and placement (Req 15.1)
# ============================================================================


class TestDiagramContainers:
    def test_diagram_nested_containers_req_15_1(self, shop_specs):
        page = _overview(shop_specs)
        subnet = page.by_arn(f"{EC2}:subnet/subnet-priv")
        labels = [
            page.cells[a].get("value") or page.cells[a].get("label")
            for a in page.ancestors(subnet["id"])
        ]
        assert labels[0] == "us-east-1a"
        assert "shop-vpc" in labels[1] and "10.0.0.0/16" in labels[1]
        assert labels[2] == "us-east-1"
        assert labels[3].startswith("AWS Cloud")
        styles = [page.cells[a]["style"] for a in page.ancestors(subnet["id"])[:4]]
        styles.append(subnet["style"])
        for style in styles:
            assert "container=1" in style and "dropTarget=1" in style and "fillColor=none" in style
        assert "grIcon=mxgraph.aws4.group_vpc" in styles[1]
        assert "grIcon=mxgraph.aws4.group_region" in styles[2]
        assert "grIcon=mxgraph.aws4.group_aws_cloud_alt" in styles[3]

    def test_diagram_children_use_relative_geometry_req_15_1(self, shop_specs):
        page = _overview(shop_specs)
        for cell in page.vertices():
            parent = cell.get("parent")
            if parent not in page.cells or page.cells[parent].get("vertex") != "1":
                continue
            geometry, box = cell["geometry"], page.cells[parent]["geometry"]
            assert 0 <= float(geometry.get("x")) < float(box.get("width"))
            assert 0 <= float(geometry.get("y")) < float(box.get("height"))
            assert float(geometry.get("x")) + float(geometry.get("width")) <= float(
                box.get("width")
            )
            assert float(geometry.get("y")) + float(geometry.get("height")) <= float(
                box.get("height")
            )

    def test_diagram_places_resources_in_subnet_named_by_spec_req_15_1(self, shop_specs):
        page = _overview(shop_specs)
        public = page.by_arn(f"{EC2}:subnet/subnet-pub")
        private = page.by_arn(f"{EC2}:subnet/subnet-priv")
        assert page.by_arn(LB_ARN)["parent"] == public["id"]
        assert page.by_arn(SERVICE_ARN)["parent"] == private["id"]
        assert page.by_arn(DB_ARN)["parent"] == private["id"]
        assert page.by_arn(INSTANCE_1)["parent"] == private["id"]
        # Public = the subnet's route table routes to an internet gateway.
        assert public["subnet_type"] == "public" and "strokeColor=#7AA116" in public["style"]
        assert private["subnet_type"] == "private" and "strokeColor=#147EBA" in private["style"]
        # The internet gateway sits on the VPC, not in a subnet.
        vpc = page.by_arn(f"{EC2}:vpc/vpc-1")
        assert vpc["id"] in page.ancestors(page.by_arn(f"{EC2}:internet-gateway/igw-1")["id"])

    def test_diagram_edge_services_left_of_vpc_req_15_1(self, shop_specs):
        page = _overview(shop_specs)
        vpc_x = page.absolute(page.by_arn(f"{EC2}:vpc/vpc-1")["id"])[0]
        for arn in (ZONE_ARN, CF_ARN, WAF_ARN):
            x, _, width, _ = page.absolute(page.by_arn(arn)["id"])
            assert x + width < vpc_x
        users = [c for c in page.vertices() if "shape=mxgraph.aws4.users" in c["style"]]
        assert len(users) == 1
        assert page.absolute(users[0]["id"])[0] < page.absolute(page.by_arn(CF_ARN)["id"])[0]


# ============================================================================
# Edges (Req 15.2)
# ============================================================================


def _edge_pairs(page: Page) -> dict[tuple[str, str], dict]:
    def name(cell_id: str) -> str:
        cell = page.cells[cell_id]
        arns = cell.get("arns")
        return arns.split("\n")[0] if arns else cell.get("value") or cell.get("label")

    return {(name(e["source"]), name(e["target"])): e for e in page.edges()}


class TestDiagramEdges:
    def test_diagram_draws_data_flow_edges_only_req_15_2(self, shop_specs):
        page = _overview(shop_specs)
        pairs = _edge_pairs(page)
        assert set(pairs) == {
            ("Users", CF_ARN),
            (ZONE_ARN, CF_ARN),
            (CF_ARN, WAF_ARN),
            (CF_ARN, BUCKET_ARN),
            (CF_ARN, LB_ARN),
            (LB_ARN, SERVICE_ARN),
            (SERVICE_ARN, DB_ARN),
        }
        assert pairs[(LB_ARN, SERVICE_ARN)]["label"] == "HTTPS:443"
        assert pairs[(LB_ARN, SERVICE_ARN)]["relationships"] == "forwards_to,lb_listener,lb_target"
        assert pairs[(SERVICE_ARN, DB_ARN)]["label"] == "5432"
        assert "dashed=1" in pairs[(ZONE_ARN, CF_ARN)]["style"]

    def test_diagram_edges_cite_their_evidence_req_15_2(self, shop_specs):
        page = _overview(shop_specs)
        edge = _edge_pairs(page)[(SERVICE_ARN, DB_ARN)]
        evidence = edge["evidence"].split("\n")
        assert (
            f"{EC2}:security-group/sg-db#specifications.IpPermissions[0].UserIdGroupPairs[0].GroupId"
            in evidence
        )
        assert _edge_pairs(page)[("Users", CF_ARN)]["relationships"] == "entry_point"

    def test_diagram_edges_attach_and_route_left_to_right_req_15_2(self, shop_specs):
        page = _overview(shop_specs)
        for edge in page.edges():
            assert edge["geometry"].get("relative") == "1"
            # The edge belongs to the innermost container holding both ends.
            common = [
                a for a in page.ancestors(edge["source"]) if a in page.ancestors(edge["target"])
            ]
            assert edge["parent"] == (common[0] if common else "1")
        edge = _edge_pairs(page)[(LB_ARN, SERVICE_ARN)]
        assert "exitX=1;exitY=0.5" in edge["style"] and "entryX=0;entryY=0.5" in edge["style"]


# ============================================================================
# Grouping, labels, stencils (Req 15.3)
# ============================================================================


class TestDiagramGrouping:
    def test_diagram_groups_identical_resources_req_15_3(self, shop_specs):
        page = _overview(shop_specs)
        batch = page.by_arn(INSTANCE_1)
        assert batch is page.by_arn(INSTANCE_2)
        assert batch["arns"].split("\n") == [INSTANCE_1, INSTANCE_2]
        assert "batch ×2" in batch["label"]

    def test_diagram_supporting_resources_not_in_flow_req_15_3(self, shop_specs):
        page = _overview(shop_specs)
        roles = page.by_arn(ROLE_A)
        assert roles is page.by_arn(ROLE_B)
        assert "×2" in roles["label"]
        panel = page.cells[roles["parent"]]
        assert panel["value"] == "Supporting resources"
        for arn in (ROLE_A, LOG_ARN, LISTENER_ARN, TG_ARN, f"{EC2}:security-group/sg-app"):
            cell_id = page.by_arn(arn)["id"]
            assert panel["id"] in page.ancestors(cell_id)
            assert all(cell_id not in (e["source"], e["target"]) for e in page.edges())

    def test_diagram_labels_use_name_tags_req_15_3(self, shop_specs):
        page = _overview(shop_specs)
        assert page.by_arn(f"{EC2}:subnet/subnet-pub")["label"].startswith("shop-public-a")
        assert "10.0.1.0/24" in page.by_arn(f"{EC2}:subnet/subnet-pub")["label"]
        assert "<b>web</b>" in page.by_arn(SERVICE_ARN)["label"]
        assert "<b>shop.example.com</b>" in page.by_arn(CF_ARN)["label"]
        assert "ECS service" in page.by_arn(SERVICE_ARN)["label"]

    def test_diagram_uses_verified_stencils_only_req_15_3(self, shop_specs):
        verified = _verified_stencils()
        for page in _pages(DiagramGenerator().generate_diagram(shop_specs)).values():
            for cell in page.vertices():
                for name in _stencils(cell.get("style", "")):
                    assert name in verified, f"unverified stencil {name}"

    def test_registry_styles_use_verified_stencils_req_15_3(self):
        verified = _verified_stencils()
        for info in REGISTRY.values():
            for name in _stencils(info.drawio_style):
                assert name in verified, f"{info.type_id}: unverified stencil {name}"


# ============================================================================
# Pages, layout, determinism (Req 15.4)
# ============================================================================


class TestDiagramPages:
    def test_diagram_has_overview_and_network_pages_req_15_4(self, shop_specs):
        pages = _pages(DiagramGenerator().generate_diagram(shop_specs))
        assert list(pages) == ["Overview", "Network detail"]
        for page in pages.values():
            first = list(page.cells.values())[2]
            assert "fillColor=#F5F5F5" in first["style"]  # background, lowest z-order
            titles = [c for c in page.vertices() if c.get("style", "").startswith("text;")]
            assert titles and "AWS architecture" in titles[0]["value"]
            assert ACCOUNT in titles[0]["value"]

    def test_diagram_network_page_shows_routing_req_15_4(self, shop_specs):
        page = _pages(DiagramGenerator().generate_diagram(shop_specs))["Network detail"]
        pairs = _edge_pairs(page)
        rtb = f"{EC2}:route-table/rtb-pub"
        assert pairs[(rtb, f"{EC2}:internet-gateway/igw-1")]["label"] == "0.0.0.0/0"
        assert (rtb, f"{EC2}:subnet/subnet-pub") in pairs
        assert page.by_arn(f"{EC2}:security-group/sg-db")
        assert not [c for c in page.vertices() if SERVICE_ARN in c.get("arns", "")]

    def test_diagram_is_deterministic_req_15_4(self, shop_specs):
        generator = DiagramGenerator()
        assert generator.generate_diagram(shop_specs) == generator.generate_diagram(
            list(reversed(shop_specs))
        )

    def test_diagram_golden_file_for_sample_account_req_15_4(self):
        """examples/output/diagrams/architecture.drawio is what the generator produces."""
        specs = OutputGenerator.load_specs(EXAMPLE_DIR)
        relationships = AnalysisEngine().analyze(specs).relationships
        golden = (EXAMPLE_DIR / "diagrams" / "architecture.drawio").read_text(encoding="utf-8")
        assert DiagramGenerator().generate_diagram(specs, relationships) == golden

    def test_diagram_sample_account_traffic_flow_req_15_2(self):
        specs = OutputGenerator.load_specs(EXAMPLE_DIR)
        page = _pages(DiagramGenerator().generate_diagram(specs))["Overview"]
        kinds = {
            (
                page.cells[e["source"]].get("resource_type", "users"),
                page.cells[e["target"]].get("resource_type"),
            )
            for e in page.edges()
        }
        assert {
            ("users", "aws_cloudfront_distribution"),
            ("aws_cloudfront_distribution", "aws_lb"),
            ("aws_lb", "aws_ecs_service"),
            ("aws_ecs_service", "aws_db_instance"),
            ("aws_ecs_service", "aws_elasticache_replication_group"),
        } <= kinds
        assert not {k for k in kinds if "aws_iam_role" in k or "aws_cloudwatch_log_group" in k}

    def test_diagram_empty_specs_is_valid(self):
        pages = _pages(DiagramGenerator().generate_diagram([]))
        assert list(pages) == ["Overview", "Network detail"]


# ============================================================================
# External CLIs: drawio-ai validation and PNG export (Req 6.4, 15.4)
# ============================================================================


def test_diagram_validate_with_drawio_ai_skipped_when_missing_req_6_4(tmp_path, monkeypatch):
    from src import diagram_generator as module

    monkeypatch.setattr(module.shutil, "which", lambda name: None)
    ok, message = module.validate_with_drawio_ai(tmp_path / "x.drawio")
    assert ok is None and "skipped" in message


def test_diagram_validate_with_drawio_ai_runs_cli_req_6_4(tmp_path, monkeypatch):
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


def test_diagram_export_png_skipped_without_drawio_cli_req_15_4(tmp_path, monkeypatch):
    from src import diagram_generator as module

    monkeypatch.setattr(module.shutil, "which", lambda name: None)
    monkeypatch.setattr(module, "DRAWIO_APP_PATHS", ())
    ok, message = module.export_png(tmp_path / "architecture.drawio")
    assert ok is None and "skipped" in message


def test_diagram_export_png_runs_drawio_cli_req_15_4(tmp_path, monkeypatch):
    from unittest.mock import Mock

    from src import diagram_generator as module

    monkeypatch.setattr(
        module.shutil, "which", lambda name: "/usr/bin/drawio" if name == "drawio" else None
    )
    run = Mock(return_value=Mock(returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(module.subprocess, "run", run)
    source = tmp_path / "architecture.drawio"
    ok, message = module.export_png(source)
    assert ok is True and "architecture.drawio.png" in message
    assert run.call_args.args[0] == [
        "/usr/bin/drawio",
        "-x",
        "-f",
        "png",
        "-e",
        "-b",
        "10",
        "-o",
        str(tmp_path / "architecture.drawio.png"),
        str(source),
    ]
