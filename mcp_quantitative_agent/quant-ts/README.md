# Quant-TS - Quantitative Market Analysis MCP Server

A TypeScript-based Model Context Protocol (MCP) server for quantitative analysis of Kalshi prediction markets.

## Features

- **5 MCP Tools** for market analysis:
  - `get_market_categories` - List available categories and data sources
  - `analyze_weather_markets` - Analyze weather markets with statistical sources
  - `analyze_politics_markets` - Analyze politics markets
  - `analyze_economics_markets` - Analyze economics markets
  - `analyze_single_market` - Deep dive on specific market ticker

- **Dual Transport Support**:
  - STDIO (default) - For Dedalus and MCP clients
  - HTTP/SSE - For testing and production deployments

## Quick Start

```bash
# Install dependencies
npm install

# Build
npm run build

# Run with STDIO (for Dedalus)
npm start

# Run with HTTP (for testing)
npm start -- --http
```

## Usage

### STDIO Transport (Default)

For Dedalus and MCP clients:

```bash
npm start
# or
npm start -- --stdio
```

### HTTP Transport

For testing and production:

```bash
# Default port 8000
npm start -- --http

# Custom port
npm start -- --http --port 3000
```

**Health Check:**
```bash
curl http://localhost:8000/health
```

## Dedalus Integration

1. **Configure MCP Server** in `~/.config/dedalus/mcp.json`:

```json
{
  "mcpServers": {
    "quant-ts": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "/home/mo/hackprinceton/quant-ts"
    }
  }
}
```

2. **Create Dedalus Agent:**

```typescript
import { AsyncDedalus, DedalusRunner } from 'dedalus_labs';

const client = new AsyncDedalus();
const runner = new DedalusRunner(client);

const result = await runner.run({
  input: "Analyze the top 5 weather markets",
  model: "anthropic/claude-sonnet-4-5-20250929",
  mcp_servers: ["quant-ts"],
  stream: false
});

console.log(result.final_output);
```

## Project Structure

```
quant-ts/
├── src/
│   ├── index.ts           # Main entry point
│   ├── cli.ts             # CLI argument parsing
│   ├── config.ts          # Configuration
│   ├── server.ts          # MCP server instance
│   ├── client.ts          # Kalshi API client
│   ├── types.ts           # TypeScript types
│   ├── tools/
│   │   ├── index.ts       # Tool exports
│   │   └── markets.ts     # Market analysis tools
│   └── transport/
│       ├── index.ts       # Transport exports
│       ├── http.ts        # HTTP/SSE transport
│       └── stdio.ts       # STDIO transport
├── dist/                  # Built JavaScript
├── package.json
├── tsconfig.json
└── .env
```

## Environment Variables

Create a `.env` file:

```bash
# Port for HTTP transport
PORT=8000

# Kalshi API
KALSHI_BASE_URL=https://api.elections.kalshi.com/trade-api/v2
REQUEST_TIMEOUT=15000

# Optional API Keys
CLAUDE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Available Tools

### 1. get_market_categories

Get list of available market categories and their quantitative sources.

**Input:** None

**Output:**
```json
{
  "categories": [
    {
      "name": "weather",
      "sources": ["NOAA (GFS)", "Open-Meteo (ECMWF)", "Climatology"],
      "confidence": "70-85%",
      "indicators": ["Temperature", "Precipitation", "Weather Events"]
    }
  ]
}
```

### 2. analyze_weather_markets

Analyze weather markets using 3 statistical sources.

**Input:**
- `limit` (number, optional): Max markets to analyze (default: 10)

**Output:**
```json
{
  "status": "success",
  "category": "weather",
  "summary": {
    "markets_analyzed": 5,
    "average_edge": 3.5,
    "max_edge": 8.2
  },
  "markets": [...]
}
```

### 3-5. analyze_politics_markets / analyze_economics_markets / analyze_single_market

Similar structure for politics, economics, and single market analysis.

## Development

```bash
# Watch mode
npm run watch

# Clean build
npm run clean && npm run build

# Run development server
npm run dev
```

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Test with Dedalus
python quantitative_agent.py
```

## License

MIT
