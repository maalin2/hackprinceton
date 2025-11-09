#!/usr/bin/env python3
"""
Find the best betting opportunities across all categories
Uses both quantitative (weather/politics/economics data) and semantic (sentiment) analysis
"""

import asyncio
import sys
from weather_test import get_open_weather_markets, enrich_with_weather_probs
from politics_test import get_open_politics_markets, enrich_with_politics_probs
from economics_test import get_open_economics_markets, enrich_with_economics_probs

def analyze_weather():
    """Analyze weather markets"""
    print("\n" + "="*100)
    print("🌤️  WEATHER MARKETS - QUANTITATIVE ANALYSIS")
    print("="*100)
    print("📊 Data Sources: NOAA (GFS Model), Open-Meteo (ECMWF Model), Climatology")
    print()
    
    df = get_open_weather_markets(limit=50)
    if df.empty:
        print("⚠️  No weather markets available")
        return []
    
    df = enrich_with_weather_probs(df)
    
    # Filter for strong opportunities (edge > 10%)
    opportunities = df[df['edge'].abs() > 0.10].copy()
    opportunities = opportunities.sort_values('edge', key=abs, ascending=False)
    
    results = []
    for idx, row in opportunities.head(5).iterrows():
        action = 'BUY YES' if row['edge'] > 0 else 'BUY NO'
        results.append({
            'category': 'Weather',
            'ticker': row['ticker'],
            'title': row['title'],
            'action': action,
            'edge': row['edge'],
            'confidence': row.get('confidence', 0.8),
            'quant_prob': row.get('p_noaa', 0.5),  # Use first source as proxy
            'market_prob': row.get('market_p', 0.5),
        })
    
    return results

def analyze_politics():
    """Analyze politics markets"""
    print("\n" + "="*100)
    print("🏛️  POLITICS MARKETS - QUANTITATIVE ANALYSIS")
    print("="*100)
    print("📊 Data Sources: Kalshi Market Consensus, Historical Voting Patterns, Betting Models")
    print()
    
    df = get_open_politics_markets(limit=50)
    if df.empty:
        print("⚠️  No politics markets available")
        return []
    
    df = enrich_with_politics_probs(df)
    
    # Filter for strong opportunities (edge > 10%)
    opportunities = df[df['edge'].abs() > 0.10].copy()
    opportunities = opportunities.sort_values('edge', key=abs, ascending=False)
    
    results = []
    for idx, row in opportunities.head(5).iterrows():
        action = 'BUY YES' if row['edge'] > 0 else 'BUY NO'
        results.append({
            'category': 'Politics',
            'ticker': row['ticker'],
            'title': row['title'],
            'action': action,
            'edge': row['edge'],
            'confidence': row.get('confidence', 0.7),
            'quant_prob': row.get('p_consensus', 0.5),
            'market_prob': row.get('market_p', 0.5),
        })
    
    return results

def analyze_economics():
    """Analyze economics markets"""
    print("\n" + "="*100)
    print("💰 ECONOMICS MARKETS - QUANTITATIVE ANALYSIS")
    print("="*100)
    print("📊 Data Sources: FRED (Federal Reserve), Economic Indicators, Market Consensus")
    print()
    
    df = get_open_economics_markets(limit=50)
    if df.empty:
        print("⚠️  No economics markets available")
        return []
    
    df = enrich_with_economics_probs(df)
    
    # Filter for strong opportunities (edge > 10%)
    opportunities = df[df['edge'].abs() > 0.10].copy()
    opportunities = opportunities.sort_values('edge', key=abs, ascending=False)
    
    results = []
    for idx, row in opportunities.head(5).iterrows():
        action = 'BUY YES' if row['edge'] > 0 else 'BUY NO'
        results.append({
            'category': 'Economics',
            'ticker': row['ticker'],
            'title': row['title'],
            'action': action,
            'edge': row['edge'],
            'confidence': row.get('confidence', 0.7),
            'quant_prob': row.get('p_fred', 0.5),
            'market_prob': row.get('market_p', 0.5),
        })
    
    return results

def print_recommendations(opportunities):
    """Print final recommendations"""
    if not opportunities:
        print("\n⚠️  No high-confidence opportunities found across all categories")
        print("   Try lowering the edge threshold or checking back later")
        return
    
    # Sort by absolute edge (strongest opportunities first)
    opportunities.sort(key=lambda x: abs(x['edge']), reverse=True)
    
    print("\n" + "="*100)
    print("🎯 TOP BETTING OPPORTUNITIES - RANKED BY EDGE")
    print("="*100)
    print()
    print(f"Found {len(opportunities)} opportunities with >10% edge")
    print()
    
    for i, opp in enumerate(opportunities[:10], 1):
        print(f"{'='*100}")
        print(f"#{i} - {opp['category'].upper()}")
        print(f"{'='*100}")
        print()
        print(f"🎲 {opp['action']}: {opp['ticker']}")
        print(f"📝 Market: {opp['title'][:80]}")
        print(f"🔗 Link: https://kalshi.com/markets/{opp['ticker']}")
        print()
        print(f"📊 QUANTITATIVE ANALYSIS:")
        print(f"   Model Probability: {opp['quant_prob']:.1%}")
        print(f"   Market Price: {opp['market_prob']:.1%}")
        print(f"   ⚡ EDGE: {opp['edge']:.1%}")
        print(f"   Confidence: {opp['confidence']:.1%}")
        print()
        
        # Explain the edge
        if opp['edge'] > 0:
            print(f"💡 WHY BET YES:")
            print(f"   The quantitative model thinks this event is {opp['quant_prob']:.1%} likely,")
            print(f"   but the market is only pricing it at {opp['market_prob']:.1%}.")
            print(f"   This represents a {abs(opp['edge']):.1%} edge in your favor!")
        else:
            print(f"💡 WHY BET NO:")
            print(f"   The quantitative model thinks this event is only {opp['quant_prob']:.1%} likely,")
            print(f"   but the market is pricing it at {opp['market_prob']:.1%}.")
            print(f"   This represents a {abs(opp['edge']):.1%} edge in your favor!")
        
        print()
    
    print("="*100)
    print("📈 SUMMARY")
    print("="*100)
    print(f"Weather opportunities: {sum(1 for o in opportunities if o['category'] == 'Weather')}")
    print(f"Politics opportunities: {sum(1 for o in opportunities if o['category'] == 'Politics')}")
    print(f"Economics opportunities: {sum(1 for o in opportunities if o['category'] == 'Economics')}")
    print()
    print(f"Average edge: {sum(abs(o['edge']) for o in opportunities) / len(opportunities):.1%}")
    print(f"Highest edge: {max(abs(o['edge']) for o in opportunities):.1%}")
    print()
    print("⚠️  NOTE: These are quantitative predictions. Always do your own research!")
    print("💬 For semantic/sentiment analysis, check Twitter trends for each market")

def main():
    """Main entry point"""
    print("\n" + "🚀"*50)
    print("KALSHI BETTING OPPORTUNITY SCANNER")
    print("🚀"*50)
    print()
    print("Using multi-source quantitative analysis to find statistical arbitrage opportunities")
    print()
    
    # Analyze all categories
    weather_opps = analyze_weather()
    politics_opps = analyze_politics()
    econ_opps = analyze_economics()
    
    # Combine all opportunities
    all_opportunities = weather_opps + politics_opps + econ_opps
    
    # Print recommendations
    print_recommendations(all_opportunities)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()

