/**
 * Configuration management
 */

import { config as dotenvConfig } from 'dotenv';
import type { ServerConfig } from './types.js';

// Load environment variables
dotenvConfig();

export const config: ServerConfig = {
  port: parseInt(process.env.PORT || '8000', 10),
  kalshiBaseUrl: process.env.KALSHI_BASE_URL || 'https://api.elections.kalshi.com/trade-api/v2',
  requestTimeout: parseInt(process.env.REQUEST_TIMEOUT || '15000', 10),
};

export const API_KEYS = {
  kalshi: process.env.KALSHI_API_KEY,
  openai: process.env.OPENAI_API_KEY,
  claude: process.env.CLAUDE_API_KEY || process.env.ANTHROPIC_API_KEY,
  xai: process.env.X_API_KEY,
  fred: process.env.FRED_API_KEY,
  alphaVantage: process.env.ALPHA_VANTAGE_API_KEY,
};
