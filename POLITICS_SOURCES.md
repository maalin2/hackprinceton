# Politics Market Analysis - 3 Source STATISTICAL System

## Overview

The `politics_test.py` script analyzes Kalshi politics markets using **3 STATISTICAL data sources** (no sentiment analysis) to calculate probabilities and identify trading edges.

## The 3 STATISTICAL Sources

### 1. 🔵 Kalshi Market Consensus - Market Aggregation (STATISTICAL)

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

### 2. 🟢 Historical Voting Patterns - Statistical Models (STATISTICAL)

- **Source**: Historical election results (2000-2024)
- **Method**: Statistical models based on past voting patterns
- **Confidence**: 65-75%
- **Coverage**: 20+ states with state-specific data
- **Strengths**:
  - Based on actual historical outcomes (statistical)
  - State-specific models (more accurate than national)
  - Office-specific patterns (Senate vs Governor vs President)
  - Party-specific baselines
- **How it works**:
  - Looks up historical win rates by state/office/party
  - Uses state-specific data when available
  - Falls back to national baseline
  - Example: FL Senate Republican → 52% (based on historical FL Senate races)

### 3. 🟡 Betting Market Model - Statistical Adjustments (STATISTICAL)

- **Source**: Statistical model with state/office/party adjustments
- **Method**: Base probability + statistical adjustments
- **Confidence**: 70-85%
- **Strengths**:
  - Combines multiple statistical factors
  - State adjustments (swing states vs safe states)
  - Office adjustments (elections vs nominations)
  - Event type adjustments
- **How it works**:
  - Base probability from historical patterns
  - State adjustment: ±5% based on state leanings
  - Event type adjustment: Nominations less certain than elections
  - Formula: `P = base + state_adj × 0.7 + event_adj`

## Why STATISTICAL (Not Semantic)?

### ❌ What We DON'T Use:

- **News sentiment analysis** (semantic - based on text meaning)
- **Social media sentiment** (semantic - based on posts/comments)
- **Keyword analysis** (semantic - counting positive/negative words)

### ✅ What We DO Use:

- **Market prices** (statistical - aggregated probabilities)
- **Historical data** (statistical - past outcomes)
- **Statistical models** (statistical - mathematical relationships)

## Statistical Methods

### 1. Market Consensus (Volume-Weighted Average)

```python
# For each market in the series:
P_i = (yes_bid + yes_ask) / 200  # Implied probability
V_i = volume                      # Trading volume

# Weighted average:
P_combined = Σ(P_i × V_i) / Σ(V_i)
```

**Example:**

- Market A: P=0.60, Volume=1000
- Market B: P=0.55, Volume=500
- Market C: P=0.65, Volume=2000

**Weighted Average:**

```
P = (0.60×1000 + 0.55×500 + 0.65×2000) / (1000+500+2000)
  = (600 + 275 + 1300) / 3500
  = 2175 / 3500
  = 0.621
```

### 2. Historical Patterns (State-Specific Models)

```python
# Lookup table based on historical election results
HISTORICAL_PATTERNS[state][office][party] = probability

# Example:
HISTORICAL_PATTERNS["FL"]["Senate"]["Republican"] = 0.52
# Based on: FL Senate races 2000-2024, Republican win rate = 52%
```

### 3. Betting Model (Statistical Adjustments)

```python
# Base probability
base_prob = NATIONAL_BASELINE[office][party]  # e.g., 0.50

# State adjustment (if state data available)
state_prob = HISTORICAL_PATTERNS[state][office][party]  # e.g., 0.52
state_adjustment = state_prob - base_prob  # e.g., +0.02

# Event type adjustment
event_adjustment = -0.05 if nomination else 0.0

# Final probability
P = base_prob + state_adjustment × 0.7 + event_adjustment
```

## How Sources Are Combined

### Weighted Average by Confidence

```python
combined_prob = Σ(probability_i × confidence_i) / Σ(confidence_i)
```

**Example:**

- Kalshi Consensus: P = 0.65, Confidence = 0.80
- Historical Patterns: P = 0.52, Confidence = 0.75
- Betting Model: P = 0.58, Confidence = 0.78

**Combined:**

```
P_combined = (0.65×0.80 + 0.52×0.75 + 0.58×0.78) / (0.80 + 0.75 + 0.78)
           = (0.52 + 0.39 + 0.4524) / 2.33
           = 1.3624 / 2.33
           = 0.585
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

### 1. Election Outcomes

- Example: "Will [Candidate] win the 2028 election?"
- Uses: Historical patterns + market consensus

### 2. Nominations

- Example: "Will [Candidate] run for [Office]?"
- Uses: Betting model (with nomination adjustment)

### 3. State-Specific Races

- Example: "Will Republicans win Florida Senate?"
- Uses: State-specific historical patterns

## Data Sources

### Historical Patterns Database

Covers 20+ states with data for:

- **Senate** races
- **Governor** races
- **President** (electoral votes)

Based on 2000-2024 election results:

- Swing states: FL, PA, MI, WI, NC, AZ, GA, NV
- Strongly Republican: TX, OH, IN, MO, TN
- Strongly Democratic: CA, NY, IL, MA, MD, NJ, WA, OR, CT, DE

### Market Consensus

- Uses Kalshi's own market data
- Volume-weighted aggregation
- Real-time prices

## Setup

### No API Keys Required!

The statistical system works entirely with:

- ✅ Kalshi API (free, no key needed)
- ✅ Historical data (built-in)
- ✅ Statistical models (built-in)

### Installation

```bash
pip3 install requests pandas numpy
```

## Running the Script

```bash
python3 politics_test.py
```

## Output Format

### Per-Market Analysis

```
📊 Analyzing: SENATEFL-28-R
   Title: Will Republicans win the Florida Senate race in 2028?
   State: FL
   Party: Republican
   Office: Senate
   🔵 Fetching Kalshi Consensus (Market Aggregation)...
      ✅ Kalshi Consensus: P=0.620, Markets=5, Vol=12500
   🟢 Fetching Historical Patterns (Statistical Model)...
      ✅ Historical Patterns (State): P=0.520
   🟡 Fetching Betting Model (Statistical)...
      ✅ Betting Model (Statistical): P=0.550
   📈 Combined: 0.563 (conf: 0.80)
   💰 Market: 0.855
   🎯 Edge: -29.2% (BUY NO)
```

## Advantages of Statistical Approach

1. **Objective**: No interpretation of text/sentiment
2. **Quantitative**: Based on numbers and data
3. **Historical**: Uses actual past outcomes
4. **Market-Based**: Uses real market prices
5. **Reproducible**: Same inputs → same outputs

## Limitations

1. **Historical Data**: May not reflect current political climate
2. **Market Consensus**: Requires multiple markets in same series
3. **State Coverage**: Only 20+ states in historical database
4. **Static Models**: Don't adapt to changing conditions
5. **No Polling**: Doesn't use real-time polling data (would require API)

## Future Statistical Enhancements

1. **Polling Aggregators**: Integrate RealClearPolitics, 538 (if APIs available)
2. **PredictIt Odds**: Add prediction market odds (statistical)
3. **Polymarket Odds**: Add crypto prediction market odds
4. **Time Series Models**: Use historical trends, not just averages
5. **Regression Models**: Machine learning on historical features
6. **Demographic Models**: Incorporate demographic data
7. **Economic Indicators**: GDP, unemployment, etc. correlated with elections

## Example Output

```
================================================================================
🗳️  POLITICS MARKET ANALYSIS - 3 SOURCE STATISTICAL SYSTEM
================================================================================

Sources (ALL STATISTICAL):
  1. Kalshi Market Consensus - Confidence: 70-85%
     (Volume-weighted average from other markets in same series)
  2. Historical Voting Patterns - Confidence: 65-75%
     (Statistical models based on past election results)
  3. Betting Market Model - Confidence: 70-85%
     (Statistical model with state/office/party adjustments)

================================================================================

✅ Found 25 open politics markets
================================================================================

📊 Analyzing: SENATEFL-28-R
   Title: Will Republicans win the Florida Senate race in 2028?
   State: FL
   Party: Republican
   Office: Senate
   🔵 Fetching Kalshi Consensus...
      ✅ Kalshi Consensus: P=0.620, Markets=5, Vol=12500
   🟢 Fetching Historical Patterns...
      ✅ Historical Patterns (State): P=0.520
   🟡 Fetching Betting Model...
      ✅ Betting Model (Statistical): P=0.550
   📈 Combined: 0.563 (conf: 0.80)
   💰 Market: 0.855
   🎯 Edge: -29.2% (BUY NO)

================================================================================
📈 RESULTS SUMMARY
================================================================================

ticker                        combined_p  market_p  edge_pct  sources  confidence
SENATEFL-28-R                 0.563       0.855     -29.2     3        0.80
...

================================================================================
📊 SUMMARY STATISTICS
================================================================================
Markets analyzed: 25
Average edge: -3.5%
Max edge: 29.2%
Markets with >8% edge: 12
Average sources per market: 2.8
Average confidence: 0.78
```

## Statistical vs Semantic

| Aspect              | Statistical (This System)            | Semantic (Old Approach)            |
| ------------------- | ------------------------------------ | ---------------------------------- |
| **Data**            | Numbers, prices, historical outcomes | Text, sentiment, keywords          |
| **Method**          | Mathematical aggregation             | Text analysis                      |
| **Sources**         | Markets, historical data, models     | News, social media, sentiment      |
| **Accuracy**        | Based on past performance            | Based on text interpretation       |
| **Bias**            | Less prone to interpretation bias    | Can be biased by wording           |
| **Reproducibility** | High (same inputs → same outputs)    | Lower (text interpretation varies) |

---

**Built for quantitative, statistical politics market analysis on Kalshi** 🗳️

**No sentiment analysis - pure statistics!**
