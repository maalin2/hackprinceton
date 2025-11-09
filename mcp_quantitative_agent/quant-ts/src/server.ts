/**
 * MCP Server instance creation
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { registerMarketTools } from './tools/index.js';

/**
 * Create and configure the MCP server
 */
export function createServer(): Server {
  const server = new Server(
    {
      name: 'quant-ts',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Register all tools
  registerMarketTools(server);

  // Error handling
  server.onerror = (error) => {
    console.error('[MCP Error]', error);
  };

  return server;
}
