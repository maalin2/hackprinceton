/**
 * HTTP/SSE transport for MCP server (primary)
 */

import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import type { Server } from '@modelcontextprotocol/sdk/server/index.js';
import express from 'express';
import { config } from '../config.js';

/**
 * Start the server with HTTP/SSE transport
 */
export async function startHttpTransport(server: Server): Promise<void> {
  const app = express();

  // Health check endpoint
  app.get('/health', (_req, res) => {
    res.json({ status: 'healthy', server: 'quant-ts' });
  });

  // SSE endpoint for MCP
  app.get('/sse', async (req, res) => {
    console.error('[HTTP] New SSE connection');

    const transport = new SSEServerTransport('/messages', res);
    await server.connect(transport);

    // Handle client disconnect
    req.on('close', () => {
      console.error('[HTTP] SSE connection closed');
    });
  });

  // POST endpoint for messages
  app.post('/messages', express.json(), async (req, res) => {
    // This will be handled by the SSE transport
    res.status(200).json({ received: true });
  });

  // Start server
  app.listen(config.port, () => {
    console.error(`🚀 Quant-TS MCP Server running on http://localhost:${config.port}`);
    console.error(`📡 SSE endpoint: http://localhost:${config.port}/sse`);
    console.error(`💚 Health check: http://localhost:${config.port}/health`);
  });
}
