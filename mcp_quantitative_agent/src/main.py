#!/usr/bin/env python3
"""
Dedalus-compatible MCP Server for Quantitative Market Analysis

This server provides quantitative analysis tools for Kalshi markets using HTTP transport.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pandas as pd

# Import test modules
try:
    import weather_test
    import politics_test
    import economics_test
except ImportError as e:
    print(f"Warning: Could not import test modules: {e}", file=sys.stderr)
    weather_test = None
    politics_test = None
    economics_test = None

# Import openmcp for HTTP transport
from openmcp import MCPServer, tool

# Initialize the MCP server
server = MCPServer("quantitative-agent")

# ============================================================================
# Helper Functions
# ============================================================================

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

# ============================================================================
# Tool Definitions
# ============================================================================

with server.binding():

    @tool(description="Get available market categories and their quantitative sources")
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

    @tool(description="Analyze weather markets using 3 statistical sources: NOAA (GFS), Open-Meteo (ECMWF), and Climatology")
    async def analyze_weather_markets(limit: int = 10) -> str:
        """Analyze weather markets using quantitative sources

        Args:
            limit: Maximum number of markets to analyze (default: 10)

        Returns:
            JSON string with market analysis including probabilities, edge calculations, and recommendations
        """
        try:
            if weather_test is None:
                return json.dumps({
                    "status": "error",
                    "error": "weather_test module not available",
                    "message": "Could not import weather_test module"
                }, indent=2)

            # Get markets
            df = weather_test.get_open_weather_markets()

            if df.empty:
                return json.dumps({
                    "status": "no_markets",
                    "message": "No open weather markets found",
                    "markets_analyzed": 0
                }, indent=2)

            # Limit markets
            df = df.head(limit)

            # Analyze markets
            df_out = weather_test.enrich_with_weather_probs(df)

            if df_out.empty:
                return json.dumps({
                    "status": "analysis_failed",
                    "message": "Could not analyze markets",
                    "markets_analyzed": 0
                }, indent=2)

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

            return json.dumps({
                "status": "success",
                "category": "weather",
                "sources": ["NOAA (GFS)", "Open-Meteo (ECMWF)", "Climatology"],
                "summary": summary,
                "markets": results
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Error analyzing weather markets: {e}"
            }, indent=2)

    @tool(description="Analyze politics markets using 3 statistical sources: Kalshi Market Consensus, Historical Voting Patterns, and Betting Market Model")
    async def analyze_politics_markets(limit: int = 10) -> str:
        """Analyze politics markets using quantitative sources

        Args:
            limit: Maximum number of markets to analyze (default: 10)

        Returns:
            JSON string with market analysis including probabilities, edge calculations, and recommendations
        """
        try:
            if politics_test is None:
                return json.dumps({
                    "status": "error",
                    "error": "politics_test module not available",
                    "message": "Could not import politics_test module"
                }, indent=2)

            # Get markets
            df = politics_test.get_open_politics_markets()

            if df.empty:
                return json.dumps({
                    "status": "no_markets",
                    "message": "No open politics markets found",
                    "markets_analyzed": 0
                }, indent=2)

            # Limit markets
            df = df.head(limit)

            # Analyze markets
            df_out = politics_test.enrich_with_politics_probs(df)

            if df_out.empty:
                return json.dumps({
                    "status": "analysis_failed",
                    "message": "Could not analyze markets",
                    "markets_analyzed": 0
                }, indent=2)

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

            return json.dumps({
                "status": "success",
                "category": "politics",
                "sources": ["Kalshi Market Consensus", "Historical Voting Patterns", "Betting Market Model"],
                "summary": summary,
                "markets": results
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Error analyzing politics markets: {e}"
            }, indent=2)

    @tool(description="Analyze economics markets using 3 statistical sources: FRED (Federal Reserve), Economic Indicators (Alpha Vantage/BLS/World Bank), and Kalshi Market Consensus")
    async def analyze_economics_markets(limit: int = 10) -> str:
        """Analyze economics markets using quantitative sources

        Args:
            limit: Maximum number of markets to analyze (default: 10)

        Returns:
            JSON string with market analysis including probabilities, edge calculations, and recommendations
        """
        try:
            if economics_test is None:
                return json.dumps({
                    "status": "error",
                    "error": "economics_test module not available",
                    "message": "Could not import economics_test module"
                }, indent=2)

            # Get markets
            df = economics_test.get_open_economics_markets()

            if df.empty:
                return json.dumps({
                    "status": "no_markets",
                    "message": "No open economics markets found",
                    "markets_analyzed": 0
                }, indent=2)

            # Limit markets
            df = df.head(limit)

            # Analyze markets
            df_out = economics_test.enrich_with_economics_probs(df)

            if df_out.empty:
                return json.dumps({
                    "status": "analysis_failed",
                    "message": "Could not analyze markets",
                    "markets_analyzed": 0
                }, indent=2)

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

            return json.dumps({
                "status": "success",
                "category": "economics",
                "sources": ["FRED", "Economic Indicators (Alpha Vantage/BLS/World Bank)", "Kalshi Market Consensus"],
                "summary": summary,
                "markets": results
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Error analyzing economics markets: {e}"
            }, indent=2)

    @tool(description="Analyze a single market by ticker. Automatically determines category (weather/politics/economics) and uses appropriate quantitative sources")
    async def analyze_single_market(ticker: str) -> str:
        """Analyze a single market by ticker

        Args:
            ticker: Kalshi market ticker (e.g., 'KXHIGHNY-25NOV08-T71')

        Returns:
            JSON string with detailed market analysis
        """
        try:
            # Determine category from ticker
            category = None
            if ticker.startswith(("KXHIGH", "KXRAIN")):
                category = "weather"
                if weather_test is None:
                    return json.dumps({
                        "status": "error",
                        "error": "weather_test module not available",
                        "message": "Could not import weather_test module"
                    }, indent=2)
            elif any(keyword in ticker.upper() for keyword in ["GDP", "INFLATION", "UNEMPLOYMENT", "INTEREST", "STOCK"]):
                category = "economics"
                if economics_test is None:
                    return json.dumps({
                        "status": "error",
                        "error": "economics_test module not available",
                        "message": "Could not import economics_test module"
                    }, indent=2)
            else:
                category = "politics"  # Default to politics
                if politics_test is None:
                    return json.dumps({
                        "status": "error",
                        "error": "politics_test module not available",
                        "message": "Could not import politics_test module"
                    }, indent=2)

            # Fetch and analyze based on category
            if category == "weather":
                df = weather_test.get_open_weather_markets()
                if not df.empty:
                    market_df = df[df["ticker"] == ticker]
                    if not market_df.empty:
                        df_out = weather_test.enrich_with_weather_probs(market_df)
                        if not df_out.empty:
                            row = df_out.iloc[0]
                            return json.dumps(format_market_result(row, "weather"), indent=2)

            elif category == "politics":
                df = politics_test.get_open_politics_markets()
                if not df.empty:
                    market_df = df[df["ticker"] == ticker]
                    if not market_df.empty:
                        df_out = politics_test.enrich_with_politics_probs(market_df)
                        if not df_out.empty:
                            row = df_out.iloc[0]
                            return json.dumps(format_market_result(row, "politics"), indent=2)

            elif category == "economics":
                df = economics_test.get_open_economics_markets()
                if not df.empty:
                    market_df = df[df["ticker"] == ticker]
                    if not market_df.empty:
                        df_out = economics_test.enrich_with_economics_probs(market_df)
                        if not df_out.empty:
                            row = df_out.iloc[0]
                            return json.dumps(format_market_result(row, "economics"), indent=2)

            return json.dumps({
                "status": "not_found",
                "message": f"Market {ticker} not found or could not be analyzed"
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": f"Error analyzing market {ticker}: {e}"
            }, indent=2)

# ============================================================================
# Main Entry Point - HTTP Transport for Dedalus
# ============================================================================

async def main() -> None:
    """Run the MCP server with HTTP transport"""
    await server.serve(transport="streamable-http", verbose=True)

if __name__ == "__main__":
    asyncio.run(main())
