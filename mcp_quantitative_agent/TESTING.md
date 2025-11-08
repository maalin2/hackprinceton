# Testing the Quantitative Agent MCP Server

This guide will help you test the MCP server both as a standalone tool and as an MCP server.

## Prerequisites

1. Python 3.8+ installed
2. All dependencies installed
3. Test modules in parent directory

## Step 1: Install Dependencies

```bash
cd mcp_quantitative_agent
pip install -r requirements.txt
```

## Step 2: Test Standalone Agent (Recommended First Step)

Before testing MCP, verify the standalone agent works:

### Test 1: Get Categories

```bash
python quantitative_agent.py categories
```

Expected output:
```
Available Categories:

WEATHER:
  Sources: NOAA (GFS), Open-Meteo (ECMWF), Climatology
  Methodology: Statistical/Quantitative methods only (no sentiment analysis)

POLITICS:
  Sources: Kalshi Market Consensus, Historical Voting Patterns, Betting Market Model
  Methodology: Statistical/Quantitative methods only (no sentiment analysis)

ECONOMICS:
  Sources: FRED, Economic Indicators, Kalshi Market Consensus
  Methodology: Statistical/Quantitative methods only (no sentiment analysis)
```

### Test 2: Analyze Weather Markets (JSON)

```bash
python quantitative_agent.py analyze --category weather --limit 3 --json
```

This should return JSON with market analysis.

### Test 3: Analyze Single Market

```bash
# First, get a market ticker from the weather analysis above
python quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71 --json
```

## Step 3: Install MCP Library

```bash
pip install mcp
```

Verify installation:
```bash
python -c "import mcp; print('MCP installed successfully')"
```

## Step 4: Test MCP Server

### Test 4: Run MCP Server (Manual Test)

The MCP server communicates via STDIN/STDOUT. You can test it manually:

```bash
# Start the server
python server_simple.py
```

The server will wait for MCP protocol messages on STDIN.

### Test 5: Test MCP Server with Python Script

Create a test script to communicate with the MCP server:

```python
# test_mcp.py
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test the MCP server"""
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["server_simple.py"],
        env=None
    )
    
    # Create client session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test: Get categories
            print("\n=== Testing get_market_categories ===")
            result = await session.call_tool("get_market_categories", {})
            print(json.dumps(result.content, indent=2))
            
            # Test: Analyze weather markets
            print("\n=== Testing analyze_weather_markets ===")
            result = await session.call_tool("analyze_weather_markets", {"limit": 2})
            print(json.dumps(result.content, indent=2))

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
```

Run the test:
```bash
python test_mcp.py
```

## Step 5: Test with MCP Inspector (Recommended)

The MCP Inspector is a tool for testing MCP servers:

### Install MCP Inspector

```bash
npm install -g @modelcontextprotocol/inspector
```

### Run Inspector

```bash
npx @modelcontextprotocol/inspector python server_simple.py
```

This will open a web interface where you can:
- See available tools
- Call tools with parameters
- View results
- Debug issues

## Step 6: Integrate with Claude Desktop

### Step 6.1: Find Claude Desktop Config

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Step 6.2: Add MCP Server Configuration

Edit the config file and add:

```json
{
  "mcpServers": {
    "quantitative-agent": {
      "command": "python",
      "args": [
        "/full/path/to/mcp_quantitative_agent/server_simple.py"
      ],
      "cwd": "/full/path/to/mcp_quantitative_agent"
    }
  }
}
```

**Important:** Use absolute paths, not relative paths!

### Step 6.3: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. The MCP server should be available

### Step 6.4: Test in Claude

In Claude, you can now ask:
- "Analyze weather markets"
- "What are the available market categories?"
- "Analyze the market KXHIGHNY-25NOV08-T71"

## Step 7: Debugging

### Check Server Logs

If the server fails, check for errors:

```bash
# Run server directly to see errors
python server_simple.py
```

### Common Issues

1. **Import Errors**
   - Ensure test modules are in parent directory
   - Check Python path is correct

2. **MCP Not Found**
   - Install MCP: `pip install mcp`
   - Verify: `python -c "import mcp"`

3. **Server Not Starting**
   - Check file permissions
   - Verify Python path in config
   - Check for syntax errors

4. **Tools Not Available**
   - Verify server is running
   - Check MCP protocol version
   - Review server logs

## Step 8: Advanced Testing

### Test All Tools

Create a comprehensive test script:

```python
# test_all_tools.py
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_all_tools():
    """Test all MCP tools"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["server_simple.py"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test 1: Get categories
            print("Test 1: get_market_categories")
            result = await session.call_tool("get_market_categories", {})
            print(f"  Status: {result.content[0].text[:100]}...")
            
            # Test 2: Analyze weather markets
            print("Test 2: analyze_weather_markets")
            result = await session.call_tool("analyze_weather_markets", {"limit": 2})
            data = json.loads(result.content[0].text)
            print(f"  Status: {data.get('status')}")
            print(f"  Markets analyzed: {data.get('summary', {}).get('markets_analyzed', 0)}")
            
            # Test 3: Analyze politics markets
            print("Test 3: analyze_politics_markets")
            result = await session.call_tool("analyze_politics_markets", {"limit": 2})
            data = json.loads(result.content[0].text)
            print(f"  Status: {data.get('status')}")
            
            # Test 4: Analyze economics markets
            print("Test 4: analyze_economics_markets")
            result = await session.call_tool("analyze_economics_markets", {"limit": 2})
            data = json.loads(result.content[0].text)
            print(f"  Status: {data.get('status')}")
            
            # Test 5: Analyze single market
            print("Test 5: analyze_single_market")
            result = await session.call_tool("analyze_single_market", {"ticker": "KXHIGHNY-25NOV08-T71"})
            data = json.loads(result.content[0].text)
            print(f"  Status: {data.get('status')}")

if __name__ == "__main__":
    asyncio.run(test_all_tools())
```

Run:
```bash
python test_all_tools.py
```

## Quick Test Checklist

- [ ] Standalone agent works (`python quantitative_agent.py categories`)
- [ ] MCP library installed (`pip install mcp`)
- [ ] Server starts without errors (`python server_simple.py`)
- [ ] MCP Inspector can connect
- [ ] All tools are available
- [ ] Tools return expected results
- [ ] Claude Desktop configuration added
- [ ] Claude can use the tools

## Troubleshooting

### Server Won't Start

```bash
# Check for syntax errors
python -m py_compile server_simple.py

# Check imports
python -c "from quantitative_agent import QuantitativeAgent; print('OK')"
```

### Tools Return Errors

```bash
# Test standalone agent first
python quantitative_agent.py analyze --category weather --limit 1 --json

# If this works, the issue is with MCP, not the agent
```

### Claude Can't Find Server

1. Check absolute paths in config
2. Verify Python is in PATH
3. Check file permissions
4. Review Claude Desktop logs

## Next Steps

Once testing is complete:

1. **Use in Claude**: Ask Claude to analyze markets
2. **Monitor Performance**: Check response times
3. **Add More Tools**: Extend the agent as needed
4. **Optimize**: Improve performance based on usage

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop MCP Guide](https://claude.ai/docs/mcp)

