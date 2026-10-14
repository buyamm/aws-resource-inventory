"""
MCP stdio transport

Registers the four whitelisted tools on a FastMCP server (official ``mcp`` SDK);
every tool delegates to ``MCPServer.handle_request`` and returns its dict.
The server process runs without AWS credentials (``sandbox_environment``).

Usage: ``aws-inventory mcp-serve --cache-dir <Output_Dir>``
(or ``python -m src.mcp_stdio --cache-dir <Output_Dir>``).

Requirements Coverage:
- Requirement 5.1: Four MCP tools over stdio
- Requirement 9.7: No AWS credentials in the MCP server environment
"""

from __future__ import annotations

import argparse
import os
from collections.abc import MutableMapping
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.mcp_server import MCPServer

SANDBOX_CONFIG_PATH = "/nonexistent/aws-resource-inventory"

INSTRUCTIONS = (
    "Read-only access to AWS resource specifications collected by `aws-inventory collect`. "
    "Answers come only from the cached spec files; every analysis statement carries "
    "citations (spec_file, property_path, source_checksum, evidence_value)."
)


def sandbox_environment(environ: MutableMapping[str, str]) -> MutableMapping[str, str]:
    """Remove every ``AWS_*`` variable and point the AWS config files nowhere (Req 9.7)."""
    for name in [key for key in environ if key.startswith("AWS_")]:
        del environ[name]
    environ["AWS_SHARED_CREDENTIALS_FILE"] = SANDBOX_CONFIG_PATH
    environ["AWS_CONFIG_FILE"] = SANDBOX_CONFIG_PATH
    return environ


def _present(**params: Any) -> dict[str, Any]:
    return {name: value for name, value in params.items() if value is not None}


def build_server(cache_dir: str, core: MCPServer | None = None) -> FastMCP:
    """FastMCP server exposing the four tools over the cache at ``cache_dir``."""
    handler = core or MCPServer(cache_dir)
    server = FastMCP("aws-resource-inventory", instructions=INSTRUCTIONS, log_level="WARNING")

    @server.tool(
        name="list-resources",
        description=(
            "List collected resources (arn, resource_type, region, account_id, resource_id, "
            "spec_file, checksum). Optional filters: region (e.g. us-east-1 or global) and "
            "resource_type (canonical Terraform type such as aws_lambda_function, or an alias)."
        ),
    )
    def list_resources(region: str | None = None, resource_type: str | None = None) -> dict:
        return handler.handle_request(
            "list-resources", _present(region=region, resource_type=resource_type)
        )

    @server.tool(
        name="get-resource-spec",
        description="Return the sanitized specification file of the collected resource with this ARN.",
    )
    def get_resource_spec(arn: str) -> dict:
        return handler.handle_request("get-resource-spec", {"arn": arn})

    @server.tool(
        name="analyze-activity-flow",
        description=(
            "Rule-based relationships, architecture patterns and security findings over the "
            "collected resources, each with citations. With arn, only statements involving it."
        ),
    )
    def analyze_activity_flow(arn: str | None = None) -> dict:
        return handler.handle_request("analyze-activity-flow", _present(arn=arn))

    @server.tool(
        name="generate-documentation",
        description=(
            "Generate infrastructure documentation (Markdown) in memory; every statement has "
            "[cite: ...] markers and the citations are returned alongside."
        ),
    )
    def generate_documentation() -> dict:
        return handler.handle_request("generate-documentation", {})

    return server


def serve(cache_dir: str) -> None:
    """Run the MCP server on stdio without AWS credentials."""
    sandbox_environment(os.environ)
    build_server(cache_dir).run("stdio")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="AWS Resource Inventory MCP server (stdio)")
    parser.add_argument("--cache-dir", required=True, help="Output_Dir of `aws-inventory collect`")
    args = parser.parse_args(argv)
    serve(args.cache_dir)


if __name__ == "__main__":
    main()
