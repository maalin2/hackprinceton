export type Domain = "Politics" | "Weather" | "Crypto" | "Sports" | "Economics" | "Technology" | "Entertainment";

export type Side = "YES" | "NO";

export interface Market {
  id: string;
  ticker: string;
  title: string;
  domain: Domain;
  series: string;
  yesBid: number;
  yesAsk: number;
  noBid: number;
  noAsk: number;
  spread: number;
  impliedProb: number;
  combinedProb: number;
  edge: number;
  volume24h: number;
  openInterest: number;
  closeTime: Date;
}

export interface PortfolioSnapshot {
  timestamp: Date;
  equity: number;
  pnl: number;
}

export interface PortfolioKPIs {
  totalEquity: number;
  pnl24h: number;
  winRate: number;
  openRisk: number;
}

export interface AgentRecommendation {
  id: string;
  timestamp: Date;
  domain: Domain;
  ticker: string;
  market: string;
  action: "BUY_YES" | "BUY_NO" | "SELL_YES" | "SELL_NO" | "HOLD";
  edge: number;
  confidence: number;
  rationale?: string;
  priority: "high" | "medium" | "low";
  status: "pending" | "accepted" | "snoozed" | "dismissed";
}

export interface UISettings {
  quantWeight: number;
  sentimentWeight: number;
  minEdgeThreshold: number;
  maxSpread: number;
  maxPositionSize: number;
}

export interface TradingPickSentiment {
  label: "positive" | "negative" | "neutral";
  score: number; // 0-100
  confidence: "high" | "medium" | "low";
}

export interface TradingPick {
  ticker: string;
  market_question?: string; // Optional human-readable market question
  topic?: string; // Topic category (politics, weather, crypto, etc.)
  decision: "BUY" | "SHORT" | "PASS";
  technical_direction: "buy" | "short" | null;
  market_p: number; // 0.0-1.0 probability
  volatility_confidence: number; // 0.0-1.0
  volume_confidence: number; // 0.0-1.0
  momentum: "bullish" | "bearish" | "neutral";
  final_confidence: number; // 0.0-1.0
  reasoning: string;
  sentiment: TradingPickSentiment;
  key_themes: string[];
  market_impact: string;
}

