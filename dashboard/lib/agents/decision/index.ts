import { Decision, QuantSignal, SentimentSignal, MarketLite } from "@/lib/types";

/**
 * Decision Engine
 * 
 * Combines P_quant and P_sentiment → P_combined
 * Compares to P_market (implied from Kalshi prices)
 * Emits Buy YES / Buy NO / Hold with rationale
 */

export interface DecisionWeights {
  quantWeight: number;
  sentimentWeight: number;
}

export class DecisionEngine {
  private weights: DecisionWeights;
  private edgeThreshold: number;

  constructor(
    weights: DecisionWeights = { quantWeight: 0.8, sentimentWeight: 0.2 },
    edgeThreshold: number = 0.08
  ) {
    this.weights = weights;
    this.edgeThreshold = edgeThreshold;
  }

  /**
   * Make a trading decision based on quant and sentiment signals
   */
  decide(
    market: MarketLite,
    quantSignal: QuantSignal,
    sentimentSignal: SentimentSignal
  ): Decision {
    // Compute P_market from quotes
    const pMarket = this.computeMarketProbability(market);

    // Adjust sentiment weight if sample size is low
    let wq = this.weights.quantWeight;
    let ws = this.weights.sentimentWeight;

    if (sentimentSignal.nSamples < 20) {
      // Downweight sentiment when sample size is insufficient
      const penalty = sentimentSignal.nSamples / 20;
      ws = ws * penalty;
      wq = 1 - ws; // Renormalize
    }

    // Compute P_combined
    const pCombined = wq * quantSignal.pQuant + ws * sentimentSignal.pSent;

    // Compute edge
    const edge = pCombined - pMarket;

    // Determine action
    let action: Decision["action"];
    if (edge >= this.edgeThreshold) {
      action = "BUY_YES";
    } else if (edge <= -this.edgeThreshold) {
      action = "BUY_NO";
    } else {
      action = "HOLD";
    }

    // Compute confidence
    const confidence = this.computeConfidence(edge, quantSignal, sentimentSignal);

    // Generate rationale
    const rationale = this.generateRationale(
      action,
      edge,
      quantSignal,
      sentimentSignal,
      pMarket,
      pCombined
    );

    // Collect all sources
    const sources = this.collectSources(quantSignal, sentimentSignal);

    return {
      action,
      pMarket,
      pQuant: quantSignal.pQuant,
      pSent: sentimentSignal.pSent,
      pCombined,
      edge,
      confidence,
      rationale,
      sources,
      quantSignal,
      sentimentSignal,
      timestamp: new Date(),
    };
  }

  /**
   * Compute implied probability from market prices
   */
  private computeMarketProbability(market: MarketLite): number {
    // Prefer mid price: (yesBid + yesAsk) / 200
    if (market.yesBid > 0 && market.yesAsk > 0) {
      return (market.yesBid + market.yesAsk) / 200;
    }

    // Fallback to last price
    if (market.lastPrice > 0) {
      return market.lastPrice / 100;
    }

    // Default to 50% if no price data
    return 0.5;
  }

  /**
   * Compute overall confidence in the decision
   */
  private computeConfidence(
    edge: number,
    quantSignal: QuantSignal,
    sentimentSignal: SentimentSignal
  ): number {
    // Base confidence from edge magnitude
    const edgeConfidence = Math.min(1, 0.5 + Math.abs(edge));

    // Combine with signal confidences
    const avgSignalConfidence =
      (quantSignal.confidence + sentimentSignal.confidence) / 2;

    // Weighted combination
    const confidence = 0.6 * edgeConfidence + 0.4 * avgSignalConfidence;

    return Math.max(0.3, Math.min(0.99, confidence));
  }

  /**
   * Generate human-readable rationale
   */
  private generateRationale(
    action: Decision["action"],
    edge: number,
    quantSignal: QuantSignal,
    sentimentSignal: SentimentSignal,
    pMarket: number,
    pCombined: number
  ): string {
    const parts: string[] = [];

    // Action summary
    if (action === "BUY_YES") {
      parts.push(`Strong YES signal with ${(edge * 100).toFixed(1)}% edge.`);
    } else if (action === "BUY_NO") {
      parts.push(`Strong NO signal with ${(Math.abs(edge) * 100).toFixed(1)}% edge.`);
    } else {
      parts.push(`Market fairly priced. Edge (${(edge * 100).toFixed(1)}%) below threshold.`);
    }

    // Quant analysis
    if (quantSignal.sources.length > 0) {
      const topSource = quantSignal.sources.sort((a, b) => b.confidence - a.confidence)[0];
      parts.push(
        `Quant model (${(quantSignal.pQuant * 100).toFixed(1)}%) led by ${topSource.source} at ${(topSource.probability * 100).toFixed(1)}%.`
      );
    }

    // Sentiment analysis
    if (sentimentSignal.nSamples > 0) {
      parts.push(
        `Sentiment (${(sentimentSignal.pSent * 100).toFixed(1)}%) from ${sentimentSignal.nSamples} samples across Kalshi (${sentimentSignal.sources.kalshi}) + Twitter (${sentimentSignal.sources.twitter}).`
      );
    }

    // Market comparison
    parts.push(
      `Market pricing: ${(pMarket * 100).toFixed(1)}%. Combined model: ${(pCombined * 100).toFixed(1)}%.`
    );

    return parts.join(" ");
  }

  /**
   * Collect all source names
   */
  private collectSources(quantSignal: QuantSignal, sentimentSignal: SentimentSignal): string[] {
    const sources: string[] = [];

    // Add quant sources
    quantSignal.sources.forEach(s => {
      sources.push(s.source);
    });

    // Add sentiment sources
    if (sentimentSignal.sources.kalshi > 0) {
      sources.push("Kalshi Comments");
    }
    if (sentimentSignal.sources.twitter > 0) {
      sources.push("Twitter");
    }

    return sources;
  }

  /**
   * Update weights dynamically
   */
  setWeights(weights: DecisionWeights): void {
    this.weights = weights;
  }

  /**
   * Update edge threshold
   */
  setEdgeThreshold(threshold: number): void {
    this.edgeThreshold = threshold;
  }
}

// Export singleton instance
export const decisionEngine = new DecisionEngine();

