# Volume-Based Real-Time Market Fetching

## Overview

All market fetching functions now:

1. ✅ **Filter for ACTIVE markets only** (`status="active"` - open for trading in real-time)
2. ✅ **Sort by volume** (24h volume, highest first)
3. ✅ **Include volume data** in output for transparency

## What Changed

### All Category Scripts Updated

- `weather_test.py` - Weather markets
- `politics_test.py` - Politics markets
- `economics_test.py` - Economics markets

### New Function Signature

```python
def get_open_{category}_markets(sort_by_volume=True, limit=50):
    """
    Fetch open markets from Kalshi in real-time.

    Args:
        sort_by_volume: If True, sort by 24h volume (highest first)
        limit: Maximum number of markets to return

    Returns:
        DataFrame with open markets sorted by volume
    """
```

### Key Features

1. **Real-Time Filtering**

   - Only markets with `status="active"` (currently open for trading)
   - Excludes closed, settled, or paused markets

2. **Volume-Based Sorting**

   - Primary: `volume_24h` (24-hour trading volume)
   - Fallback: `volume` (total volume)
   - Highest volume first (most liquid/active markets)

3. **Volume Data in Output**
   - `volume_24h`: Trading volume in last 24 hours
   - `volume`: Total trading volume
   - `open_interest`: Current open positions

## Usage

### Basic Usage (Default: Sorted by Volume)

```python
import weather_test

# Get top 10 weather markets by volume
df = weather_test.get_open_weather_markets(limit=10)
```

### Disable Volume Sorting

```python
# Get markets without volume sorting
df = weather_test.get_open_weather_markets(sort_by_volume=False, limit=10)
```

### Custom Limit

```python
# Get top 50 markets by volume
df = weather_test.get_open_weather_markets(limit=50)
```

## Example Output

```
Testing Updated Volume-Based Market Fetching
================================================================================

Fetching weather markets (sorted by volume)...
--------------------------------------------------------------------------------
📊 Sorted by 24h volume (highest volume first)
✅ Found 5 active weather markets (status=active, open for trading)

Top 5 Weather Markets by Volume:
--------------------------------------------------------------------------------
KXHIGHCHI-25NOV08-B48.5
  Title: Will the high temp in Chicago be 48-49° on Nov 8, ...
  Volume (24h): 48,425
  Volume (Total): 48,472
  Open Interest: 44,106

KXHIGHCHI-25NOV08-T48
  Title: Will the high temp in Chicago be <48° on Nov 8, 20...
  Volume (24h): 42,078
  Volume (Total): 42,345
  Open Interest: 40,223

KXHIGHMIA-25NOV08-B84.5
  Title: Will the **high temp in Miami** be 84-85° on Nov 8...
  Volume (24h): 22,892
  Volume (Total): 24,241
  Open Interest: 19,560
```

## Why Volume Matters

### High Volume = Better Markets

1. **Liquidity**: Easier to enter/exit positions
2. **Tighter Spreads**: Smaller bid-ask spread
3. **Price Discovery**: More efficient pricing
4. **Lower Slippage**: Better execution
5. **Active Interest**: Real-time trading activity

### Volume Metrics

- **`volume_24h`**: Recent activity (best for identifying hot markets)
- **`volume`**: Total historical activity
- **`open_interest`**: Current outstanding positions

## Testing

### Test Weather Markets

```bash
python3 -c "
import weather_test
df = weather_test.get_open_weather_markets(limit=5)
print(df[['ticker', 'volume_24h', 'volume']].head())
"
```

### Test Politics Markets

```bash
python3 -c "
import politics_test
df = politics_test.get_open_politics_markets(limit=5)
print(df[['ticker', 'volume_24h', 'volume']].head())
"
```

### Test Economics Markets

```bash
python3 -c "
import economics_test
df = economics_test.get_open_economics_markets(limit=5)
print(df[['ticker', 'volume_24h', 'volume']].head())
"
```

## Integration with Quantitative Agent

The quantitative agent automatically uses these updated functions:

```python
from mcp_quantitative_agent.quantitative_agent import QuantitativeAgent

agent = QuantitativeAgent()

# Analyze top weather markets (sorted by volume)
result = agent.analyze_category("weather", limit=10)

# Markets will be sorted by volume automatically
for market in result["markets"]:
    print(f"{market['ticker']}: Edge={market['edge_pct']}%")
```

## Benefits

### Before (Random Order)

```
KXHIGHNY-25NOV09-B66.5    Volume: 127
KXHIGHNY-25NOV09-T59      Volume: 1,234
KXHIGHNY-25NOV09-B61.5    Volume: 456
```

### After (Volume Sorted)

```
KXHIGHCHI-25NOV08-B48.5   Volume: 48,425  ⬅️ Highest liquidity
KXHIGHCHI-25NOV08-T48     Volume: 42,078  ⬅️ Second highest
KXHIGHMIA-25NOV08-B84.5   Volume: 22,892  ⬅️ Third highest
```

## Real-Time Updates

Markets are fetched in real-time:

- ✅ Only `status="active"` markets
- ✅ Current volume data
- ✅ Live prices (bid/ask/last)
- ✅ Current open interest

## Status Field Values

- **`active`**: Market is open for trading (✅ We want this)
- **`closed`**: Market closed, no longer trading (❌ Filtered out)
- **`settled`**: Market resolved, final outcome determined (❌ Filtered out)
- **`finalized`**: Market completely finished (❌ Filtered out)

## Performance

- **API Calls**: ~20-30 calls per category (series + markets)
- **Execution Time**: 5-15 seconds per category
- **Markets Returned**: Up to `limit` (default: 50)

## DataFrame Columns

All market DataFrames include:

| Column          | Type | Description                                   |
| --------------- | ---- | --------------------------------------------- |
| `ticker`        | str  | Market ticker (e.g., KXHIGHCHI-25NOV08-B48.5) |
| `title`         | str  | Market question/title                         |
| `yes_bid`       | int  | Current bid price for YES (cents)             |
| `yes_ask`       | int  | Current ask price for YES (cents)             |
| `last_price`    | int  | Last traded price (cents)                     |
| `volume_24h`    | int  | Trading volume in last 24 hours               |
| `volume`        | int  | Total trading volume                          |
| `open_interest` | int  | Current open positions                        |
| `series`        | str  | Series ticker (e.g., KXHIGHCHI)               |

## Next Steps

With volume-based sorting, the quantitative agent now:

1. ✅ Fetches most liquid markets first
2. ✅ Analyzes markets with best execution
3. ✅ Prioritizes markets with real trading activity
4. ✅ Identifies arbitrage opportunities on high-volume markets

This ensures all analysis is focused on markets where you can actually trade!
