import { useState, useEffect } from "react";
import { Decision, MarketLite, Domain } from "./types";
import { quantAgent } from "./agents/quant";
import { sentimentAgent } from "./agents/sentiment";
import { decisionEngine } from "./agents/decision";
import { useUIStore } from "@/store/ui";
import { useMarkets } from "./useMarkets";

export interface RecommendationWithMarket {
  market: MarketLite;
  decision: Decision;
  id: string;
  status: "pending" | "accepted" | "snoozed" | "dismissed";
}

// Helper function to generate Kalshi market URL
function getKalshiMarketUrl(ticker: string): string {
  return `https://kalshi.com/markets/${ticker}`;
}

/**
 * Hook to manage multi-agent recommendations
 */
export function useRecommendations() {
  const [recommendations, setRecommendations] = useState<RecommendationWithMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const { settings } = useUIStore();
  const { markets, loading: marketsLoading } = useMarkets({ limit: 50 }); // Get real markets

  useEffect(() => {
    // Update decision engine weights from settings
    decisionEngine.setWeights({
      quantWeight: settings.quantWeight,
      sentimentWeight: settings.sentimentWeight,
    });
    decisionEngine.setEdgeThreshold(settings.minEdgeThreshold);
  }, [settings]);

  useEffect(() => {
    // Wait for markets to load
    if (marketsLoading) {
      setLoading(true);
      return;
    }

    // Initial analysis
    analyzeMarkets();

    // Re-analyze every 60 seconds
    const interval = setInterval(() => {
      analyzeMarkets();
    }, 60000);

    return () => clearInterval(interval);
  }, [settings, markets, marketsLoading]);

  /**
   * Analyze markets and generate recommendations
   */
  const analyzeMarkets = async () => {
    if (markets.length === 0) {
      setLoading(false);
      return;
    }

    setProcessing(true);
    
    try {
      // Convert Market to MarketLite for analysis
      const marketsToAnalyze: MarketLite[] = markets.slice(0, 20).map((m) => ({
        id: m.id,
        ticker: m.ticker,
        title: m.title,
        series: m.series,
        domain: m.domain,
        yesBid: m.yesBid,
        yesAsk: m.yesAsk,
        lastPrice: m.lastPrice || (m.yesBid + m.yesAsk) / 2,
        url: m.url,
      }));

      // Analyze each market in parallel
      const analyses = await Promise.all(
        marketsToAnalyze.map(async (market) => {
          try {
            // Run agents in parallel
            const [quantSignal, sentimentSignal] = await Promise.all([
              quantAgent.analyze(market),
              sentimentAgent.analyze(market),
            ]);

            // Make decision
            const decision = decisionEngine.decide(market, quantSignal, sentimentSignal);

            return {
              market,
              decision,
              id: `rec-${market.id}-${Date.now()}`,
              status: "pending" as const,
            };
          } catch (error) {
            console.error(`Error analyzing market ${market.ticker}:`, error);
            return null;
          }
        })
      );

      // Filter out failed analyses and only include actionable recommendations
      const validRecommendations = analyses.filter(
        (rec): rec is RecommendationWithMarket =>
          rec !== null && rec.decision.action !== "HOLD"
      );

      setRecommendations(validRecommendations);
    } catch (error) {
      console.error("Error analyzing markets:", error);
    } finally {
      setLoading(false);
      setProcessing(false);
    }
  };

  /**
   * Update recommendation status
   */
  const updateStatus = (id: string, status: RecommendationWithMarket["status"]) => {
    setRecommendations((prev) =>
      prev.map((rec) => (rec.id === id ? { ...rec, status } : rec))
    );
  };

  /**
   * Accept a recommendation
   */
  const acceptRecommendation = (id: string) => {
    updateStatus(id, "accepted");
    console.log("✅ Recommendation accepted (paper trading):", id);
  };

  /**
   * Snooze a recommendation
   */
  const snoozeRecommendation = (id: string) => {
    updateStatus(id, "snoozed");
    // Re-show after 30 seconds
    setTimeout(() => {
      setRecommendations((prev) =>
        prev.map((rec) => (rec.id === id ? { ...rec, status: "pending" } : rec))
      );
    }, 30000);
  };

  /**
   * Dismiss a recommendation
   */
  const dismissRecommendation = (id: string) => {
    updateStatus(id, "dismissed");
    // Remove after animation
    setTimeout(() => {
      setRecommendations((prev) => prev.filter((rec) => rec.id !== id));
    }, 500);
  };

  /**
   * Manually trigger re-analysis
   */
  const refresh = () => {
    analyzeMarkets();
  };

  return {
    recommendations: recommendations.filter((r) => r.status === "pending"),
    loading,
    processing,
    acceptRecommendation,
    snoozeRecommendation,
    dismissRecommendation,
    refresh,
  };
}

