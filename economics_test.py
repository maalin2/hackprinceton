import requests, math, datetime as dt, pandas as pd, numpy as np, re

KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
UA = {"User-Agent": "economics-agent/0.1 (mangalapallianshul@gmail.com)"}

# API Keys (optional - for enhanced data)
FRED_API_KEY = "b3f3d3d25657f07bfd0b6e0bfc2af9d3"  # Get from https://fred.stlouisfed.org/docs/api/api_key.html (free)
ALPHA_VANTAGE_KEY = "DHYN79SWRDII5BC4"  # Get from https://www.alphavantage.co/support/#api-key (free)
BLS_API_KEY = None  # Get from https://www.bls.gov/developers/api_signature.htm (free, but requires registration)
WORLD_BANK_KEY = None  # World Bank API is free, no key needed (but can register for higher limits)

# 1) Fetch open ECONOMICS markets from Kalshi
def get_open_economics_markets(sort_by_volume=True, limit=50):
    """
    Fetch open economics markets from Kalshi in real-time.
    
    Args:
        sort_by_volume: If True, sort by 24h volume (highest first)
        limit: Maximum number of markets to return
    
    Returns:
        DataFrame with open economics markets sorted by volume
    """
    r_series = requests.get(f"{KALSHI}/series", params={"limit":500}, timeout=15)
    r_series.raise_for_status()
    all_series = r_series.json().get("series", [])
    
    # Filter for Economics category (might be "Economics" or "Economic Indicators")
    economics_series = [s for s in all_series 
                       if "economic" in s.get("category", "").lower() or 
                          "economics" in s.get("category", "").lower() or
                          "gdp" in s.get("ticker", "").lower() or
                          "inflation" in s.get("ticker", "").lower() or
                          "unemployment" in s.get("ticker", "").lower()]
    
    all_markets = []
    for series in economics_series[:30]:  # Check more series for volume data
        r = requests.get(f"{KALSHI}/markets", 
                        params={"series_ticker": series["ticker"], "status":"open", "limit":100}, 
                        timeout=15)
        if r.status_code == 200:
            ms = r.json().get("markets", [])
            # Filter for only ACTIVE markets (open for trading in real-time)
            active_markets = [m for m in ms if m.get("status") == "active"]
            all_markets.extend(active_markets)
    
    if not all_markets:
        print("⚠️  No active economics markets found.")
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
    
    # Get available columns (include volume for visibility)
    available_cols = ["ticker","title","yes_bid","yes_ask","last_price"]
    if "volume_24h" in df.columns:
        available_cols.append("volume_24h")
    if "volume" in df.columns:
        available_cols.append("volume")
    if "open_interest" in df.columns:
        available_cols.append("open_interest")
    if "series_ticker" in df.columns:
        available_cols.append("series_ticker")
    
    df = df[[c for c in available_cols if c in df.columns]]
    df["series"] = df["ticker"].str.split("-").str[0]
    
    print(f"✅ Found {len(df)} active economics markets (status=active, open for trading)")
    
    return df

# 2) Parse economics market to extract indicators and thresholds
def parse_economics_market(ticker: str, title: str):
    """Extract economic indicator, threshold, and date from economics market"""
    title_lower = title.lower()
    
    # Extract economic indicator type
    indicators = {
        "gdp": ["gdp", "gross domestic product", "economic growth"],
        "inflation": ["inflation", "cpi", "consumer price index", "price index"],
        "unemployment": ["unemployment", "jobless", "employment rate"],
        "interest_rate": ["interest rate", "fed rate", "federal reserve", "fomc"],
        "stock_market": ["s&p", "sp500", "dow", "nasdaq", "stock market"],
        "housing": ["housing", "home prices", "case-shiller"],
        "retail_sales": ["retail sales", "consumer spending"],
    }
    
    indicator_type = "general"
    for key, keywords in indicators.items():
        if any(kw in title_lower for kw in keywords):
            indicator_type = key
            break
    
    # Extract threshold value
    threshold = None
    # Look for patterns like ">3%", "above $500", "<5.5%"
    threshold_patterns = [
        r">\s*(\d+\.?\d*)%?",  # >3%, > 3
        r"above\s+(\d+\.?\d*)%?",  # above 3%
        r"<\s*(\d+\.?\d*)%?",  # <3%, < 3
        r"below\s+(\d+\.?\d*)%?",  # below 3%
        r"(\d+\.?\d*)%?\s*or\s*(more|higher|above)",  # 3% or more
        r"(\d+\.?\d*)%?\s*or\s*(less|lower|below)",  # 3% or less
    ]
    
    for pattern in threshold_patterns:
        match = re.search(pattern, title_lower)
        if match:
            threshold = float(match.group(1))
            break
    
    # Extract date
    target_date = None
    # Look for dates like "2025 Q1", "Q1 2025", "January 2025"
    date_patterns = [
        r"(\d{4})\s*q(\d)",  # 2025 Q1
        r"q(\d)\s*(\d{4})",  # Q1 2025
        r"(\w+)\s+(\d{4})",  # January 2025
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, title_lower)
        if match:
            # Parse date (simplified - could be more sophisticated)
            try:
                if "q" in pattern.lower():
                    year = int(match.group(1) if match.group(1).isdigit() else match.group(2))
                    quarter = int(match.group(2) if match.group(2).isdigit() else match.group(1))
                    target_date = dt.date(year, quarter * 3, 1)
                else:
                    # Try to parse month name
                    month_names = ["january", "february", "march", "april", "may", "june",
                                 "july", "august", "september", "october", "november", "december"]
                    month_str = match.group(1).lower()
                    if month_str in month_names:
                        month = month_names.index(month_str) + 1
                        year = int(match.group(2))
                        target_date = dt.date(year, month, 1)
            except:
                pass
    
    # Determine comparison type
    comparison = "GT"  # Greater than
    if "<" in title or "below" in title_lower or "less than" in title_lower:
        comparison = "LT"
    elif ">" in title or "above" in title_lower or "more than" in title_lower:
        comparison = "GT"
    else:
        comparison = "GT"  # Default
    
    return {
        "ticker": ticker,
        "title": title,
        "indicator_type": indicator_type,
        "threshold": threshold,
        "target_date": target_date,
        "comparison": comparison,
    }

# ============================================================================
# SOURCE 1: FRED (Federal Reserve Economic Data) - STATISTICAL
# ============================================================================

# FRED Series IDs for common economic indicators
FRED_SERIES = {
    "gdp": "GDP",  # Real GDP
    "inflation": "CPIAUCSL",  # CPI for All Urban Consumers
    "unemployment": "UNRATE",  # Unemployment Rate
    "interest_rate": "FEDFUNDS",  # Federal Funds Rate
    "stock_market": "SP500",  # S&P 500 (though this might not be in FRED)
    "housing": "CSUSHPISA",  # Case-Shiller Home Price Index
    "retail_sales": "RSAFS",  # Retail and Food Services Sales
}

def fetch_fred_data(indicator_type, target_date=None):
    """Source 1: FRED Economic Data (Statistical)"""
    if not FRED_API_KEY:
        print("      ⚠️  FRED API key not set (skipping)")
        return None
    
    try:
        series_id = FRED_SERIES.get(indicator_type)
        if not series_id:
            return None
        
        # Build FRED API URL
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "limit": 100,
            "sort_order": "desc",  # Most recent first
        }
        
        # If target date specified, get data up to that date
        if target_date:
            params["observation_end"] = target_date.strftime("%Y-%m-%d")
        
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        
        observations = data.get("observations", [])
        if not observations:
            return None
        
        # Get most recent value
        recent = observations[0]
        value = recent.get("value")
        
        if value == "." or not value:  # FRED uses "." for missing data
            return None
        
        value = float(value)
        
        # Calculate forecast (simple: use recent trend)
        trend = 0.0
        forecast = value
        
        if len(observations) >= 3:
            recent_values = [float(o.get("value", 0)) for o in observations[:3] if o.get("value") != "." and o.get("value")]
            if len(recent_values) >= 2:
                trend = (recent_values[0] - recent_values[-1]) / max(1, len(recent_values) - 1)
                forecast = recent_values[0] + trend * 1  # Project 1 period ahead
            elif len(recent_values) >= 1:
                forecast = recent_values[0]
        
        return {
            "source": "FRED",
            "current_value": value,
            "forecast": forecast,
            "trend": trend,
            "confidence": 0.85,  # FRED data is very reliable
            "series_id": series_id,
        }
    except Exception as e:
        print(f"      ⚠️  FRED fetch failed: {e}")
        return None

# ============================================================================
# SOURCE 2: Stock Market Data (Yahoo Finance) - STATISTICAL
# ============================================================================

def fetch_stock_market_data():
    """Source 2a: S&P 500 Data from Yahoo Finance (Statistical)"""
    try:
        # Yahoo Finance API (free, no key needed)
        # Get S&P 500 current value
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
        params = {
            "interval": "1d",
            "range": "1mo",
        }
        
        r = requests.get(url, params=params, timeout=15)
        if r.ok:
            data = r.json()
            result = data.get("chart", {}).get("result", [])
            if result:
                quote = result[0].get("indicators", {}).get("quote", [])
                if quote:
                    closes = quote[0].get("close", [])
                    if closes:
                        current_value = closes[-1]
                        # Calculate trend (simple moving average)
                        if len(closes) >= 5:
                            recent_avg = np.mean(closes[-5:])
                            older_avg = np.mean(closes[-10:-5]) if len(closes) >= 10 else recent_avg
                            trend = (recent_avg - older_avg) / older_avg * 100  # % change
                            forecast = current_value * (1 + trend / 100)
                        else:
                            trend = 0
                            forecast = current_value
                        
                        return {
                            "source": "Yahoo Finance (S&P 500)",
                            "current_value": current_value,
                            "forecast": forecast,
                            "trend": trend,
                            "confidence": 0.80,  # Market data is reliable
                        }
    except Exception as e:
        print(f"      ⚠️  Stock market data fetch failed: {e}")
    
    return None

# ============================================================================
# SOURCE 2a: Alpha Vantage Economic Indicators - STATISTICAL
# ============================================================================

def fetch_alphavantage_economic(indicator_type):
    """Source 2a: Alpha Vantage Economic Indicators (Statistical)"""
    if not ALPHA_VANTAGE_KEY:
        return None
    
    try:
        # Alpha Vantage economic indicator functions
        alpha_functions = {
            "gdp": "REAL_GDP",
            "inflation": "CPI",  # Consumer Price Index
            "unemployment": "UNEMPLOYMENT",
            "interest_rate": "FEDERAL_FUNDS_RATE",
        }
        
        function = alpha_functions.get(indicator_type)
        if not function:
            return None
        
        url = "https://www.alphavantage.co/query"
        params = {
            "function": function,
            "interval": "annual" if indicator_type == "gdp" else "monthly",
            "apikey": ALPHA_VANTAGE_KEY,
        }
        
        r = requests.get(url, params=params, timeout=15)
        if not r.ok:
            return None
        
        data = r.json()
        
        # Parse Alpha Vantage response
        # Response format varies by function
        if "data" in data:
            # Most functions return data array
            data_points = data["data"]
            if not data_points:
                return None
            
            # Get most recent value
            recent = data_points[0]
            value = float(recent.get("value", 0))
            
            # Calculate trend if we have multiple data points
            trend = 0.0
            forecast = value
            if len(data_points) >= 3:
                recent_values = [float(d.get("value", 0)) for d in data_points[:3] if d.get("value")]
                if len(recent_values) >= 2:
                    trend = (recent_values[0] - recent_values[-1]) / max(1, len(recent_values) - 1)
                    forecast = recent_values[0] + trend * 1
            
            return {
                "source": "Alpha Vantage",
                "current_value": value,
                "forecast": forecast,
                "trend": trend,
                "confidence": 0.75,  # Alpha Vantage is reliable
            }
        
    except Exception as e:
        print(f"      ⚠️  Alpha Vantage fetch failed: {e}")
        return None
    
    return None

# ============================================================================
# SOURCE 2b: BLS (Bureau of Labor Statistics) - STATISTICAL
# ============================================================================

def fetch_bls_data(indicator_type):
    """Source 2b: BLS Economic Data (Statistical)"""
    if not BLS_API_KEY:
        return None
    
    try:
        # BLS Series IDs
        bls_series = {
            "inflation": "CUUR0000SA0",  # CPI for All Urban Consumers
            "unemployment": "LNS14000000",  # Unemployment Rate
        }
        
        series_id = bls_series.get(indicator_type)
        if not series_id:
            return None
        
        # BLS API v2 (requires registration but free)
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "seriesid": [series_id],
            "startyear": "2020",
            "endyear": str(dt.date.today().year),
            "registrationkey": BLS_API_KEY,
        }
        
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        if not r.ok:
            return None
        
        data = r.json()
        
        # Parse BLS response
        if data.get("status") == "REQUEST_SUCCEEDED":
            results = data.get("Results", {}).get("series", [])
            if results:
                series_data = results[0].get("data", [])
                if series_data:
                    # Get most recent value
                    recent = series_data[0]
                    value = float(recent.get("value", 0))
                    
                    # Calculate trend
                    trend = 0.0
                    forecast = value
                    if len(series_data) >= 3:
                        recent_values = [float(d.get("value", 0)) for d in series_data[:3] if d.get("value")]
                        if len(recent_values) >= 2:
                            trend = (recent_values[0] - recent_values[-1]) / max(1, len(recent_values) - 1)
                            forecast = recent_values[0] + trend * 1
                    
                    return {
                        "source": "BLS",
                        "current_value": value,
                        "forecast": forecast,
                        "trend": trend,
                        "confidence": 0.85,  # BLS is official government data
                    }
        
    except Exception as e:
        print(f"      ⚠️  BLS fetch failed: {e}")
        return None
    
    return None

# ============================================================================
# SOURCE 2c: World Bank API - STATISTICAL
# ============================================================================

def fetch_worldbank_data(indicator_type):
    """Source 2c: World Bank Economic Data (Statistical)"""
    try:
        # World Bank indicator codes
        wb_indicators = {
            "gdp": "NY.GDP.MKTP.KD.ZG",  # GDP growth (annual %)
            "inflation": "FP.CPI.TOTL.ZG",  # Inflation, consumer prices (annual %)
            "unemployment": "SL.UEM.TOTL.ZS",  # Unemployment, total (% of total labor force)
        }
        
        indicator_code = wb_indicators.get(indicator_type)
        if not indicator_code:
            return None
        
        # World Bank API (free, no key needed)
        url = "https://api.worldbank.org/v2/country/USA/indicator/" + indicator_code
        params = {
            "format": "json",
            "date": "2020:2025",  # Last 5 years
            "per_page": 10,
        }
        
        r = requests.get(url, params=params, timeout=15)
        if not r.ok:
            return None
        
        data = r.json()
        
        # Parse World Bank response
        if len(data) >= 2 and data[1]:
            # Get most recent value
            recent = data[1][0]
            value = recent.get("value")
            
            if value is None:
                return None
            
            value = float(value)
            
            # Calculate trend
            trend = 0.0
            forecast = value
            if len(data[1]) >= 3:
                recent_values = [float(d.get("value", 0)) for d in data[1][:3] if d.get("value") is not None]
                if len(recent_values) >= 2:
                    trend = (recent_values[0] - recent_values[-1]) / max(1, len(recent_values) - 1)
                    forecast = recent_values[0] + trend * 1
            
            return {
                "source": "World Bank",
                "current_value": value,
                "forecast": forecast,
                "trend": trend,
                "confidence": 0.80,  # World Bank is reliable
            }
        
    except Exception as e:
        print(f"      ⚠️  World Bank fetch failed: {e}")
        return None
    
    return None

# ============================================================================
# SOURCE 2: Economic Indicators from Public Sources - STATISTICAL
# ============================================================================

def fetch_economic_indicators(indicator_type, target_date=None):
    """Source 2: Economic Indicators from Public Sources (Statistical)
    
    Tries multiple free APIs in order of preference:
    1. Alpha Vantage (if key available)
    2. BLS (if key available)
    3. World Bank (no key needed)
    4. Yahoo Finance (for stock market)
    5. Statistical baselines (fallback)
    """
    try:
        # For stock market, use Yahoo Finance
        if indicator_type == "stock_market":
            return fetch_stock_market_data()
        
        # Try Alpha Vantage first (if key available)
        if ALPHA_VANTAGE_KEY:
            alpha_data = fetch_alphavantage_economic(indicator_type)
            if alpha_data:
                return alpha_data
        
        # Try BLS (if key available, best for CPI/unemployment)
        if BLS_API_KEY and indicator_type in ["inflation", "unemployment"]:
            bls_data = fetch_bls_data(indicator_type)
            if bls_data:
                return bls_data
        
        # Try World Bank (no key needed, good for GDP/inflation/unemployment)
        if indicator_type in ["gdp", "inflation", "unemployment"]:
            wb_data = fetch_worldbank_data(indicator_type)
            if wb_data:
                return wb_data
        
        # Fallback to statistical baselines
        baseline_values = {
            "gdp": 2.5,  # Annual GDP growth % (US average 2020-2024)
            "inflation": 3.2,  # Annual inflation % (recent CPI)
            "unemployment": 3.8,  # Unemployment rate % (recent average)
            "interest_rate": 5.25,  # Federal funds rate % (recent)
            "housing": 310,  # Case-Shiller index (recent)
            "retail_sales": 710,  # Retail sales billions (recent)
        }
        
        baseline = baseline_values.get(indicator_type)
        if baseline is None:
            return None
        
        # Historical volatility
        historical_volatility = {
            "gdp": 1.5,
            "inflation": 1.0,
            "unemployment": 1.0,
            "interest_rate": 0.5,
            "housing": 20,
            "retail_sales": 30,
        }
        
        vol = historical_volatility.get(indicator_type, baseline * 0.1)
        
        return {
            "source": "Statistical Baseline (Fallback)",
            "current_value": baseline,
            "forecast": baseline,
            "volatility": vol,
            "confidence": 0.60,  # Lower confidence for baseline
            "note": "Real-time API data not available",
        }
        
    except Exception as e:
        print(f"      ⚠️  Economic indicators fetch failed: {e}")
        return None

# ============================================================================
# SOURCE 3: Kalshi Market Consensus - STATISTICAL
# ============================================================================

def fetch_kalshi_economics_consensus(ticker: str, series: str, df_markets: pd.DataFrame):
    """Source 3: Aggregate probabilities from other markets in same series (Statistical)"""
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
            
            volume = 1
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
# Convert Economic Data to Probability
# ============================================================================

def economic_value_to_probability(value, threshold, comparison, indicator_type, forecast=None, volatility=None):
    """Convert economic indicator value to probability using statistical models
    
    Uses Normal distribution to calculate P(value > threshold) or P(value < threshold)
    based on predicted value and statistical uncertainty.
    """
    if value is None:
        return None
    
    # Use forecast if available, otherwise use current value
    predicted_value = forecast if forecast is not None else value
    
    if threshold is None:
        return 0.5  # No threshold specified
    
    # Statistical uncertainty by indicator type
    # Based on historical volatility and forecast accuracy
    default_uncertainty = {
        "gdp": 0.8,  # GDP forecasts have ~0.8% standard error
        "inflation": 0.4,  # Inflation forecasts have ~0.4% standard error
        "unemployment": 0.3,  # Unemployment forecasts have ~0.3% standard error
        "interest_rate": 0.25,  # Interest rate forecasts have ~0.25% standard error
        "stock_market": 50,  # S&P 500 has ~50 point standard error (1-2% volatility)
        "housing": 5,  # Housing index has ~5 point standard error
        "retail_sales": 10,  # Retail sales has ~10 billion standard error
    }
    
    # Use provided volatility if available, otherwise use default
    sigma = volatility if volatility is not None else default_uncertainty.get(indicator_type, abs(threshold) * 0.1)
    
    # Ensure sigma is positive and reasonable
    if sigma <= 0:
        sigma = abs(threshold) * 0.1  # Default: 10% of threshold
    
    # Calculate probability using Normal distribution
    if comparison == "GT":
        # P(value > threshold)
        z = (threshold - predicted_value) / sigma
        prob = 0.5 * (1 - math.erf(z / math.sqrt(2)))  # 1 - Phi(z)
    else:  # LT
        # P(value < threshold)
        z = (threshold - predicted_value) / sigma
        prob = 0.5 * (1 + math.erf(z / math.sqrt(2)))  # Phi(z)
    
    # Cap probability
    prob = max(0.01, min(0.99, prob))
    
    return prob

# ============================================================================
# Combine Sources
# ============================================================================

def combine_sources(sources, market_info):
    """Combine forecasts from multiple sources using weighted average"""
    valid_sources = [s for s in sources if s is not None and s.get("probability") is not None and s.get("confidence", 0) > 0]
    
    if not valid_sources:
        return None, [], 0.0
    
    # Weighted average by confidence
    total_weight = sum(s["confidence"] for s in valid_sources)
    if total_weight == 0:
        return None, [], 0.0
    
    combined_prob = sum(s["probability"] * s["confidence"] for s in valid_sources) / total_weight
    
    # Combined confidence
    if len(valid_sources) >= 2:
        avg_conf = sum(s["confidence"] for s in valid_sources) / len(valid_sources)
        bonus = min(0.1, (len(valid_sources) - 1) * 0.05)
        combined_conf = min(0.95, avg_conf + bonus)
    else:
        combined_conf = valid_sources[0]["confidence"]
    
    # Cap probability
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

def enrich_with_economics_probs(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich markets with combined forecast from 3 STATISTICAL sources"""
    rows = []
    
    for _, row in df.iterrows():
        market_info = parse_economics_market(row["ticker"], row["title"])
        
        print(f"\n📊 Analyzing: {row['ticker']}")
        print(f"   Title: {row['title'][:70]}")
        print(f"   Indicator: {market_info['indicator_type']}")
        if market_info["threshold"]:
            print(f"   Threshold: {market_info['threshold']} ({market_info['comparison']})")
        if market_info["target_date"]:
            print(f"   Target Date: {market_info['target_date']}")
        
        # Fetch from all 3 STATISTICAL sources
        sources = []
        
        # Source 1: FRED Economic Data (Statistical)
        print("   🔵 Fetching FRED (Economic Data)...")
        fred_data = fetch_fred_data(market_info["indicator_type"], market_info["target_date"])
        if fred_data:
            # Convert economic value to probability
            # Calculate volatility from trend if available
            volatility = None
            if fred_data.get("trend") is not None:
                # Use trend-based volatility estimate
                volatility = abs(fred_data["trend"]) * 0.5  # Rough estimate
            
            prob = economic_value_to_probability(
                fred_data["current_value"],
                market_info["threshold"],
                market_info["comparison"],
                market_info["indicator_type"],
                fred_data.get("forecast"),
                volatility
            )
            if prob is not None:
                sources.append({
                    "source": "FRED",
                    "probability": prob,
                    "confidence": fred_data["confidence"],
                    "current_value": fred_data["current_value"],
                    "forecast": fred_data.get("forecast"),
                })
                print(f"      ✅ FRED: Value={fred_data['current_value']:.2f}, Forecast={fred_data.get('forecast', fred_data['current_value']):.2f}, P={prob:.3f}")
        
        # Source 2: Economic Indicators (Statistical)
        print("   🟢 Fetching Economic Indicators...")
        indicators = fetch_economic_indicators(market_info["indicator_type"], market_info["target_date"])
        if indicators:
            # Use volatility from indicators if available
            volatility = indicators.get("volatility")
            
            prob = economic_value_to_probability(
                indicators["current_value"],
                market_info["threshold"],
                market_info["comparison"],
                market_info["indicator_type"],
                indicators.get("forecast"),
                volatility
            )
            if prob is not None:
                sources.append({
                    "source": indicators["source"],
                    "probability": prob,
                    "confidence": indicators["confidence"],
                    "current_value": indicators["current_value"],
                })
                print(f"      ✅ {indicators['source']}: Value={indicators['current_value']:.2f}, P={prob:.3f}")
        
        # Source 3: Kalshi Market Consensus (Statistical)
        print("   🟡 Fetching Kalshi Consensus...")
        consensus = fetch_kalshi_economics_consensus(row["ticker"], row["series"], df)
        if consensus:
            sources.append(consensus)
            print(f"      ✅ Kalshi Consensus: P={consensus['probability']:.3f}, Markets={consensus['num_markets']}")
        
        if not sources:
            print("   ❌ No statistical sources available")
            continue
        
        # Combine sources
        combined_prob, source_probs, combined_conf = combine_sources(sources, market_info)
        
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
        print("📈 ECONOMICS MARKET ANALYSIS - 3 SOURCE STATISTICAL SYSTEM")
        print("=" * 80)
        print("\nSources (ALL STATISTICAL):")
        print("  1. FRED (Federal Reserve Economic Data) - Confidence: 85%")
        print("     (Official US economic data: GDP, inflation, unemployment, etc.)")
        print("  2. Economic Indicators (Multiple Free APIs) - Confidence: 60-85%")
        print("     - Alpha Vantage (GDP, CPI, Unemployment, Fed Rate)")
        print("     - BLS (Bureau of Labor Statistics - CPI, Unemployment)")
        print("     - World Bank (GDP, Inflation, Unemployment - no key needed)")
        print("     - Yahoo Finance (S&P 500 stock market data)")
        print("  3. Kalshi Market Consensus - Confidence: 70-85%")
        print("     (Volume-weighted average from other markets in same series)")
        print("\n" + "=" * 80)
        
        if not FRED_API_KEY:
            print("\n⚠️  WARNING: FRED API key not set!")
            print("   Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html")
            print("   Set FRED_API_KEY in the script to enable FRED data.")
            print("   Script will continue with other sources (Alpha Vantage, World Bank, etc.)\n")
        
        if ALPHA_VANTAGE_KEY:
            print("✅ Alpha Vantage API key found - will use for economic indicators")
        else:
            print("⚠️  Alpha Vantage API key not set (optional)")
            print("   Get a free key at: https://www.alphavantage.co/support/#api-key\n")
        
        if BLS_API_KEY:
            print("✅ BLS API key found - will use for CPI and unemployment data")
        else:
            print("ℹ️  BLS API key not set (optional, for enhanced CPI/unemployment data)")
            print("   Register at: https://www.bls.gov/developers/api_signature.htm\n")
        
        print("ℹ️  World Bank API: No key needed (free, will be used automatically)\n")
        
        print("\n🔍 Fetching economics markets from Kalshi...")
        df = get_open_economics_markets()
        
        if df.empty:
            print("\n❌ No economics markets available to analyze.")
        else:
            print(f"\n✅ Found {len(df)} open economics markets")
            print("=" * 80)
            print(f"\n⚙️  Analyzing {len(df)} markets (statistical analysis)...")
            print("=" * 80)
            
            df_out = enrich_with_economics_probs(df)
            
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

