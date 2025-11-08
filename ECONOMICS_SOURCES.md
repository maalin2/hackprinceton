# Economics Market Analysis - 3 Source STATISTICAL System

## Overview

The `economics_test.py` script analyzes Kalshi economics markets using **3 STATISTICAL data sources** to calculate probabilities and identify trading edges.

## The 3 STATISTICAL Sources

### 1. 🔵 FRED (Federal Reserve Economic Data) - STATISTICAL

- **Source**: Federal Reserve Economic Data API
- **Method**: Official US economic data with trend analysis
- **Confidence**: 85% (official government data)
- **Coverage**:
  - GDP (Real Gross Domestic Product)
  - Inflation (CPI - Consumer Price Index)
  - Unemployment Rate
  - Federal Funds Rate (Interest Rates)
  - Case-Shiller Home Price Index (Housing)
  - Retail Sales
- **Strengths**:
  - Official government data (most reliable)
  - Historical time series data
  - Trend-based forecasting
  - Real-time updates
- **How it works**:
  1. Fetches latest observations from FRED API
  2. Calculates trend from recent data points
  3. Projects forecast using trend
  4. Converts to probability using Normal distribution

### 2. 🟢 Economic Indicators (Multiple Free APIs) - STATISTICAL

- **Source**: Multiple free APIs with fallback chain
- **Method**: Real-time economic data from multiple sources
- **Confidence**: 60-85% (depending on data source)
- **API Priority Order**:
  1. **Alpha Vantage** (if key available)
     - GDP, CPI, Unemployment, Federal Funds Rate
     - Confidence: 75%
  2. **BLS (Bureau of Labor Statistics)** (if key available)
     - CPI, Unemployment Rate
     - Confidence: 85% (official government data)
  3. **World Bank API** (no key needed, always available)
     - GDP, Inflation, Unemployment
     - Confidence: 80%
  4. **Yahoo Finance** (for stock market)
     - S&P 500 real-time data
     - Confidence: 80%
  5. **Statistical Baselines** (fallback)
     - Historical averages when APIs unavailable
     - Confidence: 60%
- **Strengths**:
  - Multiple redundant sources (automatic fallback)
  - Real-time data from official sources
  - No single point of failure
  - Free APIs (no cost)
- **How it works**:
  - Tries APIs in order of preference
  - Falls back to next API if previous fails
  - Uses statistical baselines as last resort

### 3. 🟡 Kalshi Market Consensus - STATISTICAL

- **Source**: Other markets in the same Kalshi series
- **Method**: Volume-weighted average of market-implied probabilities
- **Confidence**: 70-85% (depending on number of markets and volume)
- **Strengths**:
  - Uses actual market prices (statistical, not semantic)
  - Volume-weighted (more liquid markets = higher weight)
  - Real-time market consensus
- **How it works**:
  - Finds all other markets in the same series
  - Calculates implied probability from each market's bid/ask
  - Weighted average by trading volume
  - Formula: `P = Σ(P_i × V_i) / Σ(V_i)`

## Why STATISTICAL (Not Semantic)?

### ❌ What We DON'T Use:

- **News sentiment analysis** (semantic - based on text meaning)
- **Social media sentiment** (semantic - based on posts/comments)
- **Keyword analysis** (semantic - counting positive/negative words)

### ✅ What We DO Use:

- **Economic data** (statistical - official numbers)
- **Market prices** (statistical - aggregated probabilities)
- **Statistical models** (statistical - mathematical relationships)
- **Historical volatility** (statistical - past variation)

## Statistical Methods

### 1. FRED Data (Trend-Based Forecasting)

```python
# Fetch latest observations
observations = fetch_fred_observations(series_id)

# Calculate trend
recent_values = [obs.value for obs in observations[:3]]
trend = (recent_values[0] - recent_values[-1]) / (len(recent_values) - 1)

# Forecast
forecast = recent_values[0] + trend * 1  # Project 1 period ahead
```

**Example:**

- Recent GDP values: [2.5, 2.6, 2.7] (quarterly %)
- Trend: (2.7 - 2.5) / 2 = 0.1% per quarter
- Forecast: 2.7 + 0.1 = 2.8%

### 2. Stock Market Data (Moving Average Trend)

```python
# Fetch S&P 500 data
closes = fetch_yahoo_finance("^GSPC")

# Calculate moving averages
recent_avg = np.mean(closes[-5:])  # Last 5 days
older_avg = np.mean(closes[-10:-5])  # Previous 5 days

# Trend (% change)
trend = (recent_avg - older_avg) / older_avg * 100

# Forecast
forecast = closes[-1] * (1 + trend / 100)
```

**Example:**

- Recent 5-day avg: 4,500
- Previous 5-day avg: 4,480
- Trend: (4,500 - 4,480) / 4,480 \* 100 = 0.45%
- Forecast: 4,500 \* 1.0045 = 4,520

### 3. Market Consensus (Volume-Weighted Average)

```python
# For each market in the series:
P_i = (yes_bid + yes_ask) / 200  # Implied probability
V_i = volume                      # Trading volume

# Weighted average:
P_combined = Σ(P_i × V_i) / Σ(V_i)
```

**Example:**

- Market A: P=0.65, Volume=2000
- Market B: P=0.60, Volume=1000
- Market C: P=0.70, Volume=500

**Weighted Average:**

```
P = (0.65×2000 + 0.60×1000 + 0.70×500) / (2000+1000+500)
  = (1300 + 600 + 350) / 3500
  = 2250 / 3500
  = 0.643
```

### 4. Economic Value to Probability (Normal Distribution)

```python
# Statistical uncertainty by indicator type
sigma = {
    "gdp": 0.8,           # GDP forecasts have ~0.8% standard error
    "inflation": 0.4,     # Inflation forecasts have ~0.4% standard error
    "unemployment": 0.3,  # Unemployment forecasts have ~0.3% standard error
    "interest_rate": 0.25,# Interest rate forecasts have ~0.25% standard error
    "stock_market": 50,   # S&P 500 has ~50 point standard error
    "housing": 5,         # Housing index has ~5 point standard error
    "retail_sales": 10,   # Retail sales has ~10 billion standard error
}

# Calculate probability using Normal distribution
if comparison == "GT":  # P(value > threshold)
    z = (threshold - predicted_value) / sigma
    prob = 1 - Phi(z)  # Standard normal CDF
else:  # LT: P(value < threshold)
    z = (threshold - predicted_value) / sigma
    prob = Phi(z)
```

**Example:**

- Market: "Will GDP be >3%?"
- FRED Forecast: 2.8%
- Threshold: 3.0%
- Sigma: 0.8% (GDP standard error)
- Z-score: (3.0 - 2.8) / 0.8 = 0.25
- Probability: P(Z > 0.25) = 1 - Φ(0.25) = 1 - 0.5987 = **0.4013** (40.13%)

## How Sources Are Combined

### Weighted Average by Confidence

```python
combined_prob = Σ(probability_i × confidence_i) / Σ(confidence_i)
```

**Example:**

- FRED: P = 0.40, Confidence = 0.85
- Economic Indicators: P = 0.45, Confidence = 0.65
- Kalshi Consensus: P = 0.38, Confidence = 0.80

**Combined:**

```
P_combined = (0.40×0.85 + 0.45×0.65 + 0.38×0.80) / (0.85 + 0.65 + 0.80)
           = (0.34 + 0.2925 + 0.304) / 2.30
           = 0.9265 / 2.30
           = 0.403
```

## Edge Calculation

```
Edge = P_combined - P_market
```

Where:

- `P_combined` = Weighted average from 3 statistical sources
- `P_market` = Implied probability from current market prices
  - `P_market = (yes_bid + yes_ask) / 200`

### Trading Signals

- **BUY YES**: Edge > +8% (model says much higher than market)
- **BUY NO**: Edge < -8% (model says much lower than market)
- **HOLD**: -8% ≤ Edge ≤ +8% (no clear edge)

## Market Types Supported

### 1. GDP Markets

- Example: "Will Q1 2025 GDP be >3%?"
- Uses: FRED GDP data + trend forecasting
- Statistical method: Normal distribution with 0.8% standard error

### 2. Inflation Markets

- Example: "Will CPI be <2.5% in 2025?"
- Uses: FRED CPI data + trend forecasting
- Statistical method: Normal distribution with 0.4% standard error

### 3. Unemployment Markets

- Example: "Will unemployment be <4%?"
- Uses: FRED unemployment data + trend forecasting
- Statistical method: Normal distribution with 0.3% standard error

### 4. Stock Market Markets

- Example: "Will S&P 500 be >5000?"
- Uses: Yahoo Finance S&P 500 data + moving average trend
- Statistical method: Normal distribution with 50 point standard error

### 5. Interest Rate Markets

- Example: "Will Fed rate be >5%?"
- Uses: FRED federal funds rate data + trend forecasting
- Statistical method: Normal distribution with 0.25% standard error

## Data Sources

### FRED API (Primary Source)

- **URL**: https://api.stlouisfed.org/fred/
- **Cost**: Free (requires API key)
- **Rate Limit**: 120 requests per minute
- **Get API Key**: https://fred.stlouisfed.org/docs/api/api_key.html
- **Confidence**: 85% (official government data)

**Series IDs:**

- `GDP`: Real Gross Domestic Product
- `CPIAUCSL`: Consumer Price Index for All Urban Consumers
- `UNRATE`: Unemployment Rate
- `FEDFUNDS`: Federal Funds Rate
- `CSUSHPISA`: Case-Shiller Home Price Index
- `RSAFS`: Retail and Food Services Sales

### Alpha Vantage API (Alternative Source)

- **URL**: https://www.alphavantage.co/query
- **Cost**: Free (requires API key)
- **Rate Limit**: 5 API requests per minute, 500 per day (free tier)
- **Get API Key**: https://www.alphavantage.co/support/#api-key
- **Confidence**: 75%
- **Coverage**: GDP, CPI, Unemployment, Federal Funds Rate

**Functions:**

- `REAL_GDP`: Real Gross Domestic Product
- `CPI`: Consumer Price Index
- `UNEMPLOYMENT`: Unemployment Rate
- `FEDERAL_FUNDS_RATE`: Federal Funds Rate

### BLS (Bureau of Labor Statistics) API (Alternative Source)

- **URL**: https://api.bls.gov/publicAPI/v2/timeseries/data/
- **Cost**: Free (requires registration)
- **Rate Limit**: Reasonable use
- **Register**: https://www.bls.gov/developers/api_signature.htm
- **Confidence**: 85% (official government data)
- **Coverage**: CPI, Unemployment Rate

**Series IDs:**

- `CUUR0000SA0`: CPI for All Urban Consumers
- `LNS14000000`: Unemployment Rate

### World Bank API (Alternative Source - No Key Needed!)

- **URL**: https://api.worldbank.org/v2/country/USA/indicator/
- **Cost**: Free (no key needed)
- **Rate Limit**: Reasonable use
- **Confidence**: 80%
- **Coverage**: GDP, Inflation, Unemployment

**Indicator Codes:**

- `NY.GDP.MKTP.KD.ZG`: GDP growth (annual %)
- `FP.CPI.TOTL.ZG`: Inflation, consumer prices (annual %)
- `SL.UEM.TOTL.ZS`: Unemployment, total (% of total labor force)

### Yahoo Finance API (Stock Market Data)

- **URL**: https://query1.finance.yahoo.com/v8/finance/chart/
- **Cost**: Free (no key needed)
- **Rate Limit**: Reasonable use (no official limit)
- **Confidence**: 80%
- **Example**: `https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC` (S&P 500)

### Kalshi API (Market Consensus)

- **URL**: https://api.elections.kalshi.com/trade-api/v2
- **Cost**: Free (no key needed for public data)
- **Rate Limit**: Reasonable use

## Setup

### API Keys (Optional but Recommended)

1. **FRED API Key** (Recommended - Primary Source):

   - Get free key at: https://fred.stlouisfed.org/docs/api/api_key.html
   - Set `FRED_API_KEY` in script
   - **Best for**: GDP, Inflation, Unemployment, Interest Rates

2. **Alpha Vantage Key** (Optional - Alternative Source):

   - Get free key at: https://www.alphavantage.co/support/#api-key
   - Set `ALPHA_VANTAGE_KEY` in script
   - **Best for**: GDP, CPI, Unemployment, Fed Rate
   - **Rate Limit**: 5 requests/min, 500/day (free tier)

3. **BLS API Key** (Optional - Alternative Source):

   - Register at: https://www.bls.gov/developers/api_signature.htm
   - Set `BLS_API_KEY` in script
   - **Best for**: CPI, Unemployment (official government data)

4. **World Bank API** (No Key Needed!):
   - No registration required
   - Automatically used as fallback
   - **Best for**: GDP, Inflation, Unemployment
   - **Always available** - no key needed!

### Installation

```bash
pip3 install requests pandas numpy
```

## Running the Script

```bash
python3 economics_test.py
```

## Output Format

### Per-Market Analysis

```
📊 Analyzing: GDP-2025-Q1-GT3
   Title: Will Q1 2025 GDP be >3%?
   Indicator: gdp
   Threshold: 3.0 (GT)
   Target Date: 2025-01-01
   🔵 Fetching FRED (Economic Data)...
      ✅ FRED: Value=2.70, Forecast=2.80, P=0.401
   🟢 Fetching Economic Indicators...
      ✅ Economic Indicators (Statistical Baseline): Value=2.50, P=0.265
   🟡 Fetching Kalshi Consensus...
      ✅ Kalshi Consensus: P=0.380, Markets=3
   📈 Combined: 0.403 (conf: 0.82)
   💰 Market: 0.650
   🎯 Edge: -24.7% (BUY NO)
```

## Advantages of Statistical Approach

1. **Objective**: No interpretation of text/sentiment
2. **Quantitative**: Based on numbers and data
3. **Official Data**: Uses government economic data (FRED)
4. **Market-Based**: Uses real market prices
5. **Reproducible**: Same inputs → same outputs
6. **Time Series**: Uses trend analysis for forecasting

## Limitations

1. **FRED API Key**: Requires free API key for best results
2. **Historical Data**: Baselines may not reflect current conditions
3. **Market Consensus**: Requires multiple markets in same series
4. **Forecast Accuracy**: Simple trend models may not capture all factors
5. **Volatility Estimates**: Based on historical averages, may vary

## Future Statistical Enhancements

1. **Advanced Time Series Models**: ARIMA, Prophet, LSTM for better forecasting
2. **Multiple Economic Indicators**: Combine GDP, inflation, unemployment for composite forecasts
3. **Cross-Market Analysis**: Compare similar markets across different time periods
4. **Volatility Models**: GARCH, stochastic volatility for better uncertainty estimates
5. **Machine Learning**: Train models on historical economic data + market outcomes
6. **Real-Time Data**: Integrate more real-time economic indicators
7. **International Data**: Add international economic data sources

## Example Output

```
================================================================================
📈 ECONOMICS MARKET ANALYSIS - 3 SOURCE STATISTICAL SYSTEM
================================================================================

Sources (ALL STATISTICAL):
  1. FRED (Federal Reserve Economic Data) - Confidence: 85%
     (Official US economic data: GDP, inflation, unemployment, etc.)
  2. Economic Indicators (Public APIs) - Confidence: 60-80%
     (Economic data from various public sources)
  3. Kalshi Market Consensus - Confidence: 70-85%
     (Volume-weighted average from other markets in same series)

================================================================================

⚠️  WARNING: FRED API key not set!
   Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html
   Set FRED_API_KEY in the script to enable FRED data.
   Script will continue with other sources only.

✅ Found 15 open economics markets
================================================================================

📊 Analyzing: GDP-2025-Q1-GT3
   Title: Will Q1 2025 GDP be >3%?
   Indicator: gdp
   Threshold: 3.0 (GT)
   🔵 Fetching FRED (Economic Data)...
      ⚠️  FRED API key not set (skipping)
   🟢 Fetching Economic Indicators...
      ✅ Economic Indicators (Statistical Baseline): Value=2.50, P=0.265
   🟡 Fetching Kalshi Consensus...
      ✅ Kalshi Consensus: P=0.380, Markets=3
   📈 Combined: 0.332 (conf: 0.73)
   💰 Market: 0.650
   🎯 Edge: -31.8% (BUY NO)

================================================================================
📈 RESULTS SUMMARY
================================================================================

ticker                    combined_p  market_p  edge_pct  sources  confidence
GDP-2025-Q1-GT3           0.332       0.650     -31.8     2        0.73
...

================================================================================
📊 SUMMARY STATISTICS
================================================================================
Markets analyzed: 15
Average edge: -5.2%
Max edge: 31.8%
Markets with >8% edge: 8
Average sources per market: 2.1
Average confidence: 0.71
```

## Statistical vs Semantic

| Aspect              | Statistical (This System)                | Semantic (Old Approach)            |
| ------------------- | ---------------------------------------- | ---------------------------------- |
| **Data**            | Numbers, economic data, market prices    | Text, sentiment, keywords          |
| **Method**          | Mathematical models, Normal distribution | Text analysis                      |
| **Sources**         | FRED, Yahoo Finance, market prices       | News, social media, sentiment      |
| **Accuracy**        | Based on economic data and models        | Based on text interpretation       |
| **Bias**            | Less prone to interpretation bias        | Can be biased by wording           |
| **Reproducibility** | High (same inputs → same outputs)        | Lower (text interpretation varies) |
| **Forecasting**     | Trend analysis, time series models       | Sentiment analysis                 |

---

**Built for quantitative, statistical economics market analysis on Kalshi** 📈

**No sentiment analysis - pure statistics!**
