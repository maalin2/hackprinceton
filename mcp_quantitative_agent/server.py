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
from typing import Any, Optional, List, Dict
import importlib.util
import os
from pathlib import Path
import pandas as pd
import numpy as np
import math
import requests
from dotenv import load_dotenv

load_dotenv()

# API Configuration for Kalshi
KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
REQUEST_TIMEOUT = 15


# Try to import xai_sdk for Grok integration
try:
    from xai_sdk import Client as XAIClient
    XAI_AVAILABLE = True
except ImportError:
    XAI_AVAILABLE = False
    XAIClient = None

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
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    # MCP not available, use simple implementation
    MCP_AVAILABLE = False
    FastMCP = None

if MCP_AVAILABLE:
    # Initialize the MCP server using FastMCP
    app = FastMCP("quantitative-agent")
else:
    app = None

# ============================================================================
# Helper Functions (from kalshi-mcp.py)
# ============================================================================

def implied_prob(yes_bid: float, yes_ask: float, last_price: Optional[float] = None) -> Optional[float]:
    """
    Calculate implied probability from market prices.

    Args:
        yes_bid: Current bid price for YES (cents)
        yes_ask: Current ask price for YES (cents)
        last_price: Last traded price (cents)

    Returns:
        Probability between 0 and 1, or None if insufficient data
    """
    if pd.notnull(yes_bid) and pd.notnull(yes_ask) and yes_ask > 0:
        return ((yes_bid + yes_ask) / 2) / 100.0
    if pd.notnull(last_price):
        return last_price / 100.0
    return None


def spread_confidence(yes_bid: float, yes_ask: float) -> float:
    """
    Calculate confidence from bid-ask spread.
    Tight spread = high confidence, wide spread = low confidence.

    Args:
        yes_bid: Bid price in cents
        yes_ask: Ask price in cents

    Returns:
        Confidence score 0-1
    """
    if pd.isnull(yes_bid) or pd.isnull(yes_ask):
        return 0.0
    spread = yes_ask - yes_bid
    # Normalize: 1-cent spread = 0.99 confidence, 50-cent spread = 0.5 confidence
    return max(0.0, 1.0 - (spread / 100.0))


def fetch_market_history(ticker: str, limit: int = 100) -> List[Dict]:
    """
    Fetch recent price history for a market.

    Args:
        ticker: Market ticker
        limit: Number of recent trades to fetch

    Returns:
        List of trade records with prices and timestamps
    """
    try:
        r = requests.get(
            f"{KALSHI_BASE}/markets/{ticker}/trades",
            params={"limit": limit},
            timeout=REQUEST_TIMEOUT
        )

        if r.status_code == 200:
            return r.json().get("trades", [])

        return []

    except Exception as e:
        print(f"Could not fetch history for {ticker}: {e}", file=sys.stderr)
        return []

# ============================================================================
# Tool Definitions (MCP Mode)
# ============================================================================

if MCP_AVAILABLE:
    # FastMCP Tool Definitions - each function is decorated with @app.tool()

    @app.tool()
    async def analyze_weather_markets_tool(limit: int = 10):
        """Analyze weather markets using 3 statistical sources: NOAA (GFS), Open-Meteo (ECMWF), and Climatology.

        Returns market analysis with probabilities, edge calculations, and trading recommendations.

        Args:
            limit: Maximum number of markets to analyze (default: 10)
        """
        result = await analyze_weather_markets(limit)
        return result

    @app.tool()
    async def analyze_politics_markets_tool(limit: int = 10):
        """Analyze politics markets using 3 statistical sources: Kalshi Market Consensus, Historical Voting Patterns, and Betting Market Model.

        Returns market analysis with probabilities, edge calculations, and trading recommendations.

        Args:
            limit: Maximum number of markets to analyze (default: 10)
        """
        result = await analyze_politics_markets(limit)
        return result

    @app.tool()
    async def analyze_economics_markets_tool(limit: int = 10):
        """Analyze economics markets using 3 statistical sources: FRED (Federal Reserve), Economic Indicators (Alpha Vantage/BLS/World Bank), and Kalshi Market Consensus.

        Returns market analysis with probabilities, edge calculations, and trading recommendations.

        Args:
            limit: Maximum number of markets to analyze (default: 10)
        """
        result = await analyze_economics_markets(limit)
        return result

    @app.tool()
    async def analyze_single_market_tool(ticker: str):
        """Analyze a single market by ticker. Automatically determines category (weather/politics/economics) and uses appropriate quantitative sources.

        Args:
            ticker: Kalshi market ticker (e.g., 'KXHIGHNY-25NOV08-T71')
        """
        result = await analyze_single_market(ticker)
        return result

    @app.tool()
    def get_market_categories_tool():
        """Get available market categories and their quantitative sources."""
        result = get_market_categories()
        return result

    @app.tool()
    async def sentiment_analysis_tool(market_title: str, market_ticker: str = None):
        """Analyze X (Twitter) sentiment for a specific Kalshi market using Grok.

        Searches X for what people are saying about the market topic and returns JSON with sentiment score, key themes, trends, and market impact analysis.

        Args:
            market_title: The title/description of the market to analyze sentiment for
            market_ticker: Optional ticker symbol for the market
        """
        result = await sentiment_analysis(market_title, market_ticker)
        return result

    @app.tool()
    async def get_markets_with_probabilities_tool(categories: list[str]):
        """Fetch all open markets from specified categories with probability calculations.

        Returns market data including tickers, prices, volumes, implied probabilities, and spread confidence scores.

        Args:
            categories: List of category names (e.g., ['Politics', 'Sports', 'Economics'])
        """
        result = await get_markets_with_probabilities(categories)
        return json.loads(result)

    @app.tool()
    async def analyze_market_volatility_tool(ticker: str, current_price: float, yes_bid: float, yes_ask: float, previous_price: float = None):
        """Analyze market volatility and price momentum.

        Returns volatility metrics, confidence scores, momentum indicators (bullish/bearish/neutral), and price trends.

        Args:
            ticker: Market ticker
            current_price: Current market price (last_price)
            yes_bid: Current bid price
            yes_ask: Current ask price
            previous_price: Previous price if available
        """
        result = await analyze_market_volatility(ticker, current_price, yes_bid, yes_ask, previous_price)
        return json.loads(result)

    @app.tool()
    async def analyze_market_volume_tool(ticker: str):
        """Analyze market volume and convert to confidence metric.

        Returns volume metrics, confidence scores, and liquidity indicators.

        Args:
            ticker: Market ticker
        """
        result = await analyze_market_volume(ticker)
        return json.loads(result)

    @app.tool()
    async def greenlight_analysis_tool(ticker: str, market_title: str, market_p: float,
                                      volatility_confidence: float, volume_confidence: float,
                                      momentum: str, spread_conf: float, include_sentiment: bool = True):
        """Aggregate all signals into trading decision.

        Combines volatility, volume, spread confidence, and X/Twitter sentiment analysis (via Grok) to generate trading recommendations (BUY/SHORT/PASS) with detailed reasoning.

        Args:
            ticker: Market ticker
            market_title: Market title/description for sentiment analysis
            market_p: Market implied probability (0-1)
            volatility_confidence: Confidence from volatility analysis (0-1)
            volume_confidence: Volume confidence score (0-1)
            momentum: Price momentum: 'bullish', 'bearish', or 'neutral'
            spread_conf: Confidence from bid-ask spread (0-1)
            include_sentiment: Whether to include X/Twitter sentiment analysis (default: true)
        """
        result = await _greenlight_analysis_impl(ticker, market_title, market_p, volatility_confidence,
                                                 volume_confidence, momentum, spread_conf, include_sentiment)
        return json.loads(result)

    @app.tool()
    async def scan_categories_for_opportunities_tool(categories: list[str], min_confidence: float = 0.5, top_n: int = 10):
        """Scan categories for trading opportunities with full technical analysis.

        Runs complete pipeline: market discovery → volatility → volume → greenlight decision. Returns ranked opportunities by confidence.

        Args:
            categories: List of categories to scan (e.g., ['Politics', 'Economics'])
            min_confidence: Minimum confidence threshold (0-1, default: 0.5)
            top_n: Return top N opportunities (default: 10)
        """
        result = await scan_categories_for_opportunities(categories, min_confidence, top_n)
        return json.loads(result)

# ============================================================================
# Tool Implementations (called by FastMCP tool wrappers above)
# ============================================================================

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

async def sentiment_analysis(market_title: str, market_ticker: str = None) -> dict:
    """
    Analyze X (Twitter) sentiment for a specific Kalshi market using Grok

    Args:
        market_title: The title/description of the market
        market_ticker: Optional ticker symbol for the market

    Returns:
        dict: JSON response with sentiment analysis
    """
    try:
        if not XAI_AVAILABLE:
            return {
                "status": "error",
                "error": "xai_sdk not available",
                "message": "Could not import xai_sdk. Install with: pip install xai-sdk"
            }

        # Get API key from environment
        api_key = os.getenv("X_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "error": "X_API_KEY not set",
                "message": "X_API_KEY environment variable is not set"
            }

        # Initialize Grok client
        from xai_sdk.chat import user, system
        from xai_sdk.tools import x_search

        client = XAIClient(api_key=api_key)

        # Create system prompt for sentiment analysis
        system_prompt = """You are a sentiment analysis expert with access to X (Twitter) data.
Your job is to analyze what people are saying on X about specific topics related to prediction markets.

When given a market topic, you should search X for relevant posts and discussions, then respond ONLY with a JSON object in this exact format:
{
  "sentiment_score": <number 0-100>,
  "sentiment_label": "<positive/negative/neutral>",
  "key_themes": ["theme1", "theme2", "theme3"],
  "notable_trends": ["trend1", "trend2"],
  "market_impact": "<brief analysis of how sentiment affects market>",
  "confidence": "<high/medium/low>"
}

Do not include any text outside the JSON object."""

        # Create user prompt with market information
        if market_ticker:
            user_prompt = f"""Search X (Twitter) for sentiment about this Kalshi prediction market:

Market: {market_title}
Ticker: {market_ticker}

Return ONLY a JSON object with sentiment analysis."""
        else:
            user_prompt = f"""Search X (Twitter) for sentiment about this Kalshi prediction market:

Market: {market_title}

Return ONLY a JSON object with sentiment analysis."""

        # Create chat and send message
        chat = client.chat.create(
                model="grok-4-fast",
                tools=[x_search()],
        )
        chat.append(system(system_prompt))
        chat.append(user(user_prompt))

        # Get response
        response = chat.sample()
        grok_response = response.content

        # Try to parse as JSON
        try:
            result = json.loads(grok_response)
            result["status"] = "success"
            result["ticker"] = market_ticker
            result["title"] = market_title
            return result
        except json.JSONDecodeError:
            return {
                "status": "error",
                "error": "Invalid JSON response",
                "ticker": market_ticker,
                "title": market_title,
                "raw_response": grok_response
            }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Error calling Grok API: {e}"
        }

# ============================================================================
# New Technical Analysis Tools (from kalshi-mcp.py)
# ============================================================================

async def get_markets_with_probabilities_tool(categories: List[str]) -> str:
    """
    Fetch all open markets from specified categories with probability calculations.

    Args:
        categories: List of category names (e.g., ["Politics", "Sports"])

    Returns:
        JSON string with market data including tickers, prices, volumes, and probabilities
    """
    try:
        df = _get_markets_with_probabilities_impl(categories)

        if df.empty:
            return json.dumps({"error": "No markets found"})

        # Convert DataFrame to JSON for MCP response
        result = df.to_dict(orient='records')
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "message": f"Error fetching markets: {e}"}, indent=2)


def _get_markets_with_probabilities_impl(categories: List[str]) -> pd.DataFrame:
    """
    Fetch all open markets from specified categories with probability calculations.

    Args:
        categories: List of category names (e.g., ["Politics", "Sports"])

    Returns:
        DataFrame with columns: ticker, title, series_ticker, category,
                                yes_bid, yes_ask, last_price, market_p,
                                spread_conf, volume
    """
    # Step 1: Get all series
    r_series = requests.get(
        f"{KALSHI_BASE}/series",
        params={"limit": 200},
        timeout=REQUEST_TIMEOUT
    )
    r_series.raise_for_status()
    all_series = r_series.json().get("series", [])

    # Step 2: Filter by categories (case-insensitive)
    matching_series = [
        s for s in all_series
        if s.get('category', '').lower() in [c.lower() for c in categories]
    ]

    print(f"Found {len(matching_series)} series across {len(categories)} categories", file=sys.stderr)

    # Step 3: For each matching series, get open markets
    all_markets = []
    for series in matching_series[:50]:  # Increased to 50 series to find more opportunities
        r_markets = requests.get(
            f"{KALSHI_BASE}/markets",
            params={"series_ticker": series["ticker"], "status": "open", "limit": 200},
            timeout=REQUEST_TIMEOUT
        )
        if r_markets.status_code == 200:
            markets = r_markets.json().get("markets", [])
            for m in markets:
                m["category"] = series.get("category")
            all_markets.extend(markets)

    if not all_markets:
        print("No open markets found", file=sys.stderr)
        return pd.DataFrame()

    # Step 4: Build DataFrame with probability calculations
    df = pd.DataFrame(all_markets)

    # Extract key columns
    cols = ["ticker", "title", "yes_bid", "yes_ask", "last_price", "volume", "category"]
    df = df[[c for c in cols if c in df.columns]]

    # Add series ticker
    df["series_ticker"] = df["ticker"].str.split("-").str[0]

    # Calculate probabilities
    df["market_p"] = df.apply(
        lambda row: implied_prob(row.get("yes_bid"), row.get("yes_ask"), row.get("last_price")),
        axis=1
    )

    # Calculate spread confidence
    df["spread_conf"] = df.apply(
        lambda row: spread_confidence(row.get("yes_bid"), row.get("yes_ask")),
        axis=1
    )

    return df


async def analyze_market_volatility_tool(ticker: str,
                                        current_price: float,
                                        yes_bid: float,
                                        yes_ask: float,
                                        previous_price: Optional[float] = None) -> str:
    """
    Analyze market volatility and price momentum.

    Args:
        ticker: Market ticker
        current_price: Current market price (last_price)
        yes_bid: Current bid price
        yes_ask: Current ask price
        previous_price: Previous price if available

    Returns:
        JSON string with volatility metrics, confidence scores, and momentum indicators
    """
    try:
        result = _analyze_market_volatility_impl(ticker, current_price, yes_bid, yes_ask, previous_price)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "message": f"Error analyzing volatility: {e}"}, indent=2)


def _analyze_market_volatility_impl(ticker: str,
                                    current_price: float,
                                    yes_bid: float,
                                    yes_ask: float,
                                    previous_price: Optional[float] = None) -> Dict:
    """
    Analyze market volatility and price momentum.

    Returns:
        {
            'volatility': float (standard deviation of prices),
            'volatility_confidence': float (0-1, low volatility = high confidence),
            'momentum': str ('bullish'|'bearish'|'neutral'),
            'price_trend': float (change from previous),
            'spread_volatility': float (bid-ask spread as volatility measure)
        }
    """
    # Calculate spread-based volatility (immediate volatility indicator)
    spread = yes_ask - yes_bid if (yes_bid and yes_ask) else 50
    spread_pct = spread / 100.0  # Convert to percentage

    # Volatility confidence: tight spread = low volatility = high confidence
    volatility_confidence = 1.0 / (1.0 + (spread_pct * 5.0))

    # Detect momentum from price change
    momentum = "neutral"
    price_trend = 0.0

    if previous_price and current_price:
        price_trend = current_price - previous_price
        if price_trend > 2:  # Price increased by >2 cents
            momentum = "bullish"
        elif price_trend < -2:  # Price decreased by >2 cents
            momentum = "bearish"

    # Try to fetch historical data for better volatility calculation
    trades = fetch_market_history(ticker, limit=50)
    volatility = spread_pct  # Default to spread-based volatility

    if trades and len(trades) > 5:
        # Calculate actual price volatility from trades
        prices = [t.get('yes_price', t.get('price', 0)) for t in trades]
        prices = [p for p in prices if p]  # Filter out None/0 values

        if len(prices) > 1:
            volatility = np.std(prices) / 100.0  # Normalize to 0-1

            # Recalculate confidence based on actual volatility
            volatility_confidence = 1.0 / (1.0 + (volatility * 10.0))

            # Better momentum detection from trend
            if len(prices) >= 10:
                recent_avg = np.mean(prices[-5:])
                older_avg = np.mean(prices[-10:-5] if len(prices) >= 10 else prices[:5])
                if recent_avg > older_avg * 1.05:
                    momentum = "bullish"
                elif recent_avg < older_avg * 0.95:
                    momentum = "bearish"

    return {
        'volatility': round(volatility, 4),
        'volatility_confidence': round(volatility_confidence, 3),
        'momentum': momentum,
        'price_trend': round(price_trend, 2),
        'spread_volatility': round(spread_pct, 4)
    }


async def analyze_market_volume_tool(ticker: str) -> str:
    """
    Analyze market volume and convert to confidence metric.

    Args:
        ticker: Market ticker

    Returns:
        JSON string with volume metrics, confidence scores, and liquidity indicators
    """
    try:
        result = _analyze_market_volume_impl(ticker)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "message": f"Error analyzing volume: {e}"}, indent=2)


def _analyze_market_volume_impl(ticker: str) -> Dict:
    """
    Analyze market volume and convert to confidence metric.

    Returns:
        {
            'volume': int,
            'volume_confidence': float (0-1),
            'liquidity_score': float
        }
    """
    # Fetch detailed market info
    try:
        r = requests.get(f"{KALSHI_BASE}/markets/{ticker}", timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        market = r.json().get("market", {})

        volume = market.get("volume", 0)
        open_interest = market.get("open_interest", 0)

        # Calculate volume confidence using logarithmic scaling
        # Assume 10,000 volume = high confidence (1.0)
        # 100 volume = low confidence (~0.5)
        volume_threshold = 10000
        if volume > 0:
            volume_confidence = min(1.0, math.log(volume + 1) / math.log(volume_threshold))
        else:
            volume_confidence = 0.0

        # Liquidity score combines volume and open interest
        liquidity_score = (volume + open_interest) / 2

        return {
            'volume': volume,
            'open_interest': open_interest,
            'volume_confidence': round(volume_confidence, 3),
            'liquidity_score': liquidity_score
        }
    except Exception as e:
        print(f"Error fetching volume for {ticker}: {e}", file=sys.stderr)
        return {
            'volume': 0,
            'open_interest': 0,
            'volume_confidence': 0.0,
            'liquidity_score': 0.0
        }


async def greenlight_analysis_tool(ticker: str,
                                   market_title: str,
                                   market_p: float,
                                   volatility_confidence: float,
                                   volume_confidence: float,
                                   momentum: str,
                                   spread_conf: float,
                                   include_sentiment: bool = True) -> str:
    """
    Aggregate all signals into trading decision with sentiment analysis.

    Args:
        ticker: Market ticker
        market_title: Market title for sentiment analysis
        market_p: Market implied probability
        volatility_confidence: Confidence from volatility analysis
        volume_confidence: Volume confidence score
        momentum: Price momentum ('bullish'|'bearish'|'neutral')
        spread_conf: Confidence from bid-ask spread
        include_sentiment: Whether to include sentiment analysis (default: True)

    Returns:
        JSON string with trading decision (STRONG_BUY/BUY/STRONG_SHORT/SHORT/WATCH/PASS) and reasoning
    """
    try:
        result = await _greenlight_analysis_impl(ticker, market_title, market_p, volatility_confidence,
                                                 volume_confidence, momentum, spread_conf, include_sentiment)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "message": f"Error in greenlight analysis: {e}"}, indent=2)


async def _greenlight_analysis_impl(ticker: str,
                                    market_title: str,
                                    market_p: float,
                                    volatility_confidence: float,
                                    volume_confidence: float,
                                    momentum: str,
                                    spread_conf: float,
                                    include_sentiment: bool = True) -> Dict:
    """
    Binary trading decision with sentiment check.

    LOGIC:
    - Technical says BUY + Sentiment is positive → BUY
    - Technical says SHORT + Sentiment is negative → SHORT
    - Otherwise → PASS

    Returns:
        {
            ticker, decision (BUY/SHORT/PASS), market_p, volatility_confidence,
            volume_confidence, momentum, final_confidence, reasoning, sentiment
        }
    """
    # Calculate final confidence: combine volatility, volume, and spread
    # Weight: volatility 40%, volume 40%, spread 20%
    final_confidence = (
        volatility_confidence * 0.4 +
        volume_confidence * 0.4 +
        spread_conf * 0.2
    )

    # Step 1: Get technical direction
    # Lowered thresholds to find more opportunities
    technical_direction = None  # "buy", "short", or None

    if momentum == "bullish" and final_confidence > 0.4 and market_p < 0.75:
        technical_direction = "buy"
    elif momentum == "bearish" and final_confidence > 0.4 and market_p > 0.25:
        technical_direction = "short"

    # Step 2: Get sentiment analysis if enabled
    sentiment_data = None
    sentiment_label = None
    final_decision = "PASS"

    if include_sentiment and technical_direction:
        try:
            sentiment_result = await sentiment_analysis(market_title, ticker)
            if sentiment_result.get("status") == "success":
                sentiment_data = sentiment_result
                sentiment_label = sentiment_result.get("sentiment_label", "neutral").lower()

                # Check agreement
                if technical_direction == "buy" and sentiment_label == "positive":
                    final_decision = "BUY"
                elif technical_direction == "short" and sentiment_label == "negative":
                    final_decision = "SHORT"
                else:
                    final_decision = "PASS"
            else:
                print(f"Sentiment analysis failed: {sentiment_result.get('error')}", file=sys.stderr)
                final_decision = "PASS"
        except Exception as e:
            print(f"Error getting sentiment: {e}", file=sys.stderr)
            final_decision = "PASS"
    else:
        # No technical direction or sentiment disabled
        final_decision = "PASS"

    # Generate reasoning
    reasoning_parts = []
    reasoning_parts.append(f"Market price: {market_p:.1%}")
    reasoning_parts.append(f"Technical momentum: {momentum}")
    reasoning_parts.append(f"Technical confidence: {final_confidence:.1%}")

    if sentiment_label:
        reasoning_parts.append(f"Sentiment: {sentiment_label}")

    if final_decision == "BUY":
        reasoning_parts.append("✅ GREENLIGHT BUY: Bullish technical + positive sentiment")
    elif final_decision == "SHORT":
        reasoning_parts.append("✅ GREENLIGHT SHORT: Bearish technical + negative sentiment")
    else:
        if technical_direction and sentiment_label:
            reasoning_parts.append(f"❌ PASS: Technical ({technical_direction}) and sentiment ({sentiment_label}) disagree")
        elif not technical_direction:
            reasoning_parts.append("❌ PASS: No strong technical signal")
        else:
            reasoning_parts.append("❌ PASS: Sentiment analysis unavailable")

    reasoning = ". ".join(reasoning_parts)

    result = {
        'ticker': ticker,
        'decision': final_decision,
        'technical_direction': technical_direction,
        'market_p': round(market_p, 3) if market_p else None,
        'volatility_confidence': round(volatility_confidence, 3),
        'volume_confidence': round(volume_confidence, 3),
        'momentum': momentum,
        'final_confidence': round(final_confidence, 3),
        'reasoning': reasoning
    }

    if sentiment_data:
        result['sentiment'] = {
            'label': sentiment_label,
            'score': sentiment_data.get('sentiment_score'),
            'confidence': sentiment_data.get('confidence'),
            'key_themes': sentiment_data.get('key_themes'),
            'market_impact': sentiment_data.get('market_impact')
        }

    return result


async def scan_categories_for_opportunities_tool(categories: List[str],
                                                min_confidence: float = 0.5,
                                                top_n: int = 10) -> str:
    """
    Scan categories for trading opportunities with full technical analysis.

    Args:
        categories: List of categories to scan (e.g., ["Politics", "Economics"])
        min_confidence: Minimum confidence threshold (0-1)
        top_n: Return top N opportunities

    Returns:
        JSON string with ranked trading opportunities including all analysis metrics
    """
    try:
        df = await _scan_categories_for_opportunities_impl(categories, min_confidence, top_n)

        if df.empty:
            return json.dumps({"message": "No trading opportunities found"})

        # Convert DataFrame to JSON for MCP response
        result = df.to_dict(orient='records')
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e), "message": f"Error scanning categories: {e}"}, indent=2)


async def _scan_categories_for_opportunities_impl(categories: List[str],
                                                  min_confidence: float = 0.5,
                                                  top_n: int = 10) -> pd.DataFrame:
    """
    Scan categories for trading opportunities.

    Args:
        categories: List of categories to scan
        min_confidence: Minimum confidence threshold
        top_n: Return top N opportunities

    Returns:
        DataFrame of greenlight markets sorted by confidence
    """
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"SCANNING CATEGORIES: {', '.join(categories)}", file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)

    # Step 1: Get all markets with probabilities
    print("Step 1: Fetching markets...", file=sys.stderr)
    markets_df = _get_markets_with_probabilities_impl(categories)

    if markets_df.empty:
        print("No markets found", file=sys.stderr)
        return pd.DataFrame()

    print(f"Found {len(markets_df)} open markets\n", file=sys.stderr)

    # Step 2-4: Analyze each market
    results = []

    # Pre-filter: only analyze markets with some minimum liquidity/quality
    # Loosened filters to find more opportunities
    filtered_markets = markets_df[
        (markets_df['market_p'].notna()) &
        (markets_df['spread_conf'] > 0.2) &  # Lowered from 0.3
        (markets_df['volume'] > 5)  # Lowered from 10
    ]

    print(f"After pre-filtering: {len(filtered_markets)} markets to analyze\n", file=sys.stderr)

    for idx, row in filtered_markets.iterrows():
        ticker = row['ticker']
        market_p = row.get('market_p')
        spread_conf = row.get('spread_conf', 0.5)

        print(f"Analyzing {ticker}...", file=sys.stderr)

        # Tool 2: Volatility
        volatility_result = _analyze_market_volatility_impl(
            ticker,
            row.get('last_price', 50),
            row.get('yes_bid', 0),
            row.get('yes_ask', 100),
            row.get('previous_price')
        )

        # Tool 3: Volume
        volume_result = _analyze_market_volume_impl(ticker)

        # Tool 4: Greenlight (with sentiment)
        greenlight_result = await _greenlight_analysis_impl(
            ticker,
            row.get('title', ticker),  # Use title for sentiment analysis
            market_p,
            volatility_result['volatility_confidence'],
            volume_result['volume_confidence'],
            volatility_result['momentum'],
            spread_conf,
            include_sentiment=True
        )

        # Combine all data
        combined = {
            **row.to_dict(),
            **volatility_result,
            **volume_result,
            **greenlight_result
        }

        results.append(combined)

    # Step 5: Filter and sort
    results_df = pd.DataFrame(results)

    if results_df.empty:
        return results_df

    # Only include actual BUY/SHORT decisions (not PASS)
    # Lowered confidence requirement to find more opportunities
    greenlight_df = results_df[
        (results_df['decision'].isin(['BUY', 'SHORT'])) &
        (results_df['final_confidence'] >= max(min_confidence * 0.8, 0.3))
    ]

    # Sort by final confidence (highest first)
    greenlight_df = greenlight_df.sort_values('final_confidence', ascending=False)

    return greenlight_df.head(top_n)

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run the MCP server with stdio transport (default for MCP clients)"""
    # FastMCP handles stdio automatically when run() is called without transport arg
    app.run()

def main_http(port=8000):
    """Run the MCP server with HTTP SSE transport"""
    import os

    print("🚀 MCP Quantitative Agent HTTP Server starting...")
    print(f"📡 Server will be available at: http://localhost:{port}")
    print("📚 Available tools: scan_categories_for_opportunities, analyze_market_volume, greenlight_analysis, etc.")

    # Set port via environment variable (FastMCP reads this)
    os.environ["PORT"] = str(port)

    # Use FastMCP's SSE transport
    app.run(transport="sse")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # Run with HTTP transport
        main_http()
    else:
        # Run with stdio transport (default for MCP)
        main()

