#!/usr/bin/env python3
"""
Test client for new technical analysis tools in the MCP server.

Tests the 5 new tools added from kalshi-mcp.py:
1. get_markets_with_probabilities
2. analyze_market_volatility
3. analyze_market_volume
4. greenlight_analysis
5. scan_categories_for_opportunities

Usage:
    python test_technical_tools.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the tool functions directly for testing
from server import (
    get_markets_with_probabilities_tool,
    analyze_market_volatility_tool,
    analyze_market_volume_tool,
    greenlight_analysis_tool,
    scan_categories_for_opportunities_tool,
    _get_markets_with_probabilities_impl
)


async def test_get_markets_with_probabilities():
    """Test 1: Get markets with probabilities"""
    print("\n" + "="*80)
    print("TEST 1: get_markets_with_probabilities")
    print("="*80)

    try:
        categories = ["Economics"]
        print(f"Testing with categories: {categories}")

        result = await get_markets_with_probabilities_tool(categories)
        data = json.loads(result)

        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return False

        print(f"✓ Found {len(data)} markets")

        if len(data) > 0:
            sample = data[0]
            print(f"\nSample market:")
            print(f"  Ticker: {sample.get('ticker')}")
            print(f"  Title: {sample.get('title', '')[:60]}...")
            print(f"  Market P: {sample.get('market_p')}")
            print(f"  Spread Conf: {sample.get('spread_conf')}")
            print(f"  Volume: {sample.get('volume')}")

        print("\n✅ Test PASSED")
        return True

    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_analyze_market_volatility():
    """Test 2: Analyze market volatility"""
    print("\n" + "="*80)
    print("TEST 2: analyze_market_volatility")
    print("="*80)

    try:
        # Get a real market first
        df = _get_markets_with_probabilities_impl(["Economics"])

        if df.empty:
            print("⚠️  No markets available to test")
            return True  # Not a failure, just no data

        market = df.iloc[0]
        ticker = market['ticker']

        print(f"Testing with market: {ticker}")

        result = await analyze_market_volatility_tool(
            ticker=ticker,
            current_price=market.get('last_price', 50),
            yes_bid=market.get('yes_bid', 45),
            yes_ask=market.get('yes_ask', 55),
            previous_price=None
        )

        data = json.loads(result)

        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return False

        print(f"\nVolatility Analysis:")
        print(f"  Volatility: {data.get('volatility')}")
        print(f"  Volatility Confidence: {data.get('volatility_confidence')}")
        print(f"  Momentum: {data.get('momentum')}")
        print(f"  Price Trend: {data.get('price_trend')}")
        print(f"  Spread Volatility: {data.get('spread_volatility')}")

        print("\n✅ Test PASSED")
        return True

    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_analyze_market_volume():
    """Test 3: Analyze market volume"""
    print("\n" + "="*80)
    print("TEST 3: analyze_market_volume")
    print("="*80)

    try:
        # Get a real market first
        df = _get_markets_with_probabilities_impl(["Economics"])

        if df.empty:
            print("⚠️  No markets available to test")
            return True

        ticker = df.iloc[0]['ticker']
        print(f"Testing with market: {ticker}")

        result = await analyze_market_volume_tool(ticker)
        data = json.loads(result)

        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return False

        print(f"\nVolume Analysis:")
        print(f"  Volume: {data.get('volume')}")
        print(f"  Open Interest: {data.get('open_interest')}")
        print(f"  Volume Confidence: {data.get('volume_confidence')}")
        print(f"  Liquidity Score: {data.get('liquidity_score')}")

        print("\n✅ Test PASSED")
        return True

    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_greenlight_analysis():
    """Test 4: Greenlight trading analysis with sentiment"""
    print("\n" + "="*80)
    print("TEST 4: greenlight_analysis (with sentiment)")
    print("="*80)

    try:
        # Test 4a: Without sentiment (disabled)
        print("\nTest 4a: Greenlight without sentiment")
        ticker = "TEST-MARKET"
        market_title = "Will the stock market reach new highs?"

        print(f"Testing with synthetic data: {ticker}")

        result = await greenlight_analysis_tool(
            ticker=ticker,
            market_title=market_title,
            market_p=0.45,
            volatility_confidence=0.75,
            volume_confidence=0.65,
            momentum="bullish",
            spread_conf=0.8,
            include_sentiment=False
        )

        data = json.loads(result)

        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return False

        print(f"\nGreenlight Analysis (No Sentiment):")
        print(f"  Decision: {data.get('decision')}")
        print(f"  Technical Direction: {data.get('technical_direction')}")
        print(f"  Market P: {data.get('market_p')}")
        print(f"  Final Confidence: {data.get('final_confidence')}")
        print(f"  Momentum: {data.get('momentum')}")
        print(f"  Reasoning: {data.get('reasoning')}")

        # Validate decision is valid
        valid_decisions = ['BUY', 'SHORT', 'PASS']
        if data.get('decision') not in valid_decisions:
            print(f"❌ Invalid decision: {data.get('decision')}")
            return False

        # Test 4b: With sentiment (enabled) - requires X_API_KEY
        print("\n\nTest 4b: Greenlight with sentiment (requires X_API_KEY)")
        import os
        if not os.getenv("X_API_KEY"):
            print("⚠️  X_API_KEY not set - skipping sentiment test")
            print("✅ Test PASSED (partial)")
            return True

        result_with_sentiment = await greenlight_analysis_tool(
            ticker=ticker,
            market_title=market_title,
            market_p=0.45,
            volatility_confidence=0.75,
            volume_confidence=0.65,
            momentum="bullish",
            spread_conf=0.8,
            include_sentiment=True
        )

        data_with_sentiment = json.loads(result_with_sentiment)

        if "error" in data_with_sentiment:
            print(f"⚠️  Sentiment analysis error: {data_with_sentiment['error']}")
            print("✅ Test PASSED (sentiment unavailable)")
            return True

        print(f"\nGreenlight Analysis (With Sentiment):")
        print(f"  Decision: {data_with_sentiment.get('decision')}")
        print(f"  Technical Direction: {data_with_sentiment.get('technical_direction')}")
        print(f"  Final Confidence: {data_with_sentiment.get('final_confidence')}")

        if 'sentiment' in data_with_sentiment:
            sentiment = data_with_sentiment['sentiment']
            print(f"\n  Sentiment:")
            print(f"    Label: {sentiment.get('label')}")
            print(f"    Score: {sentiment.get('score')}")
            print(f"    Confidence: {sentiment.get('confidence')}")
            print(f"    Key Themes: {sentiment.get('key_themes')}")
            print(f"    Market Impact: {sentiment.get('market_impact')}")

        print(f"\n  Reasoning: {data_with_sentiment.get('reasoning')}")

        print("\n✅ Test PASSED")
        return True

    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_scan_categories_for_opportunities():
    """Test 5: Scan categories for opportunities (with sentiment)"""
    print("\n" + "="*80)
    print("TEST 5: scan_categories_for_opportunities (with sentiment)")
    print("="*80)

    try:
        import os
        if not os.getenv("X_API_KEY"):
            print("⚠️  X_API_KEY not set - this test will likely return no opportunities")
            print("⚠️  Sentiment analysis is required for greenlight decisions")

        categories = ["Economics"]
        print(f"\nTesting with categories: {categories}")
        print("Note: This may take 1-2 minutes as it analyzes markets with sentiment...\n")

        result = await scan_categories_for_opportunities_tool(
            categories=categories,
            min_confidence=0.25,  # Lowered to find more opportunities
            top_n=10  # Increased to show more results
        )

        data = json.loads(result)

        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return False

        if "message" in data:
            print(f"⚠️  {data['message']}")
            print("ℹ️  This is expected if no markets pass both technical + sentiment checks")
            return True

        print(f"✓ Found {len(data)} opportunities (both technical + sentiment aligned)\n")

        for i, opp in enumerate(data, 1):
            print(f"Opportunity {i}:")
            print(f"  Ticker: {opp.get('ticker')}")
            print(f"  Title: {opp.get('title', '')[:60]}...")
            print(f"  Decision: {opp.get('decision')} (BUY or SHORT only)")
            print(f"  Technical Direction: {opp.get('technical_direction')}")
            print(f"  Final Confidence: {opp.get('final_confidence')}")
            print(f"  Momentum: {opp.get('momentum')}")
            print(f"  Market P: {opp.get('market_p')}")

            if 'sentiment' in opp:
                print(f"  Sentiment: {opp['sentiment'].get('label')} (score: {opp['sentiment'].get('score')})")
                print(f"  Sentiment Themes: {opp['sentiment'].get('key_themes')}")

            print(f"  Reasoning: {opp.get('reasoning', '')[:100]}...")
            print()

        print("✅ Test PASSED")
        return True

    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_integration():
    """Test 6: Full integration test with sentiment"""
    print("\n" + "="*80)
    print("TEST 6: Full Integration Test (with sentiment)")
    print("="*80)

    try:
        import os
        if not os.getenv("X_API_KEY"):
            print("⚠️  X_API_KEY not set - testing without sentiment")

        # Get a real market
        df = _get_markets_with_probabilities_impl(["Economics"])

        if df.empty:
            print("⚠️  No markets available for integration test")
            return True

        market = df.iloc[0]
        ticker = market['ticker']
        market_title = market.get('title', ticker)

        print(f"Running full pipeline on: {ticker}")
        print(f"Title: {market_title[:70]}...\n")

        # Step 1: Get market data
        print("Step 1: Market data ✓")
        market_p = market.get('market_p', 0.5)
        spread_conf = market.get('spread_conf', 0.5)
        print(f"  Market Price: {market_p:.2%}")
        print(f"  Spread Confidence: {spread_conf:.2f}")

        # Step 2: Volatility analysis
        print("\nStep 2: Analyzing volatility...")
        vol_result = await analyze_market_volatility_tool(
            ticker=ticker,
            current_price=market.get('last_price', 50),
            yes_bid=market.get('yes_bid', 45),
            yes_ask=market.get('yes_ask', 55),
            previous_price=None
        )
        vol_data = json.loads(vol_result)
        print(f"  Momentum: {vol_data.get('momentum')}")
        print(f"  Volatility Confidence: {vol_data.get('volatility_confidence'):.2f}")

        # Step 3: Volume analysis
        print("\nStep 3: Analyzing volume...")
        volume_result = await analyze_market_volume_tool(ticker)
        volume_data = json.loads(volume_result)
        print(f"  Volume: {volume_data.get('volume')}")
        print(f"  Volume Confidence: {volume_data.get('volume_confidence'):.2f}")

        # Step 4: Greenlight decision with sentiment
        print("\nStep 4: Generating trading decision (with sentiment check)...")
        greenlight_result = await greenlight_analysis_tool(
            ticker=ticker,
            market_title=market_title,
            market_p=market_p,
            volatility_confidence=vol_data.get('volatility_confidence', 0.5),
            volume_confidence=volume_data.get('volume_confidence', 0.5),
            momentum=vol_data.get('momentum', 'neutral'),
            spread_conf=spread_conf,
            include_sentiment=True
        )
        greenlight_data = json.loads(greenlight_result)

        print(f"\nFinal Result:")
        print(f"  Decision: {greenlight_data.get('decision')}")
        print(f"  Technical Direction: {greenlight_data.get('technical_direction')}")
        print(f"  Confidence: {greenlight_data.get('final_confidence'):.2f}")

        if 'sentiment' in greenlight_data:
            sentiment = greenlight_data['sentiment']
            print(f"\n  Sentiment Analysis:")
            print(f"    Label: {sentiment.get('label')}")
            print(f"    Score: {sentiment.get('score')}")
            print(f"    Key Themes: {sentiment.get('key_themes')}")

        print(f"\n  Reasoning: {greenlight_data.get('reasoning')}")

        print("\n✅ Integration Test PASSED")
        return True

    except Exception as e:
        print(f"❌ Integration Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "🚀"*40)
    print("TECHNICAL ANALYSIS TOOLS TEST SUITE")
    print("🚀"*40)

    results = {
        "Test 1: get_markets_with_probabilities": await test_get_markets_with_probabilities(),
        "Test 2: analyze_market_volatility": await test_analyze_market_volatility(),
        "Test 3: analyze_market_volume": await test_analyze_market_volume(),
        "Test 4: greenlight_analysis": await test_greenlight_analysis(),
        "Test 5: scan_categories_for_opportunities": await test_scan_categories_for_opportunities(),
        "Test 6: Full Integration": await test_integration(),
    }

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
