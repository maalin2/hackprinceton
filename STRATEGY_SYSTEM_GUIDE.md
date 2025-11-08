# Strategy System - User Guide

## Overview

You can now choose different **technical analysis strategies** to analyze Kalshi markets:

1. **Statistical Arbitrage** (default) - Multi-source comparison
2. **Moving Average** - Price trend analysis

## Quick Start

### Use Statistical Arbitrage (Default)

```bash
python3 analyze_with_strategy.py --category weather --strategy statistical_arbitrage --limit 5
```

### Use Moving Average

```bash
python3 analyze_with_strategy.py --category weather --strategy moving_average --ma-period 7 --limit 5
```

## Strategies Explained

### 1. Statistical Arbitrage ⚡

**What it does:** Compares multiple independent data sources to find mispricing

**How it works:**
- **Weather**: NOAA + Open-Meteo + Climatology → find edge
- **Politics**: Kalshi consensus + historical patterns + betting models → find edge
- **Economics**: FRED + economic indicators + Kalshi consensus → find edge

**Best for:**
- All categories
- Finding true mispricing
- Statistical opportunities

**Example:**
```bash
python3 analyze_with_strategy.py \
  --category weather \
  --strategy statistical_arbitrage \
  --limit 10
```

**Output:**
```
📊 Analyzing: KXHIGHLAX-25NOV08-T74
   📈 P(Quant): 0.823 (confidence: 0.50)
   💰 P(Market): 0.995
   🔴 Edge: -17.2% → BUY NO
   📊 Sources:
      - NOAA: 0.800
      - Open-Meteo: 0.850
      - Climatology: 0.820
```

### 2. Moving Average 📈

**What it does:** Analyzes price trends using moving averages

**How it works:**
- Fetches historical price data from Kalshi
- Calculates SMA or EMA
- Identifies mean reversion or trend following signals

**Best for:**
- High-volume markets with price history
- Politics and Economics (trending markets)
- Identifying momentum or mean reversion

**Configurable Parameters:**
- `--ma-period`: Window size (default: 7 days)
- `--ma-type`: `sma` or `ema` (default: sma)
- `--signal-type`: `mean_reversion` or `trend_following` (default: mean_reversion)
- `--lookback-days`: Historical data window (default: 30 days)

**Example - Mean Reversion:**
```bash
python3 analyze_with_strategy.py \
  --category politics \
  --strategy moving_average \
  --ma-period 7 \
  --signal-type mean_reversion \
  --limit 10
```

**Example - Trend Following:**
```bash
python3 analyze_with_strategy.py \
  --category economics \
  --strategy moving_average \
  --ma-period 14 \
  --ma-type ema \
  --signal-type trend_following \
  --limit 10
```

**Output:**
```
📊 Analyzing: KXHIGHCHI-25NOV08-B48.5
   📈 P(Quant): 0.450 (confidence: 0.75)
   💰 P(Market): 0.005
   🟢 Edge: +44.5% → BUY YES
   🔧 Signals:
      - ma_value: 0.520
      - current_price: 0.005
      - deviation: -0.515
      - deviation_pct: -99.04
      - recent_trend: down
      - days_of_data: 15
```

## Full Command Reference

### General Options

```bash
python3 analyze_with_strategy.py \
  --category {weather|politics|economics} \  # Required
  --strategy {statistical_arbitrage|moving_average} \  # Optional (default: statistical_arbitrage)
  --limit 10  # Number of markets to analyze
```

### Moving Average Options

```bash
--ma-period 7              # MA window size (days)
--ma-type {sma|ema}        # Simple or Exponential MA
--signal-type {mean_reversion|trend_following}  # Signal type
--lookback-days 30         # Days of historical data to fetch
```

## Strategy Comparison

| Feature | Statistical Arbitrage | Moving Average |
|---------|----------------------|----------------|
| **Data Source** | External APIs | Kalshi price history |
| **Speed** | Slower (API calls) | Fast (historical data) |
| **Best For** | All categories | High-volume markets |
| **Requires** | API keys (optional) | Price history |
| **Confidence** | High (0.7-0.9) | Medium (0.5-0.8) |
| **Categories** | Weather, Politics, Economics | Politics, Economics |

## When to Use Each Strategy

### Use Statistical Arbitrage When:
✅ You want to compare independent data sources
✅ You're analyzing weather markets (no price trends)
✅ You want high-confidence signals
✅ You have API keys for data sources

### Use Moving Average When:
✅ You want to analyze price trends
✅ Market has sufficient price history
✅ You're analyzing politics or economics (trending markets)
✅ You want fast analysis (no external APIs)

## Examples by Category

### Weather Markets

**Best strategy: Statistical Arbitrage**
```bash
# Weather works best with statistical arbitrage
python3 analyze_with_strategy.py --category weather --strategy statistical_arbitrage --limit 10
```

Why? Weather forecasts from NOAA/Open-Meteo are more reliable than price trends.

### Politics Markets

**Both strategies work well:**

```bash
# Statistical arbitrage (high confidence)
python3 analyze_with_strategy.py --category politics --strategy statistical_arbitrage --limit 10

# Moving average for trending markets
python3 analyze_with_strategy.py --category politics --strategy moving_average --ma-period 14 --signal-type trend_following --limit 10
```

### Economics Markets

**Both strategies work well:**

```bash
# Statistical arbitrage with FRED data
python3 analyze_with_strategy.py --category economics --strategy statistical_arbitrage --limit 10

# Moving average for market sentiment
python3 analyze_with_strategy.py --category economics --strategy moving_average --ma-period 7 --signal-type mean_reversion --limit 10
```

## Understanding the Output

### Statistical Arbitrage Output

```
📊 Analyzing: KXHIGHLAX-25NOV08-T74
   Title: Will the high temp in LA be <74° on Nov 8, 2025?
   
   📈 P(Quant): 0.823           ← Probability from quantitative sources
   💰 P(Market): 0.995           ← Current market price
   🔴 Edge: -17.2% → BUY NO     ← Edge and recommended action
   
   📊 Sources:                   ← Breakdown by source
      - NOAA: 0.800
      - Open-Meteo: 0.850
      - Climatology: 0.820
```

### Moving Average Output

```
📊 Analyzing: KXHIGHCHI-25NOV08-B48.5
   Title: Will the high temp in Chicago be 48-49° on Nov 8, 2025?
   
   📈 P(Quant): 0.450           ← Probability from MA strategy
   💰 P(Market): 0.005           ← Current market price
   🟢 Edge: +44.5% → BUY YES    ← Edge and recommended action
   
   🔧 Signals:                   ← Strategy-specific signals
      - ma_value: 0.520          ← Moving average value
      - current_price: 0.005     ← Current price
      - deviation: -0.515        ← Distance from MA
      - deviation_pct: -99.04    ← Deviation as percentage
      - recent_trend: down       ← Price trend direction
      - days_of_data: 15         ← Data points available
```

## Advanced Usage

### Combine with Volume Filtering

All strategies automatically fetch markets sorted by volume (highest first):

```bash
# Analyze top 5 highest volume markets
python3 analyze_with_strategy.py --category politics --strategy statistical_arbitrage --limit 5
```

### Test Different MA Periods

```bash
# Short-term (3 days)
python3 analyze_with_strategy.py --category politics --strategy moving_average --ma-period 3

# Medium-term (7 days) - default
python3 analyze_with_strategy.py --category politics --strategy moving_average --ma-period 7

# Long-term (21 days)
python3 analyze_with_strategy.py --category politics --strategy moving_average --ma-period 21
```

### Compare SMA vs EMA

```bash
# Simple Moving Average (default)
python3 analyze_with_strategy.py --category economics --strategy moving_average --ma-type sma

# Exponential Moving Average (more recent weight)
python3 analyze_with_strategy.py --category economics --strategy moving_average --ma-type ema
```

## Troubleshooting

### "No historical data available"

**Problem:** Moving average strategy can't find price history

**Solution:**
- Use statistical arbitrage instead
- Try a market with more trading history
- Reduce `--lookback-days` parameter

### "Analysis failed"

**Problem:** Statistical arbitrage can't fetch external data

**Solution:**
- Check API keys (FRED, Alpha Vantage)
- Check internet connection
- Some markets may not be supported

### Low confidence scores

**Problem:** Confidence < 0.5

**Reasons:**
- Insufficient data (moving average)
- Sources disagree (statistical arbitrage)
- Market is ambiguous

**Solution:**
- Wait for more data
- Try different strategy
- Use caution with low-confidence signals

## Future Strategies

Coming soon:
- **Momentum Strategy**: Price momentum indicators
- **Volatility Strategy**: Bollinger Bands
- **Hybrid Strategy**: Combine multiple strategies

## API Reference

### Strategy Factory

```python
from strategies import get_strategy

# Get a strategy
strategy = get_strategy('moving_average', 'weather', ma_period=7)

# Analyze a market
result = strategy.analyze(market)

# Access results
print(f"P(Quant): {result.p_quant}")
print(f"Confidence: {result.confidence}")
print(f"Signals: {result.signals}")
print(f"Sources: {result.sources}")
```

### Strategy Result Object

```python
@dataclass
class StrategyResult:
    p_quant: float          # 0-1 probability
    confidence: float       # 0-1 confidence
    signals: Dict           # Strategy-specific signals
    sources: Dict           # Source breakdown
    strategy_name: str      # Name of strategy used
    timestamp: str          # ISO timestamp
```

## Summary

✅ **2 strategies available**: Statistical Arbitrage & Moving Average
✅ **Flexible configuration**: Customize parameters per strategy
✅ **All categories supported**: Weather, Politics, Economics
✅ **Volume-sorted markets**: Highest liquidity first
✅ **Easy to use**: Simple CLI interface

**Choose your strategy and start finding edges!** 🎯

