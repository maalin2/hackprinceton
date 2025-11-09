#!/usr/bin/env python3
"""
Hybrid Analysis System: Statistical Screening + Grok AI Sentiment Verification

Pipeline:
1. Statistical screening: Filter markets by quantitative edge (fast, cheap)
2. Grok sentiment analysis: Verify filtered bets with AI (slow, costs $)
3. Combine signals: Weighted decision with reasoning

Usage:
    from hybrid_analysis import analyze_all_markets
    opportunities = await analyze_all_markets(edge_threshold=0.10)
"""

import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Any
from weather_test import get_open_weather_markets, enrich_with_weather_probs
from politics_test import get_open_politics_markets, enrich_with_politics_probs
from economics_test import get_open_economics_markets, enrich_with_economics_probs

# Import Grok sentiment analysis from MCP server
sys.path.insert(0, 'mcp_quantitative_agent')
from server import sentiment_analysis

# ============================================================================
# STEP 1: STATISTICAL SCREENING
# ============================================================================

def statistical_screening(edge_threshold: float = 0.10) -> List[Dict[str, Any]]:
    """
    Screen all markets using quantitative analysis.
    Returns only high-edge opportunities (fast filtering).
    
    Args:
        edge_threshold: Minimum absolute edge to keep (default: 10%)
    
    Returns:
        List of opportunities with statistical edge
    """
    print("\n" + "="*100)
    print("🔍 STEP 1: STATISTICAL SCREENING")
    print("="*100)
    print(f"Edge threshold: {edge_threshold:.1%}")
    print()
    
    all_opportunities = []
    
    # Weather markets
    print("🌤️  Analyzing weather markets...")
    try:
        df_weather = get_open_weather_markets(limit=50)
        if not df_weather.empty:
            df_weather = enrich_with_weather_probs(df_weather)
            weather_filtered = df_weather[df_weather['edge'].abs() > edge_threshold].copy()
            
            for idx, row in weather_filtered.iterrows():
                all_opportunities.append({
                    'category': 'Weather',
                    'ticker': row['ticker'],
                    'title': row['title'],
                    'action': 'BUY_YES' if row['edge'] > 0 else 'BUY_NO',
                    'quant_edge': float(row['edge']),
                    'quant_prob': float(row.get('p_noaa', 0.5)),
                    'market_prob': float(row.get('market_p', 0.5)),
                    'confidence': float(row.get('confidence', 0.8)),
                    'sources': ['NOAA', 'Open-Meteo', 'Climatology'],
                })
            
            print(f"   Found {len(weather_filtered)} high-edge weather bets")
    except Exception as e:
        print(f"   ⚠️  Weather analysis failed: {e}")
    
    # Politics markets
    print("🏛️  Analyzing politics markets...")
    try:
        df_politics = get_open_politics_markets(limit=50)
        if not df_politics.empty:
            df_politics = enrich_with_politics_probs(df_politics)
            politics_filtered = df_politics[df_politics['edge'].abs() > edge_threshold].copy()
            
            for idx, row in politics_filtered.iterrows():
                all_opportunities.append({
                    'category': 'Politics',
                    'ticker': row['ticker'],
                    'title': row['title'],
                    'action': 'BUY_YES' if row['edge'] > 0 else 'BUY_NO',
                    'quant_edge': float(row['edge']),
                    'quant_prob': float(row.get('p_consensus', 0.5)),
                    'market_prob': float(row.get('market_p', 0.5)),
                    'confidence': float(row.get('confidence', 0.7)),
                    'sources': ['Kalshi Consensus', 'Historical Patterns', 'Betting Models'],
                })
            
            print(f"   Found {len(politics_filtered)} high-edge politics bets")
    except Exception as e:
        print(f"   ⚠️  Politics analysis failed: {e}")
    
    # Economics markets
    print("💰 Analyzing economics markets...")
    try:
        df_economics = get_open_economics_markets(limit=50)
        if not df_economics.empty:
            df_economics = enrich_with_economics_probs(df_economics)
            economics_filtered = df_economics[df_economics['edge'].abs() > edge_threshold].copy()
            
            for idx, row in economics_filtered.iterrows():
                all_opportunities.append({
                    'category': 'Economics',
                    'ticker': row['ticker'],
                    'title': row['title'],
                    'action': 'BUY_YES' if row['edge'] > 0 else 'BUY_NO',
                    'quant_edge': float(row['edge']),
                    'quant_prob': float(row.get('p_fred', 0.5)),
                    'market_prob': float(row.get('market_p', 0.5)),
                    'confidence': float(row.get('confidence', 0.7)),
                    'sources': ['FRED', 'Economic Indicators', 'Market Consensus'],
                })
            
            print(f"   Found {len(economics_filtered)} high-edge economics bets")
    except Exception as e:
        print(f"   ⚠️  Economics analysis failed: {e}")
    
    # Sort by absolute edge (highest first)
    all_opportunities.sort(key=lambda x: abs(x['quant_edge']), reverse=True)
    
    print()
    print(f"✅ Statistical screening complete: {len(all_opportunities)} opportunities")
    print(f"   (Filtered from ~150 markets → {len(all_opportunities)} high-edge bets)")
    print()
    
    return all_opportunities


# ============================================================================
# STEP 2: GROK SENTIMENT VERIFICATION
# ============================================================================

async def grok_sentiment_verification(opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Run Grok sentiment analysis on filtered opportunities.
    
    Args:
        opportunities: List from statistical screening
    
    Returns:
        Same list with 'grok_sentiment' added to each
    """
    print("="*100)
    print("🤖 STEP 2: GROK SENTIMENT VERIFICATION")
    print("="*100)
    print(f"Running Grok analysis on {len(opportunities)} markets...")
    print()
    
    # Run Grok analysis in parallel for speed
    async def analyze_single(opp):
        try:
            print(f"   🔍 Analyzing: {opp['ticker']}")
            print(f"      Market: {opp['title'][:60]}...")
            
            sentiment = await sentiment_analysis(
                market_title=opp['title'],
                market_ticker=opp['ticker']
            )
            opp['grok_sentiment'] = sentiment
            
            # Print Grok result
            if sentiment.get('status') == 'success':
                print(f"      ✅ Grok: {sentiment.get('sentiment_label', sentiment.get('label', 'neutral'))} ({sentiment.get('sentiment_score', sentiment.get('score', 50))}%)")
                themes = sentiment.get('key_themes', [])
                if themes:
                    print(f"      🏷️  Themes: {', '.join(themes[:3])}")
            else:
                print(f"      ⚠️  Grok failed: {sentiment.get('error', 'Unknown error')}")
                print(f"         Message: {sentiment.get('message', 'No details available')}")
                print(f"         Using neutral sentiment fallback (50%)")
            
            return opp
        except Exception as e:
            print(f"   ⚠️  Grok failed for {opp['ticker']}: {e}")
            # Fallback: neutral sentiment
            opp['grok_sentiment'] = {
                'status': 'error',
                'label': 'neutral',
                'score': 50,
                'confidence': 'low',
                'key_themes': [],
                'error': str(e)
            }
            return opp
    
    # Analyze in parallel (but limit concurrency to avoid rate limits)
    results = []
    for i in range(0, len(opportunities), 5):  # Process 5 at a time
        batch = opportunities[i:i+5]
        print(f"\n   📦 Batch {i//5 + 1}: Analyzing {len(batch)} markets in parallel...")
        batch_results = await asyncio.gather(*[analyze_single(opp) for opp in batch])
        results.extend(batch_results)
        print(f"   ✅ Batch {i//5 + 1} complete")
    
    print()
    print(f"✅ Grok analysis complete")
    print()
    
    return results


# ============================================================================
# STEP 3: COMBINE SIGNALS
# ============================================================================

def combine_signals(opportunities: List[Dict[str, Any]], 
                   quant_weight: float = 0.75,
                   sentiment_weight: float = 0.25) -> List[Dict[str, Any]]:
    """
    Combine quantitative edge with Grok sentiment.
    
    Weighting:
    - 75% quantitative edge
    - 25% Grok sentiment
    
    Alignment check:
    - If both positive → HIGH CONFIDENCE
    - If both negative → SKIP (don't show)
    - If disagree → MEDIUM CONFIDENCE (flag for review)
    
    Args:
        opportunities: List with quant + sentiment data
        quant_weight: Weight for quantitative signal (default 0.75)
        sentiment_weight: Weight for sentiment signal (default 0.25)
    
    Returns:
        Opportunities with combined decision and reasoning
    """
    print("="*100)
    print("🎯 STEP 3: COMBINE SIGNALS")
    print("="*100)
    print(f"Weights: {quant_weight:.0%} quantitative, {sentiment_weight:.0%} sentiment")
    print()
    
    final_recommendations = []
    
    for opp in opportunities:
        # Get quantitative signal
        quant_edge = opp['quant_edge']
        quant_positive = quant_edge > 0
        
        # Get sentiment signal
        sentiment = opp.get('grok_sentiment', {})
        sentiment_score = sentiment.get('score', 50) / 100  # Convert to 0-1
        sentiment_positive = sentiment_score > 0.5
        
        # Check alignment
        aligned = quant_positive == sentiment_positive
        
        # Calculate combined confidence
        quant_confidence = abs(quant_edge)
        sentiment_confidence = abs(sentiment_score - 0.5) * 2  # Convert to 0-1 range
        
        combined_confidence = (
            quant_weight * quant_confidence + 
            sentiment_weight * sentiment_confidence
        )
        
        # Skip if signals disagree AND confidence is low
        if not aligned and combined_confidence < 0.5:
            print(f"   ⚠️  SKIPPED: {opp['ticker']} (signals disagree, low confidence)")
            continue
        
        # Generate reasoning
        reasoning_parts = []
        
        # Quantitative reasoning
        reasoning_parts.append(
            f"Statistical analysis shows a {abs(quant_edge):.1%} edge. "
            f"Models predict {opp['quant_prob']:.1%} probability vs market price of {opp['market_prob']:.1%}."
        )
        
        # Sentiment reasoning
        if sentiment.get('status') == 'success':
            sentiment_label = sentiment.get('label', 'neutral')
            key_themes = sentiment.get('key_themes', [])
            reasoning_parts.append(
                f"Grok AI sentiment analysis: {sentiment_label} ({sentiment.get('score')}%). "
                f"Key themes: {', '.join(key_themes[:3])}."
            )
        else:
            reasoning_parts.append("Sentiment analysis unavailable.")
        
        # Alignment reasoning
        if aligned:
            reasoning_parts.append(
                "✅ Both quantitative and sentiment signals AGREE, increasing confidence."
            )
        else:
            reasoning_parts.append(
                "⚠️ Quantitative and sentiment signals DISAGREE. Consider with caution."
            )
        
        reasoning = " ".join(reasoning_parts)
        
        # Create final recommendation
        final_recommendations.append({
            'ticker': opp['ticker'],
            'title': opp['title'],
            'category': opp['category'],
            'url': f"https://kalshi.com/markets/{opp['ticker']}",
            
            # Decision
            'action': opp['action'],
            'combined_confidence': float(combined_confidence),
            'aligned': aligned,
            'reasoning': reasoning,
            
            # Quantitative data
            'quant_edge': opp['quant_edge'],
            'quant_prob': opp['quant_prob'],
            'market_prob': opp['market_prob'],
            'quant_sources': opp['sources'],
            
            # Sentiment data
            'grok_sentiment': sentiment,
            
            # Metadata
            'timestamp': datetime.now().isoformat(),
        })
        
        status = "✅ HIGH" if aligned else "⚠️  MEDIUM"
        print(f"   {status} confidence: {opp['ticker']} ({combined_confidence:.1%})")
        print(f"      Action: {opp['action']}, Edge: {opp['quant_edge']:.1%}")
        print(f"      Quant: {opp['quant_prob']:.1%} | Grok: {sentiment_score:.1%} | Market: {opp['market_prob']:.1%}")
    
    print()
    print(f"✅ Combined {len(final_recommendations)} final recommendations")
    print()
    
    return final_recommendations


# ============================================================================
# MAIN PIPELINE
# ============================================================================

async def analyze_all_markets(
    edge_threshold: float = 0.10,
    quant_weight: float = 0.75,
    sentiment_weight: float = 0.25,
    max_recommendations: int = 20
) -> List[Dict[str, Any]]:
    """
    Full hybrid analysis pipeline.
    
    Args:
        edge_threshold: Minimum edge for statistical screening (default: 10%)
        quant_weight: Weight for quantitative signal (default: 75%)
        sentiment_weight: Weight for sentiment signal (default: 25%)
        max_recommendations: Maximum recommendations to return
    
    Returns:
        List of final recommendations with combined analysis
    """
    print("\n" + "🚀"*50)
    print("HYBRID ANALYSIS: STATISTICAL + GROK AI")
    print("🚀"*50)
    print()
    
    # Step 1: Statistical screening (fast)
    opportunities = statistical_screening(edge_threshold=edge_threshold)
    
    # Limit to top N by edge (avoid too many Grok calls)
    opportunities = opportunities[:max_recommendations]
    
    if not opportunities:
        print("⚠️  No opportunities found in statistical screening")
        return []
    
    # Step 2: Grok sentiment verification (slow, costs money)
    opportunities = await grok_sentiment_verification(opportunities)
    
    # Step 3: Combine signals
    final_recommendations = combine_signals(
        opportunities,
        quant_weight=quant_weight,
        sentiment_weight=sentiment_weight
    )
    
    print("="*100)
    print("📊 ANALYSIS COMPLETE")
    print("="*100)
    print(f"Total recommendations: {len(final_recommendations)}")
    print(f"Average confidence: {sum(r['combined_confidence'] for r in final_recommendations) / len(final_recommendations):.1%}")
    print(f"Aligned signals: {sum(1 for r in final_recommendations if r['aligned'])}/{len(final_recommendations)}")
    print()
    
    return final_recommendations


# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hybrid betting analysis: Stats + Grok AI')
    parser.add_argument('--edge', type=float, default=0.10, help='Edge threshold (default: 0.10)')
    parser.add_argument('--max', type=int, default=20, help='Max recommendations (default: 20)')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    # Run analysis
    recommendations = await analyze_all_markets(
        edge_threshold=args.edge,
        max_recommendations=args.max
    )
    
    if args.json:
        import json
        print(json.dumps(recommendations, indent=2))
    else:
        # Pretty print
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{'='*100}")
            print(f"#{i} - {rec['category'].upper()}")
            print(f"{'='*100}")
            print(f"🎲 {rec['action']}: {rec['ticker']}")
            print(f"📝 {rec['title']}")
            print(f"🔗 {rec['url']}")
            print()
            print(f"📊 Quantitative Edge: {rec['quant_edge']:.1%}")
            print(f"🤖 Grok Sentiment: {rec['grok_sentiment'].get('label')} ({rec['grok_sentiment'].get('score')}%)")
            print(f"🎯 Combined Confidence: {rec['combined_confidence']:.1%}")
            print(f"✅ Aligned: {'YES' if rec['aligned'] else 'NO'}")
            print()
            print(f"💡 {rec['reasoning']}")


if __name__ == "__main__":
    asyncio.run(main())

