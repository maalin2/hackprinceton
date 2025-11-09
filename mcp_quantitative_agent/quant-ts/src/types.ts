/**
 * Type definitions for Quant-TS MCP Server
 */

export interface MarketResult {
  status: string;
  category?: string;
  ticker: string;
  title: string;
  combined_p?: number;
  market_p?: number;
  edge?: number;
  edge_pct?: number;
  sources?: number;
  confidence?: number;
  source_breakdown?: string;
  recommendation: string;
}

export interface MarketSummary {
  markets_analyzed: number;
  average_edge?: number;
  max_edge?: number;
  markets_with_edge_gt_8?: number;
  average_confidence?: number;
}

export interface AnalysisResponse {
  status: string;
  category?: string;
  sources?: string[];
  summary?: MarketSummary;
  markets?: MarketResult[];
  error?: string;
  message?: string;
}

export interface KalshiMarket {
  ticker: string;
  title: string;
  yes_bid?: number;
  yes_ask?: number;
  last_price?: number;
  volume?: number;
  category?: string;
  status?: string;
}

export interface CategoryInfo {
  name: string;
  sources: string[];
  confidence: string;
  indicators: string[];
}

export interface ServerConfig {
  port: number;
  kalshiBaseUrl: string;
  requestTimeout: number;
}

export interface SentimentAnalysisResult {
  status: 'success' | 'error';
  sentiment_score?: number;
  sentiment_label?: string;
  key_themes?: string[];
  notable_trends?: string[];
  market_impact?: string;
  confidence?: string;
  ticker?: string | null;
  title?: string;
  error?: string;
  message?: string;
  raw_response?: string;
  requirements?: string;
}
