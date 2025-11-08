#!/usr/bin/env python3
"""
MCP Server for Quantitative Market Analysis Agent

This server exposes quantitative analysis tools for Kalshi markets:
- Weather markets (3 sources: NOAA, Open-Meteo, Climatology)
- Politics markets (3 sources: Kalshi Consensus, Historical Patterns, Betting Model)
- Economics markets (3 sources: FRED, Economic Indicators, Kalshi Consensus)

Usage:
    python server.py
"""

import asyncio
import json
import sys
from typing import Any, Optional
import importlib.util
import os
from pathlib import Path
import pandas as pd

# Add parent directory to path to import test modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import the test modules
try:
    import weather_test
    import politics_test
    import economics_test
except ImportError as e:
    print(f"Warning: Could not import test modules: {e}", file=sys.stderr)
    # Set dummy modules to avoid errors
    weather_test = None
    politics_test = None
    economics_test = None

# Try to import MCP, fallback to simple implementation if not available
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    # MCP not available, use simple implementation
    MCP_AVAILABLE = False
    Server = None
    stdio_server = None
    Tool = None
    TextContent = None

if MCP_AVAILABLE:
    # Initialize the MCP server
    app = Server("quantitative-agent")
else:
    app = None

# ============================================================================
# Tool Definitions (MCP Mode)
# ============================================================================

if MCP_AVAILABLE:
    @app.list_tools()
    async def list_tools() -> list[Tool]:
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

# ============================================================================
# Tool Implementations
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute quantitative analysis tools"""
    
    if name == "analyze_weather_markets":
        limit = arguments.get("limit", 10)
        result = await analyze_weather_markets(limit)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "analyze_politics_markets":
        limit = arguments.get("limit", 10)
        result = await analyze_politics_markets(limit)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "analyze_economics_markets":
        limit = arguments.get("limit", 10)
        result = await analyze_economics_markets(limit)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "analyze_single_market":
        ticker = arguments.get("ticker")
        if not ticker:
            return [TextContent(type="text", text=json.dumps({"error": "Ticker is required"}, indent=2))]
        result = await analyze_single_market(ticker)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_market_categories":
        result = get_market_categories()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2))]

# ============================================================================
# Analysis Functions
# ============================================================================

async def analyze_weather_markets(limit: int = 10) -> dict:
    """Analyze weather markets using quantitative sources"""
    try:
        if weather_test is None:
            return {
                "status": "error",
                "error": "weather_test module not available",
                "message": "Could not import weather_test module"
            }
        
        # Get markets
        df = weather_test.get_open_weather_markets()
        
        if df.empty:
            return {
                "status": "no_markets",
                "message": "No open weather markets found",
                "markets_analyzed": 0
            }
        
        # Limit markets
        df = df.head(limit)
        
        # Analyze markets
        df_out = weather_test.enrich_with_weather_probs(df)
        
        if df_out.empty:
            return {
                "status": "analysis_failed",
                "message": "Could not analyze markets",
                "markets_analyzed": 0
            }
        
        # Convert to JSON-serializable format
        results = []
        for _, row in df_out.iterrows():
            results.append({
                "ticker": str(row.get("ticker", "")),
                "title": str(row.get("title", "")),
                "combined_p": float(row.get("combined_p", 0)) if pd.notnull(row.get("combined_p")) else None,
                "market_p": float(row.get("market_p", 0)) if pd.notnull(row.get("market_p")) else None,
                "edge": float(row.get("edge", 0)) if pd.notnull(row.get("edge")) else None,
                "edge_pct": float(row.get("edge_pct", 0)) if pd.notnull(row.get("edge_pct")) else None,
                "sources": int(row.get("sources", 0)),
                "confidence": float(row.get("confidence", 0)) if pd.notnull(row.get("confidence")) else None,
                "source_breakdown": str(row.get("source_breakdown", "")),
                "recommendation": get_recommendation(row.get("edge_pct"))
            })
        
        # Calculate summary statistics
        summary = {
            "markets_analyzed": len(df_out),
            "average_edge": float(df_out["edge_pct"].mean()) if df_out["edge_pct"].notna().any() else None,
            "max_edge": float(df_out["edge_pct"].max()) if df_out["edge_pct"].notna().any() else None,
            "markets_with_edge_gt_8": int((df_out["edge_pct"].abs() > 8).sum()) if df_out["edge_pct"].notna().any() else 0,
            "average_confidence": float(df_out["confidence"].mean()) if df_out["confidence"].notna().any() else None
        }
        
        return {
            "status": "success",
            "category": "weather",
            "sources": ["NOAA (GFS)", "Open-Meteo (ECMWF)", "Climatology"],
            "summary": summary,
            "markets": results
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Error analyzing weather markets: {e}"
        }

async def analyze_politics_markets(limit: int = 10) -> dict:
    """Analyze politics markets using quantitative sources"""
    try:
        if politics_test is None:
            return {
                "status": "error",
                "error": "politics_test module not available",
                "message": "Could not import politics_test module"
            }
        
        # Get markets
        df = politics_test.get_open_politics_markets()
        
        if df.empty:
            return {
                "status": "no_markets",
                "message": "No open politics markets found",
                "markets_analyzed": 0
            }
        
        # Limit markets
        df = df.head(limit)
        
        # Analyze markets
        df_out = politics_test.enrich_with_politics_probs(df)
        
        if df_out.empty:
            return {
                "status": "analysis_failed",
                "message": "Could not analyze markets",
                "markets_analyzed": 0
            }
        
        # Convert to JSON-serializable format
        results = []
        for _, row in df_out.iterrows():
            results.append({
                "ticker": str(row.get("ticker", "")),
                "title": str(row.get("title", "")),
                "combined_p": float(row.get("combined_p", 0)) if pd.notnull(row.get("combined_p")) else None,
                "market_p": float(row.get("market_p", 0)) if pd.notnull(row.get("market_p")) else None,
                "edge": float(row.get("edge", 0)) if pd.notnull(row.get("edge")) else None,
                "edge_pct": float(row.get("edge_pct", 0)) if pd.notnull(row.get("edge_pct")) else None,
                "sources": int(row.get("sources", 0)),
                "confidence": float(row.get("confidence", 0)) if pd.notnull(row.get("confidence")) else None,
                "source_breakdown": str(row.get("source_breakdown", "")),
                "recommendation": get_recommendation(row.get("edge_pct"))
            })
        
        # Calculate summary statistics
        summary = {
            "markets_analyzed": len(df_out),
            "average_edge": float(df_out["edge_pct"].mean()) if df_out["edge_pct"].notna().any() else None,
            "max_edge": float(df_out["edge_pct"].max()) if df_out["edge_pct"].notna().any() else None,
            "markets_with_edge_gt_8": int((df_out["edge_pct"].abs() > 8).sum()) if df_out["edge_pct"].notna().any() else 0,
            "average_confidence": float(df_out["confidence"].mean()) if df_out["confidence"].notna().any() else None
        }
        
        return {
            "status": "success",
            "category": "politics",
            "sources": ["Kalshi Market Consensus", "Historical Voting Patterns", "Betting Market Model"],
            "summary": summary,
            "markets": results
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Error analyzing politics markets: {e}"
        }

async def analyze_economics_markets(limit: int = 10) -> dict:
    """Analyze economics markets using quantitative sources"""
    try:
        if economics_test is None:
            return {
                "status": "error",
                "error": "economics_test module not available",
                "message": "Could not import economics_test module"
            }
        
        # Get markets
        df = economics_test.get_open_economics_markets()
        
        if df.empty:
            return {
                "status": "no_markets",
                "message": "No open economics markets found",
                "markets_analyzed": 0
            }
        
        # Limit markets
        df = df.head(limit)
        
        # Analyze markets
        df_out = economics_test.enrich_with_economics_probs(df)
        
        if df_out.empty:
            return {
                "status": "analysis_failed",
                "message": "Could not analyze markets",
                "markets_analyzed": 0
            }
        
        # Convert to JSON-serializable format
        results = []
        for _, row in df_out.iterrows():
            results.append({
                "ticker": str(row.get("ticker", "")),
                "title": str(row.get("title", "")),
                "combined_p": float(row.get("combined_p", 0)) if pd.notnull(row.get("combined_p")) else None,
                "market_p": float(row.get("market_p", 0)) if pd.notnull(row.get("market_p")) else None,
                "edge": float(row.get("edge", 0)) if pd.notnull(row.get("edge")) else None,
                "edge_pct": float(row.get("edge_pct", 0)) if pd.notnull(row.get("edge_pct")) else None,
                "sources": int(row.get("sources", 0)),
                "confidence": float(row.get("confidence", 0)) if pd.notnull(row.get("confidence")) else None,
                "source_breakdown": str(row.get("source_breakdown", "")),
                "recommendation": get_recommendation(row.get("edge_pct"))
            })
        
        # Calculate summary statistics
        summary = {
            "markets_analyzed": len(df_out),
            "average_edge": float(df_out["edge_pct"].mean()) if df_out["edge_pct"].notna().any() else None,
            "max_edge": float(df_out["edge_pct"].max()) if df_out["edge_pct"].notna().any() else None,
            "markets_with_edge_gt_8": int((df_out["edge_pct"].abs() > 8).sum()) if df_out["edge_pct"].notna().any() else 0,
            "average_confidence": float(df_out["confidence"].mean()) if df_out["confidence"].notna().any() else None
        }
        
        return {
            "status": "success",
            "category": "economics",
            "sources": ["FRED", "Economic Indicators (Alpha Vantage/BLS/World Bank)", "Kalshi Market Consensus"],
            "summary": summary,
            "markets": results
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Error analyzing economics markets: {e}"
        }

async def analyze_single_market(ticker: str) -> dict:
    """Analyze a single market by ticker"""
    try:
        # Determine category from ticker
        category = None
        if ticker.startswith(("KXHIGH", "KXRAIN")):
            category = "weather"
            if weather_test is None:
                return {
                    "status": "error",
                    "error": "weather_test module not available",
                    "message": "Could not import weather_test module"
                }
        elif any(keyword in ticker.upper() for keyword in ["GDP", "INFLATION", "UNEMPLOYMENT", "INTEREST", "STOCK"]):
            category = "economics"
            if economics_test is None:
                return {
                    "status": "error",
                    "error": "economics_test module not available",
                    "message": "Could not import economics_test module"
                }
        else:
            category = "politics"  # Default to politics
            if politics_test is None:
                return {
                    "status": "error",
                    "error": "politics_test module not available",
                    "message": "Could not import politics_test module"
                }
        
        # Fetch and analyze based on category
        if category == "weather":
            df = weather_test.get_open_weather_markets()
            if not df.empty:
                market_df = df[df["ticker"] == ticker]
                if not market_df.empty:
                    df_out = weather_test.enrich_with_weather_probs(market_df)
                    if not df_out.empty:
                        row = df_out.iloc[0]
                        return format_market_result(row, "weather")
        
        elif category == "politics":
            df = politics_test.get_open_politics_markets()
            if not df.empty:
                market_df = df[df["ticker"] == ticker]
                if not market_df.empty:
                    df_out = politics_test.enrich_with_politics_probs(market_df)
                    if not df_out.empty:
                        row = df_out.iloc[0]
                        return format_market_result(row, "politics")
        
        elif category == "economics":
            df = economics_test.get_open_economics_markets()
            if not df.empty:
                market_df = df[df["ticker"] == ticker]
                if not market_df.empty:
                    df_out = economics_test.enrich_with_economics_probs(market_df)
                    if not df_out.empty:
                        row = df_out.iloc[0]
                        return format_market_result(row, "economics")
        
        return {
            "status": "not_found",
            "message": f"Market {ticker} not found or could not be analyzed"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Error analyzing market {ticker}: {e}"
        }

def format_market_result(row, category: str) -> dict:
    """Format a single market result"""
    return {
        "status": "success",
        "category": category,
        "ticker": str(row.get("ticker", "")),
        "title": str(row.get("title", "")),
        "combined_p": float(row.get("combined_p", 0)) if pd.notnull(row.get("combined_p")) else None,
        "market_p": float(row.get("market_p", 0)) if pd.notnull(row.get("market_p")) else None,
        "edge": float(row.get("edge", 0)) if pd.notnull(row.get("edge")) else None,
        "edge_pct": float(row.get("edge_pct", 0)) if pd.notnull(row.get("edge_pct")) else None,
        "sources": int(row.get("sources", 0)),
        "confidence": float(row.get("confidence", 0)) if pd.notnull(row.get("confidence")) else None,
        "source_breakdown": str(row.get("source_breakdown", "")),
        "recommendation": get_recommendation(row.get("edge_pct"))
    }

def get_recommendation(edge_pct) -> str:
    """Get trading recommendation based on edge"""
    if pd.isna(edge_pct):
        return "HOLD (no edge data)"
    
    edge_pct = float(edge_pct)
    if edge_pct > 8:
        return "BUY YES"
    elif edge_pct < -8:
        return "BUY NO"
    else:
        return "HOLD"

def get_market_categories() -> dict:
    """Get available market categories and their quantitative sources"""
    return {
        "categories": [
            {
                "name": "weather",
                "sources": [
                    "NOAA (GFS Model)",
                    "Open-Meteo (ECMWF Model)",
                    "Climatology (Historical Averages)"
                ],
                "confidence": "70-85%",
                "indicators": ["Temperature", "Precipitation", "Weather Events"]
            },
            {
                "name": "politics",
                "sources": [
                    "Kalshi Market Consensus",
                    "Historical Voting Patterns",
                    "Betting Market Model"
                ],
                "confidence": "65-85%",
                "indicators": ["Elections", "Nominations", "Approval Ratings", "Policy Outcomes"]
            },
            {
                "name": "economics",
                "sources": [
                    "FRED (Federal Reserve Economic Data)",
                    "Economic Indicators (Alpha Vantage/BLS/World Bank)",
                    "Kalshi Market Consensus"
                ],
                "confidence": "60-85%",
                "indicators": ["GDP", "Inflation", "Unemployment", "Interest Rates", "Stock Market"]
            }
        ],
        "methodology": "All sources use statistical/quantitative methods only (no sentiment analysis)"
    }

# ============================================================================
# Main Entry Point
# ============================================================================

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

