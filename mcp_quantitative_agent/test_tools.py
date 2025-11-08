#!/usr/bin/env python3
"""Test the MCP server tools"""

import asyncio
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openmcp.client import open_connection
from openmcp.types import ClientRequest, CallToolRequest, CallToolRequestParams, CallToolResult

SERVER_URL = "http://127.0.0.1:8000/mcp"

async def test_tools():
    """Test all MCP server tools"""

    print("=" * 80)
    print("Testing MCP Quantitative Agent Tools")
    print("=" * 80)
    print()

    async with open_connection(url=SERVER_URL, transport="streamable-http") as client:
        print(f"Connected to server: {client.initialize_result.serverInfo.name}")
        print(f"Protocol version: {client.initialize_result.protocolVersion}")
        print()

        # Test 1: Get market categories
        print("Test 1: Getting market categories...")
        print("-" * 80)
        try:
            result = await client.send_request(
                ClientRequest(CallToolRequest(
                    params=CallToolRequestParams(
                        name="get_market_categories",
                        arguments={}
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

        # Test 2: Analyze weather markets (limit 3)
        print("Test 2: Analyzing weather markets (limit 3)...")
        print("-" * 80)
        try:
            result = await client.send_request(
                ClientRequest(CallToolRequest(
                    params=CallToolRequestParams(
                        name="analyze_weather_markets",
                        arguments={"limit": 3}
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

        # Test 3: Analyze politics markets (limit 10 - some may be filtered)
        print("Test 3: Analyzing politics markets (limit 10)...")
        print("-" * 80)
        try:
            result = await client.send_request(
                ClientRequest(CallToolRequest(
                    params=CallToolRequestParams(
                        name="analyze_politics_markets",
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

        # Test 4: Analyze economics markets (limit 3)
        print("Test 4: Analyzing economics markets (limit 3)...")
        print("-" * 80)
        try:
            result = await client.send_request(
                ClientRequest(CallToolRequest(
                    params=CallToolRequestParams(
                        name="analyze_economics_markets",
                        arguments={"limit": 3}
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

    print("=" * 80)
    print("All tests completed!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_tools())
