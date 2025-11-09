# What Happens When You Run server.py

## Overview

`server.py` is an **MCP (Model Context Protocol) Server** that exposes your quantitative analysis tools as AI-callable functions. This allows AI assistants (like Claude Desktop, Cline, etc.) to use your Kalshi analysis capabilities.

## What It Does

### 🚀 Primary Function

**Starts an MCP server** that makes your quantitative agent's analysis tools available to AI assistants through the Model Context Protocol.

### 🛠️ Available Tools (12 total)

When the server runs, it exposes these tools:

1. **`analyze_weather_markets_tool`**

   - Analyzes weather markets using NOAA, Open-Meteo, and Climatology
   - Returns edge calculations and recommendations

2. **`analyze_politics_markets_tool`**

   - Analyzes politics markets using Kalshi Consensus, Historical Patterns, and Betting Model
   - Returns probabilities and trading opportunities

3. **`analyze_economics_markets_tool`**

   - Analyzes economics markets using FRED, Economic Indicators, and Kalshi Consensus
   - Returns statistical arbitrage opportunities

4. **`analyze_single_market_tool`**

   - Analyzes any single market by ticker
   - Auto-detects category (weather/politics/economics)

5. **`get_market_categories_tool`**

   - Lists available categories and their sources
   - Shows methodology for each category

6. **`sentiment_analysis_tool`**

   - Analyzes Twitter sentiment using Grok (xAI)
   - Returns sentiment probability and confidence

7. **`get_markets_with_probabilities_tool`**

   - Fetches open markets with probability calculations
   - Returns implied probabilities from prices

8. **`analyze_market_volatility_tool`**

   - Analyzes price momentum and volatility
   - Returns volatility confidence score

9. **`analyze_market_volume_tool`**

   - Analyzes trading volume
   - Converts volume to confidence metric

10. **`greenlight_analysis_tool`**

    - Combines all signals for final decision
    - Returns BUY/SHORT/PASS with confidence

11. **`scan_categories_for_opportunities_tool`**

    - Scans multiple categories for top opportunities
    - Returns ranked list of best trades

12. **`get_kalshi_events_tool`**
    - Fetches current Kalshi events
    - Returns market data with probabilities

## How to Run It

### Option 1: Standard MCP Mode (stdio)

```bash
cd mcp_quantitative_agent
python server.py
```

**What happens**:

- ✅ Server starts in stdio (standard input/output) mode
- ✅ Waits for MCP messages from an AI client
- ✅ Responds to tool calls with analysis results
- ⚠️ No HTTP endpoint - only works with MCP clients

**Used by**: Claude Desktop, Cline, other MCP-compatible AI tools

### Option 2: HTTP Mode (for testing)

```bash
cd mcp_quantitative_agent
python server.py --http
```

**What happens**:

- ✅ Server starts with HTTP SSE transport
- ✅ Listens on http://localhost:8000
- ✅ Can receive HTTP requests
- ✅ Shows startup message with URL

**Output**:

```
🚀 MCP Quantitative Agent HTTP Server starting...
📡 Server will be available at: http://localhost:8000
📚 Available tools: scan_categories_for_opportunities, analyze_market_volume, greenlight_analysis, etc.
```

**Used by**: Testing, debugging, HTTP clients

## What You'll See

### When Starting (stdio mode):

```
(Server waits silently for MCP messages)
```

### When Starting (HTTP mode):

```
🚀 MCP Quantitative Agent HTTP Server starting...
📡 Server will be available at: http://localhost:8000
📚 Available tools: scan_categories_for_opportunities, analyze_market_volume, greenlight_analysis, etc.
```

### When Tools Are Called:

```
🔍 Fetching weather markets...
✅ Found 10 active weather markets (status=active, open for trading)
📊 Analyzing markets with statistical arbitrage...
[More analysis output...]
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   AI Assistant                          │
│           (Claude Desktop, Cline, etc.)                 │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ MCP Protocol
                  │
┌─────────────────▼───────────────────────────────────────┐
│                   server.py                             │
│              (MCP Server with 12 tools)                 │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
┌───────▼──┐ ┌───▼────┐ ┌──▼──────┐
│ weather  │ │politics│ │economics│
│ _test.py │ │_test.py│ │_test.py │
└──────────┘ └────────┘ └─────────┘
        │         │         │
        └─────────┼─────────┘
                  │
        ┌─────────▼─────────┐
        │  Kalshi API       │
        │  NOAA, FRED, etc. │
        └───────────────────┘
```

## Use Cases

### 1. Integrate with Claude Desktop

Configure Claude Desktop to use your quantitative agent:

```json
{
  "mcpServers": {
    "quantitative-agent": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

Now Claude can:

- Analyze weather markets
- Find political arbitrage opportunities
- Scan economics markets
- Get real-time Kalshi data

### 2. Use with Cline (VS Code Extension)

Add to your MCP config:

```json
{
  "servers": {
    "quantitative-agent": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/mcp_quantitative_agent"
    }
  }
}
```

Cline can now use your tools in VS Code.

### 3. HTTP Testing

```bash
# Start HTTP server
python server.py --http

# Test with curl
curl http://localhost:8000/tools
```

## What It Imports

The server imports your analysis modules:

- `weather_test.py` - Weather market analysis
- `politics_test.py` - Politics market analysis
- `economics_test.py` - Economics market analysis

And external APIs:

- Kalshi API (market data)
- NOAA (weather forecasts)
- FRED (economic data)
- Open-Meteo (weather forecasts)
- Alpha Vantage (economic indicators)

## Error Handling

If modules can't be imported:

```python
Warning: Could not import test modules: ModuleNotFoundError: No module named 'weather_test'
```

**Solution**: Run from the parent directory or ensure modules are in Python path.

## Environment Variables

The server reads from `.env`:

- `FRED_API_KEY` - For FRED economic data
- `ALPHA_VANTAGE_KEY` - For Alpha Vantage
- `XAI_API_KEY` - For Grok sentiment analysis (optional)

## When to Run It

### ✅ Run server.py when:

- You want to use quantitative analysis with AI assistants
- You're integrating with Claude Desktop
- You're using Cline or other MCP clients
- You want to expose analysis as callable tools

### ❌ DON'T run server.py when:

- You just want to analyze markets (use `weather_test.py`, etc. directly)
- You're running the Next.js dashboard (uses different system)
- You want a web UI (use dashboard instead)

## Comparison: server.py vs Dashboard

| Feature       | server.py                | Dashboard              |
| ------------- | ------------------------ | ---------------------- |
| **Purpose**   | MCP server for AI tools  | Web UI for traders     |
| **Interface** | stdio/HTTP               | Browser                |
| **Usage**     | AI assistants call tools | Users interact with UI |
| **Analysis**  | On-demand (when called)  | Auto-refresh (60s)     |
| **Best For**  | Claude Desktop, Cline    | Manual trading         |

## Testing the Server

### Test in HTTP Mode:

```bash
# Start server
cd mcp_quantitative_agent
python server.py --http

# In another terminal, test tools
python test_tools.py
```

### Test with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python server.py
```

## Troubleshooting

### "MCP not available"

**Problem**: `mcp` library not installed

**Solution**:

```bash
pip install mcp
```

### "Could not import test modules"

**Problem**: `weather_test.py`, etc. not found

**Solution**:

```bash
cd /path/to/hackprinceton
python mcp_quantitative_agent/server.py
```

### Server doesn't respond

**Problem**: Running in stdio mode but no MCP client connected

**Solution**: Use HTTP mode for testing:

```bash
python server.py --http
```

## Quick Reference

```bash
# Start MCP server (stdio)
python server.py

# Start HTTP server (testing)
python server.py --http

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python server.py

# Check available tools
# (In HTTP mode) curl http://localhost:8000/tools

# Run analysis directly (without server)
cd ..
python weather_test.py
```

## Summary

**server.py** is an **MCP server** that:

- ✅ Exposes 12 quantitative analysis tools
- ✅ Works with Claude Desktop, Cline, etc.
- ✅ Provides real-time Kalshi market analysis
- ✅ Supports stdio (MCP) and HTTP modes
- ✅ Integrates weather, politics, and economics analysis

**It does NOT**:

- ❌ Provide a web UI (use dashboard for that)
- ❌ Auto-refresh (only runs when called)
- ❌ Execute trades (analysis only)

---

**Related Files**:

- `quantitative_agent.py` - Standalone CLI tool
- `weather_test.py` - Weather analysis module
- `politics_test.py` - Politics analysis module
- `economics_test.py` - Economics analysis module
- `HOW_TO_USE.md` - Integration guide
- `HOW_TO_TEST.md` - Testing guide
