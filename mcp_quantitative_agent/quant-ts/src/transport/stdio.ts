/**
 * STDIO transport for MCP server (development/testing)
 */

import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import type { Server } from '@modelcontextprotocol/sdk/server/index.js';

/**
 * Start the server with STDIO transport
 */
export async function startStdioTransport(server: Server): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Quant-TS MCP Server running on stdio');
}
