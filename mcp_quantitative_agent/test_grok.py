#!/usr/bin/env python3
"""
Test Grok sentiment analysis for Kalshi markets

This script tests using Grok to search X (Twitter) for sentiment
about specific Kalshi markets and returns JSON format.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user, system

# Load environment variables
load_dotenv()

# Add parent directory to path to import test modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import market data functions
try:
    import weather_test
    import politics_test
    import economics_test
except ImportError as e:
    print(f"Warning: Could not import test modules: {e}")
    weather_test = None
    politics_test = None
    economics_test = None


def test_grok_sentiment(market_title: str, market_ticker: str = None):
    """
    Test Grok sentiment analysis for a Kalshi market

    Args:
        market_title: The title/description of the market
        market_ticker: Optional ticker symbol for the market

    Returns:
        dict: JSON response with sentiment analysis
    """

    # Initialize Grok client
    api_key = os.getenv("X_API_KEY")
    if not api_key:
        print("Error: X_API_KEY not set in environment")
        return None

    client = Client(api_key=api_key)

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

    print("=" * 80)
    print("GROK SENTIMENT ANALYSIS TEST")
    print("=" * 80)
    print(f"\nMarket: {market_title}")
    if market_ticker:
        print(f"Ticker: {market_ticker}")
    print("\nQuerying Grok...\n")

    try:
        # Create chat and send message
        chat = client.chat.create(model="grok-4-fast")
        chat.append(system(system_prompt))
        chat.append(user(user_prompt))

        # Get response
        response = chat.sample()

        print("=" * 80)
        print("GROK RESPONSE")
        print("=" * 80)
        print(response.content)
        print("\n")

        # Try to parse as JSON
        try:
            result = json.loads(response.content)
            result["ticker"] = market_ticker
            result["title"] = market_title
            return result
        except json.JSONDecodeError:
            print("Warning: Response is not valid JSON")
            return {
                "ticker": market_ticker,
                "title": market_title,
                "raw_response": response.content
            }

    except Exception as e:
        print(f"Error calling Grok API: {e}")
        return None


def test_simple_grok():
    """Simple test to verify Grok API is working"""

    api_key = os.getenv("X_API_KEY")
    if not api_key:
        print("Error: X_API_KEY not set in environment")
        return False

    client = Client(api_key=api_key)

    print("=" * 80)
    print("SIMPLE GROK TEST")
    print("=" * 80)
    print("\nTesting basic Grok connectivity...\n")

    try:
        chat = client.chat.create(model="grok-4-fast")
        chat.append(user("Say hi and tell me what is 2+2?"))

        response = chat.sample()

        print("Response:")
        print(response.content)
        print("\n✓ Grok API is working!\n")

        return True

    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


def get_recent_markets():
    """Fetch recent open markets from Kalshi"""
    results = {
        "weather": [],
        "politics": [],
        "economics": []
    }

    # Get weather markets
    if weather_test:
        try:
            df = weather_test.get_open_weather_markets()
            if not df.empty:
                results["weather"] = df.head(3).to_dict('records')
        except Exception as e:
            print(f"Could not fetch weather markets: {e}")

    # Get politics markets
    if politics_test:
        try:
            df = politics_test.get_open_politics_markets()
            if not df.empty:
                results["politics"] = df.head(3).to_dict('records')
        except Exception as e:
            print(f"Could not fetch politics markets: {e}")

    # Get economics markets
    if economics_test:
        try:
            df = economics_test.get_open_economics_markets()
            if not df.empty:
                results["economics"] = df.head(3).to_dict('records')
        except Exception as e:
            print(f"Could not fetch economics markets: {e}")

    return results


if __name__ == "__main__":
    # First test basic connectivity
    print("\n")
    if not test_simple_grok():
        print("Basic Grok test failed. Exiting.")
        sys.exit(1)

    print("\n")
    print("=" * 80)
    print("FETCHING RECENT MARKETS")
    print("=" * 80)
    print("\n")

    # Get recent markets
    markets = get_recent_markets()

    # Test sentiment analysis on recent markets
    all_results = []

    # Test one market from each category
    if markets["weather"]:
        print("\n--- Testing Weather Market ---\n")
        market = markets["weather"][0]
        result = test_grok_sentiment(
            market_title=market.get("title", ""),
            market_ticker=market.get("ticker", "")
        )
        if result:
            all_results.append(result)

    if markets["politics"]:
        print("\n--- Testing Politics Market ---\n")
        market = markets["politics"][0]
        result = test_grok_sentiment(
            market_title=market.get("title", ""),
            market_ticker=market.get("ticker", "")
        )
        if result:
            all_results.append(result)

    if markets["economics"]:
        print("\n--- Testing Economics Market ---\n")
        market = markets["economics"][0]
        result = test_grok_sentiment(
            market_title=market.get("title", ""),
            market_ticker=market.get("ticker", "")
        )
        if result:
            all_results.append(result)

    # Print summary
    print("\n")
    print("=" * 80)
    print("SUMMARY - ALL RESULTS")
    print("=" * 80)
    print(json.dumps(all_results, indent=2))
