# Quantitative Market Analysis Agent (MCP Server)

An MCP (Model Context Protocol) server that exposes quantitative analysis tools for Kalshi markets. This agent uses **only statistical/quantitative methods** (no sentiment analysis) to analyze weather, politics, and economics markets.

## Features

### 3 Quantitative Sources Per Category

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

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure the parent directory contains the test modules:
   - `weather_test.py`
   - `politics_test.py`
   - `economics_test.py`

## Usage

### Standalone Mode (Recommended for Testing)

The agent can be used as a standalone CLI tool without MCP:

```bash
# Get available categories
python quantitative_agent.py categories

# Analyze weather markets
python quantitative_agent.py analyze --category weather --limit 10

# Analyze single market
python quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71

# JSON output
python quantitative_agent.py analyze --category weather --limit 5 --json
```

### MCP Server Mode

If MCP is installed, you can run the MCP server:

```bash
python server_simple.py
```

The server communicates via STDIN/STDOUT using the MCP protocol.

### Available Tools

1. **analyze_weather_markets** - Analyze weather markets using 3 statistical sources
2. **analyze_politics_markets** - Analyze politics markets using 3 statistical sources
3. **analyze_economics_markets** - Analyze economics markets using 3 statistical sources
4. **analyze_single_market** - Analyze a single market by ticker
5. **get_market_categories** - Get available categories and their quantitative sources

### Example Usage

#### Analyze Weather Markets

```json
{
  "tool": "analyze_weather_markets",
  "arguments": {
    "limit": 10
  }
}
```

#### Analyze Single Market

```json
{
  "tool": "analyze_single_market",
  "arguments": {
    "ticker": "KXHIGHNY-25NOV08-T71"
  }
}
```

#### Get Market Categories

```json
{
  "tool": "get_market_categories",
  "arguments": {}
}
```

## Output Format

### Market Analysis Result

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

### Trading Recommendations

- **BUY YES**: Edge > +8% (model probability much higher than market)
- **BUY NO**: Edge < -8% (model probability much lower than market)
- **HOLD**: -8% ≤ Edge ≤ +8% (no clear edge)

## Configuration

### API Keys (Optional but Recommended)

Set API keys in the respective test modules:

- **FRED API Key** (for economics): Set in `economics_test.py`
- **Alpha Vantage Key** (for economics): Set in `economics_test.py`
- **BLS API Key** (for economics): Set in `economics_test.py`

See individual test module documentation for API key setup.

## Architecture

```
mcp_quantitative_agent/
├── server.py              # MCP server implementation
├── requirements.txt       # Python dependencies
└── README.md             # This file

../                         # Parent directory
├── weather_test.py        # Weather analysis module
├── politics_test.py       # Politics analysis module
└── economics_test.py      # Economics analysis module
```

## Methodology

All analysis uses **statistical/quantitative methods only**:

- ✅ Market prices (statistical aggregation)
- ✅ Economic data (official numbers)
- ✅ Historical patterns (statistical models)
- ✅ Mathematical models (Normal distribution, weighted averages)
- ❌ No sentiment analysis
- ❌ No text analysis
- ❌ No keyword counting

## Error Handling

The server handles various error conditions:

- Missing modules: Returns error if test modules are not available
- No markets: Returns appropriate status when no markets found
- Analysis failures: Returns error with details
- Market not found: Returns not_found status

## Integration with AI Assistants

This MCP server can be integrated with AI assistants that support MCP, such as:

- Claude (Anthropic)
- Other MCP-compatible assistants

The server exposes quantitative analysis tools that can be called by the AI assistant to perform market analysis.

## License

MIT
