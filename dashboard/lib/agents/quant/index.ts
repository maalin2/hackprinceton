import { Domain, QuantSignal, MarketLite, SourceComponent } from "@/lib/types";
import { getWeatherSources } from "./providers/weather";
import { getPoliticsSources } from "./providers/politics";
import { getCryptoSources } from "./providers/crypto";
import { getSportsSources } from "./providers/sports";

/**
 * Quant Agent
 * 
 * Fetches ≥3 credible sources for the selected category and computes P_quant.
 * Returns QuantSignal with per-source components.
 */

export class QuantAgent {
  /**
   * Compute quantitative signal for a market
   */
  async analyze(market: MarketLite): Promise<QuantSignal> {
    const sources = await this.fetchSources(market);
    
    if (sources.length === 0) {
      // Fallback if no sources available
      return {
        pQuant: 0.5,
        confidence: 0.3,
        sources: [],
        timestamp: new Date(),
      };
    }

    // Compute weighted average probability
    const { pQuant, confidence } = this.combineSources(sources);

    return {
      pQuant: Math.max(0.01, Math.min(0.99, pQuant)), // Cap extremes
      confidence,
      sources,
      timestamp: new Date(),
    };
  }

  /**
   * Fetch sources based on market category
   */
  private async fetchSources(market: MarketLite): Promise<SourceComponent[]> {
    try {
      switch (market.domain) {
        case "Weather":
          return await getWeatherSources(market.ticker, market.title);
        case "Politics":
          return await getPoliticsSources(market.ticker, market.title);
        case "Crypto":
          return await getCryptoSources(market.ticker, market.title);
        case "Sports":
          return await getSportsSources(market.ticker, market.title);
        default:
          return [];
      }
    } catch (error) {
      console.error("QuantAgent: Error fetching sources", error);
      return [];
    }
  }

  /**
   * Combine sources with confidence-weighted averaging
   */
  private combineSources(sources: SourceComponent[]): { pQuant: number; confidence: number } {
    if (sources.length === 0) {
      return { pQuant: 0.5, confidence: 0 };
    }

    // Weighted average by confidence
    let weightedSum = 0;
    let totalWeight = 0;

    for (const source of sources) {
      const weight = source.confidence;
      weightedSum += source.probability * weight;
      totalWeight += weight;
    }

    const pQuant = totalWeight > 0 ? weightedSum / totalWeight : 0.5;
    const confidence = this.computeConfidence(sources);

    return { pQuant, confidence };
  }

  /**
   * Compute overall confidence from source confidences
   * Uses harmonic mean to penalize missing sources
   */
  private computeConfidence(sources: SourceComponent[]): number {
    if (sources.length === 0) return 0;
    
    const n = sources.length;
    const harmonicMean = n / sources.reduce((sum, s) => sum + 1 / Math.max(s.confidence, 0.01), 0);
    
    // Penalize if fewer than 3 sources
    const penalty = n < 3 ? n / 3 : 1.0;
    
    return Math.max(0.1, Math.min(0.95, harmonicMean * penalty));
  }
}

// Export singleton instance
export const quantAgent = new QuantAgent();

