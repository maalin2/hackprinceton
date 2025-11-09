/**
 * Command-line argument parsing
 */

export interface CliOptions {
  transport: 'stdio' | 'http';
  port?: number;
}

/**
 * Parse command-line arguments
 */
export function parseArgs(): CliOptions {
  const args = process.argv.slice(2);

  const options: CliOptions = {
    transport: 'stdio', // Default to stdio for MCP/Dedalus
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    switch (arg) {
      case '--stdio':
      case '-s':
        options.transport = 'stdio';
        break;

      case '--http':
      case '-h':
        options.transport = 'http';
        break;

      case '--port':
      case '-p':
        const port = parseInt(args[++i], 10);
        if (!isNaN(port)) {
          options.port = port;
        }
        break;

      case '--help':
        printHelp();
        process.exit(0);
        break;
    }
  }

  return options;
}

function printHelp(): void {
  console.log(`
Quant-TS - Quantitative Market Analysis MCP Server

Usage:
  quant-ts [options]

Options:
  --stdio, -s        Use STDIO transport (default, for Dedalus/MCP)
  --http, -h         Use HTTP/SSE transport (for testing/production)
  --port, -p <port>  Specify port for HTTP transport (default: 8000)
  --help             Show this help message

Examples:
  quant-ts                    # Run with stdio transport (default, for Dedalus)
  quant-ts --stdio            # Explicitly use stdio transport
  quant-ts --http             # Run with HTTP transport on port 8000
  quant-ts --http --port 3000 # Run with HTTP transport on port 3000

For Dedalus integration:
  Configure in ~/.config/dedalus/mcp.json:
  {
    "mcpServers": {
      "quant-ts": {
        "command": "node",
        "args": ["dist/index.js"],
        "cwd": "/path/to/quant-ts"
      }
    }
  }
  `);
}
