#!/usr/bin/env python3
"""Test economics markets through MCP server"""

import asyncio
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from openmcp.client import open_connection
from openmcp.types import ClientRequest, CallToolRequest, CallToolRequestParams, CallToolResult

SERVER_URL = "http://127.0.0.1:8000/mcp"

async def test_economics():
    """Test economics markets analysis"""

    print("=" * 80)
    print("Testing Economics Markets via MCP Server")
    print("=" * 80)
    print()

    async with open_connection(url=SERVER_URL, transport="streamable-http") as client:
        print(f"Connected to server: {client.initialize_result.serverInfo.name}")
        print()

        # Test with limit 10
        print("Analyzing economics markets (limit 10)...")
        print("-" * 80)
        try:
            result = await client.send_request(
                ClientRequest(CallToolRequest(
                    params=CallToolRequestParams(
                        name="analyze_economics_markets",
                        arguments={"limit": 10}
                    )
                )),
                CallToolResult
            )
            for content in result.content:
                if hasattr(content, 'text'):
                    data = json.loads(content.text)
                    print(json.dumps(data, indent=2))
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()

if __name__ == "__main__":
    asyncio.run(test_economics())
