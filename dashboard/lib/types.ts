export type Domain = "Politics" | "Weather" | "Crypto" | "Sports";

export type Side = "YES" | "NO";

export type PositionStatus = "open" | "closed";

export interface Position {
  id: string;
  ticker: string;
  market: string;
  domain: Domain;
  side: Side;
  entry: number;
  mark: number;
  size: number;
  pnl: number;
  edge: number;
  status: PositionStatus;
  openedAt: Date;
  closedAt?: Date;
  rationale?: string;
  fills: Fill[];
}

export interface Fill {
  timestamp: Date;
  price: number;
  quantity: number;
}

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
  lastPrice?: number; // Last trade price (optional)
  url: string; // Link to Kalshi market page
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

// Multi-Agent System Types

export interface SourceComponent {
  source: string;
  probability: number;
  confidence: number;
  data?: any;
}

export interface QuantSignal {
  pQuant: number;
  confidence: number;
  sources: SourceComponent[];
  timestamp: Date;
}

export interface SentimentSignal {
  pSent: number;
  confidence: number;
  nSamples: number;
  sources: {
    kalshi: number;
    twitter: number;
  };
  rawData?: {
    comments: Array<{ text: string; author: string; url: string; timestamp: Date }>;
    tweets: Array<{ text: string; author: string; url: string; likes: number; timestamp: Date }>;
  };
  timestamp: Date;
}

export interface Decision {
  action: "BUY_YES" | "BUY_NO" | "HOLD";
  pMarket: number;
  pQuant: number;
  pSent: number;
  pCombined: number;
  edge: number;
  confidence: number;
  rationale: string;
  sources: string[];
  quantSignal?: QuantSignal;
  sentimentSignal?: SentimentSignal;
  timestamp: Date;
}

export interface MarketLite {
  id: string;
  ticker: string;
  title: string;
  series: string;
  domain: Domain;
  yesBid: number;
  yesAsk: number;
  lastPrice: number;
  url: string; // Link to Kalshi market page
}

