import { SentimentSignal, MarketLite } from "@/lib/types";
import { fetchKalshiComments } from "./kalshi";
import { fetchTwitterPosts } from "./twitter";
import { analyzeSentiment, compoundToProbability } from "./vader";

/**
 * Sentiment Agent
 * 
 * Gathers Kalshi discussion comments + X (Twitter) posts for a market/series
 * and computes P_sentiment (0–1) with a confidence score using VADER sentiment analysis.
 */

export class SentimentAgent {
  /**
   * Analyze sentiment for a market
   */
  async analyze(market: MarketLite): Promise<SentimentSignal> {
    try {
      // Fetch comments and tweets in parallel
      const [comments, tweets] = await Promise.all([
        fetchKalshiComments(market.series).catch(() => []),
        fetchTwitterPosts(this.buildSearchQuery(market)).catch(() => []),
      ]);

      const allTexts = [
        ...comments.map(c => c.text),
        ...tweets.map(t => t.text),
      ];

      // Log raw data with links for debugging
      if (comments.length > 0) {
        console.log(`📝 Kalshi Comments (${comments.length}):`);
        comments.forEach((c, i) => {
          console.log(`  ${i + 1}. "${c.text}"`);
          console.log(`     👤 ${c.author} | 🔗 ${c.url}`);
        });
      }
      if (tweets.length > 0) {
        console.log(`🐦 Twitter Posts (${tweets.length}):`);
        tweets.forEach((t, i) => {
          console.log(`  ${i + 1}. "${t.text}"`);
          console.log(`     👤 ${t.author} | ❤️  ${t.likes} | 🔗 ${t.url}`);
        });
      }

      if (allTexts.length === 0) {
        // No sentiment data available
        return {
          pSent: 0.5,
          confidence: 0.3,
          nSamples: 0,
          sources: { kalshi: 0, twitter: 0 },
          timestamp: new Date(),
        };
      }

      // Analyze sentiment for each text
      const sentiments = allTexts.map(text => analyzeSentiment(text));
      
      // Convert compound scores to probabilities
      const probabilities = sentiments.map(s => compoundToProbability(s.compound));
      
      // Compute trimmed mean (remove top and bottom 10%)
      const pSent = this.trimmedMean(probabilities);
      
      // Compute confidence based on sample size and agreement
      const confidence = this.computeConfidence(probabilities, allTexts.length);

      return {
        pSent: Math.max(0.2, Math.min(0.8, pSent)), // Cap extremes for sentiment
        confidence,
        nSamples: allTexts.length,
        sources: {
          kalshi: comments.length,
          twitter: tweets.length,
        },
        rawData: {
          comments: comments.map(c => ({
            text: c.text,
            author: c.author,
            url: c.url,
            timestamp: c.timestamp,
          })),
          tweets: tweets.map(t => ({
            text: t.text,
            author: t.author,
            url: t.url,
            likes: t.likes,
            timestamp: t.timestamp,
          })),
        },
        timestamp: new Date(),
      };
    } catch (error) {
      console.error("SentimentAgent: Error analyzing sentiment", error);
      return {
        pSent: 0.5,
        confidence: 0.3,
        nSamples: 0,
        sources: { kalshi: 0, twitter: 0 },
        timestamp: new Date(),
      };
    }
  }

  /**
   * Build search query for Twitter based on market
   */
  private buildSearchQuery(market: MarketLite): string {
    // Extract key terms from title
    // For example: "Will Philadelphia hit >71°F on Nov 8?" → "Philadelphia weather temperature"
    const title = market.title.toLowerCase();
    
    // Simple keyword extraction
    const keywords: string[] = [];
    
    if (market.domain === "Weather") {
      keywords.push("weather", "forecast", "temperature");
    } else if (market.domain === "Politics") {
      keywords.push("election", "poll", "politics");
    } else if (market.domain === "Crypto") {
      keywords.push("crypto", "bitcoin", "ethereum");
    } else if (market.domain === "Sports") {
      keywords.push("sports", "game", "team");
    }
    
    // Add series identifier
    keywords.push(market.series);
    
    return keywords.join(" ");
  }

  /**
   * Compute trimmed mean (remove outliers)
   */
  private trimmedMean(values: number[]): number {
    if (values.length === 0) return 0.5;
    if (values.length < 4) {
      // Too few samples for trimming
      return values.reduce((a, b) => a + b, 0) / values.length;
    }
    
    // Sort values
    const sorted = [...values].sort((a, b) => a - b);
    
    // Remove top and bottom 10%
    const trimCount = Math.floor(sorted.length * 0.1);
    const trimmed = sorted.slice(trimCount, sorted.length - trimCount);
    
    return trimmed.reduce((a, b) => a + b, 0) / trimmed.length;
  }

  /**
   * Compute confidence based on sample size and agreement
   */
  private computeConfidence(probabilities: number[], nSamples: number): number {
    if (nSamples === 0) return 0;
    
    // Sample size factor (more samples = more confidence)
    const sampleFactor = Math.min(1.0, nSamples / 50); // Cap at 50 samples
    
    // Agreement factor (lower variance = higher confidence)
    const mean = probabilities.reduce((a, b) => a + b, 0) / probabilities.length;
    const variance = probabilities.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / probabilities.length;
    const stdDev = Math.sqrt(variance);
    const agreementFactor = Math.max(0.5, 1 - stdDev); // Lower std dev = better agreement
    
    // Combined confidence
    const confidence = 0.5 * sampleFactor + 0.5 * agreementFactor;
    
    return Math.max(0.3, Math.min(0.85, confidence));
  }
}

// Export singleton instance
export const sentimentAgent = new SentimentAgent();

