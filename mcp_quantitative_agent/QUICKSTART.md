# Quick Start Guide - Testing the MCP Server

## 🚀 Quick Test (5 minutes)

### Step 1: Test Standalone Agent

```bash
cd mcp_quantitative_agent
python quantitative_agent.py categories
```

If this works, the agent is functioning correctly!

### Step 2: Install MCP

```bash
pip install mcp
```

### Step 3: Run Test Script

```bash
python test_mcp.py
```

This will test all MCP tools automatically.

## 📋 Detailed Testing Steps

### 1. Test Standalone Agent

```bash
# Get categories
python quantitative_agent.py categories

# Analyze weather markets
python quantitative_agent.py analyze --category weather --limit 3 --json

# Analyze single market
python quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71 --json
```

### 2. Test MCP Server with Test Script

```bash
# Run the test script
python test_mcp.py
```

Expected output:

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

================================================================================
Test 1: get_market_categories
================================================================================
✓ Success
  Categories: 3
    - weather: 3 sources
    - politics: 3 sources
    - economics: 3 sources

...
```

### 3. Test with MCP Inspector (Visual Testing)

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
npx @modelcontextprotocol/inspector python server_simple.py
```

This opens a web interface where you can:

- See all available tools
- Call tools with parameters
- View results visually
- Debug issues

### 4. Integrate with Claude Desktop

1. **Find config file:**

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add MCP server config:**

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

   **Important:** Use absolute paths!

3. **Restart Claude Desktop**

4. **Test in Claude:**
   - "What market categories are available?"
   - "Analyze weather markets"
   - "Analyze the market KXHIGHNY-25NOV08-T71"

## 🔍 Troubleshooting

### Issue: "MCP library not installed"

```bash
pip install mcp
```

### Issue: "Module not found: weather_test"

Ensure test modules are in the parent directory:

- `../weather_test.py`
- `../politics_test.py`
- `../economics_test.py`

### Issue: "Server won't start"

```bash
# Check for syntax errors
python -m py_compile server_simple.py

# Test imports
python -c "from quantitative_agent import QuantitativeAgent; print('OK')"
```

### Issue: "Claude can't find server"

1. Check absolute paths in config
2. Verify Python is in PATH
3. Check file permissions
4. Restart Claude Desktop

## ✅ Success Checklist

- [ ] Standalone agent works
- [ ] MCP library installed
- [ ] Test script runs successfully
- [ ] All tools are available
- [ ] Tools return expected results
- [ ] Claude Desktop configured (optional)
- [ ] Claude can use tools (optional)

## 📚 Next Steps

- Read [TESTING.md](TESTING.md) for detailed testing instructions
- Read [SETUP.md](SETUP.md) for setup instructions
- Read [README.md](README.md) for usage guide

## 🆘 Need Help?

1. Check [TESTING.md](TESTING.md) for detailed troubleshooting
2. Verify all dependencies are installed
3. Test standalone agent first
4. Check server logs for errors
