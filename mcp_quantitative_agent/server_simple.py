#!/usr/bin/env python3
"""
Simple MCP Server Wrapper for Quantitative Agent

This is a simplified version that uses the standalone quantitative_agent module.
Works with or without MCP library installed.
"""

import sys
import json
from pathlib import Path

# Import standalone agent
from quantitative_agent import QuantitativeAgent

# Try to import MCP
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    import asyncio
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP library not available. Install with: pip install mcp", file=sys.stderr)
    print("The quantitative_agent.py can still be used as a standalone CLI tool.", file=sys.stderr)
    sys.exit(1)

# Initialize agent
agent = QuantitativeAgent()

# Initialize MCP server
app = Server("quantitative-agent")

@app.list_tools()
async def list_tools():
    """List available quantitative analysis tools"""
    return [
        Tool(
            name="analyze_weather_markets",
            description="Analyze weather markets using 3 statistical sources: NOAA (GFS), Open-Meteo (ECMWF), and Climatology. Returns market analysis with probabilities, edge calculations, and trading recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of markets to analyze (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="analyze_politics_markets",
            description="Analyze politics markets using 3 statistical sources: Kalshi Market Consensus, Historical Voting Patterns, and Betting Market Model. Returns market analysis with probabilities, edge calculations, and trading recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of markets to analyze (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="analyze_economics_markets",
            description="Analyze economics markets using 3 statistical sources: FRED (Federal Reserve), Economic Indicators (Alpha Vantage/BLS/World Bank), and Kalshi Market Consensus. Returns market analysis with probabilities, edge calculations, and trading recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of markets to analyze (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="analyze_single_market",
            description="Analyze a single market by ticker. Automatically determines category (weather/politics/economics) and uses appropriate quantitative sources.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Kalshi market ticker (e.g., 'KXHIGHNY-25NOV08-T71')"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_market_categories",
            description="Get available market categories and their quantitative sources",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute quantitative analysis tools"""
    
    try:
        if name == "analyze_weather_markets":
            limit = arguments.get("limit", 10)
            result = agent.analyze_category("weather", limit)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analyze_politics_markets":
            limit = arguments.get("limit", 10)
            result = agent.analyze_category("politics", limit)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analyze_economics_markets":
            limit = arguments.get("limit", 10)
            result = agent.analyze_category("economics", limit)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "analyze_single_market":
            ticker = arguments.get("ticker")
            if not ticker:
                return [TextContent(type="text", text=json.dumps({"error": "Ticker is required"}, indent=2))]
            result = agent.analyze_single_market(ticker)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_market_categories":
            result = agent.get_categories()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2))]
    
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e), "message": f"Error executing tool {name}: {e}"}, indent=2))]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())

