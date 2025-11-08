#!/usr/bin/env python3
"""
Analyze Kalshi Markets with Configurable Strategies

Allows users to choose between different analysis strategies:
- statistical_arbitrage: Multi-source comparison (default)
- moving_average: Price trend analysis with MAs
"""

import argparse
import sys
from strategies import get_strategy
import weather_test
import politics_test
import economics_test


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Kalshi markets using different strategies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Statistical arbitrage (default)
  python analyze_with_strategy.py --category weather --strategy statistical_arbitrage

  # Moving average with 7-day window
  python analyze_with_strategy.py --category weather --strategy moving_average --ma-period 7

  # Moving average with trend following
  python analyze_with_strategy.py --category politics --strategy moving_average --signal-type trend_following

  # EMA instead of SMA
  python analyze_with_strategy.py --category economics --strategy moving_average --ma-type ema --ma-period 14
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--category',
        required=True,
        choices=['weather', 'politics', 'economics'],
        help='Market category to analyze'
    )
    
    # Strategy selection
    parser.add_argument(
        '--strategy',
        default='statistical_arbitrage',
        choices=['statistical_arbitrage', 'moving_average'],
        help='Analysis strategy to use (default: statistical_arbitrage)'
    )
    
    # Common arguments
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of markets to analyze (default: 5)'
    )
    
    # Moving Average strategy parameters
    ma_group = parser.add_argument_group('Moving Average Strategy Options')
    ma_group.add_argument(
        '--ma-period',
        type=int,
        default=7,
        help='Moving average period in days (default: 7)'
    )
    ma_group.add_argument(
        '--ma-type',
        choices=['sma', 'ema'],
        default='sma',
        help='Moving average type: sma (simple) or ema (exponential) (default: sma)'
    )
    ma_group.add_argument(
        '--signal-type',
        choices=['mean_reversion', 'trend_following'],
        default='mean_reversion',
        help='Signal type for MA strategy (default: mean_reversion)'
    )
    ma_group.add_argument(
        '--lookback-days',
        type=int,
        default=30,
        help='Days of historical data to fetch (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("=" * 80)
    print(f"📊 KALSHI MARKET ANALYSIS - {args.category.upper()}")
    print("=" * 80)
    print()
    print(f"Strategy: {args.strategy}")
    if args.strategy == 'moving_average':
        print(f"  MA Type: {args.ma_type.upper()}")
        print(f"  MA Period: {args.ma_period} days")
        print(f"  Signal Type: {args.signal_type}")
        print(f"  Lookback: {args.lookback_days} days")
    print()
    print("=" * 80)
    print()
    
    # Fetch markets
    print(f"🔍 Fetching {args.category} markets...")
    if args.category == 'weather':
        df = weather_test.get_open_weather_markets(limit=args.limit)
    elif args.category == 'politics':
        df = politics_test.get_open_politics_markets(limit=args.limit)
    else:  # economics
        df = economics_test.get_open_economics_markets(limit=args.limit)
    
    if df.empty:
        print(f"❌ No {args.category} markets found")
        return
    
    print(f"✅ Found {len(df)} markets")
    print()
    print("=" * 80)
    print()
    
    # Initialize strategy
    strategy_config = {}
    if args.strategy == 'moving_average':
        strategy_config = {
            'ma_period': args.ma_period,
            'ma_type': args.ma_type,
            'signal_type': args.signal_type,
            'lookback_days': args.lookback_days,
        }
    
    strategy = get_strategy(args.strategy, args.category, **strategy_config)
    
    print(f"⚙️  Analyzing {len(df)} markets with {strategy.get_description()}...")
    print("=" * 80)
    print()
    
    # Analyze each market
    results = []
    for idx, row in df.iterrows():
        market = row.to_dict()
        
        print(f"📊 Analyzing: {market['ticker']}")
        print(f"   Title: {market.get('title', 'N/A')[:70]}...")
        
        try:
            result = strategy.analyze(market)
            
            # Get market price
            p_market = None
            if 'yes_bid' in market and 'yes_ask' in market:
                yes_bid = market.get('yes_bid', 0)
                yes_ask = market.get('yes_ask', 100)
                if yes_bid or yes_ask:
                    p_market = ((yes_bid + yes_ask) / 2) / 100.0
            if p_market is None and 'last_price' in market:
                last_price = market.get('last_price', 50)
                p_market = last_price / 100.0 if last_price and last_price > 1 else (last_price or 0.5)
            if p_market is None:
                p_market = 0.5
            
            # Calculate edge
            edge = result.p_quant - p_market
            edge_pct = edge * 100
            
            # Determine action
            if edge >= 0.08:
                action = "BUY YES"
                emoji = "🟢"
            elif edge <= -0.08:
                action = "BUY NO"
                emoji = "🔴"
            else:
                action = "HOLD"
                emoji = "⚪"
            
            print(f"   📈 P(Quant): {result.p_quant:.3f} (confidence: {result.confidence:.2f})")
            print(f"   💰 P(Market): {p_market:.3f}")
            print(f"   {emoji} Edge: {edge_pct:+.1f}% → {action}")
            
            # Print strategy-specific signals
            if result.signals:
                print(f"   🔧 Signals:")
                for key, value in result.signals.items():
                    if key != 'error' and not key.startswith('_'):
                        print(f"      - {key}: {value}")
            
            # Print sources if available
            if result.sources:
                print(f"   📊 Sources:")
                for source, value in result.sources.items():
                    if isinstance(value, (int, float)):
                        print(f"      - {source}: {value:.3f}")
                    else:
                        print(f"      - {source}: {value}")
            
            print()
            
            results.append({
                'ticker': market['ticker'],
                'p_quant': result.p_quant,
                'p_market': p_market,
                'edge': edge,
                'edge_pct': edge_pct,
                'action': action,
                'confidence': result.confidence,
            })
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
            continue
    
    # Summary
    if results:
        print("=" * 80)
        print("📈 SUMMARY")
        print("=" * 80)
        print()
        
        # Sort by absolute edge
        results_sorted = sorted(results, key=lambda x: abs(x['edge']), reverse=True)
        
        buy_yes = [r for r in results if r['action'] == 'BUY YES']
        buy_no = [r for r in results if r['action'] == 'BUY NO']
        hold = [r for r in results if r['action'] == 'HOLD']
        
        print(f"Total Markets Analyzed: {len(results)}")
        print(f"  🟢 BUY YES:  {len(buy_yes)}")
        print(f"  🔴 BUY NO:   {len(buy_no)}")
        print(f"  ⚪ HOLD:     {len(hold)}")
        print()
        
        if buy_yes or buy_no:
            print("Top Opportunities:")
            print()
            for r in results_sorted[:5]:
                if r['action'] != 'HOLD':
                    emoji = "🟢" if r['action'] == 'BUY YES' else "🔴"
                    print(f"  {emoji} {r['ticker']}")
                    print(f"     Edge: {r['edge_pct']:+.1f}% | Confidence: {r['confidence']:.2f} | Action: {r['action']}")
                    print()


if __name__ == "__main__":
    main()

