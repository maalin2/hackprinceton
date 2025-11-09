# Quantitative Agent - Summary

## What We Built

A **Quantitative Market Analysis Agent** that uses MCP (Model Context Protocol) to provide statistical/quantitative analysis for Kalshi markets. The agent analyzes three categories: Weather, Politics, and Economics.

## Key Components

### 1. Standalone Agent (`quantitative_agent.py`)

A Python CLI tool that can be used independently or integrated with MCP:

- **Categories Command**: List available market categories
- **Analyze Command**: Analyze markets in a category
- **Market Command**: Analyze a single market by ticker
- **JSON Output**: Machine-readable output format

### 2. MCP Server (`server_simple.py`)

An MCP server wrapper that exposes the quantitative agent as MCP tools:

- **analyze_weather_markets**: Analyze weather markets
- **analyze_politics_markets**: Analyze politics markets
- **analyze_economics_markets**: Analyze economics markets
- **analyze_single_market**: Analyze a single market
- **get_market_categories**: Get available categories

### 3. Quantitative Analysis Modules

Three test modules that provide statistical analysis:

- **weather_test.py**: 3 sources (NOAA, Open-Meteo, Climatology)
- **politics_test.py**: 3 sources (Market Consensus, Historical Patterns, Betting Model)
- **economics_test.py**: 3 sources (FRED, Economic Indicators, Market Consensus)

## Statistical Methodology

### ✅ What We Use (Statistical/Quantitative)

- Market prices (statistical aggregation)
- Economic data (official numbers)
- Historical patterns (statistical models)
- Mathematical models (Normal distribution, weighted averages)
- Trend analysis (time series)

### ❌ What We Don't Use (Semantic)

- Sentiment analysis
- Text analysis
- Keyword counting
- News sentiment
- Social media sentiment

## Usage Examples

### Standalone Mode

```bash
# Get categories
python mcp_quantitative_agent/quantitative_agent.py categories

# Analyze weather markets
python mcp_quantitative_agent/quantitative_agent.py analyze --category weather --limit 10

# Analyze single market
python mcp_quantitative_agent/quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71 --json
```

### MCP Mode

```bash
# Run MCP server
python mcp_quantitative_agent/server_simple.py
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

## Trading Recommendations

- **BUY YES**: Edge > +8% (model probability much higher than market)
- **BUY NO**: Edge < -8% (model probability much lower than market)
- **HOLD**: -8% ≤ Edge ≤ +8% (no clear edge)

## Files Created

```
mcp_quantitative_agent/
├── quantitative_agent.py      # Standalone agent (CLI)
├── server_simple.py           # MCP server wrapper
├── server.py                  # Full MCP server (legacy)
├── requirements.txt           # Dependencies
├── README.md                  # Usage guide
├── SETUP.md                   # Setup instructions
├── QUANTITATIVE_AGENT.md      # Detailed documentation
└── mcp.json                   # MCP configuration (example)
```

## Next Steps

1. **Test the Agent**: Run the standalone agent to verify it works
2. **Install MCP**: Install MCP library for full integration
3. **Configure AI Assistant**: Add MCP server to Claude Desktop or other MCP-compatible assistant
4. **Set API Keys**: Configure API keys for enhanced data sources
5. **Test Integration**: Test the agent with real market data

## Benefits

1. **Quantitative Focus**: Uses only statistical methods (no sentiment)
2. **Multiple Sources**: 3 sources per category with automatic fallback
3. **MCP Integration**: Can be used with AI assistants via MCP
4. **Standalone Mode**: Works without MCP as a CLI tool
5. **Extensible**: Easy to add new categories and sources

## License

MIT
