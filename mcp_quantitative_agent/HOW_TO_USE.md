# How to Use the Quantitative Agent

## 🚀 Quick Start

### From the project root directory:

```bash
# Make sure you're in the project root
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton

# Test 1: Get available categories
python3 mcp_quantitative_agent/quantitative_agent.py categories

# Test 2: Analyze weather markets (JSON output)
python3 mcp_quantitative_agent/quantitative_agent.py analyze --category weather --limit 3 --json

# Test 3: Analyze politics markets
python3 mcp_quantitative_agent/quantitative_agent.py analyze --category politics --limit 3 --json

# Test 4: Analyze economics markets
python3 mcp_quantitative_agent/quantitative_agent.py analyze --category economics --limit 3 --json

# Test 5: Analyze a single market
python3 mcp_quantitative_agent/quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71 --json
```

## 📋 All Available Commands

### 1. Get Categories

```bash
python3 mcp_quantitative_agent/quantitative_agent.py categories
```

### 2. Analyze Markets by Category

```bash
# Weather
python3 mcp_quantitative_agent/quantitative_agent.py analyze --category weather --limit 10

# Politics
python3 mcp_quantitative_agent/quantitative_agent.py analyze --category politics --limit 10

# Economics
python3 mcp_quantitative_agent/quantitative_agent.py analyze --category economics --limit 10

# With JSON output
python3 mcp_quantitative_agent/quantitative_agent.py analyze --category weather --limit 5 --json
```

### 3. Analyze Single Market

```bash
python3 mcp_quantitative_agent/quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71

# With JSON output
python3 mcp_quantitative_agent/quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71 --json
```

## 🧪 Test the MCP Server

### Option 1: Simple Test (Recommended First)

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton/mcp_quantitative_agent
python3 test_simple.py
```

### Option 2: MCP Inspector (Visual Testing)

1. **Install MCP Inspector:**

```bash
npm install -g @modelcontextprotocol/inspector
```

2. **Run Inspector:**

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton/mcp_quantitative_agent
npx @modelcontextprotocol/inspector python3 server_simple.py
```

3. **Use the Web Interface:**
   - Opens in your browser automatically
   - See all available tools
   - Call tools with parameters
   - View results visually

### Option 3: Integrate with Claude Desktop

1. **Find Claude Desktop Config:**

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add MCP Server Config:**

```json
{
  "mcpServers": {
    "quantitative-agent": {
      "command": "python3",
      "args": [
        "/Users/anshulmangalapalli/Documents/GitHub/hackprinceton/mcp_quantitative_agent/server_simple.py"
      ],
      "cwd": "/Users/anshulmangalapalli/Documents/GitHub/hackprinceton/mcp_quantitative_agent"
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test in Claude:**
   - "What market categories are available?"
   - "Analyze weather markets"
   - "Analyze the market KXHIGHNY-25NOV08-T71"

## 📊 Understanding the Output

### Categories Output

```
Available Categories:

WEATHER:
  Sources: NOAA (GFS), Open-Meteo (ECMWF), Climatology
  Methodology: Statistical/Quantitative methods only (no sentiment analysis)
```

### Analysis Output (JSON)

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
      "recommendation": "HOLD"
    }
  ]
}
```

### Trading Recommendations

- **BUY YES**: Edge > +8% (model probability much higher than market)
- **BUY NO**: Edge < -8% (model probability much lower than market)
- **HOLD**: -8% ≤ Edge ≤ +8% (no clear edge)

## 🔍 Troubleshooting

### "No such file or directory"

Make sure you're in the project root:

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton
```

### "No markets found"

This is normal if:

- Markets are closed for the season (weather)
- No active markets in that category
- Markets haven't opened yet

### "MCP library not installed"

```bash
pip3 install --break-system-packages mcp
```

### "Module not found: weather_test"

Make sure test modules are in parent directory:

```bash
ls weather_test.py politics_test.py economics_test.py
```

## ✅ Quick Test Checklist

- [ ] Run `python3 mcp_quantitative_agent/quantitative_agent.py categories`
- [ ] Run `python3 mcp_quantitative_agent/test_simple.py`
- [ ] (Optional) Install MCP Inspector and test server
- [ ] (Optional) Configure Claude Desktop

## 📚 More Information

- [TEST_COMMANDS.md](TEST_COMMANDS.md) - Quick command reference
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [TESTING.md](TESTING.md) - Detailed testing instructions
- [SETUP.md](SETUP.md) - Setup guide
