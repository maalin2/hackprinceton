# Quantitative Agent Setup Guide

This guide explains how to set up and use the Quantitative Market Analysis Agent.

## Overview

The Quantitative Agent provides statistical/quantitative analysis for Kalshi markets across three categories:

- **Weather**: NOAA, Open-Meteo, Climatology
- **Politics**: Market Consensus, Historical Patterns, Betting Model
- **Economics**: FRED, Economic Indicators, Market Consensus

## Installation

### 1. Install Dependencies

```bash
cd mcp_quantitative_agent
pip install -r requirements.txt
```

### 2. Verify Test Modules

Ensure the following files exist in the parent directory:

- `weather_test.py`
- `politics_test.py`
- `economics_test.py`

### 3. (Optional) Install MCP Library

For MCP integration:

```bash
pip install mcp
```

If MCP is not installed, the agent will work in standalone mode.

## Usage

### Standalone Mode (CLI)

The agent can be used as a CLI tool:

#### Get Available Categories

```bash
python quantitative_agent.py categories
```

#### Analyze Weather Markets

```bash
python quantitative_agent.py analyze --category weather --limit 10
```

#### Analyze Politics Markets

```bash
python quantitative_agent.py analyze --category politics --limit 10
```

#### Analyze Economics Markets

```bash
python quantitative_agent.py analyze --category economics --limit 10
```

#### Analyze Single Market

```bash
python quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71
```

#### JSON Output

```bash
python quantitative_agent.py analyze --category weather --limit 5 --json
```

### MCP Mode

If MCP is installed, you can run the MCP server:

```bash
python server.py
```

The server will communicate via STDIN/STDOUT using the MCP protocol.

## API Keys (Optional)

### Economics Markets

Set API keys in `economics_test.py`:

- **FRED API Key**: Get from https://fred.stlouisfed.org/docs/api/api_key.html
- **Alpha Vantage Key**: Get from https://www.alphavantage.co/support/#api-key
- **BLS API Key**: Register at https://www.bls.gov/developers/api_signature.htm

### Weather Markets

- **Visual Crossing API Key** (optional): Set in `weather_test.py`

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

### Trading Recommendations

- **BUY YES**: Edge > +8% (model probability much higher than market)
- **BUY NO**: Edge < -8% (model probability much lower than market)
- **HOLD**: -8% ≤ Edge ≤ +8% (no clear edge)

## Integration with AI Assistants

### Claude (Anthropic)

To use with Claude Desktop, add to your MCP configuration:

```json
{
  "mcpServers": {
    "quantitative-agent": {
      "command": "python",
      "args": ["/path/to/mcp_quantitative_agent/server.py"],
      "cwd": "/path/to/mcp_quantitative_agent"
    }
  }
}
```

### Other MCP-Compatible Assistants

The agent follows the MCP protocol and can be integrated with any MCP-compatible assistant.

## Methodology

All analysis uses **statistical/quantitative methods only**:

✅ **What We Use:**

- Market prices (statistical aggregation)
- Economic data (official numbers)
- Historical patterns (statistical models)
- Mathematical models (Normal distribution, weighted averages)

❌ **What We Don't Use:**

- Sentiment analysis
- Text analysis
- Keyword counting
- News sentiment

## Troubleshooting

### Module Import Errors

If you get import errors, ensure:

1. Test modules are in the parent directory
2. All dependencies are installed
3. Python path is correct

### No Markets Found

If no markets are found:

- Markets may be closed for the season (weather)
- Markets may not be active (politics/economics)
- Check Kalshi website for active markets

### API Key Errors

If API calls fail:

- Check API keys are set correctly
- Verify API key permissions
- Check rate limits
- The agent will fall back to other sources if one fails

## Examples

### Example 1: Analyze Weather Markets

```bash
python quantitative_agent.py analyze --category weather --limit 5
```

Output:

```
Category: WEATHER
Sources: NOAA (GFS), Open-Meteo (ECMWF), Climatology

Summary:
  Markets Analyzed: 5
  Average Edge: 3.2%
  Max Edge: 12.5%
  Markets with >8% Edge: 1
  Average Confidence: 0.78

Markets:
  KXHIGHNY-25NOV08-T71: Will NYC high temp be >71°F on Nov 8, 2025?
    Edge: +12.5% | Recommendation: BUY YES
    Sources: NOAA: 0.650, Open-Meteo: 0.620, Climatology: 0.600
```

### Example 2: Analyze Single Market (JSON)

```bash
python quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71 --json
```

## License

MIT
