import requests, math, datetime as dt, pytz, pandas as pd, numpy as np

KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
UA     = {"User-Agent": "weather-agent/0.1 (mangalapallianshul@gmail.com)"}
TZ     = pytz.timezone("America/New_York")

# Optional: Visual Crossing API key (if available, otherwise uses fallback)
VC_API_KEY = None  # Set to your key if you have one: "YOUR_KEY_HERE"

# 1) Fetch some open WEATHER markets and build DataFrame
def get_open_weather_markets(sort_by_volume=True, limit=50):
    """
    Fetch all open weather markets from Kalshi in real-time.
    
    Args:
        sort_by_volume: If True, sort by 24h volume (highest first)
        limit: Maximum number of markets to return
    
    Returns:
        DataFrame with open weather markets sorted by volume
    """
    # Get series first
    r_series = requests.get(f"{KALSHI}/series", params={"limit":500}, timeout=15)
    r_series.raise_for_status()
    all_series = r_series.json().get("series", [])
    
    # Filter for actual weather series (not election series)
    # Include all KXHIGH/KXRAIN series that are in Climate and Weather category
    weather_series = [s for s in all_series 
                      if (s["ticker"].startswith(("KXHIGH", "KXRAIN"))
                          and not s["ticker"].startswith(("KXHIGHMOV"))  # exclude election series
                          and s.get("category", "") == "Climate and Weather")]
    
    all_markets = []
    for series in weather_series[:20]:  # Check more series to get volume data
        r = requests.get(f"{KALSHI}/markets", 
                        params={"series_ticker": series["ticker"], "status":"open", "limit":100}, 
                        timeout=15)
        if r.status_code == 200:
            ms = r.json().get("markets", [])
            # Filter for only ACTIVE markets (open for trading in real-time)
            active_markets = [m for m in ms if m.get("status") == "active"]
            all_markets.extend(active_markets)
    
    if not all_markets:
        print("⚠️  No active weather markets found. Weather markets may be closed for the season.")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_markets)
    
    # Sort by volume (24h volume is best for real-time activity)
    if sort_by_volume:
        if "volume_24h" in df.columns:
            df = df.sort_values("volume_24h", ascending=False)
            print(f"📊 Sorted by 24h volume (highest volume first)")
        elif "volume" in df.columns:
            df = df.sort_values("volume", ascending=False)
            print(f"📊 Sorted by total volume (highest volume first)")
    
    # Limit results
    df = df.head(limit)
    
    # Select columns (include volume for visibility)
    cols_to_keep = ["ticker","title","yes_bid","yes_ask","last_price"]
    if "volume_24h" in df.columns:
        cols_to_keep.append("volume_24h")
    if "volume" in df.columns:
        cols_to_keep.append("volume")
    if "open_interest" in df.columns:
        cols_to_keep.append("open_interest")
    
    df = df[[c for c in cols_to_keep if c in df.columns]]
    df["series"] = df["ticker"].str.split("-").str[0]
    
    print(f"✅ Found {len(df)} active weather markets (status=active, open for trading)")
    
    return df

# 2) Map series → lat/lon + kind
SERIES_MAP = {
    "KXHIGHNY":    {"lat":40.7128, "lon":-74.0060, "kind":"HIGH"},
    "KXRAINNY":    {"lat":40.7128, "lon":-74.0060, "kind":"RAIN"},
    "KXHIGHCHI":   {"lat":41.8781, "lon":-87.6298, "kind":"HIGH"},
    "KXRAINCHI":   {"lat":41.8781, "lon":-87.6298, "kind":"RAIN"},
    "KXHIGHLAX":   {"lat":34.0522, "lon":-118.2437, "kind":"HIGH"},
    "KXHIGHDEN":   {"lat":39.7392, "lon":-104.9903, "kind":"HIGH"},
    "KXHIGHMIA":   {"lat":25.7617, "lon":-80.1918, "kind":"HIGH"},
    "KXHIGHHOU":   {"lat":29.7604, "lon":-95.3698, "kind":"HIGH"},
    "KXHIGHOU":    {"lat":29.7604, "lon":-95.3698, "kind":"HIGH"},
    "KXRAINHOU":   {"lat":29.7604, "lon":-95.3698, "kind":"RAIN"},
    "KXHIGHPHIL":  {"lat":39.9526, "lon":-75.1652, "kind":"HIGH"},
    "KXRAINSEA":   {"lat":47.6062, "lon":-122.3321, "kind":"RAIN"},
}

# ============================================================================
# SOURCE 1: NOAA (National Weather Service) - GFS Model
# ============================================================================

def nws_points(lat, lon):
    r = requests.get(f"https://api.weather.gov/points/{lat},{lon}", headers=UA, timeout=15)
    r.raise_for_status()
    j = r.json()
    return j["properties"]["forecastHourly"]

def hourly_periods(hourly_url):
    r = requests.get(hourly_url, headers=UA, timeout=15)
    r.raise_for_status()
    return r.json()["properties"]["periods"]

def slice_local_day(periods, day):
    out=[]
    for p in periods:
        t = dt.datetime.fromisoformat(p["startTime"].replace("Z","+00:00")).astimezone(TZ)
        if t.date()==day:
            out.append(p)
    return out

def summarize_day(periods):
    if not periods:
        return {"tmax": None, "pop": None}
    tmax = max(p["temperature"] for p in periods if p.get("temperature") is not None)
    pops = [ (p.get("probabilityOfPrecipitation",{}).get("value") or 0)/100.0 for p in periods ]
    pop_day = 1 - math.prod((1-x) for x in pops) if pops else None
    return {"tmax": tmax, "pop": pop_day}

def fetch_noaa_forecast(lat, lon, target_date):
    """Source 1: NOAA GFS Model Forecast"""
    try:
        h_url = nws_points(lat, lon)
        periods = hourly_periods(h_url)
        day_periods = slice_local_day(periods, target_date)
        fx = summarize_day(day_periods)
        return {
            "source": "NOAA",
            "tmax": fx["tmax"],
            "pop": fx["pop"],
            "confidence": 0.85,  # NOAA is very reliable
        }
    except Exception as e:
        print(f"  ⚠️  NOAA fetch failed: {e}")
        return {"source": "NOAA", "tmax": None, "pop": None, "confidence": 0.0}

# ============================================================================
# SOURCE 2: Open-Meteo - ECMWF Model
# ============================================================================

def fetch_openmeteo_forecast(lat, lon, target_date):
    """Source 2: Open-Meteo ECMWF Model Forecast"""
    try:
        date_str = target_date.strftime("%Y-%m-%d")
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
            f"&start_date={date_str}&end_date={date_str}"
            f"&temperature_unit=fahrenheit&timezone=America/New_York"
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        
        daily = data.get("daily", {})
        if not daily or not daily.get("temperature_2m_max"):
            return {"source": "Open-Meteo", "tmax": None, "pop": None, "confidence": 0.0}
        
        tmax = daily["temperature_2m_max"][0] if daily["temperature_2m_max"] else None
        pop = daily["precipitation_probability_max"][0] / 100.0 if daily.get("precipitation_probability_max") else None
        
        return {
            "source": "Open-Meteo",
            "tmax": tmax,
            "pop": pop,
            "confidence": 0.80,  # ECMWF is also very reliable
        }
    except Exception as e:
        print(f"  ⚠️  Open-Meteo fetch failed: {e}")
        return {"source": "Open-Meteo", "tmax": None, "pop": None, "confidence": 0.0}

# ============================================================================
# SOURCE 3: Climatology (Historical Averages)
# ============================================================================

# Historical average temperatures by city and month (simplified climatology)
CLIMATOLOGY_AVG = {
    "NY": {"avg_high": [38, 40, 48, 59, 70, 79, 84, 83, 75, 64, 54, 43]},  # NYC monthly avg highs
    "CHI": {"avg_high": [32, 36, 47, 59, 70, 80, 84, 82, 74, 62, 49, 36]},  # Chicago
    "LAX": {"avg_high": [68, 69, 70, 72, 73, 76, 79, 80, 79, 77, 73, 69]},  # LA
    "PHIL": {"avg_high": [40, 43, 52, 63, 73, 82, 86, 85, 78, 66, 56, 45]},  # Philadelphia
    "DEN": {"avg_high": [45, 47, 54, 61, 71, 82, 88, 86, 78, 66, 53, 45]},  # Denver
    "MIA": {"avg_high": [76, 77, 79, 81, 84, 87, 88, 89, 88, 85, 81, 78]},  # Miami
    "HOU": {"avg_high": [63, 67, 74, 80, 87, 92, 94, 95, 90, 82, 72, 65]},  # Houston
    "SEA": {"avg_high": [47, 51, 55, 59, 65, 70, 75, 76, 71, 61, 53, 47]},  # Seattle
}

def get_climatology_key(series_ticker):
    """Extract city code from series ticker"""
    if "NY" in series_ticker: return "NY"
    if "CHI" in series_ticker: return "CHI"
    if "LAX" in series_ticker: return "LAX"
    if "PHIL" in series_ticker: return "PHIL"
    if "DEN" in series_ticker: return "DEN"
    if "MIA" in series_ticker: return "MIA"
    if "HOU" in series_ticker or "OU" in series_ticker: return "HOU"
    if "SEA" in series_ticker: return "SEA"
    return None

def fetch_climatology_forecast(series_ticker, target_date):
    """Source 3: Historical Climatology (Baseline)"""
    try:
        city_key = get_climatology_key(series_ticker)
        if not city_key or city_key not in CLIMATOLOGY_AVG:
            return {"source": "Climatology", "tmax": None, "pop": None, "confidence": 0.0}
        
        month_idx = target_date.month - 1  # 0-indexed
        avg_high = CLIMATOLOGY_AVG[city_key]["avg_high"][month_idx]
        
        # Climatology gives us average, but for probability we need distribution
        # Assume ±5°F standard deviation for climatology
        return {
            "source": "Climatology",
            "tmax": avg_high,  # This is the average, we'll use it as mean
            "pop": 0.3,  # Generic precipitation probability (can be improved)
            "confidence": 0.70,  # Lower confidence than forecasts
            "std": 5.0,  # Standard deviation for climatology
        }
    except Exception as e:
        print(f"  ⚠️  Climatology fetch failed: {e}")
        return {"source": "Climatology", "tmax": None, "pop": None, "confidence": 0.0}

# 4) Parse a market to know threshold/date
def parse_weather_market(ticker: str):
    # e.g., KXHIGHNY-25NOV08-T69, KXHIGHNY-25NOV08-B64.5, KXRAINNY-25NOV08
    parts = ticker.split("-")
    series = parts[0]
    day = dt.datetime.strptime(parts[1], "%y%b%d").date()  # assumes English locale
    kind = "RAIN" if series.startswith("KXRAIN") else "HIGH"
    sub  = parts[2] if len(parts)>2 else ""
    if kind=="HIGH":
        if sub.startswith("T"):
            T = float(sub[1:].replace("F",""))
            return {"day":day, "type":"GT", "T":T}
        if sub.startswith("B"):
            c = float(sub[1:])
            return {"day":day, "type":"BAND", "L":math.floor(c), "U":math.floor(c)+1}
    return {"day":day, "type":"RAIN"}

# 5) Convert forecast to probabilities
def p_high_gt(mu, T, lead_days, sigma=None):
    """Probability that high temp > T, given forecast mean mu and uncertainty sigma"""
    if mu is None: return None
    if sigma is None:
        sigma = 3.0 if lead_days<=1 else (4.0 if lead_days==2 else 5.0)
    z = (T - mu)/sigma
    return 0.5*(1 - math.erf(z/math.sqrt(2)))  # 1 - Phi(z)

def p_high_band(mu, L, U, lead_days, sigma=None):
    """Probability that high temp is in [L, U], given forecast mean mu"""
    if mu is None: return None
    if sigma is None:
        sigma = 3.0 if lead_days<=1 else (4.0 if lead_days==2 else 5.0)
    Phi = lambda x: 0.5*(1+math.erf(x/math.sqrt(2)))
    return max(0.0, min(1.0, Phi((U-mu)/sigma) - Phi((L-mu)/sigma)))

# 6) Combine multiple sources with weighted average
def combine_sources(sources, market_type, threshold, lead_days):
    """
    Combine forecasts from multiple sources using weighted average by confidence.
    
    Args:
        sources: List of dicts with keys: source, tmax, pop, confidence
        market_type: "GT", "BAND", or "RAIN"
        threshold: Temperature threshold (T) or dict with L, U for bands
        lead_days: Days until target date
    
    Returns:
        Combined probability, individual source probabilities, combined confidence
    """
    valid_sources = [s for s in sources if s.get("confidence", 0) > 0]
    
    if not valid_sources:
        return None, [], 0.0
    
    # Calculate probability for each source
    source_probs = []
    total_weight = 0.0
    
    for src in valid_sources:
        tmax = src.get("tmax")
        pop = src.get("pop")
        conf = src.get("confidence", 0.0)
        
        if market_type == "GT":
            prob = p_high_gt(tmax, threshold, lead_days, src.get("std"))
        elif market_type == "BAND":
            prob = p_high_band(tmax, threshold["L"], threshold["U"], lead_days, src.get("std"))
        else:  # RAIN
            # For rain, use precipitation probability directly
            prob = pop if pop is not None else None
            # If no pop but we have climatology, use a baseline
            if prob is None and src["source"] == "Climatology":
                prob = 0.3  # Generic baseline for rain
        
        if prob is not None:
            source_probs.append({
                "source": src["source"],
                "probability": prob,
                "confidence": conf,
                "tmax": tmax,
            })
            total_weight += conf
    
    if not source_probs:
        return None, [], 0.0
    
    # Weighted average probability
    combined_prob = sum(p["probability"] * p["confidence"] for p in source_probs) / total_weight
    
    # Combined confidence (harmonic mean, weighted by number of sources)
    if len(source_probs) >= 2:
        # More sources = higher confidence (up to a point)
        source_conf_avg = sum(p["confidence"] for p in source_probs) / len(source_probs)
        num_sources_bonus = min(0.1, (len(source_probs) - 1) * 0.05)
        combined_conf = min(0.95, source_conf_avg + num_sources_bonus)
    else:
        combined_conf = source_probs[0]["confidence"]
    
    # Cap probability at reasonable bounds
    combined_prob = max(0.01, min(0.99, combined_prob))
    
    return combined_prob, source_probs, combined_conf

def implied_prob(yes_bid, yes_ask, last):
    if pd.notnull(yes_bid) and pd.notnull(yes_ask) and yes_ask>0:
        return ((yes_bid + yes_ask)/2)/100.0
    if pd.notnull(last):
        return last/100.0
    return None

# 7) Main: enrich the DataFrame with forecast probs and edge (using 3 sources)
def enrich_with_weather_probs(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich markets with combined forecast from 3 sources"""
    today = dt.datetime.now(TZ).date()
    
    rows = []
    for _, row in df.iterrows():
        s = row["series"]
        cfg = SERIES_MAP.get(s)
        if not cfg:
            continue
        
        parsed = parse_weather_market(row["ticker"])
        lead_days = abs((parsed["day"] - today).days)
        
        print(f"\n📊 Analyzing: {row['ticker']}")
        print(f"   Target date: {parsed['day']} (lead: {lead_days} days)")
        
        # Fetch from all 3 sources
        sources = []
        
        # Source 1: NOAA
        print("   🔵 Fetching NOAA (GFS)...")
        noaa = fetch_noaa_forecast(cfg["lat"], cfg["lon"], parsed["day"])
        if noaa.get("tmax") is not None or noaa.get("pop") is not None:
            sources.append(noaa)
            print(f"      ✅ NOAA: tmax={noaa.get('tmax')}, pop={noaa.get('pop')}")
        
        # Source 2: Open-Meteo
        print("   🟢 Fetching Open-Meteo (ECMWF)...")
        openmeteo = fetch_openmeteo_forecast(cfg["lat"], cfg["lon"], parsed["day"])
        if openmeteo.get("tmax") is not None or openmeteo.get("pop") is not None:
            sources.append(openmeteo)
            print(f"      ✅ Open-Meteo: tmax={openmeteo.get('tmax')}, pop={openmeteo.get('pop')}")
        
        # Source 3: Climatology
        print("   🟡 Fetching Climatology...")
        clim = fetch_climatology_forecast(s, parsed["day"])
        if clim.get("tmax") is not None:
            sources.append(clim)
            print(f"      ✅ Climatology: tmax={clim.get('tmax')} (avg)")
        
        if not sources:
            print("   ❌ No sources available")
            continue
        
        # Determine threshold based on market type
        if parsed["type"] == "GT":
            threshold = parsed["T"]
        elif parsed["type"] == "BAND":
            threshold = {"L": parsed["L"], "U": parsed["U"]}
        else:  # RAIN
            threshold = None
        
        # Combine sources
        combined_prob, source_probs, combined_conf = combine_sources(
            sources, parsed["type"], threshold, lead_days
        )
        
        if combined_prob is None:
            print("   ❌ Could not calculate probability")
            continue
        
        # Market probability
        p_mkt = implied_prob(row["yes_bid"], row["yes_ask"], row["last_price"])
        
        # Edge = combined forecast - market price
        edge = None if p_mkt is None else (combined_prob - p_mkt)
        
        # Format source breakdown
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

# ---- Run once ----
if __name__ == "__main__":
    try:
        print("=" * 80)
        print("🌤️  WEATHER MARKET ANALYSIS - 3 SOURCE QUANTITATIVE SYSTEM")
        print("=" * 80)
        print("\nSources:")
        print("  1. NOAA (GFS Model) - Confidence: 85%")
        print("  2. Open-Meteo (ECMWF Model) - Confidence: 80%")
        print("  3. Climatology (Historical Averages) - Confidence: 70%")
        print("\n" + "=" * 80)
        
        print("\n🔍 Fetching weather markets from Kalshi...")
        df = get_open_weather_markets()
        
        if df.empty:
            print("\n❌ No weather markets available to analyze.")
            print("Weather markets are typically only active during certain seasons or specific dates.")
            print("\n💡 Tip: Weather markets are often seasonal. Try again during active weather periods.")
        else:
            print(f"\n✅ Found {len(df)} open weather markets")
            print("=" * 80)
            print(f"\n⚙️  Analyzing {len(df)} markets (this may take a minute)...")
            print("=" * 80)
            
            df_out = enrich_with_weather_probs(df)
            
            if df_out.empty:
                print("\n❌ No markets could be analyzed (missing data or parsing errors)")
            else:
                print("\n" + "=" * 80)
                print("📈 RESULTS SUMMARY")
                print("=" * 80)
                
                # Sort by absolute edge (best opportunities first)
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
                
                # Best opportunities (filter out NaN)
                buy_yes = df_sorted[(df_sorted["edge_pct"].notna()) & (df_sorted["edge_pct"] > 8)]
                buy_no = df_sorted[(df_sorted["edge_pct"].notna()) & (df_sorted["edge_pct"] < -8)]
                
                if len(buy_yes) > 0:
                    print("\n" + "=" * 80)
                    print("🟢 BUY YES OPPORTUNITIES (Edge > 8%)")
                    print("=" * 80)
                    for _, row in buy_yes.head(5).iterrows():
                        print(f"{row['ticker']:30} | Edge: {row['edge_pct']:+.1f}% | "
                              f"Combined: {row['combined_p']:.3f} | Market: {row['market_p']:.3f}")
                        print(f"  Sources: {row['source_breakdown']}")
                
                if len(buy_no) > 0:
                    print("\n" + "=" * 80)
                    print("🔴 BUY NO OPPORTUNITIES (Edge < -8%)")
                    print("=" * 80)
                    for _, row in buy_no.head(5).iterrows():
                        print(f"{row['ticker']:30} | Edge: {row['edge_pct']:+.1f}% | "
                              f"Combined: {row['combined_p']:.3f} | Market: {row['market_p']:.3f}")
                        print(f"  Sources: {row['source_breakdown']}")
                
                print("\n" + "=" * 80)
                print("✅ Analysis complete!")
                print("=" * 80)
    
    except Exception as e:
        print(f"\n❌ Error running script: {e}")
        import traceback
        traceback.print_exc()
