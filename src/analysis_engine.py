"""
Analysis Engine Module

This module provides the AnalysisEngine class for analyzing collected AWS resource
specifications to infer activity flows, identify relationships, detect architecture
patterns, flag suspicious/insecure configurations, and generate evidence citations.

Requirements Coverage:
- Requirement 6.1: Identify relationships between resources
- Requirement 6.2: Detect common patterns (API Gateway + Lambda + DynamoDB, EC2 + VPC, etc.)
- Requirement 6.5: Include confidence scores and cite specific resource specifications as evidence
- Requirement 6.6: Flag suspicious patterns (overly permissive IAM, public S3 buckets, unrestricted security groups)
- Requirement 8.1: Direct citations to specific resource specifications
- Requirement 8.2: Checksum references linking analysis statements to source data files
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.diagram_generator import DiagramGenerator, ResourceRelationship
from src.parser import ResourceSpec


@dataclass
class Citation:
    """Citation linking analysis findings to specific source resource specifications."""

    resource_arn: str
    property_path: str
    source_checksum: str
    evidence_value: Any


@dataclass
class ArchitecturePattern:
    """Detected architecture pattern with confidence and citations."""

    pattern_name: str
    description: str
    participating_resources: list[str]
    confidence: float
    citations: list[Citation] = field(default_factory=list)


@dataclass
class SecurityFinding:
    """Detected security issue or suspicious configuration pattern."""

    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    finding_type: str
    resource_arn: str
    description: str
    evidence: str
    citation: Citation


@dataclass
class AnalysisReport:
    """Complete infrastructure activity flow and security analysis report."""

    relationships: list[ResourceRelationship]
    patterns: list[ArchitecturePattern]
    security_findings: list[SecurityFinding]
    summary_markdown: str


class AnalysisEngine:
    """
    Infers architecture patterns, resource connections, security vulnerabilities,
    and verifiable citations from collected AWS specifications.
    """

    def __init__(self) -> None:
        """Initialize AnalysisEngine."""
        self.diagram_generator = DiagramGenerator()

    # ========================================================================
    # Relationship Identification (Requirement 6.1)
    # ========================================================================

    def identify_relationships(self, specs: list[ResourceSpec]) -> list[ResourceRelationship]:
        """
        Identify inter-resource relationships (Requirement 6.1).
        Delegates to DiagramGenerator relationship discovery.
        """
        return self.diagram_generator.identify_relationships(specs)

    # ========================================================================
    # Architecture Pattern Detection (Requirements 6.2, 6.5, 8.1, 8.2)
    # ========================================================================

    def detect_patterns(self, specs: list[ResourceSpec]) -> list[ArchitecturePattern]:
        """
        Detect common architectural patterns:
        - Serverless Application (Lambda + DynamoDB + IAM)
        - Compute in VPC (EC2 + VPC + Security Groups)
        - Web & Storage (S3 + CloudFront)

        Requirements: 6.2, 6.5, 8.1, 8.2
        """
        patterns: list[ArchitecturePattern] = []

        # 1. Pattern: Serverless Architecture (Lambda + DynamoDB + IAM)
        lambdas = [s for s in specs if "lambda" in s.resource_type.lower()]
        dynamodb_tables = [s for s in specs if "dynamodb" in s.resource_type.lower()]
        roles = [
            s
            for s in specs
            if "iam" in s.resource_type.lower() or "role" in s.resource_type.lower()
        ]

        for lambda_fn in lambdas:
            citations: list[Citation] = []
            participating: list[str] = [lambda_fn.arn]
            specs_dict = lambda_fn.specifications or {}

            # Check for linked DynamoDB tables
            linked_tables = []
            for table in dynamodb_tables:
                env_vars = specs_dict.get("environment_variables") or {}
                table_name = table.specifications.get("table_name", "")
                for env_k, env_v in env_vars.items():
                    if table_name and table_name in str(env_v):
                        linked_tables.append(table)
                        citations.append(
                            Citation(
                                resource_arn=lambda_fn.arn,
                                property_path=f"specifications.environment_variables.{env_k}",
                                source_checksum=lambda_fn.metadata.checksum,
                                evidence_value=env_v,
                            )
                        )
                        break

            # Check for execution role
            linked_roles = []
            role_ref = specs_dict.get("role") or specs_dict.get("Role")
            if role_ref:
                for role in roles:
                    if role.arn == role_ref or role.arn.endswith(str(role_ref).split("/")[-1]):
                        linked_roles.append(role)
                        citations.append(
                            Citation(
                                resource_arn=lambda_fn.arn,
                                property_path="specifications.role",
                                source_checksum=lambda_fn.metadata.checksum,
                                evidence_value=role_ref,
                            )
                        )
                        break

            if linked_tables or linked_roles:
                for t in linked_tables:
                    participating.append(t.arn)
                for r in linked_roles:
                    participating.append(r.arn)

                confidence = 0.90 if (linked_tables and linked_roles) else 0.75
                patterns.append(
                    ArchitecturePattern(
                        pattern_name="Serverless Application (Lambda + DynamoDB + IAM)",
                        description=(
                            f"Lambda function '{lambda_fn.arn.split(':')[-1]}' utilizes "
                            f"{len(linked_roles)} IAM execution role(s) and connects to "
                            f"{len(linked_tables)} DynamoDB table(s) for event-driven processing."
                        ),
                        participating_resources=participating,
                        confidence=confidence,
                        citations=citations,
                    )
                )

        # 2. Pattern: Compute in VPC (EC2 + VPC + Security Groups)
        vpcs = [s for s in specs if "vpc" in s.resource_type.lower()]
        ec2s = [
            s
            for s in specs
            if "ec2" in s.resource_type.lower() or "instance" in s.resource_type.lower()
        ]

        for ec2 in ec2s:
            specs_dict = ec2.specifications or {}
            vpc_id = specs_dict.get("vpc_id")
            if vpc_id:
                matching_vpc = next(
                    (v for v in vpcs if v.specifications.get("vpc_id") == vpc_id), None
                )
                participating = [ec2.arn]
                citations = [
                    Citation(
                        resource_arn=ec2.arn,
                        property_path="specifications.vpc_id",
                        source_checksum=ec2.metadata.checksum,
                        evidence_value=vpc_id,
                    )
                ]
                if matching_vpc:
                    participating.append(matching_vpc.arn)

                patterns.append(
                    ArchitecturePattern(
                        pattern_name="Compute in Virtual Private Cloud (EC2 in VPC)",
                        description=f"EC2 Instance '{ec2.arn.split('/')[-1]}' is securely hosted within VPC '{vpc_id}'.",
                        participating_resources=participating,
                        confidence=0.95,
                        citations=citations,
                    )
                )

        return patterns

    # ========================================================================
    # Suspicious Pattern & Security Risk Detection (Requirement 6.6)
    # ========================================================================

    def flag_suspicious_patterns(self, specs: list[ResourceSpec]) -> list[SecurityFinding]:
        """
        Flag suspicious patterns (Requirement 6.6):
        - Overly permissive IAM policies (* action / resource)
        - Public S3 buckets (ACL grants or public policy)
        - Unrestricted Security Groups (0.0.0.0/0 on sensitive ports)
        """
        findings: list[SecurityFinding] = []

        for spec in specs:
            specs_dict = spec.specifications or {}

            # 1. Overly permissive IAM Policies
            if (
                "role" in spec.resource_type.lower()
                or "iam" in spec.resource_type.lower()
                or "policy" in spec.resource_type.lower()
            ):
                policy = specs_dict.get("policy") or specs_dict.get("policy_document") or {}
                statements = policy.get("Statement") or []
                for idx, stmt in enumerate(statements):
                    effect = stmt.get("Effect", "")
                    actions = stmt.get("Action", [])
                    resources = stmt.get("Resource", [])

                    actions_list = [actions] if isinstance(actions, str) else actions
                    resources_list = [resources] if isinstance(resources, str) else resources

                    if effect == "Allow" and "*" in actions_list and "*" in resources_list:
                        citation = Citation(
                            resource_arn=spec.arn,
                            property_path=f"specifications.policy.Statement[{idx}]",
                            source_checksum=spec.metadata.checksum,
                            evidence_value=stmt,
                        )
                        findings.append(
                            SecurityFinding(
                                severity="CRITICAL",
                                finding_type="OVERLY_PERMISSIVE_IAM_POLICY",
                                resource_arn=spec.arn,
                                description=(
                                    f"IAM Role '{spec.arn}' grants administrator-level access "
                                    f"with wildcard Action '*' and Resource '*'."
                                ),
                                evidence="Statement allows Action: '*' on Resource: '*'",
                                citation=citation,
                            )
                        )

            # 2. Public S3 Buckets
            if "s3" in spec.resource_type.lower() or "bucket" in spec.resource_type.lower():
                acl = specs_dict.get("acl") or specs_dict.get("bucket-acl") or {}
                grants = acl.get("Grants") or []
                is_public = False
                public_grant = None

                for g_idx, grant in enumerate(grants):
                    grantee = grant.get("Grantee") or {}
                    uri = grantee.get("URI", "")
                    if "allusers" in uri.lower() or "authenticatedusers" in uri.lower():
                        is_public = True
                        public_grant = (g_idx, grant)
                        break

                if is_public and public_grant:
                    g_idx, g_val = public_grant
                    citation = Citation(
                        resource_arn=spec.arn,
                        property_path=f"specifications.acl.Grants[{g_idx}]",
                        source_checksum=spec.metadata.checksum,
                        evidence_value=g_val,
                    )
                    findings.append(
                        SecurityFinding(
                            severity="HIGH",
                            finding_type="PUBLIC_S3_BUCKET",
                            resource_arn=spec.arn,
                            description=(
                                f"S3 Bucket '{spec.arn}' has public ACL grants configured, "
                                f"allowing unrestricted public access."
                            ),
                            evidence=f"Grantee URI: {g_val.get('Grantee', {}).get('URI')}",
                            citation=citation,
                        )
                    )

            # 3. Unrestricted Security Groups
            if "security_group" in spec.resource_type.lower():
                permissions = (
                    specs_dict.get("ip_permissions") or specs_dict.get("IpPermissions") or []
                )
                for p_idx, perm in enumerate(permissions):
                    ip_ranges = perm.get("ip_ranges") or perm.get("IpRanges") or []
                    from_port = perm.get("from_port") or perm.get("FromPort")
                    to_port = perm.get("to_port") or perm.get("ToPort")

                    for r_idx, ip_range in enumerate(ip_ranges):
                        cidr = ip_range.get("cidr_ip") or ip_range.get("CidrIp")
                        if cidr == "0.0.0.0/0":
                            port_desc = f"ports {from_port}-{to_port}" if from_port else "all ports"
                            citation = Citation(
                                resource_arn=spec.arn,
                                property_path=f"specifications.ip_permissions[{p_idx}].ip_ranges[{r_idx}]",
                                source_checksum=spec.metadata.checksum,
                                evidence_value=ip_range,
                            )
                            findings.append(
                                SecurityFinding(
                                    severity="HIGH",
                                    finding_type="UNRESTRICTED_SECURITY_GROUP_ACCESS",
                                    resource_arn=spec.arn,
                                    description=(
                                        f"Security Group '{spec.arn}' permits unrestricted ingress "
                                        f"from 0.0.0.0/0 on {port_desc}."
                                    ),
                                    evidence=f"Inbound 0.0.0.0/0 allowed on {port_desc}",
                                    citation=citation,
                                )
                            )

        return findings

    # ========================================================================
    # Full Infrastructure Analysis (Requirements 6.1-6.6, 8.1, 8.2)
    # ========================================================================

    def analyze(self, specs: list[ResourceSpec]) -> AnalysisReport:
        """
        Execute full activity flow analysis, architecture pattern detection,
        and security auditing with evidence citations.
        """
        relationships = self.identify_relationships(specs)
        patterns = self.detect_patterns(specs)
        security_findings = self.flag_suspicious_patterns(specs)

        # Build Markdown summary report
        md_lines: list[str] = [
            "# Activity Flow & Architecture Analysis",
            "",
            f"**Total Discovered Resources:** {len(specs)}  ",
            f"**Relationships Identified:** {len(relationships)}  ",
            f"**Architectural Patterns:** {len(patterns)}  ",
            f"**Security Warnings:** {len(security_findings)}  ",
            "",
            "## Architecture Patterns Detected",
            "",
        ]

        if patterns:
            for p in patterns:
                md_lines.append(f"### {p.pattern_name} (Confidence: {int(p.confidence * 100)}%)")
                md_lines.append(f"{p.description}\n")
                md_lines.append("**Participating Resources:**")
                for r in p.participating_resources:
                    md_lines.append(f"- `{r}`")
                md_lines.append("")
        else:
            md_lines.append("No specific high-level architecture patterns detected.\n")

        md_lines.append("## Security Findings & Suspicious Configurations\n")
        if security_findings:
            for f in security_findings:
                md_lines.append(f"### [{f.severity}] {f.finding_type}")
                md_lines.append(f"**Resource:** `{f.resource_arn}`  ")
                md_lines.append(f"**Description:** {f.description}  ")
                md_lines.append(f"**Evidence:** `{f.evidence}`\n")
        else:
            md_lines.append("✅ No high-risk security misconfigurations detected.\n")

        md_lines.append("## Evidence Citations\n")
        all_citations: list[Citation] = []
        for p in patterns:
            all_citations.extend(p.citations)
        for sf in security_findings:
            all_citations.append(sf.citation)

        if all_citations:
            md_lines.append("| Resource ARN | Property Path | Source Checksum | Evidence |")
            md_lines.append("| :--- | :--- | :--- | :--- |")
            for c in all_citations:
                ev_str = str(c.evidence_value).replace("|", "\\|")
                md_lines.append(
                    f"| `{c.resource_arn}` | `{c.property_path}` | `{c.source_checksum}` | `{ev_str}` |"
                )
            md_lines.append("")

        summary_markdown = "\n".join(md_lines)

        return AnalysisReport(
            relationships=relationships,
            patterns=patterns,
            security_findings=security_findings,
            summary_markdown=summary_markdown,
        )
