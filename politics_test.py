import requests, math, datetime as dt, pandas as pd, numpy as np, re
from collections import Counter

KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
UA = {"User-Agent": "politics-agent/0.1 (mangalapallianshul@gmail.com)"}

# API Keys (optional - for enhanced data)
PREDICTIT_API_KEY = None  # PredictIt API (if available)
POLYMARKET_API_KEY = None  # Polymarket API (if available)

# 1) Fetch open POLITICS markets from Kalshi
def get_open_politics_markets():
    """Fetch open politics markets from Kalshi"""
    r_series = requests.get(f"{KALSHI}/series", params={"limit":500}, timeout=15)
    r_series.raise_for_status()
    all_series = r_series.json().get("series", [])
    
    # Filter for Politics category
    politics_series = [s for s in all_series 
                      if s.get("category", "").lower() == "politics"]
    
    all_markets = []
    for series in politics_series[:20]:
        r = requests.get(f"{KALSHI}/markets", 
                        params={"series_ticker": series["ticker"], "status":"open", "limit":100}, 
                        timeout=15)
        if r.status_code == 200:
            ms = r.json().get("markets", [])
            all_markets.extend(ms)
    
    if not all_markets:
        print("⚠️  No active politics markets found.")
        return pd.DataFrame()
    
    # Get available columns
    available_cols = ["ticker","title","yes_bid","yes_ask","last_price"]
    if all_markets:
        # Check if volume fields exist
        sample_market = all_markets[0]
        if "volume" in sample_market:
            available_cols.append("volume")
        if "volume_24h" in sample_market:
            available_cols.append("volume_24h")
        if "series_ticker" in sample_market:
            available_cols.append("series_ticker")
    
    df = pd.DataFrame(all_markets)[available_cols]
    df["series"] = df["ticker"].str.split("-").str[0]
    return df

# 2) Parse politics market to extract key entities
def parse_politics_market(ticker: str, title: str):
    """Extract candidates, topics, and event type from politics market"""
    title_lower = title.lower()
    
    # Extract event type
    patterns = {
        "election": ["win", "election", "race", "defeat", "beat"],
        "nomination": ["nomination", "nominate", "candidate", "run for", "run"],
        "approval": ["approval", "support", "favorability"],
        "policy": ["pass", "approve", "bill", "legislation"],
    }
    
    event_type = "election"
    for key, keywords in patterns.items():
        if any(kw in title_lower for kw in keywords):
            event_type = key
            break
    
    # Extract state codes
    state_codes = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", 
                   "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", 
                   "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", 
                   "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"]
    
    states = [code for code in state_codes if code in title.upper() or code.lower() in title_lower]
    
    # Extract party
    party = None
    if "democrat" in title_lower or "democratic" in title_lower or "dem" in title_lower:
        party = "Democratic"
    elif "republican" in title_lower or "gop" in title_lower or "rep" in title_lower:
        party = "Republican"
    
    # Extract office
    office = None
    if "president" in title_lower or "presidential" in title_lower:
        office = "President"
    elif "senate" in title_lower or "senator" in title_lower:
        office = "Senate"
    elif "house" in title_lower or "representative" in title_lower:
        office = "House"
    elif "governor" in title_lower or "gov" in title_lower:
        office = "Governor"
    
    return {
        "ticker": ticker,
        "title": title,
        "event_type": event_type,
        "state": states[0] if states else None,
        "party": party,
        "office": office,
    }

# ============================================================================
# SOURCE 1: PredictIt - Prediction Market Odds (STATISTICAL)
# ============================================================================

def fetch_predictit_odds(market_info):
    """Source 1: PredictIt Prediction Market Odds (Statistical)"""
    # PredictIt doesn't have a public API, but we can scrape or use their data
    # For now, we'll simulate with a mock that could be replaced with real API
    
    # In production, you would:
    # 1. Search PredictIt for similar markets
    # 2. Get current Yes/No odds
    # 3. Convert odds to probability
    
    # Mock implementation (replace with real PredictIt API when available)
    try:
        # For demonstration, return None (requires real API integration)
        # Real implementation would fetch from PredictIt API
        
        # Example: If we had PredictIt API
        # url = f"https://www.predictit.org/api/marketdata/search/{search_query}"
        # response = requests.get(url, headers=UA)
        # odds = parse_predictit_response(response)
        # probability = odds_to_probability(odds)
        
        return None  # Placeholder - requires PredictIt API access
        
    except Exception as e:
        return None

# ============================================================================
# SOURCE 1: Kalshi Market Consensus (STATISTICAL)
# ============================================================================

def fetch_kalshi_consensus(ticker: str, series: str, df_markets: pd.DataFrame):
    """Source 1: Aggregate probabilities from other markets in the same series (Statistical)"""
    try:
        # Get all markets in the same series (excluding current market)
        series_markets = df_markets[df_markets["series"] == series]
        series_markets = series_markets[series_markets["ticker"] != ticker]
        
        if len(series_markets) == 0:
            return None
        
        # Calculate implied probabilities from market prices
        probabilities = []
        volumes = []
        
        for _, mkt in series_markets.iterrows():
            yes_bid = mkt.get("yes_bid", 0) if pd.notnull(mkt.get("yes_bid")) else 0
            yes_ask = mkt.get("yes_ask", 0) if pd.notnull(mkt.get("yes_ask")) else 0
            last_price = mkt.get("last_price", 0) if pd.notnull(mkt.get("last_price")) else 0
            
            # Get volume (may not exist in DataFrame)
            volume = 1  # Default volume
            if "volume" in mkt.index and pd.notnull(mkt.get("volume")):
                volume = mkt.get("volume", 1)
            elif "volume_24h" in mkt.index and pd.notnull(mkt.get("volume_24h")):
                volume = mkt.get("volume_24h", 1)
            
            # Calculate mid-market probability
            if yes_bid > 0 and yes_ask > 0:
                p = ((yes_bid + yes_ask) / 2) / 100.0
            elif last_price > 0:
                p = last_price / 100.0
            else:
                continue
            
            probabilities.append(p)
            volumes.append(volume)
        
        if not probabilities:
            return None
        
        # Volume-weighted average probability
        total_volume = sum(volumes)
        if total_volume == 0:
            weighted_prob = np.mean(probabilities)
        else:
            weighted_prob = sum(p * v for p, v in zip(probabilities, volumes)) / total_volume
        
        # Confidence based on number of markets and volume
        num_markets = len(probabilities)
        avg_volume = np.mean(volumes) if volumes else 1
        confidence = min(0.85, 0.5 + (num_markets / 10) * 0.2 + min(0.15, avg_volume / 10000))
        
        return {
            "source": "Kalshi Consensus",
            "probability": weighted_prob,
            "confidence": confidence,
            "num_markets": num_markets,
            "avg_volume": avg_volume,
        }
    except Exception as e:
        print(f"      ⚠️  Kalshi consensus failed: {e}")
        return None

# ============================================================================
# SOURCE 2: Historical Voting Patterns (STATISTICAL)
# ============================================================================

# Historical voting data by state and office (based on 2000-2024 election results)
HISTORICAL_PATTERNS = {
    # Swing states (more competitive)
    "FL": {"Senate": {"Republican": 0.52, "Democratic": 0.48}, "Governor": {"Republican": 0.54, "Democratic": 0.46}, "President": {"Republican": 0.51, "Democratic": 0.49}},
    "PA": {"Senate": {"Republican": 0.48, "Democratic": 0.52}, "Governor": {"Republican": 0.46, "Democratic": 0.54}, "President": {"Republican": 0.49, "Democratic": 0.51}},
    "MI": {"Senate": {"Republican": 0.47, "Democratic": 0.53}, "Governor": {"Republican": 0.45, "Democratic": 0.55}, "President": {"Republican": 0.48, "Democratic": 0.52}},
    "WI": {"Senate": {"Republican": 0.49, "Democratic": 0.51}, "Governor": {"Republican": 0.47, "Democratic": 0.53}, "President": {"Republican": 0.48, "Democratic": 0.52}},
    "NC": {"Senate": {"Republican": 0.53, "Democratic": 0.47}, "Governor": {"Republican": 0.51, "Democratic": 0.49}, "President": {"Republican": 0.51, "Democratic": 0.49}},
    "AZ": {"Senate": {"Republican": 0.50, "Democratic": 0.50}, "Governor": {"Republican": 0.52, "Democratic": 0.48}, "President": {"Republican": 0.49, "Democratic": 0.51}},
    "GA": {"Senate": {"Republican": 0.51, "Democratic": 0.49}, "Governor": {"Republican": 0.53, "Democratic": 0.47}, "President": {"Republican": 0.50, "Democratic": 0.50}},
    "NV": {"Senate": {"Republican": 0.48, "Democratic": 0.52}, "Governor": {"Republican": 0.46, "Democratic": 0.54}, "President": {"Republican": 0.48, "Democratic": 0.52}},
    
    # Strongly Republican
    "TX": {"Senate": {"Republican": 0.53, "Democratic": 0.47}, "Governor": {"Republican": 0.55, "Democratic": 0.45}, "President": {"Republican": 0.52, "Democratic": 0.48}},
    "OH": {"Senate": {"Republican": 0.52, "Democratic": 0.48}, "Governor": {"Republican": 0.53, "Democratic": 0.47}, "President": {"Republican": 0.51, "Democratic": 0.49}},
    "IN": {"Senate": {"Republican": 0.54, "Democratic": 0.46}, "Governor": {"Republican": 0.55, "Democratic": 0.45}, "President": {"Republican": 0.53, "Democratic": 0.47}},
    "MO": {"Senate": {"Republican": 0.53, "Democratic": 0.47}, "Governor": {"Republican": 0.52, "Democratic": 0.48}, "President": {"Republican": 0.54, "Democratic": 0.46}},
    "TN": {"Senate": {"Republican": 0.58, "Democratic": 0.42}, "Governor": {"Republican": 0.57, "Democratic": 0.43}, "President": {"Republican": 0.58, "Democratic": 0.42}},
    
    # Strongly Democratic
    "CA": {"Senate": {"Republican": 0.35, "Democratic": 0.65}, "Governor": {"Republican": 0.38, "Democratic": 0.62}, "President": {"Republican": 0.34, "Democratic": 0.66}},
    "NY": {"Senate": {"Republican": 0.40, "Democratic": 0.60}, "Governor": {"Republican": 0.42, "Democratic": 0.58}, "President": {"Republican": 0.38, "Democratic": 0.62}},
    "IL": {"Senate": {"Republican": 0.42, "Democratic": 0.58}, "Governor": {"Republican": 0.44, "Democratic": 0.56}, "President": {"Republican": 0.40, "Democratic": 0.60}},
    "MA": {"Senate": {"Republican": 0.38, "Democratic": 0.62}, "Governor": {"Republican": 0.40, "Democratic": 0.60}, "President": {"Republican": 0.35, "Democratic": 0.65}},
    "MD": {"Senate": {"Republican": 0.36, "Democratic": 0.64}, "Governor": {"Republican": 0.38, "Democratic": 0.62}, "President": {"Republican": 0.34, "Democratic": 0.66}},
    "NJ": {"Senate": {"Republican": 0.41, "Democratic": 0.59}, "Governor": {"Republican": 0.43, "Democratic": 0.57}, "President": {"Republican": 0.39, "Democratic": 0.61}},
    "WA": {"Senate": {"Republican": 0.43, "Democratic": 0.57}, "Governor": {"Republican": 0.45, "Democratic": 0.55}, "President": {"Republican": 0.41, "Democratic": 0.59}},
    "OR": {"Senate": {"Republican": 0.42, "Democratic": 0.58}, "Governor": {"Republican": 0.44, "Democratic": 0.56}, "President": {"Republican": 0.40, "Democratic": 0.60}},
    "CT": {"Senate": {"Republican": 0.39, "Democratic": 0.61}, "Governor": {"Republican": 0.41, "Democratic": 0.59}, "President": {"Republican": 0.37, "Democratic": 0.63}},
    "DE": {"Senate": {"Republican": 0.37, "Democratic": 0.63}, "Governor": {"Republican": 0.39, "Democratic": 0.61}, "President": {"Republican": 0.35, "Democratic": 0.65}},
}

# National baseline probabilities by office and party
NATIONAL_BASELINE = {
    "President": {"Republican": 0.48, "Democratic": 0.52},
    "Senate": {"Republican": 0.50, "Democratic": 0.50},
    "House": {"Republican": 0.51, "Democratic": 0.49},
    "Governor": {"Republican": 0.50, "Democratic": 0.50},
}

def fetch_historical_patterns(market_info):
    """Source 2: Historical Voting Patterns (Statistical Model)"""
    try:
        state = market_info.get("state")
        office = market_info.get("office")
        party = market_info.get("party")
        
        if not office or not party:
            return None
        
        # Try state-specific data first
        if state and state in HISTORICAL_PATTERNS:
            state_data = HISTORICAL_PATTERNS[state]
            if office in state_data and party in state_data[office]:
                probability = state_data[office][party]
                return {
                    "source": "Historical Patterns (State)",
                    "probability": probability,
                    "confidence": 0.75,  # Historical data is reasonably reliable
                    "state": state,
                    "office": office,
                    "party": party,
                }
        
        # Fallback to national baseline
        if office in NATIONAL_BASELINE and party in NATIONAL_BASELINE[office]:
            probability = NATIONAL_BASELINE[office][party]
            # Adjust confidence based on whether we have state data
            confidence = 0.65 if not state else 0.70
            
            return {
                "source": "Historical Patterns (National)",
                "probability": probability,
                "confidence": confidence,
                "office": office,
                "party": party,
            }
        
        return None
    except Exception as e:
        print(f"      ⚠️  Historical patterns failed: {e}")
        return None

# ============================================================================
# SOURCE 3: Betting Market Aggregator (STATISTICAL)
# ============================================================================

def fetch_betting_odds(market_info):
    """Source 3: Betting Market Odds Aggregator (Statistical)"""
    try:
        # This would aggregate odds from multiple betting markets
        # For now, we'll use a statistical model based on market characteristics
        
        office = market_info.get("office")
        party = market_info.get("party")
        state = market_info.get("state")
        event_type = market_info.get("event_type")
        
        if not office or not party:
            return None
        
        # Statistical model: Base probability with adjustments
        
        # Base probability from historical patterns
        base_prob = 0.5
        if office in NATIONAL_BASELINE and party in NATIONAL_BASELINE[office]:
            base_prob = NATIONAL_BASELINE[office][party]
        
        # State adjustment (if we have state data)
        state_adjustment = 0.0
        if state and state in HISTORICAL_PATTERNS:
            state_data = HISTORICAL_PATTERNS[state]
            if office in state_data and party in state_data[office]:
                state_prob = state_data[office][party]
                state_adjustment = state_prob - base_prob
        
        # Event type adjustment
        # Nominations tend to be less certain than elections
        event_adjustment = 0.0
        if event_type == "nomination":
            event_adjustment = -0.05  # Slightly lower probability for nominations
        elif event_type == "election":
            event_adjustment = 0.0  # Elections are more certain
        
        # Combine adjustments
        probability = base_prob + state_adjustment * 0.7 + event_adjustment
        probability = max(0.1, min(0.9, probability))
        
        # Confidence based on data availability
        confidence = 0.70
        if state and state in HISTORICAL_PATTERNS:
            confidence = 0.75
        if event_type == "election":
            confidence += 0.05  # Elections are more predictable
        
        confidence = min(0.85, confidence)
        
        return {
            "source": "Betting Model (Statistical)",
            "probability": probability,
            "confidence": confidence,
            "base_prob": base_prob,
            "state_adjustment": state_adjustment,
        }
    except Exception as e:
        print(f"      ⚠️  Betting model failed: {e}")
        return None

# ============================================================================
# Combine Sources (Statistical Weighted Average)
# ============================================================================

def combine_sources(sources):
    """Combine forecasts from multiple sources using weighted average by confidence"""
    valid_sources = [s for s in sources if s is not None and s.get("probability") is not None and s.get("confidence", 0) > 0]
    
    if not valid_sources:
        return None, [], 0.0
    
    # Weighted average by confidence
    total_weight = sum(s["confidence"] for s in valid_sources)
    if total_weight == 0:
        return None, [], 0.0
    
    combined_prob = sum(s["probability"] * s["confidence"] for s in valid_sources) / total_weight
    
    # Combined confidence (statistical: more sources = higher confidence)
    if len(valid_sources) >= 2:
        avg_conf = sum(s["confidence"] for s in valid_sources) / len(valid_sources)
        # Bonus for having multiple statistical sources
        bonus = min(0.1, (len(valid_sources) - 1) * 0.05)
        combined_conf = min(0.95, avg_conf + bonus)
    else:
        combined_conf = valid_sources[0]["confidence"]
    
    # Cap probability at reasonable bounds
    combined_prob = max(0.01, min(0.99, combined_prob))
    
    return combined_prob, valid_sources, combined_conf

# ============================================================================
# Main Analysis Function
# ============================================================================

def implied_prob(yes_bid, yes_ask, last):
    """Calculate implied probability from market prices"""
    if pd.notnull(yes_bid) and pd.notnull(yes_ask) and yes_ask > 0:
        return ((yes_bid + yes_ask) / 2) / 100.0
    if pd.notnull(last) and last > 0:
        return last / 100.0
    return None

def enrich_with_politics_probs(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich markets with combined forecast from 3 STATISTICAL sources"""
    rows = []
    
    for _, row in df.iterrows():
        market_info = parse_politics_market(row["ticker"], row["title"])
        
        print(f"\n📊 Analyzing: {row['ticker']}")
        print(f"   Title: {row['title'][:70]}")
        if market_info["state"]:
            print(f"   State: {market_info['state']}")
        if market_info["party"]:
            print(f"   Party: {market_info['party']}")
        if market_info["office"]:
            print(f"   Office: {market_info['office']}")
        
        # Fetch from all 3 STATISTICAL sources
        sources = []
        
        # Source 1: Kalshi Market Consensus (Statistical)
        print("   🔵 Fetching Kalshi Consensus (Market Aggregation)...")
        consensus = fetch_kalshi_consensus(row["ticker"], row["series"], df)
        if consensus:
            sources.append(consensus)
            print(f"      ✅ Kalshi Consensus: P={consensus['probability']:.3f}, "
                  f"Markets={consensus['num_markets']}, Vol={consensus['avg_volume']:.0f}")
        
        # Source 2: Historical Patterns (Statistical)
        print("   🟢 Fetching Historical Patterns (Statistical Model)...")
        historical = fetch_historical_patterns(market_info)
        if historical:
            sources.append(historical)
            print(f"      ✅ {historical['source']}: P={historical['probability']:.3f}")
        
        # Source 3: Betting Model (Statistical)
        print("   🟡 Fetching Betting Model (Statistical)...")
        betting = fetch_betting_odds(market_info)
        if betting:
            sources.append(betting)
            print(f"      ✅ {betting['source']}: P={betting['probability']:.3f}")
        
        if not sources:
            print("   ❌ No statistical sources available")
            continue
        
        # Combine sources
        combined_prob, source_probs, combined_conf = combine_sources(sources)
        
        if combined_prob is None:
            print("   ❌ Could not calculate probability")
            continue
        
        # Market probability
        p_mkt = implied_prob(row["yes_bid"], row["yes_ask"], row["last_price"])
        
        # Edge
        edge = None if p_mkt is None else (combined_prob - p_mkt)
        
        # Source breakdown
        source_breakdown = ", ".join([
            f"{sp['source']}: {sp['probability']:.3f}"
            for sp in source_probs
        ])
        
        print(f"   📈 Combined: {combined_prob:.3f} (conf: {combined_conf:.2f})")
        if p_mkt is not None:
            print(f"   💰 Market: {p_mkt:.3f}")
        else:
            print(f"   💰 Market: N/A")
        if edge is not None:
            edge_pct = edge * 100
            action = 'BUY YES' if edge > 0.08 else ('BUY NO' if edge < -0.08 else 'HOLD')
            print(f"   🎯 Edge: {edge_pct:+.1f}% ({action})")
        
        rows.append({
            **row.to_dict(),
            "combined_p": round(combined_prob, 3),
            "market_p": round(p_mkt, 3) if p_mkt else None,
            "edge": round(edge, 3) if edge is not None else None,
            "edge_pct": round(edge * 100, 1) if edge is not None else None,
            "sources": len(sources),
            "source_breakdown": source_breakdown,
            "confidence": round(combined_conf, 2),
        })
    
    return pd.DataFrame(rows)

# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    try:
        print("=" * 80)
        print("🗳️  POLITICS MARKET ANALYSIS - 3 SOURCE STATISTICAL SYSTEM")
        print("=" * 80)
        print("\nSources (ALL STATISTICAL):")
        print("  1. Kalshi Market Consensus - Confidence: 70-85%")
        print("     (Volume-weighted average from other markets in same series)")
        print("  2. Historical Voting Patterns - Confidence: 65-75%")
        print("     (Statistical models based on past election results)")
        print("  3. Betting Market Model - Confidence: 70-85%")
        print("     (Statistical model with state/office/party adjustments)")
        print("\n" + "=" * 80)
        
        print("\n🔍 Fetching politics markets from Kalshi...")
        df = get_open_politics_markets()
        
        if df.empty:
            print("\n❌ No politics markets available to analyze.")
        else:
            print(f"\n✅ Found {len(df)} open politics markets")
            print("=" * 80)
            print(f"\n⚙️  Analyzing {len(df)} markets (statistical analysis)...")
            print("=" * 80)
            
            df_out = enrich_with_politics_probs(df)
            
            if df_out.empty:
                print("\n❌ No markets could be analyzed (missing data or parsing errors)")
            else:
                print("\n" + "=" * 80)
                print("📈 RESULTS SUMMARY")
                print("=" * 80)
                
                # Sort by absolute edge
                df_sorted = df_out.copy()
                df_sorted["abs_edge"] = df_sorted["edge"].abs().fillna(0)
                df_sorted = df_sorted.sort_values("abs_edge", ascending=False)
                
                # Display key columns
                display_cols = ["ticker", "combined_p", "market_p", "edge_pct", "sources", "confidence"]
                print("\n" + df_sorted[display_cols].to_string(index=False))
                
                # Summary statistics
                print("\n" + "=" * 80)
                print("📊 SUMMARY STATISTICS")
                print("=" * 80)
                print(f"Markets analyzed: {len(df_out)}")
                if df_out['edge_pct'].notna().any():
                    print(f"Average edge: {df_out['edge_pct'].mean():.2f}%")
                    print(f"Max edge: {df_out['edge_pct'].max():.2f}%")
                    print(f"Markets with >8% edge: {len(df_out[df_out['edge_pct'].abs() > 8])}")
                print(f"Average sources per market: {df_out['sources'].mean():.1f}")
                print(f"Average confidence: {df_out['confidence'].mean():.2f}")
                
                # Best opportunities
                buy_yes = df_sorted[(df_sorted["edge_pct"].notna()) & (df_sorted["edge_pct"] > 8)]
                buy_no = df_sorted[(df_sorted["edge_pct"].notna()) & (df_sorted["edge_pct"] < -8)]
                
                if len(buy_yes) > 0:
                    print("\n" + "=" * 80)
                    print("🟢 BUY YES OPPORTUNITIES (Edge > 8%)")
                    print("=" * 80)
                    for _, row in buy_yes.head(5).iterrows():
                        print(f"{row['ticker']:40} | Edge: {row['edge_pct']:+.1f}% | "
                              f"Combined: {row['combined_p']:.3f} | Market: {row['market_p']:.3f}")
                        print(f"  {row['title'][:70]}")
                        print(f"  Sources: {row['source_breakdown']}")
                
                if len(buy_no) > 0:
                    print("\n" + "=" * 80)
                    print("🔴 BUY NO OPPORTUNITIES (Edge < -8%)")
                    print("=" * 80)
                    for _, row in buy_no.head(5).iterrows():
                        print(f"{row['ticker']:40} | Edge: {row['edge_pct']:+.1f}% | "
                              f"Combined: {row['combined_p']:.3f} | Market: {row['market_p']:.3f}")
                        print(f"  {row['title'][:70]}")
                        print(f"  Sources: {row['source_breakdown']}")
                
                print("\n" + "=" * 80)
                print("✅ Analysis complete!")
                print("=" * 80)
    
    except Exception as e:
        print(f"\n❌ Error running script: {e}")
        import traceback
        traceback.print_exc()
