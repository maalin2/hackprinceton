#!/usr/bin/env python3
"""
Test script for MCP Quantitative Agent Server

This script tests the MCP server by calling all available tools.
"""

import asyncio
import json
import sys
from pathlib import Path

# Try to import MCP
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    print("Error: MCP library not installed.")
    print("Install with: pip install mcp")
    sys.exit(1)


async def test_mcp_server():
    """Test the MCP server with all available tools"""
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    server_script = script_dir / "server.py"

    if not server_script.exists():
        print(f"Error: server.py not found at {server_script}")
        sys.exit(1)
    
    print("=" * 80)
    print("Testing MCP Quantitative Agent Server")
    print("=" * 80)
    print()
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)],
        env=None
    )
    
    try:
        # Create client session
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                print("Initializing MCP server...")
                await session.initialize()
                print("✓ Server initialized\n")
                
                # List tools
                print("Fetching available tools...")
                tools = await session.list_tools()
                print(f"✓ Found {len(tools.tools)} tools:\n")
                for tool in tools.tools:
                    print(f"  - {tool.name}")
                    print(f"    {tool.description[:80]}...")
                print()
                
                # Test 1: Get categories
                print("=" * 80)
                print("Test 1: get_market_categories")
                print("=" * 80)
                try:
                    result = await session.call_tool("get_market_categories", {})
                    data = json.loads(result.content[0].text)
                    print("✓ Success")
                    print(f"  Categories: {len(data.get('categories', []))}")
                    for cat in data.get('categories', []):
                        print(f"    - {cat['name']}: {len(cat['sources'])} sources")
                except Exception as e:
                    print(f"✗ Error: {e}")
                print()
                
                # Test 2: Analyze weather markets
                print("=" * 80)
                print("Test 2: analyze_weather_markets (limit=2)")
                print("=" * 80)
                try:
                    result = await session.call_tool("analyze_weather_markets", {"limit": 2})
                    data = json.loads(result.content[0].text)
                    print(f"✓ Status: {data.get('status')}")
                    if data.get('status') == 'success':
                        summary = data.get('summary', {})
                        print(f"  Markets analyzed: {summary.get('markets_analyzed', 0)}")
                        print(f"  Average edge: {summary.get('average_edge', 'N/A')}")
                    else:
                        print(f"  Message: {data.get('message', 'Unknown')}")
                except Exception as e:
                    print(f"✗ Error: {e}")
                print()
                
                # Test 3: Analyze politics markets
                print("=" * 80)
                print("Test 3: analyze_politics_markets (limit=2)")
                print("=" * 80)
                try:
                    result = await session.call_tool("analyze_politics_markets", {"limit": 2})
                    data = json.loads(result.content[0].text)
                    print(f"✓ Status: {data.get('status')}")
                    if data.get('status') == 'success':
                        summary = data.get('summary', {})
                        print(f"  Markets analyzed: {summary.get('markets_analyzed', 0)}")
                    else:
                        print(f"  Message: {data.get('message', 'Unknown')}")
                except Exception as e:
                    print(f"✗ Error: {e}")
                print()
                
                # Test 4: Analyze economics markets
                print("=" * 80)
                print("Test 4: analyze_economics_markets (limit=2)")
                print("=" * 80)
                try:
                    result = await session.call_tool("analyze_economics_markets", {"limit": 2})
                    data = json.loads(result.content[0].text)
                    print(f"✓ Status: {data.get('status')}")
                    if data.get('status') == 'success':
                        summary = data.get('summary', {})
                        print(f"  Markets analyzed: {summary.get('markets_analyzed', 0)}")
                    else:
                        print(f"  Message: {data.get('message', 'Unknown')}")
                except Exception as e:
                    print(f"✗ Error: {e}")
                print()
                
                # Test 5: Analyze single market (if we have a ticker)
                print("=" * 80)
                print("Test 5: analyze_single_market")
                print("=" * 80)
                # Try a common weather market ticker format
                test_ticker = "KXHIGHNY-25NOV08-T71"
                try:
                    result = await session.call_tool("analyze_single_market", {"ticker": test_ticker})
                    data = json.loads(result.content[0].text)
                    print(f"✓ Status: {data.get('status')}")
                    if data.get('status') == 'success':
                        print(f"  Ticker: {data.get('ticker')}")
                        print(f"  Recommendation: {data.get('recommendation')}")
                    else:
                        print(f"  Message: {data.get('message', 'Unknown')}")
                        print(f"  (This is OK if the market doesn't exist)")
                except Exception as e:
                    print(f"✗ Error: {e}")
                print()

                # Test 6: Sentiment Analysis (Grok API test)
                print("=" * 80)
                print("Test 6: sentiment_analysis (Grok API test)")
                print("=" * 80)
                try:
                    # Use a real market for testing
                    result = await session.call_tool("sentiment_analysis", {
                        "market_title": "Will the high temperature in New York City be above 70°F?",
                        "market_ticker": "KXHIGHNY"
                    })
                    data = json.loads(result.content[0].text)
                    print(f"✓ Status: {data.get('status')}")
                    if data.get('status') == 'success':
                        print(f"  Title: {data.get('title')}")
                        print(f"  Ticker: {data.get('ticker')}")
                        print(f"  Sentiment Score: {data.get('sentiment_score')}")
                        print(f"  Sentiment Label: {data.get('sentiment_label')}")
                        print(f"  Key Themes: {data.get('key_themes')}")
                        print(f"  Market Impact: {data.get('market_impact')}")
                        print(f"  Confidence: {data.get('confidence')}")
                    else:
                        print(f"  Error: {data.get('error', 'Unknown')}")
                        print(f"  Message: {data.get('message', 'Unknown')}")
                except Exception as e:
                    print(f"✗ Error: {e}")
                print()

                print("=" * 80)
                print("Testing Complete!")
                print("=" * 80)
    
    except Exception as e:
        print(f"\n✗ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())

