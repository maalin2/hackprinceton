# Dedalus Integration Setup Guide

This guide explains how to set up and deploy your Quantitative Agent MCP server on Dedalus.

## Prerequisites

1. **Dedalus Account**: Sign up at [Dedalus Labs](https://dedaluslabs.ai/)
2. **Project Structure**: Your MCP server is now Dedalus-compatible with the following structure:

```
mcp_quantitative_agent/
├── src/
│   └── main.py          # Main entry point (required by Dedalus)
├── requirements.txt     # Python dependencies
└── ...
```

## Local Testing

Before deploying to Dedalus, test your server locally:

### 1. Install Dependencies

```bash
cd mcp_quantitative_agent

# Install openmcp library (Dedalus-specific)
cd ../openmcp-python
pip install -e .
cd ../mcp_quantitative_agent

# Install project dependencies
pip install -r requirements.txt
```

### 2. Test the Server Locally

```bash
# Run the server (it will start on HTTP transport)
python src/main.py
```

The server should start and be accessible via HTTP. You can test it using curl or the MCP Inspector.

### 3. Using Dedalus SDK to Test

Create a test file `test_dedalus.py`:

```python
from dedalus import AsyncDedalus
import asyncio

async def test_quantitative_agent():
    client = AsyncDedalus(api_key="YOUR_DEDALUS_API_KEY")

    # Test getting market categories
    result = await client.tools.call(
        server="quantitative-agent",
        tool="get_market_categories"
    )
    print(result)

    # Test analyzing weather markets
    result = await client.tools.call(
        server="quantitative-agent",
        tool="analyze_weather_markets",
        arguments={"limit": 5}
    )
    print(result)

asyncio.run(test_quantitative_agent())
```

## Deploying to Dedalus

### Method 1: Using Dedalus CLI (Recommended)

1. **Install Dedalus CLI**:
   ```bash
   pip install dedalus-cli  # or npm install -g @dedalus/cli
   ```

2. **Login to Dedalus**:
   ```bash
   dedalus login
   ```

3. **Deploy Your MCP Server**:
   ```bash
   cd mcp_quantitative_agent
   dedalus deploy
   ```

4. **Your server is now live!** Dedalus will:
   - Automatically install dependencies from `requirements.txt`
   - Run `src/main.py` as the entry point
   - Handle autoscaling and load balancing
   - Provide a hosted endpoint

### Method 2: Using Dedalus Web Interface

1. **Navigate to Dedalus Dashboard**: https://app.dedaluslabs.ai/
2. **Click "Deploy MCP Server"**
3. **Upload your project or connect GitHub**:
   - If uploading: Zip the `mcp_quantitative_agent` folder (including `src/` directory)
   - If using GitHub: Connect your repository
4. **Configure deployment**:
   - Entry point: `src/main.py` (should be auto-detected)
   - Environment variables (if needed): Add any API keys
5. **Click "Deploy"**

## Using Your Deployed MCP Server

Once deployed, you can use your MCP server in Dedalus agents:

### Python Example

```python
from dedalus import AsyncDedalus
import asyncio

async def analyze_markets():
    client = AsyncDedalus(api_key="YOUR_DEDALUS_API_KEY")

    # Create an agent with access to your quantitative tools
    agent = client.agents.create(
        model="openai/gpt-4.1",
        servers=["quantitative-agent"]  # Your deployed MCP server
    )

    # Ask the agent to analyze markets
    response = await agent.chat(
        "Analyze the top 5 weather markets and tell me which ones have good trading opportunities"
    )

    print(response)

asyncio.run(analyze_markets())
```

### TypeScript Example

```typescript
import { AsyncDedalus } from '@dedalus/sdk';

async function analyzeMarkets() {
  const client = new AsyncDedalus({ apiKey: process.env.DEDALUS_API_KEY });

  // Create an agent with access to your quantitative tools
  const agent = await client.agents.create({
    model: 'openai/gpt-4.1',
    servers: ['quantitative-agent']
  });

  // Ask the agent to analyze markets
  const response = await agent.chat(
    'Analyze the top 5 weather markets and tell me which ones have good trading opportunities'
  );

  console.log(response);
}

analyzeMarkets();
```

## Available Tools

Your MCP server exposes the following tools:

1. **analyze_weather_markets** - Analyze weather markets using 3 statistical sources
   - Parameters: `limit` (integer, default: 10)

2. **analyze_politics_markets** - Analyze politics markets using 3 statistical sources
   - Parameters: `limit` (integer, default: 10)

3. **analyze_economics_markets** - Analyze economics markets using 3 statistical sources
   - Parameters: `limit` (integer, default: 10)

4. **analyze_single_market** - Analyze a single market by ticker
   - Parameters: `ticker` (string, required)

5. **get_market_categories** - Get available categories and their quantitative sources
   - Parameters: none

## Environment Variables

If your analysis modules need API keys, set them as environment variables in Dedalus:

- `FRED_API_KEY` - For FRED economic data
- `ALPHA_VANTAGE_API_KEY` - For Alpha Vantage data
- `BLS_API_KEY` - For Bureau of Labor Statistics data
- `VISUAL_CROSSING_API_KEY` - For weather data (optional)

## Monitoring and Logs

Access logs and monitoring through the Dedalus dashboard:
- View request/response logs
- Monitor performance metrics
- Set up alerts for errors
- Track usage and costs

## Troubleshooting

### "Module not found" errors

Ensure all parent modules (`weather_test.py`, `politics_test.py`, `economics_test.py`) are included in your deployment. You may need to:

1. Copy them into the `mcp_quantitative_agent` directory, or
2. Include them in your repository structure, or
3. Package them as a proper Python module

### API key errors

Make sure API keys are set as environment variables in the Dedalus dashboard, not hardcoded in your files.

### Server won't start

Check the logs in Dedalus dashboard for specific error messages. Common issues:
- Missing dependencies in `requirements.txt`
- Import errors (missing modules)
- Syntax errors in `src/main.py`

## Example Use Cases

### 1. Automated Market Analysis Bot

```python
from dedalus import AsyncDedalus
import asyncio

async def daily_analysis():
    client = AsyncDedalus(api_key=os.getenv("DEDALUS_API_KEY"))
    agent = client.agents.create(
        model="openai/gpt-4.1",
        servers=["quantitative-agent"]
    )

    # Analyze all categories
    response = await agent.chat("""
        Analyze the top 10 markets in each category (weather, politics, economics).
        For each category:
        1. Identify markets with >8% edge
        2. Explain the quantitative reasoning
        3. Provide trading recommendations
        Format as a daily report.
    """)

    return response

# Run daily at 9 AM
asyncio.run(daily_analysis())
```

### 2. Specific Market Deep Dive

```python
async def analyze_specific_market(ticker: str):
    client = AsyncDedalus(api_key=os.getenv("DEDALUS_API_KEY"))
    agent = client.agents.create(
        model="openai/gpt-4.1",
        servers=["quantitative-agent"]
    )

    response = await agent.chat(f"""
        Analyze the market {ticker} in detail:
        1. What are the probabilities from each source?
        2. What's the current market price?
        3. Is there a trading opportunity?
        4. What's the confidence level?
        5. Should I trade this market?
    """)

    return response
```

### 3. Portfolio Management

```python
async def manage_portfolio(holdings: list[str]):
    client = AsyncDedalus(api_key=os.getenv("DEDALUS_API_KEY"))
    agent = client.agents.create(
        model="openai/gpt-4.1",
        servers=["quantitative-agent"]
    )

    response = await agent.chat(f"""
        I hold positions in these markets: {', '.join(holdings)}

        For each market:
        1. Analyze current edge
        2. Recommend: hold, add, or exit position
        3. Identify any risk factors

        Also suggest 3 new markets with the best opportunities.
    """)

    return response
```

## Next Steps

1. **Deploy your server** using one of the methods above
2. **Test it** using the Dedalus SDK
3. **Build agents** that use your quantitative analysis tools
4. **Monitor performance** through the Dedalus dashboard
5. **Scale automatically** as your usage grows

## Support

- **Dedalus Docs**: https://docs.dedaluslabs.ai/
- **Dedalus Discord**: Join the community
- **Email**: support@dedaluslabs.ai

## License

MIT
