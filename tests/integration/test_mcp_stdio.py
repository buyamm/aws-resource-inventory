"""
Integration tests for the MCP stdio transport (official ``mcp`` SDK).

Requirements Coverage:
- Requirement 5.1: Exactly four tools over stdio; tool calls round-trip to MCPServer
- Requirement 9.7: The MCP server process runs without AWS credentials
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.mcp_stdio import SANDBOX_CONFIG_PATH, sandbox_environment
from src.output_generator import OutputGenerator
from src.parser import ResourceSpec, SpecMetadata

REPO_ROOT = Path(__file__).resolve().parents[2]
FUNCTION_ARN = "arn:aws:lambda:us-east-1:123456789012:function:my-func"


def _cache(tmp_path: Path) -> Path:
    spec = ResourceSpec(
        resource_type="aws_lambda_function",
        arn=FUNCTION_ARN,
        region="us-east-1",
        account_id="123456789012",
        specifications={"FunctionName": "my-func", "Runtime": "python3.11"},
        metadata=SpecMetadata("2026-10-07T12:00:00Z", "1.0.0", "2026-01-01", ""),
    )
    OutputGenerator(output_dir=tmp_path).generate_json([spec])
    return tmp_path


def _server_params(cache_dir: Path) -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "src.mcp_stdio", "--cache-dir", str(cache_dir)],
        cwd=str(REPO_ROOT),
    )


def _tool_json(result) -> dict:
    assert not result.isError
    return json.loads(result.content[0].text)


async def test_mcp_stdio_lists_four_tools_req_5_1(tmp_path):
    async with stdio_client(_server_params(_cache(tmp_path))) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools

    by_name = {tool.name: tool for tool in tools}
    assert sorted(by_name) == [
        "analyze-activity-flow",
        "generate-documentation",
        "get-resource-spec",
        "list-resources",
    ]
    assert by_name["get-resource-spec"].inputSchema["required"] == ["arn"]
    assert set(by_name["list-resources"].inputSchema["properties"]) == {"region", "resource_type"}
    assert set(by_name["analyze-activity-flow"].inputSchema["properties"]) == {"arn"}
    assert by_name["generate-documentation"].inputSchema.get("properties", {}) == {}


async def test_mcp_stdio_tool_call_roundtrip_req_5_1(tmp_path):
    async with stdio_client(_server_params(_cache(tmp_path))) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = _tool_json(
                await session.call_tool("list-resources", {"resource_type": "lambda"})
            )
            spec = _tool_json(await session.call_tool("get-resource-spec", {"arn": FUNCTION_ARN}))
            missing = _tool_json(
                await session.call_tool("get-resource-spec", {"arn": FUNCTION_ARN + "-x"})
            )

    assert listed["status"] == "ok"
    assert [item["arn"] for item in listed["data"]] == [FUNCTION_ARN]
    assert spec["status"] == "ok"
    assert spec["data"]["specifications"]["FunctionName"] == "my-func"
    assert missing["status"] == "error"
    assert "aws-inventory collect" in missing["message"]


def test_sandbox_environment_removes_aws_vars_req_9_7():
    environ = {
        "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "AWS_SESSION_TOKEN": "token",
        "AWS_PROFILE": "prod",
        "AWS_CONTAINER_CREDENTIALS_FULL_URI": "http://169.254.170.2/creds",
        "AWS_WEB_IDENTITY_TOKEN_FILE": "/var/run/token",
        "PATH": "/usr/bin",
        "HOME": "/home/user",
    }
    result = sandbox_environment(environ)

    assert result is environ
    assert environ == {
        "PATH": "/usr/bin",
        "HOME": "/home/user",
        "AWS_SHARED_CREDENTIALS_FILE": SANDBOX_CONFIG_PATH,
        "AWS_CONFIG_FILE": SANDBOX_CONFIG_PATH,
    }
    assert SANDBOX_CONFIG_PATH == "/nonexistent/aws-resource-inventory"
