import requests
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import os
import sys
from datetime import datetime
import math
import asyncio
import json
from mcp.server.fastmcp import FastMCP

# API Configuration
KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
REQUEST_TIMEOUT = 15

# Initialize MCP Server
mcp = FastMCP("kalshi-trading-server")

# TODO: Initialize Anthropic client
# from anthropic import Anthropic
# client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ============================================================================
# TOOL 1: Market Discovery & Probability Extraction
# ============================================================================

def implied_prob(yes_bid: float, yes_ask: float, last_price: Optional[float] = None) -> Optional[float]:
    """
    Calculate implied probability from market prices (from weather_test.py).

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


@mcp.tool()
def get_markets_with_probabilities(categories: List[str]) -> str:
    """
    Fetch all open markets from specified categories with probability calculations.

    Args:
        categories: List of category names (e.g., ["Politics", "Sports"])

    Returns:
        JSON string with market data including tickers, prices, volumes, and probabilities
    """
    df = _get_markets_with_probabilities_impl(categories)

    if df.empty:
        return json.dumps({"error": "No markets found"})

    # Convert DataFrame to JSON for MCP response
    result = df.to_dict(orient='records')
    return json.dumps(result, indent=2, default=str)

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

    print(f"Found {len(matching_series)} series across {len(categories)} categories")

    # Step 3: For each matching series, get open markets
    all_markets = []
    # TODO 2991 is too many to test. run like 15
    for series in matching_series[:15]:
        r_markets = requests.get(
            f"{KALSHI_BASE}/markets",
            params={"series_ticker": series["ticker"], "status": "open", "limit": 100},
            timeout=REQUEST_TIMEOUT
        )
        if r_markets.status_code == 200:
            markets = r_markets.json().get("markets", [])
            for m in markets:
                m["category"] = series.get("category")
            all_markets.extend(markets)
        else:
            print('taking too long')
            sys.exit(0)

    if not all_markets:
        print("No open markets found")
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


# ============================================================================
# TOOL 2: Volatility Analysis
# ============================================================================

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
        # Try to get market history/trades
        # Note: Kalshi API may require authentication for trade history
        r = requests.get(
            f"{KALSHI_BASE}/markets/{ticker}/trades",
            params={"limit": limit},
            timeout=REQUEST_TIMEOUT
        )

        if r.status_code == 200:
            return r.json().get("trades", [])

        # If trades endpoint doesn't work, we'll use market snapshots
        # and track price changes through repeated calls
        return []

    except Exception as e:
        print(f"Could not fetch history for {ticker}: {e}")
        return []


@mcp.tool()
def analyze_market_volatility(ticker: str,
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
    result = _analyze_market_volatility_impl(ticker, current_price, yes_bid, yes_ask, previous_price)
    return json.dumps(result, indent=2)

def _analyze_market_volatility_impl(ticker: str,
                                    current_price: float,
                                    yes_bid: float,
                                    yes_ask: float,
                                    previous_price: Optional[float] = None) -> Dict:
    """
    Analyze market volatility and price momentum.

    Args:
        ticker: Market ticker
        current_price: Current market price (last_price)
        yes_bid: Current bid price
        yes_ask: Current ask price
        previous_price: Previous price if available

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
    # Use inverse sigmoid to map spread to confidence
    # spread of 1-5 cents = high confidence (0.8-0.95)
    # spread of 10-20 cents = medium confidence (0.5-0.7)
    # spread of 30+ cents = low confidence (<0.5)
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
            # Low volatility (<0.05) = high confidence (>0.8)
            # High volatility (>0.15) = low confidence (<0.3)
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


# ============================================================================
# TOOL 3: Volume Analysis
# ============================================================================

@mcp.tool()
def analyze_market_volume(ticker: str) -> str:
    """
    Analyze market volume and convert to confidence metric.

    Args:
        ticker: Market ticker

    Returns:
        JSON string with volume metrics, confidence scores, and liquidity indicators
    """
    result = _analyze_market_volume_impl(ticker)
    return json.dumps(result, indent=2)

def _analyze_market_volume_impl(ticker: str) -> Dict:
    """
    Analyze market volume and convert to confidence metric.

    Args:
        ticker: Market ticker

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
        print(f"Error fetching volume for {ticker}: {e}")
        return {
            'volume': 0,
            'open_interest': 0,
            'volume_confidence': 0.0,
            'liquidity_score': 0.0
        }


# ============================================================================
# TOOL 4: Greenlight Aggregator
# ============================================================================

@mcp.tool()
def greenlight_analysis(ticker: str,
                       market_p: float,
                       volatility_confidence: float,
                       volume_confidence: float,
                       momentum: str,
                       spread_conf: float) -> str:
    """
    Aggregate all signals into trading decision.

    Args:
        ticker: Market ticker
        market_p: Market implied probability
        volatility_confidence: Confidence from volatility analysis
        volume_confidence: Volume confidence score
        momentum: Price momentum ('bullish'|'bearish'|'neutral')
        spread_conf: Confidence from bid-ask spread

    Returns:
        JSON string with trading decision (STRONG_BUY/BUY/STRONG_SHORT/WATCH/PASS) and reasoning
    """
    result = _greenlight_analysis_impl(ticker, market_p, volatility_confidence,
                                       volume_confidence, momentum, spread_conf)
    return json.dumps(result, indent=2)

def _greenlight_analysis_impl(ticker: str,
                              market_p: float,
                              volatility_confidence: float,
                              volume_confidence: float,
                              momentum: str,
                              spread_conf: float) -> Dict:
    """
    Aggregate all signals into trading decision.

    Args:
        ticker: Market ticker
        market_p: Market implied probability
        volatility_confidence: Confidence from volatility analysis
        volume_confidence: Volume confidence score
        momentum: Price momentum ('bullish'|'bearish'|'neutral')
        spread_conf: Confidence from bid-ask spread

    Returns:
        {
            ticker, decision, market_p, volatility_confidence,
            volume_confidence, momentum, final_confidence, reasoning
        }
    """
    # Calculate final confidence: combine volatility, volume, and spread
    # Weight: volatility 40%, volume 40%, spread 20%
    final_confidence = (
        volatility_confidence * 0.4 +
        volume_confidence * 0.4 +
        spread_conf * 0.2
    )

    # Decision logic based on momentum + confidence + price level
    decision = "PASS"

    # Strong signals: high confidence + clear momentum
    if momentum == "bullish" and final_confidence > 0.7:
        if market_p < 0.6:  # Price not too high
            decision = "STRONG_BUY"
        elif market_p < 0.75:
            decision = "BUY"
        else:
            decision = "WATCH"  # Price too high to buy

    elif momentum == "bearish" and final_confidence > 0.7:
        if market_p > 0.4:  # Price not too low
            decision = "STRONG_SHORT"
        elif market_p > 0.25:
            decision = "SHORT"
        else:
            decision = "WATCH"  # Price too low to short

    # Medium signals: decent confidence
    elif momentum == "bullish" and final_confidence > 0.5 and market_p < 0.7:
        decision = "BUY"
    elif momentum == "bearish" and final_confidence > 0.5 and market_p > 0.3:
        decision = "SHORT"

    # Neutral momentum but good fundamentals - identify opportunities
    elif momentum == "neutral" and final_confidence > 0.5:
        # Look for underpriced opportunities (contrarian plays)
        if market_p < 0.3:
            decision = "BUY"  # Cheap, might be undervalued
        elif market_p > 0.7:
            decision = "SHORT"  # Expensive, might be overvalued
        elif 0.4 <= market_p <= 0.6:
            decision = "WATCH"  # Fair price, watch for movement
        else:
            decision = "WATCH"  # Worth monitoring

    # High confidence but neutral momentum
    elif final_confidence > 0.4:
        decision = "WATCH"

    # Generate reasoning
    reasoning_parts = []
    reasoning_parts.append(f"Market price: {market_p:.1%}")
    reasoning_parts.append(f"Momentum: {momentum}")
    reasoning_parts.append(f"Confidence: {final_confidence:.1%} (vol={volatility_confidence:.2f}, vol_conf={volume_confidence:.2f})")

    if decision in ["STRONG_BUY", "BUY"]:
        reasoning_parts.append("Bullish momentum with strong fundamentals")
    elif decision in ["STRONG_SHORT", "SHORT"]:
        reasoning_parts.append("Bearish momentum with strong fundamentals")
    elif decision == "WATCH":
        reasoning_parts.append("High confidence but needs clearer signal or better price")

    reasoning = ". ".join(reasoning_parts)

    return {
        'ticker': ticker,
        'decision': decision,
        'market_p': round(market_p, 3) if market_p else None,
        'volatility_confidence': round(volatility_confidence, 3),
        'volume_confidence': round(volume_confidence, 3),
        'momentum': momentum,
        'final_confidence': round(final_confidence, 3),
        'reasoning': reasoning
    }


# ============================================================================
# TOOL 5: Batch Greenlight Scanner
# ============================================================================

@mcp.tool()
def scan_categories_for_opportunities(categories: List[str],
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
    df = _scan_categories_for_opportunities_impl(categories, min_confidence, top_n)

    if df.empty:
        return json.dumps({"message": "No trading opportunities found"})

    # Convert DataFrame to JSON for MCP response
    result = df.to_dict(orient='records')
    return json.dumps(result, indent=2, default=str)

def _scan_categories_for_opportunities_impl(categories: List[str],
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
    print(f"\n{'='*80}")
    print(f"SCANNING CATEGORIES: {', '.join(categories)}")
    print(f"{'='*80}\n")

    # Step 1: Get all markets with probabilities
    print("Step 1: Fetching markets...")
    markets_df = _get_markets_with_probabilities_impl(categories)

    if markets_df.empty:
        print("No markets found")
        return pd.DataFrame()

    print(f"Found {len(markets_df)} open markets\n")

    # Step 2-4: Analyze each market
    results = []

    # Pre-filter: only analyze markets with some minimum liquidity/quality
    filtered_markets = markets_df[
        (markets_df['market_p'].notna()) &
        (markets_df['spread_conf'] > 0.3) &  # At least some price stability
        (markets_df['volume'] > 10)  # At least some trading activity
    ]

    print(f"After pre-filtering: {len(filtered_markets)} markets to analyze\n")

    for idx, row in filtered_markets.iterrows():
        ticker = row['ticker']
        market_p = row.get('market_p')
        spread_conf = row.get('spread_conf', 0.5)

        print(f"Analyzing {ticker}...")

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

        # Tool 4: Greenlight
        greenlight_result = _greenlight_analysis_impl(
            ticker,
            market_p,
            volatility_result['volatility_confidence'],
            volume_result['volume_confidence'],
            volatility_result['momentum'],
            spread_conf
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

    # More lenient filtering: include WATCH decisions and lower min confidence
    # WATCH markets have good fundamentals even without clear momentum
    greenlight_df = results_df[
        (results_df['decision'].isin(['STRONG_BUY', 'BUY', 'STRONG_SHORT', 'SHORT', 'WATCH'])) &
        (results_df['final_confidence'] >= max(min_confidence * 0.7, 0.35))  # Lower threshold
    ]

    # Sort by final confidence (highest first)
    greenlight_df = greenlight_df.sort_values('final_confidence', ascending=False)

    return greenlight_df.head(top_n)


# ============================================================================
# MAIN - MCP Server Setup
# ============================================================================

def run_mcp_server():
    """
    Run the MCP server using stdio transport.
    """
    # FastMCP handles the async loop and server setup
    mcp.run()


# ============================================================================
# Test Client
# ============================================================================

def test_mcp_client():
    """
    Test client to demonstrate MCP tool usage.
    """
    print("\n" + "="*80)
    print("🧪 MCP CLIENT TEST - Kalshi Trading Tools")
    print("="*80 + "\n")

    # Test 1: Get markets with probabilities
    print("Test 1: Getting markets from Economics category...")
    categories = ["Economics"]
    result = get_markets_with_probabilities(categories)
    print(f"✓ Found markets data (length: {len(result)} chars)")
    print(f"Sample: {result[:200]}...\n")

    # Test 2: Analyze volume for a specific ticker
    print("Test 2: Analyzing volume for a sample ticker...")
    # We'll use the first ticker from the result if available
    try:
        markets_data = json.loads(result)
        if markets_data and len(markets_data) > 0:
            sample_ticker = markets_data[0]['ticker']
            volume_result = analyze_market_volume(sample_ticker)
            print(f"✓ Volume analysis for {sample_ticker}:")
            print(volume_result[:200] + "...\n")
    except Exception as e:
        print(f"⚠ Could not test volume analysis: {e}\n")

    # Test 3: Scan for opportunities
    print("Test 3: Scanning categories for opportunities...")
    scan_result = scan_categories_for_opportunities(
        categories=["Economics", "Politics"],
        min_confidence=0.3,
        top_n=5
    )
    print(f"✓ Scan completed")
    print("Sample output:")
    print(scan_result[:500] + "...\n")

    print("="*80)
    print("✅ MCP Client Test Complete")
    print("="*80 + "\n")


# ============================================================================
# Integration Tests for Greenlight Analysis
# ============================================================================

def test_greenlight_integration():
    """
    Integration tests for greenlight analysis covering real market conditions.
    Tests the full pipeline: market discovery → volatility → volume → greenlight decision
    """
    print("\n" + "="*80)
    print("🧪 GREENLIGHT INTEGRATION TESTS")
    print("="*80 + "\n")

    test_results = {
        "passed": 0,
        "failed": 0,
        "warnings": 0,
        "tests": []
    }

    # Test 1: Full pipeline with real markets
    print("Test 1: Full Pipeline Integration (Real Markets)")
    print("-" * 80)
    try:
        categories = ["Economics", "Politics"]
        opportunities_df = _scan_categories_for_opportunities_impl(
            categories=categories,
            min_confidence=0.3,
            top_n=5
        )

        if not opportunities_df.empty:
            print(f"✓ Pipeline executed successfully")
            print(f"  - Found {len(opportunities_df)} opportunities")
            print(f"  - Categories: {categories}")

            # Validate data structure
            required_cols = ['ticker', 'decision', 'market_p', 'final_confidence',
                           'volatility_confidence', 'volume_confidence', 'momentum']
            missing_cols = [col for col in required_cols if col not in opportunities_df.columns]

            if missing_cols:
                print(f"⚠ Warning: Missing columns: {missing_cols}")
                test_results["warnings"] += 1
            else:
                print(f"✓ All required columns present")
                test_results["passed"] += 1

            # Validate decision types
            valid_decisions = ['STRONG_BUY', 'BUY', 'STRONG_SHORT', 'SHORT', 'WATCH', 'PASS']
            invalid_decisions = opportunities_df[~opportunities_df['decision'].isin(valid_decisions)]

            if len(invalid_decisions) > 0:
                print(f"✗ Invalid decisions found: {invalid_decisions['decision'].unique()}")
                test_results["failed"] += 1
            else:
                print(f"✓ All decisions are valid")
                test_results["passed"] += 1
        else:
            print("⚠ No opportunities found (market conditions may not be favorable)")
            test_results["warnings"] += 1

    except Exception as e:
        print(f"✗ Test failed: {e}")
        test_results["failed"] += 1

    print()

    # Test 2: Market Condition Analysis - Bullish Scenario
    print("Test 2: Bullish Market Conditions")
    print("-" * 80)
    try:
        markets_df = _get_markets_with_probabilities_impl(["Economics"])

        if not markets_df.empty:
            # Find a market with bullish characteristics (low price, tight spread)
            bullish_candidates = markets_df[
                (markets_df['market_p'] < 0.5) &
                (markets_df['spread_conf'] > 0.5)
            ]

            if len(bullish_candidates) > 0:
                test_market = bullish_candidates.iloc[0]
                ticker = test_market['ticker']

                print(f"Testing market: {ticker}")
                print(f"  Market price: {test_market['market_p']:.1%}")

                # Run full analysis
                vol_result = _analyze_market_volatility_impl(
                    ticker,
                    test_market.get('last_price', 50),
                    test_market.get('yes_bid', 0),
                    test_market.get('yes_ask', 100),
                    None
                )

                volume_result = _analyze_market_volume_impl(ticker)

                greenlight_result = _greenlight_analysis_impl(
                    ticker,
                    test_market['market_p'],
                    vol_result['volatility_confidence'],
                    volume_result['volume_confidence'],
                    vol_result['momentum'],
                    test_market['spread_conf']
                )

                print(f"  Decision: {greenlight_result['decision']}")
                print(f"  Momentum: {greenlight_result['momentum']}")
                print(f"  Final confidence: {greenlight_result['final_confidence']:.1%}")

                # Validate logic: low price + good fundamentals should suggest BUY/WATCH
                if greenlight_result['final_confidence'] > 0.5:
                    if greenlight_result['decision'] in ['BUY', 'STRONG_BUY', 'WATCH']:
                        print(f"✓ Correct decision for bullish conditions")
                        test_results["passed"] += 1
                    else:
                        print(f"⚠ Unexpected decision: {greenlight_result['decision']}")
                        test_results["warnings"] += 1
                else:
                    print(f"⚠ Low confidence: {greenlight_result['final_confidence']:.1%}")
                    test_results["warnings"] += 1
            else:
                print("⚠ No bullish candidates found")
                test_results["warnings"] += 1
        else:
            print("⚠ No markets available for testing")
            test_results["warnings"] += 1

    except Exception as e:
        print(f"✗ Test failed: {e}")
        test_results["failed"] += 1

    print()

    # Test 3: Market Condition Analysis - Bearish Scenario
    print("Test 3: Bearish Market Conditions")
    print("-" * 80)
    try:
        markets_df = _get_markets_with_probabilities_impl(["Politics"])

        if not markets_df.empty:
            # Find a market with bearish characteristics (high price, tight spread)
            bearish_candidates = markets_df[
                (markets_df['market_p'] > 0.5) &
                (markets_df['spread_conf'] > 0.5)
            ]

            if len(bearish_candidates) > 0:
                test_market = bearish_candidates.iloc[0]
                ticker = test_market['ticker']

                print(f"Testing market: {ticker}")
                print(f"  Market price: {test_market['market_p']:.1%}")

                # Run full analysis
                vol_result = _analyze_market_volatility_impl(
                    ticker,
                    test_market.get('last_price', 50),
                    test_market.get('yes_bid', 0),
                    test_market.get('yes_ask', 100),
                    None
                )

                volume_result = _analyze_market_volume_impl(ticker)

                greenlight_result = _greenlight_analysis_impl(
                    ticker,
                    test_market['market_p'],
                    vol_result['volatility_confidence'],
                    volume_result['volume_confidence'],
                    vol_result['momentum'],
                    test_market['spread_conf']
                )

                print(f"  Decision: {greenlight_result['decision']}")
                print(f"  Momentum: {greenlight_result['momentum']}")
                print(f"  Final confidence: {greenlight_result['final_confidence']:.1%}")

                # Validate logic: high price + good fundamentals should suggest SHORT/WATCH
                if greenlight_result['final_confidence'] > 0.5:
                    if greenlight_result['decision'] in ['SHORT', 'STRONG_SHORT', 'WATCH']:
                        print(f"✓ Correct decision for bearish conditions")
                        test_results["passed"] += 1
                    else:
                        print(f"⚠ Unexpected decision: {greenlight_result['decision']}")
                        test_results["warnings"] += 1
                else:
                    print(f"⚠ Low confidence: {greenlight_result['final_confidence']:.1%}")
                    test_results["warnings"] += 1
            else:
                print("⚠ No bearish candidates found")
                test_results["warnings"] += 1
        else:
            print("⚠ No markets available for testing")
            test_results["warnings"] += 1

    except Exception as e:
        print(f"✗ Test failed: {e}")
        test_results["failed"] += 1

    print()

    # Test 4: Confidence Score Validation
    print("Test 4: Confidence Score Validation")
    print("-" * 80)
    try:
        # Test with synthetic data to validate confidence calculations
        test_cases = [
            {
                "name": "High confidence (tight spread, high volume)",
                "volatility_conf": 0.9,
                "volume_conf": 0.8,
                "spread_conf": 0.95,
                "expected_range": (0.7, 1.0)
            },
            {
                "name": "Low confidence (wide spread, low volume)",
                "volatility_conf": 0.3,
                "volume_conf": 0.2,
                "spread_conf": 0.3,
                "expected_range": (0.0, 0.4)
            },
            {
                "name": "Medium confidence (mixed signals)",
                "volatility_conf": 0.6,
                "volume_conf": 0.5,
                "spread_conf": 0.7,
                "expected_range": (0.4, 0.7)
            }
        ]

        for test_case in test_cases:
            result = _greenlight_analysis_impl(
                ticker="TEST-TICKER",
                market_p=0.5,
                volatility_confidence=test_case["volatility_conf"],
                volume_confidence=test_case["volume_conf"],
                momentum="neutral",
                spread_conf=test_case["spread_conf"]
            )

            final_conf = result['final_confidence']
            expected_min, expected_max = test_case["expected_range"]

            if expected_min <= final_conf <= expected_max:
                print(f"✓ {test_case['name']}")
                print(f"  Final confidence: {final_conf:.1%} (expected: {expected_min:.1%}-{expected_max:.1%})")
                test_results["passed"] += 1
            else:
                print(f"✗ {test_case['name']}")
                print(f"  Final confidence: {final_conf:.1%} (expected: {expected_min:.1%}-{expected_max:.1%})")
                test_results["failed"] += 1

    except Exception as e:
        print(f"✗ Test failed: {e}")
        test_results["failed"] += 1

    print()

    # Test 5: Decision Logic Validation
    print("Test 5: Decision Logic Validation")
    print("-" * 80)
    try:
        decision_test_cases = [
            {
                "name": "Strong buy signal (bullish + high conf + low price)",
                "market_p": 0.3,
                "momentum": "bullish",
                "final_confidence": 0.8,
                "expected_decisions": ['STRONG_BUY', 'BUY']
            },
            {
                "name": "Strong short signal (bearish + high conf + high price)",
                "market_p": 0.7,
                "momentum": "bearish",
                "final_confidence": 0.8,
                "expected_decisions": ['STRONG_SHORT', 'SHORT']
            },
            {
                "name": "Watch signal (neutral + good conf)",
                "market_p": 0.5,
                "momentum": "neutral",
                "final_confidence": 0.6,
                "expected_decisions": ['WATCH', 'BUY', 'SHORT']
            },
            {
                "name": "Pass signal (low confidence)",
                "market_p": 0.5,
                "momentum": "neutral",
                "final_confidence": 0.2,
                "expected_decisions": ['PASS', 'WATCH']
            }
        ]

        for test_case in decision_test_cases:
            result = _greenlight_analysis_impl(
                ticker="TEST-TICKER",
                market_p=test_case["market_p"],
                volatility_confidence=test_case["final_confidence"],
                volume_confidence=test_case["final_confidence"],
                momentum=test_case["momentum"],
                spread_conf=test_case["final_confidence"]
            )

            decision = result['decision']

            if decision in test_case["expected_decisions"]:
                print(f"✓ {test_case['name']}")
                print(f"  Decision: {decision} (expected: {test_case['expected_decisions']})")
                test_results["passed"] += 1
            else:
                print(f"✗ {test_case['name']}")
                print(f"  Decision: {decision} (expected: {test_case['expected_decisions']})")
                test_results["failed"] += 1

    except Exception as e:
        print(f"✗ Test failed: {e}")
        test_results["failed"] += 1

    print()

    # Summary
    print("="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✓ Passed:   {test_results['passed']}")
    print(f"⚠ Warnings: {test_results['warnings']}")
    print(f"✗ Failed:   {test_results['failed']}")
    print(f"Total:      {test_results['passed'] + test_results['warnings'] + test_results['failed']}")

    success_rate = test_results['passed'] / max(1, test_results['passed'] + test_results['failed']) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    print("="*80 + "\n")

    return test_results


# ============================================================================
# Legacy Test Function (kept for backwards compatibility)
# ============================================================================

def legacy_test():
    """
    Legacy pipeline: scan categories and display opportunities.
    """
    categories = ["Economics", "Politics", "Financials"]

    opportunities = _scan_categories_for_opportunities_impl(
        categories=categories,
        min_confidence=0.5,
        top_n=10
    )

    if opportunities.empty:
        print("\n❌ No trading opportunities found")
        return

    print("\n" + "="*80)
    print("🟢 GREENLIGHT TRADING OPPORTUNITIES")
    print("="*80 + "\n")

    for _, row in opportunities.iterrows():
        print(f"📊 {row['ticker']}")
        print(f"   Title: {row.get('title', 'N/A')[:70]}")
        print(f"   Decision: {row['decision']}")
        print(f"   Market Price: {row['market_p']:.1%}")
        print(f"   Final Confidence: {row['final_confidence']:.1%}")
        print(f"   Momentum: {row['momentum']}")
        print(f"   Volatility: {row['volatility']:.3f} (conf={row['volatility_confidence']:.2f})")
        print(f"   Volume: {row.get('volume', 0):,} (conf={row['volume_confidence']:.2f})")
        print(f"   Reasoning: {row['reasoning']}")
        print("-" * 80 + "\n")


if __name__ == "__main__":
    import sys

    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp-server":
        # Run as MCP server (for use with Claude Desktop or other MCP clients)
        run_mcp_server()
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run test client
        test_mcp_client()
    elif len(sys.argv) > 1 and sys.argv[1] == "--test-greenlight":
        # Run greenlight integration tests
        test_greenlight_integration()
    else:
        # Run legacy test
        print("Usage:")
        print("  python kalshi-mcp.py --mcp-server       # Run as MCP server")
        print("  python kalshi-mcp.py --test             # Run MCP client test")
        print("  python kalshi-mcp.py --test-greenlight  # Run greenlight integration tests")
        print("  python kalshi-mcp.py                    # Run legacy test (direct API calls)")
        print()
        legacy_test()
