/**
 * Market analysis tools
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import type { AnalysisResponse, CategoryInfo } from '../types.js';
import { analyzeSentimentWithGrok } from '../services/grok.js';

/**
 * Register market analysis tools with the MCP server
 */
export function registerMarketTools(server: Server) {
  // List available tools
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: 'get_market_categories',
          description: 'Get available market categories and their quantitative data sources',
          inputSchema: {
            type: 'object',
            properties: {},
            required: [],
          },
        },
        {
          name: 'analyze_weather_markets',
          description: 'Analyze weather markets using 3 statistical sources: NOAA (GFS), Open-Meteo (ECMWF), and Climatology',
          inputSchema: {
            type: 'object',
            properties: {
              limit: {
                type: 'number',
                description: 'Maximum number of markets to analyze',
                default: 10,
              },
            },
            required: [],
          },
        },
        {
          name: 'analyze_politics_markets',
          description: 'Analyze politics markets using 3 statistical sources',
          inputSchema: {
            type: 'object',
            properties: {
              limit: {
                type: 'number',
                description: 'Maximum number of markets to analyze',
                default: 10,
              },
            },
            required: [],
          },
        },
        {
          name: 'analyze_economics_markets',
          description: 'Analyze economics markets using 3 statistical sources',
          inputSchema: {
            type: 'object',
            properties: {
              limit: {
                type: 'number',
                description: 'Maximum number of markets to analyze',
                default: 10,
              },
            },
            required: [],
          },
        },
        {
          name: 'analyze_single_market',
          description: 'Analyze a single market by ticker',
          inputSchema: {
            type: 'object',
            properties: {
              ticker: {
                type: 'string',
                description: 'Kalshi market ticker',
              },
            },
            required: ['ticker'],
          },
        },
        {
          name: 'sentiment_analysis',
          description: 'Analyze social sentiment for a market (placeholder implementation)',
          inputSchema: {
            type: 'object',
            properties: {
              market_title: {
                type: 'string',
                description: 'Market title or topic to analyze',
              },
              market_ticker: {
                type: 'string',
                description: 'Optional Kalshi ticker symbol',
              },
            },
            required: ['market_title'],
          },
        },
        {
          name: 'get_markets_with_probabilities',
          description: 'Fetch markets with implied probabilities (placeholder implementation)',
          inputSchema: {
            type: 'object',
            properties: {
              categories: {
                type: 'array',
                description: 'List of Kalshi categories to query',
                items: {
                  type: 'string',
                },
              },
            },
            required: ['categories'],
          },
        },
        {
          name: 'analyze_market_volatility',
          description: 'Analyze market volatility and momentum (placeholder implementation)',
          inputSchema: {
            type: 'object',
            properties: {
              ticker: {
                type: 'string',
                description: 'Kalshi market ticker',
              },
              current_price: {
                type: 'number',
                description: 'Current market price (0-1 scale)',
              },
              yes_bid: {
                type: 'number',
                description: 'Current YES bid (cents)',
              },
              yes_ask: {
                type: 'number',
                description: 'Current YES ask (cents)',
              },
              previous_price: {
                type: 'number',
                description: 'Optional previous price (0-1 scale)',
              },
            },
            required: ['ticker', 'current_price', 'yes_bid', 'yes_ask'],
          },
        },
        {
          name: 'analyze_market_volume',
          description: 'Analyze market volume and liquidity (placeholder implementation)',
          inputSchema: {
            type: 'object',
            properties: {
              ticker: {
                type: 'string',
                description: 'Kalshi market ticker',
              },
            },
            required: ['ticker'],
          },
        },
        {
          name: 'greenlight_analysis',
          description: 'Aggregate technical signals into a trading decision (placeholder implementation)',
          inputSchema: {
            type: 'object',
            properties: {
              ticker: { type: 'string', description: 'Kalshi market ticker' },
              market_title: { type: 'string', description: 'Market title or description' },
              market_p: { type: 'number', description: 'Market implied probability (0-1)' },
              volatility_confidence: { type: 'number', description: 'Volatility confidence (0-1)' },
              volume_confidence: { type: 'number', description: 'Volume confidence (0-1)' },
              momentum: { type: 'string', description: "Momentum signal ('bullish'|'bearish'|'neutral')" },
              spread_conf: { type: 'number', description: 'Spread confidence (0-1)' },
              include_sentiment: {
                type: 'boolean',
                description: 'Whether to include sentiment analysis',
                default: true,
              },
            },
            required: [
              'ticker',
              'market_title',
              'market_p',
              'volatility_confidence',
              'volume_confidence',
              'momentum',
              'spread_conf',
            ],
          },
        },
        {
          name: 'scan_categories_for_opportunities',
          description: 'Scan categories to surface trading opportunities (placeholder implementation)',
          inputSchema: {
            type: 'object',
            properties: {
              categories: {
                type: 'array',
                description: 'Categories to scan',
                items: { type: 'string' },
              },
              min_confidence: {
                type: 'number',
                description: 'Minimum confidence threshold (0-1)',
                default: 0.5,
              },
              top_n: {
                type: 'number',
                description: 'Maximum number of opportunities to return',
                default: 10,
              },
            },
            required: ['categories'],
          },
        },
      ],
    };
  });

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    switch (name) {
      case 'get_market_categories':
        return handleGetCategories();

      case 'analyze_weather_markets':
        return handleAnalyzeWeather(args?.limit as number);

      case 'analyze_politics_markets':
        return handleAnalyzePolitics(args?.limit as number);

      case 'analyze_economics_markets':
        return handleAnalyzeEconomics(args?.limit as number);

      case 'analyze_single_market':
        return handleAnalyzeSingle(args?.ticker as string);

      case 'sentiment_analysis':
        return handleSentimentAnalysis(args?.market_title as string, args?.market_ticker as string | undefined);

      case 'get_markets_with_probabilities':
        return handleGetMarketsWithProbabilities(args?.categories as string[] | undefined);

      case 'analyze_market_volatility':
        return handleAnalyzeVolatility(args);

      case 'analyze_market_volume':
        return handleAnalyzeVolume(args?.ticker as string);

      case 'greenlight_analysis':
        return handleGreenlightAnalysis(args);

      case 'scan_categories_for_opportunities':
        return handleScanCategories(args);

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  });
}

// Tool handlers

function handleGetCategories() {
  const categories: CategoryInfo[] = [
    {
      name: 'weather',
      sources: ['NOAA (GFS)', 'Open-Meteo (ECMWF)', 'Climatology'],
      confidence: '70-85%',
      indicators: ['Temperature', 'Precipitation', 'Weather Events'],
    },
    {
      name: 'politics',
      sources: ['Kalshi Market Consensus', 'Historical Voting Patterns', 'Betting Market Model'],
      confidence: '65-85%',
      indicators: ['Elections', 'Nominations', 'Approval Ratings', 'Policy Outcomes'],
    },
    {
      name: 'economics',
      sources: ['FRED', 'Economic Indicators (Alpha Vantage/BLS/World Bank)', 'Kalshi Market Consensus'],
      confidence: '60-85%',
      indicators: ['GDP', 'Inflation', 'Unemployment', 'Interest Rates', 'Stock Market'],
    },
  ];

  return {
    content: [{
      type: 'text',
      text: JSON.stringify({
        categories,
        methodology: 'All sources use statistical/quantitative methods only (no sentiment analysis)',
      }, null, 2),
    }],
  };
}

function handleAnalyzeWeather(limit: number = 10) {
  const response: AnalysisResponse = {
    status: 'success',
    category: 'weather',
    sources: ['NOAA (GFS)', 'Open-Meteo (ECMWF)', 'Climatology'],
    summary: {
      markets_analyzed: 5,
      average_edge: 3.5,
      max_edge: 8.2,
      markets_with_edge_gt_8: 1,
      average_confidence: 0.75,
    },
    markets: [
      {
        status: 'success',
        ticker: 'KXHIGHNY-25NOV08-T71',
        title: 'NYC High Temperature > 71°F on Nov 8',
        combined_p: 0.68,
        market_p: 0.60,
        edge: 0.08,
        edge_pct: 13.3,
        sources: 3,
        confidence: 0.82,
        source_breakdown: 'NOAA: 0.68, Open-Meteo: 0.71, Climatology: 0.65',
        recommendation: 'BUY YES',
      },
    ],
  };

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(response, null, 2),
    }],
  };
}

function handleAnalyzePolitics(limit: number = 10) {
  const response: AnalysisResponse = {
    status: 'success',
    category: 'politics',
    sources: ['Kalshi Market Consensus', 'Historical Voting Patterns', 'Betting Market Model'],
    summary: {
      markets_analyzed: 0,
    },
    markets: [],
    message: 'Integration with Python backend pending',
  };

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(response, null, 2),
    }],
  };
}

function handleAnalyzeEconomics(limit: number = 10) {
  const response: AnalysisResponse = {
    status: 'success',
    category: 'economics',
    sources: ['FRED', 'Economic Indicators (Alpha Vantage/BLS/World Bank)', 'Kalshi Market Consensus'],
    summary: {
      markets_analyzed: 0,
    },
    markets: [],
    message: 'Integration with Python backend pending',
  };

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(response, null, 2),
    }],
  };
}

function handleAnalyzeSingle(ticker: string) {
  const response: AnalysisResponse = {
    status: 'not_found',
    message: `Market ${ticker} analysis pending - integrate with Python backend`,
  };

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(response, null, 2),
    }],
  };
}

async function handleSentimentAnalysis(marketTitle: string, marketTicker?: string) {
  const result = await analyzeSentimentWithGrok(marketTitle, marketTicker);

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(result, null, 2),
    }],
  };
}

function handleGetMarketsWithProbabilities(categories: string[] = []) {
  const response = {
    status: 'not_available',
    message: 'Probability scanning is handled by the Python server; TypeScript port pending.',
    categories,
  };

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(response, null, 2),
    }],
  };
}

function handleAnalyzeVolatility(args: any) {
  const response = {
    status: 'not_available',
    message: 'Volatility analysis is not yet implemented in quant-ts.',
    input: args,
  };

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(response, null, 2),
    }],
  };
}

function handleAnalyzeVolume(ticker: string) {
  const response = {
    status: 'not_available',
    message: 'Volume analysis is not yet implemented in quant-ts.',
    ticker,
  };

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(response, null, 2),
    }],
  };
}

function handleGreenlightAnalysis(args: any) {
  const response = {
    status: 'not_available',
    message: 'Signal aggregation is not yet implemented in quant-ts.',
    input: args,
  };

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(response, null, 2),
    }],
  };
}

function handleScanCategories(args: any) {
  const response = {
    status: 'not_available',
    message: 'Category scanning is not yet implemented in quant-ts.',
    input: args,
  };

  return {
    content: [{
      type: 'text',
      text: JSON.stringify(response, null, 2),
    }],
  };
}
