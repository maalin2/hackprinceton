import requests, math, datetime as dt, pytz, pandas as pd

KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
UA     = {"User-Agent": "weather-agent/0.1 (mangalapallianshul@gmail.com)"}
TZ     = pytz.timezone("America/New_York")

# 1) Fetch some open WEATHER markets and build DataFrame
def get_open_weather_markets():
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
    for series in weather_series[:10]:  # Check first 10 weather series
        r = requests.get(f"{KALSHI}/markets", 
                        params={"series_ticker": series["ticker"], "status":"open", "limit":100}, 
                        timeout=15)
        if r.status_code == 200:
            ms = r.json().get("markets", [])
            all_markets.extend(ms)
    
    if not all_markets:
        print("⚠️  No active weather markets found. Weather markets may be closed for the season.")
        return pd.DataFrame()
    
    df = pd.DataFrame(all_markets)[["ticker","title","yes_bid","yes_ask","last_price"]]
    df["series"] = df["ticker"].str.split("-").str[0]
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

# 3) NOAA helpers (fetch once per series)
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
def p_high_gt(mu, T, lead_days):
    if mu is None: return None
    sigma = 3.0 if lead_days<=1 else (4.0 if lead_days==2 else 5.0)
    z = (T - mu)/sigma
    return 0.5*(1 - math.erf(z/math.sqrt(2)))  # 1 - Phi(z)

def p_high_band(mu, L, U, lead_days):
    if mu is None: return None
    sigma = 3.0 if lead_days<=1 else (4.0 if lead_days==2 else 5.0)
    Phi = lambda x: 0.5*(1+math.erf(x/math.sqrt(2)))
    return max(0.0, min(1.0, Phi((U-mu)/sigma) - Phi((L-mu)/sigma)))

def implied_prob(yes_bid, yes_ask, last):
    if pd.notnull(yes_bid) and pd.notnull(yes_ask) and yes_ask>0:
        return ((yes_bid + yes_ask)/2)/100.0
    if pd.notnull(last):
        return last/100.0
    return None

# 6) Main: enrich the DataFrame with forecast probs and edge
def enrich_with_weather_probs(df: pd.DataFrame) -> pd.DataFrame:
    today = dt.datetime.now(TZ).date()
    # fetch forecasts once per series
    cache = {}
    for s in df["series"].unique():
        cfg = SERIES_MAP.get(s)
        if not cfg: 
            continue
        h_url = nws_points(cfg["lat"], cfg["lon"])
        periods = hourly_periods(h_url)
        cache[s] = {"periods": periods, "kind": cfg["kind"]}

    rows = []
    for _, row in df.iterrows():
        s = row["series"]
        if s not in cache:
            continue
        parsed = parse_weather_market(row["ticker"])
        periods = slice_local_day(cache[s]["periods"], parsed["day"])
        fx = summarize_day(periods)
        lead = (parsed["day"] - today).days

        if parsed["type"]=="GT":
            p_fx = p_high_gt(fx["tmax"], parsed["T"], abs(lead))
        elif parsed["type"]=="BAND":
            p_fx = p_high_band(fx["tmax"], parsed["L"], parsed["U"], abs(lead))
        else:
            p_fx = fx["pop"]

        p_mkt = implied_prob(row["yes_bid"], row["yes_ask"], row["last_price"])
        edge  = None if (p_fx is None or p_mkt is None) else (p_fx - p_mkt)

        rows.append({
            **row.to_dict(),
            "forecast_p": None if p_fx is None else round(p_fx,3),
            "market_p": None if p_mkt is None else round(p_mkt,3),
            "edge": None if edge is None else round(edge,3),
        })
    return pd.DataFrame(rows)

# ---- Run once ----
df = get_open_weather_markets()
if df.empty:
    print("\n❌ No weather markets available to analyze.")
    print("Weather markets are typically only active during certain seasons or specific dates.")
else:
    df_out = enrich_with_weather_probs(df)
    print("\n✅ Weather market analysis:")
    print(df_out.head(10)[["ticker","forecast_p","market_p","edge","yes_bid","yes_ask"]])

print(df)
