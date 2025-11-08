import { useState, useEffect } from "react";
import { Decision, MarketLite, Domain } from "./types";
import { quantAgent } from "./agents/quant";
import { sentimentAgent } from "./agents/sentiment";
import { decisionEngine } from "./agents/decision";
import { useUIStore } from "@/store/ui";

export interface RecommendationWithMarket {
  market: MarketLite;
  decision: Decision;
  id: string;
  status: "pending" | "accepted" | "snoozed" | "dismissed";
}

// Mock markets for analysis
const MOCK_MARKETS: MarketLite[] = [
  {
    id: "1",
    ticker: "KXHIGHPHIL-25NOV08-T71",
    title: "Will Philadelphia hit >71°F on Nov 8, 2025?",
    series: "KXHIGHPHIL",
    domain: "Weather",
    yesBid: 1,
    yesAsk: 3,
    lastPrice: 2,
  },
  {
    id: "2",
    ticker: "KXBTCD-25NOV1417-T99749",
    title: "Will Bitcoin price be >$99,749.99 on Nov 14, 2025?",
    series: "KXBTCD",
    domain: "Crypto",
    yesBid: 67,
    yesAsk: 74,
    lastPrice: 70,
  },
  {
    id: "3",
    ticker: "KX2028DRUN-28-JOSS",
    title: "Will Josh Shapiro run for 2028 Democratic nomination?",
    series: "KX2028DRUN",
    domain: "Politics",
    yesBid: 30,
    yesAsk: 40,
    lastPrice: 35,
  },
  {
    id: "4",
    ticker: "KXNFLEXACTWINSHOU-25-9",
    title: "Will Houston Texans win exactly 9 games this season?",
    series: "KXNFLEXACTWINSHOU",
    domain: "Sports",
    yesBid: 8,
    yesAsk: 39,
    lastPrice: 23,
  },
];

/**
 * Hook to manage multi-agent recommendations
 */
export function useRecommendations() {
  const [recommendations, setRecommendations] = useState<RecommendationWithMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const { settings } = useUIStore();

  useEffect(() => {
    // Update decision engine weights from settings
    decisionEngine.setWeights({
      quantWeight: settings.quantWeight,
      sentimentWeight: settings.sentimentWeight,
    });
    decisionEngine.setEdgeThreshold(settings.minEdgeThreshold);
  }, [settings]);

  useEffect(() => {
    // Initial analysis
    analyzeMarkets();

    // Re-analyze every 60 seconds
    const interval = setInterval(() => {
      analyzeMarkets();
    }, 60000);

    return () => clearInterval(interval);
  }, [settings]);

  /**
   * Analyze markets and generate recommendations
   */
  const analyzeMarkets = async () => {
    setProcessing(true);
    
    try {
      const newRecommendations: RecommendationWithMarket[] = [];

      // Analyze each market in parallel
      const analyses = await Promise.all(
        MOCK_MARKETS.map(async (market) => {
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

