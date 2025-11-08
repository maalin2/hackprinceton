# Quick Test Commands

## ✅ Verified Working Commands

### 1. Test Standalone Agent

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton/mcp_quantitative_agent
python3 quantitative_agent.py categories
```

### 2. Run Simple Tests

```bash
python3 test_simple.py
```

### 3. Test MCP Server with Inspector (Recommended)

First, install the MCP Inspector:

```bash
npm install -g @modelcontextprotocol/inspector
```

Then run:

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton/mcp_quantitative_agent
npx @modelcontextprotocol/inspector python3 server_simple.py
```

This will open a web interface where you can test all the MCP tools.

### 4. Test Standalone Agent Functions

```bash
# Get categories
python3 quantitative_agent.py categories

# Analyze weather markets
python3 quantitative_agent.py analyze --category weather --limit 3 --json

# Analyze politics markets
python3 quantitative_agent.py analyze --category politics --limit 3 --json

# Analyze economics markets
python3 quantitative_agent.py analyze --category economics --limit 3 --json

# Analyze single market
python3 quantitative_agent.py market --ticker KXHIGHNY-25NOV08-T71 --json
```

## 🔧 Troubleshooting

### If you get "No such file or directory"

Make sure you're in the correct directory:

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton/mcp_quantitative_agent
```

### If you get "MCP library not installed"

```bash
pip3 install --break-system-packages mcp
```

### If you get "Module not found: weather_test"

Make sure the test modules are in the parent directory:

```bash
ls ../weather_test.py ../politics_test.py ../economics_test.py
```

## 📝 Correct Paths

- **Working Directory**: `/Users/anshulmangalapalli/Documents/GitHub/hackprinceton/mcp_quantitative_agent`
- **Test Script**: `test_simple.py`
- **Server Script**: `server_simple.py`
- **Standalone Agent**: `quantitative_agent.py`

## 🎯 Next Steps After Testing

1. **Test with MCP Inspector** (easiest visual testing)
2. **Integrate with Claude Desktop** (see SETUP.md)
3. **Use in production** (all tests pass!)
