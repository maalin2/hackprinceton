#!/usr/bin/env python3
"""
Quantitative Market Analysis Agent entry point.

Default behaviour uses the Dedalus SDK to run a prompt that invokes the
quant-ts MCP server. When the environment variable QUANT_AGENT_DIRECT=1 is
set, the script connects directly to the quant-ts MCP server via the MCP
Python client. This makes it possible to run local smoke tests without
real Dedalus credentials.
"""

import asyncio
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


async def run_with_dedalus(server_name: str, query: str) -> None:
    """Execute the agent using the Dedalus SDK."""
    from dedalus_labs import AsyncDedalus, DedalusRunner

    print("Initializing Dedalus client...")
    client = AsyncDedalus()
    runner = DedalusRunner(client)

    print(f"Starting agent with MCP server: {server_name}")
    print(f"Query: {query}")
    print("=" * 80)

    result = await runner.run(
        input=query,
        model="anthropic/claude-sonnet-4-5-20250929",
        mcp_servers=["quant-ts"],
        stream=False,
    )

    print("\n" + "=" * 80)
    print("RESULT:")
    print("=" * 80)
    print(result.final_output)


async def run_direct(server_name: str, query: str, tool: str, limit: Optional[int]) -> None:
    """Direct MCP mode used for local testing without Dedalus."""
    print("Running in direct MCP mode (QUANT_AGENT_DIRECT=1)")
    quant_ts_dir = os.environ.get("QUANT_TS_DIR")
    if not quant_ts_dir:
        raise RuntimeError("QUANT_TS_DIR must be set when QUANT_AGENT_DIRECT=1")

    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command="node",
        args=["dist/index.js", "--stdio"],
        cwd=quant_ts_dir,
        env=None,
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected to quant-ts MCP server")

            arguments = {}
            if limit is not None:
                arguments["limit"] = limit

            print(f"Calling MCP tool: {tool} with arguments {arguments}")
            result = await session.call_tool(tool, arguments)

            print("\n" + "=" * 80)
            print("RESULT:")
            print("=" * 80)
            for content in result.content:
                payload = getattr(content, "text", None)
                if payload:
                    print(payload)
            print("=" * 80)


async def main():
    server_name = os.environ.get("QUANT_AGENT_SERVER", "quant-ts")
    query = os.environ.get("QUANT_AGENT_QUERY", "Get the top 5 economic markets on kalshi. Look at investor sentiment with grok")

    direct_mode = os.environ.get("QUANT_AGENT_DIRECT") == "1"
    tool = os.environ.get("QUANT_AGENT_TOOL", "analyze_weather_markets")
    limit_env = os.environ.get("QUANT_AGENT_LIMIT")
    limit = int(limit_env) if limit_env else None

    if direct_mode:
        await run_direct(server_name, query, tool, limit)
    else:
        await run_with_dedalus(server_name, query)


if __name__ == "__main__":
    asyncio.run(main())
