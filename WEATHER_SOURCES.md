# Weather Market Analysis - 3 Source Quantitative System

## Overview

The `weather_test.py` script analyzes Kalshi weather markets using **3 independent data sources** to calculate probabilities and identify trading edges.

## The 3 Sources

### 1. 🔵 NOAA (National Weather Service) - GFS Model

- **API**: `api.weather.gov`
- **Model**: GFS (Global Forecast System)
- **Confidence**: 85%
- **Coverage**: U.S. only
- **Update Frequency**: Every 6 hours
- **Strengths**: Official U.S. government forecasts, highly accurate
- **Limitations**: U.S. only, requires User-Agent header

### 2. 🟢 Open-Meteo - ECMWF Model

- **API**: `api.open-meteo.com`
- **Model**: ECMWF (European Centre for Medium-Range Weather Forecasts)
- **Confidence**: 80%
- **Coverage**: Global
- **Update Frequency**: Daily
- **Strengths**: Global coverage, free API, no key required
- **Limitations**: Slightly less accurate than NOAA for U.S.

### 3. 🟡 Climatology - Historical Averages

- **Source**: Historical monthly averages by city
- **Confidence**: 70%
- **Coverage**: Major U.S. cities
- **Update Frequency**: Static (based on historical data)
- **Strengths**: Provides baseline, works even when forecasts fail
- **Limitations**: Less accurate for short-term forecasts, no real-time data

## How Sources Are Combined

### Weighted Average by Confidence

```python
combined_prob = Σ(probability_i × confidence_i) / Σ(confidence_i)
```

**Example:**

- NOAA: P = 0.65, Confidence = 0.85
- Open-Meteo: P = 0.60, Confidence = 0.80
- Climatology: P = 0.55, Confidence = 0.70

**Combined:**

```
P_combined = (0.65×0.85 + 0.60×0.80 + 0.55×0.70) / (0.85 + 0.80 + 0.70)
           = (0.5525 + 0.48 + 0.385) / 2.35
           = 1.4175 / 2.35
           = 0.603
```

### Combined Confidence

The combined confidence increases with more sources:

- **Single source**: Uses that source's confidence
- **Multiple sources**: Average confidence + bonus for diversity
  - Formula: `avg_confidence + min(0.1, (num_sources - 1) × 0.05)`

**Example:**

- 3 sources with avg confidence 0.78 → Combined: 0.78 + 0.1 = 0.88 (capped at 0.95)

## Edge Calculation

```
Edge = P_combined - P_market
```

Where:

- `P_combined` = Weighted average from 3 sources
- `P_market` = Implied probability from Kalshi prices
  - `P_market = (yes_bid + yes_ask) / 200`

### Trading Signals

- **BUY YES**: Edge > +8% (model says much higher than market)
- **BUY NO**: Edge < -8% (model says much lower than market)
- **HOLD**: -8% ≤ Edge ≤ +8% (no clear edge)

## Market Types Supported

### 1. High Temperature > Threshold (GT)

- Example: `KXHIGHPHIL-25NOV08-T71` (Will Philadelphia hit >71°F?)
- Uses Normal distribution: `P = 1 - Φ((T - μ) / σ)`
- Uncertainty `σ` increases with lead time:
  - 1 day: σ = 3°F
  - 2 days: σ = 4°F
  - 3+ days: σ = 5°F

### 2. High Temperature Band (BAND)

- Example: `KXHIGHNY-25NOV08-B64.5` (Will NYC high be in [64, 65]°F?)
- Uses Normal distribution: `P = Φ((U - μ) / σ) - Φ((L - μ) / σ)`

### 3. Precipitation (RAIN)

- Example: `KXRAINNY-25NOV08` (Will it rain in NYC?)
- Uses precipitation probability directly from forecasts
- Climatology fallback: 30% baseline

## Output Format

### Per-Market Analysis

```
📊 Analyzing: KXHIGHPHIL-25NOV08-T71
   Target date: 2025-11-08 (lead: 5 days)
   🔵 Fetching NOAA (GFS)...
      ✅ NOAA: tmax=68.0, pop=None
   🟢 Fetching Open-Meteo (ECMWF)...
      ✅ Open-Meteo: tmax=67.5, pop=0.1
   🟡 Fetching Climatology...
      ✅ Climatology: tmax=56.0 (avg)
   📈 Combined: 0.631 (conf: 0.88)
   💰 Market: 0.020
   🎯 Edge: +61.1% (BUY YES)
```

### Summary Statistics

- Markets analyzed
- Average edge
- Max edge
- Markets with >8% edge
- Average sources per market
- Average confidence

### Best Opportunities

- **BUY YES**: Markets where combined probability >> market price
- **BUY NO**: Markets where combined probability << market price

## Running the Script

```bash
python3 weather_test.py
```

### Requirements

```bash
pip3 install requests pandas pytz numpy
```

### Optional: Visual Crossing API Key

For enhanced climatology data, set `VC_API_KEY` in the script:

```python
VC_API_KEY = "YOUR_KEY_HERE"
```

## Example Output

```
================================================================================
🌤️  WEATHER MARKET ANALYSIS - 3 SOURCE QUANTITATIVE SYSTEM
================================================================================

Sources:
  1. NOAA (GFS Model) - Confidence: 85%
  2. Open-Meteo (ECMWF Model) - Confidence: 80%
  3. Climatology (Historical Averages) - Confidence: 70%

================================================================================

📊 Found 15 open weather markets
================================================================================

📊 Analyzing: KXHIGHPHIL-25NOV08-T71
   Target date: 2025-11-08 (lead: 5 days)
   🔵 Fetching NOAA (GFS)...
      ✅ NOAA: tmax=68.0, pop=None
   🟢 Fetching Open-Meteo (ECMWF)...
      ✅ Open-Meteo: tmax=67.5, pop=0.1
   🟡 Fetching Climatology...
      ✅ Climatology: tmax=56.0 (avg)
   📈 Combined: 0.631 (conf: 0.88)
   💰 Market: 0.020
   🎯 Edge: +61.1% (BUY YES)

================================================================================
📈 RESULTS SUMMARY
================================================================================

ticker                        combined_p  market_p  edge_pct  sources  confidence
KXHIGHPHIL-25NOV08-T71        0.631       0.020     61.1      3        0.88
...

================================================================================
📊 SUMMARY STATISTICS
================================================================================
Markets analyzed: 15
Average edge: 12.5%
Max edge: 61.1%
Markets with >8% edge: 8
Average sources per market: 3.0
Average confidence: 0.85

================================================================================
🟢 BUY YES OPPORTUNITIES (Edge > 8%)
================================================================================
KXHIGHPHIL-25NOV08-T71     | Edge: +61.1% | Combined: 0.631 | Market: 0.020
  Sources: NOAA: 0.630, Open-Meteo: 0.615, Climatology: 0.520
...
```

## Advantages of 3-Source System

1. **Redundancy**: If one source fails, others provide backup
2. **Accuracy**: Multiple models reduce individual model biases
3. **Confidence**: More sources = higher confidence (up to a point)
4. **Robustness**: System works even when APIs are down
5. **Transparency**: See breakdown from each source

## Limitations

1. **API Rate Limits**: NOAA and Open-Meteo have rate limits
2. **Geographic Coverage**: Climatology only covers major U.S. cities
3. **Model Agreement**: Sources may disagree (handled by weighted average)
4. **Lead Time**: Accuracy decreases with longer forecast horizons
5. **Market Availability**: Weather markets are seasonal

## Future Improvements

1. **More Sources**: Add WeatherAPI, AccuWeather, etc.
2. **Machine Learning**: Calibrate probabilities using historical accuracy
3. **Dynamic Weights**: Adjust source weights based on recent accuracy
4. **Ensemble Methods**: Use more sophisticated combination techniques
5. **Real-Time Updates**: Continuous monitoring and re-analysis

---

**Built for quantitative weather market analysis on Kalshi** 🌤️
