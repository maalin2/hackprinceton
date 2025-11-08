# Quantitative Market Analysis Agent

## Overview

A quantitative agent for analyzing Kalshi markets using **statistical/quantitative methods only** (no sentiment analysis). The agent provides analysis across three categories: Weather, Politics, and Economics.

## Architecture

```
mcp_quantitative_agent/
├── quantitative_agent.py    # Standalone agent (CLI)
├── server_simple.py         # MCP server wrapper
├── server.py                # Full MCP server (legacy)
├── requirements.txt         # Dependencies
├── README.md               # Usage guide
├── SETUP.md                # Setup instructions
└── QUANTITATIVE_AGENT.md   # This file

../                         # Parent directory
├── weather_test.py         # Weather analysis module
├── politics_test.py        # Politics analysis module
└── economics_test.py       # Economics analysis module
```

## Key Features

### 1. Three Quantitative Sources Per Category

**Weather Markets:**

- NOAA (GFS Model) - Confidence: 85%
- Open-Meteo (ECMWF Model) - Confidence: 80%
- Climatology (Historical Averages) - Confidence: 70%

**Politics Markets:**

- Kalshi Market Consensus - Confidence: 70-85%
- Historical Voting Patterns - Confidence: 65-75%
- Betting Market Model - Confidence: 70-85%

**Economics Markets:**

- FRED (Federal Reserve) - Confidence: 85%
- Economic Indicators (Alpha Vantage/BLS/World Bank) - Confidence: 60-85%
- Kalshi Market Consensus - Confidence: 70-85%

### 2. Statistical Methodology

All analysis uses **only statistical/quantitative methods**:

✅ **What We Use:**

- Market prices (statistical aggregation)
- Economic data (official numbers)
- Historical patterns (statistical models)
- Mathematical models (Normal distribution, weighted averages)
- Trend analysis (time series)

❌ **What We Don't Use:**

- Sentiment analysis
- Text analysis
- Keyword counting
- News sentiment
- Social media sentiment

### 3. Trading Recommendations

- **BUY YES**: Edge > +8% (model probability much higher than market)
- **BUY NO**: Edge < -8% (model probability much lower than market)
- **HOLD**: -8% ≤ Edge ≤ +8% (no clear edge)

## Usage

### Standalone Mode (CLI)

```bash
# Get categories
python quantitative_agent.py categories

# Analyze weather markets
python quantitative_agent.py analyze --category weather --limit 10

# Analyze politics markets
python quantitative_agent.py analyze --category politics --limit 10

# Analyze economics markets
python quantitative_agent.py analyze --category economics --limit 10

# Analyze single market
python quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71

# JSON output
python quantitative_agent.py analyze --category weather --limit 5 --json
```

### MCP Server Mode

```bash
# Run MCP server (requires MCP library)
python server_simple.py
```

## Output Format

### Analysis Result

```json
{
  "status": "success",
  "category": "weather",
  "sources": ["NOAA (GFS)", "Open-Meteo (ECMWF)", "Climatology"],
  "summary": {
    "markets_analyzed": 10,
    "average_edge": 5.2,
    "max_edge": 15.3,
    "markets_with_edge_gt_8": 3,
    "average_confidence": 0.78
  },
  "markets": [
    {
      "ticker": "KXHIGHNY-25NOV08-T71",
      "title": "Will NYC high temp be >71°F on Nov 8, 2025?",
      "combined_p": 0.623,
      "market_p": 0.55,
      "edge": 0.073,
      "edge_pct": 7.3,
      "sources": 3,
      "confidence": 0.8,
      "source_breakdown": "NOAA: 0.650, Open-Meteo: 0.620, Climatology: 0.600",
      "recommendation": "HOLD"
    }
  ]
}
```

## Integration

### With AI Assistants (MCP)

The agent can be integrated with MCP-compatible AI assistants:

1. Install MCP library: `pip install mcp`
2. Configure MCP server in assistant settings
3. Use tools via MCP protocol

### As a Library

```python
from quantitative_agent import QuantitativeAgent

agent = QuantitativeAgent()

# Analyze category
result = agent.analyze_category("weather", limit=10)

# Analyze single market
result = agent.analyze_single_market("KXHIGHNY-25NOV08-T71")

# Get categories
categories = agent.get_categories()
```

## API Keys

### Optional (for enhanced data)

- **FRED API Key**: Set in `economics_test.py`
- **Alpha Vantage Key**: Set in `economics_test.py`
- **BLS API Key**: Set in `economics_test.py`
- **Visual Crossing Key**: Set in `weather_test.py`

The agent works without API keys but will use fallback sources.

## Methodology

### Probability Calculation

1. **Fetch Data**: Get data from 3 statistical sources
2. **Calculate Probabilities**: Convert data to probabilities using statistical models
3. **Weighted Average**: Combine probabilities using confidence-weighted average
4. **Edge Calculation**: Compare model probability to market probability
5. **Recommendation**: Generate trading recommendation based on edge

### Statistical Models

- **Normal Distribution**: For economic indicators and weather forecasts
- **Weighted Average**: For combining multiple sources
- **Trend Analysis**: For forecasting future values
- **Historical Patterns**: For politics and economics

## Advantages

1. **Objective**: No interpretation bias
2. **Quantitative**: Based on numbers and data
3. **Reproducible**: Same inputs → same outputs
4. **Multiple Sources**: Redundant data sources with automatic fallback
5. **Statistical Rigor**: Uses established statistical methods

## Limitations

1. **Historical Data**: May not reflect current conditions
2. **Market Consensus**: Requires multiple markets in same series
3. **API Dependencies**: Some sources require API keys
4. **Forecast Accuracy**: Simple models may not capture all factors
5. **Data Availability**: Markets may not be available at all times

## Future Enhancements

1. **Advanced Time Series Models**: ARIMA, Prophet, LSTM
2. **Machine Learning**: Train models on historical data
3. **More Data Sources**: Additional APIs and data providers
4. **Real-time Updates**: WebSocket integration for live data
5. **Portfolio Analysis**: Multi-market portfolio optimization

## License

MIT
