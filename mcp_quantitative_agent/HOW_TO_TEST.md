# How to Test the MCP Server

## 🎯 Three Ways to Test

### 1. Quick Test (Recommended First)

Test the standalone agent to verify everything works:

```bash
cd mcp_quantitative_agent
python quantitative_agent.py categories
```

If this works, proceed to MCP testing!

### 2. Automated Test Script

Run the test script that tests all MCP tools:

```bash
python test_mcp.py
```

This will:

- ✅ Initialize the MCP server
- ✅ List all available tools
- ✅ Test each tool
- ✅ Show results

### 3. Manual MCP Testing

Use the MCP Inspector for visual testing:

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
npx @modelcontextprotocol/inspector python server_simple.py
```

## 📝 Step-by-Step Testing

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
pip install mcp
```

### Step 2: Test Standalone Agent

```bash
# Test categories
python quantitative_agent.py categories

# Test weather analysis
python quantitative_agent.py analyze --category weather --limit 2 --json
```

### Step 3: Test MCP Server

```bash
# Run automated test
python test_mcp.py
```

### Step 4: Test with Claude Desktop (Optional)

1. Edit Claude Desktop config:

   ```json
   {
     "mcpServers": {
       "quantitative-agent": {
         "command": "python",
         "args": ["/full/path/to/mcp_quantitative_agent/server_simple.py"],
         "cwd": "/full/path/to/mcp_quantitative_agent"
       }
     }
   }
   ```

2. Restart Claude Desktop

3. Ask Claude: "What market categories are available?"

## 🐛 Common Issues

### "MCP library not installed"

```bash
pip install mcp
```

### "Module not found: weather_test"

Make sure test modules are in parent directory:

- `../weather_test.py`
- `../politics_test.py`
- `../economics_test.py`

### "Server won't start"

```bash
# Check imports
python -c "from quantitative_agent import QuantitativeAgent; print('OK')"
```

## ✅ Expected Results

### Standalone Agent Test

```
Available Categories:

WEATHER:
  Sources: NOAA (GFS), Open-Meteo (ECMWF), Climatology
  ...

POLITICS:
  Sources: Kalshi Market Consensus, Historical Voting Patterns, Betting Market Model
  ...

ECONOMICS:
  Sources: FRED, Economic Indicators, Kalshi Market Consensus
  ...
```

### MCP Test Script

```
================================================================================
Testing MCP Quantitative Agent Server
================================================================================

Initializing MCP server...
✓ Server initialized

Fetching available tools...
✓ Found 5 tools:

  - analyze_weather_markets
  - analyze_politics_markets
  - analyze_economics_markets
  - analyze_single_market
  - get_market_categories

Test 1: get_market_categories
✓ Success
  Categories: 3
    - weather: 3 sources
    - politics: 3 sources
    - economics: 3 sources

...
```

## 📚 More Information

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [TESTING.md](TESTING.md) - Detailed testing instructions
- [SETUP.md](SETUP.md) - Setup guide
- [README.md](README.md) - Full documentation
