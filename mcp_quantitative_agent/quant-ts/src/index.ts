#!/usr/bin/env node

import { config as loadEnv } from 'dotenv';
loadEnv();

import { config } from './config.js';
import { parseArgs } from './cli.js';
import { createServer } from './server.js';
import { startStdioTransport, startHttpTransport } from './transport/index.js';

/**
 * Transport selection logic:
 * 1. --stdio flag forces STDIO transport (for Dedalus)
 * 2. --http flag uses HTTP transport (for testing/production)
 * 3. Default: STDIO transport for MCP compatibility
 */
async function main() {
  try {
    const cliOptions = parseArgs();

    // Create server instance
    const server = createServer();

    if (cliOptions.transport === 'http') {
      // HTTP transport for testing/production deployment
      const port = cliOptions.port || config.port;
      await startHttpTransport(server);
    } else {
      // STDIO transport for Dedalus/MCP clients (default)
      await startStdioTransport(server);
    }
  } catch (error) {
    console.error('Fatal error running Quant-TS server:', error);
    process.exit(1);
  }
}

main();
