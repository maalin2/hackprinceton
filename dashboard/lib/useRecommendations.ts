import { useState, useEffect } from "react";
import { Decision, MarketLite, Domain } from "./types";
import { useUIStore } from "@/store/ui";

export interface RecommendationWithMarket {
  market: MarketLite;
  decision: Decision;
  id: string;
  status: "pending" | "accepted" | "snoozed" | "dismissed";
}

// Python API backend URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Helper function to generate Kalshi market URL
function getKalshiMarketUrl(ticker: string): string {
  return `https://kalshi.com/markets/${ticker}`;
}

/**
 * Hook to manage hybrid recommendations from Python backend
 * (Statistical + Grok AI)
 */
export function useRecommendations() {
  const [recommendations, setRecommendations] = useState<RecommendationWithMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const { settings } = useUIStore();

  useEffect(() => {
    // Initial fetch
    fetchRecommendations();

    // Re-fetch every 60 seconds
    const interval = setInterval(() => {
      fetchRecommendations();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  /**
   * Fetch recommendations from Python backend (hybrid analysis)
   */
  const fetchRecommendations = async () => {
    setProcessing(true);
    
    try {
      const timestamp = new Date().toLocaleTimeString();
      console.log(`\n${'='.repeat(80)}`);
      console.log(`[${timestamp}] 🔄 Fetching recommendations from Python backend`);
      console.log(`API URL: ${API_BASE_URL}/api/recommendations`);
      console.log(`${'='.repeat(80)}`);
      
      const response = await fetch(`${API_BASE_URL}/api/recommendations`);
      
      if (!response.ok) {
        throw new Error(`API failed: ${response.status}`);
      }
      
      const data = await response.json();
      
      console.log(`\n📊 Response status: ${data.status}`);
      
      if (data.status === "analyzing") {
        console.log("⏳ Backend is analyzing, keeping existing recommendations");
        console.log("   (New results will appear when analysis completes)");
        // Keep existing recommendations while analysis runs
        setProcessing(true);
        return;
      }
      
      if (data.status === "empty") {
        console.log("⚠️  No recommendations yet, waiting for first analysis");
        console.log("   ⏱️  This usually takes 30-60 seconds on first run");
        setRecommendations([]);
        setLoading(false);
        return;
      }
      
      console.log(`\n✅ Received ${data.opportunities?.length || 0} opportunities from Python backend`);
      
      // Convert Python API format to dashboard format
      const converted: RecommendationWithMarket[] = data.opportunities.map((opp: any) => {
        // Determine domain from category
        const domain: Domain = opp.category as Domain;
        
        // Convert Python recommendation to dashboard format
        const market: MarketLite = {
          id: opp.ticker,
          ticker: opp.ticker,
          title: opp.title,
          series: opp.ticker.split('-')[0], // Extract series from ticker
          domain,
          yesBid: opp.market_prob * 100, // Convert to cents
          yesAsk: opp.market_prob * 100,
          lastPrice: opp.market_prob * 100,
          url: opp.url,
        };
        
        const decision: Decision = {
          action: opp.action === "BUY_YES" ? "BUY_YES" : "BUY_NO",
          pMarket: opp.market_prob,
          pQuant: opp.quant_prob,
          pSent: opp.grok_sentiment?.status === 'success' ? 
                 (opp.grok_sentiment.sentiment_score || opp.grok_sentiment.score || 50) / 100 : 0.5,
          pCombined: opp.quant_prob, // Use quant as combined for now
          edge: opp.quant_edge,
          confidence: opp.combined_confidence,
          rationale: opp.reasoning,
          sources: opp.quant_sources,
          quantSignal: {
            pQuant: opp.quant_prob,
            confidence: opp.confidence,
            sources: opp.quant_sources.map((source: string) => ({
              source,
              probability: opp.quant_prob,
              confidence: opp.confidence,
            })),
            timestamp: new Date(opp.timestamp),
          },
          sentimentSignal: opp.grok_sentiment && opp.grok_sentiment.status === 'success' ? {
            pSent: (opp.grok_sentiment.sentiment_score || opp.grok_sentiment.score || 50) / 100,
            confidence: opp.grok_sentiment.confidence === 'high' ? 0.8 : 
                       opp.grok_sentiment.confidence === 'medium' ? 0.6 : 0.4,
            nSamples: 1, // Grok is single analysis
            sources: {
              kalshi: 0,
              twitter: 1,
            },
            rawData: {
              comments: [],
              tweets: [{
                text: `Grok analysis: ${opp.grok_sentiment.sentiment_label || opp.grok_sentiment.label || 'neutral'} (${opp.grok_sentiment.sentiment_score || opp.grok_sentiment.score || 50}%)`,
                author: 'Grok AI',
                url: opp.url,
                likes: 0,
                timestamp: new Date(opp.timestamp),
              }],
            },
            timestamp: new Date(opp.timestamp),
          } : undefined,
          timestamp: new Date(opp.timestamp),
        };
        
        return {
          market,
          decision,
          id: `rec-${opp.ticker}-${Date.now()}`,
          status: "pending" as const,
        };
      });
      
      console.log(`\n🔄 Converting ${converted.length} recommendations to dashboard format...`);
      
      // Log each recommendation with detailed Grok status
      converted.forEach((rec, i) => {
        const oppData = data.opportunities[i];
        console.log(`\n📌 Recommendation #${i + 1}:`);
        console.log(`   Ticker: ${rec.market.ticker}`);
        console.log(`   Market: ${rec.market.title.substring(0, 60)}...`);
        console.log(`   Action: ${rec.decision.action}`);
        console.log(`   📊 Quant Edge: ${(rec.decision.edge * 100).toFixed(1)}%`);
        
        // Detailed Grok logging
        if (oppData.grok_sentiment) {
          const grok = oppData.grok_sentiment;
          console.log(`   🤖 Grok Status: ${grok.status}`);
          if (grok.status === 'success') {
            console.log(`      └─ Sentiment: ${grok.sentiment_label || grok.label} (${grok.sentiment_score || grok.score}%)`);
            console.log(`      └─ Confidence: ${grok.confidence}`);
            if (grok.key_themes && grok.key_themes.length > 0) {
              console.log(`      └─ Themes: ${grok.key_themes.slice(0, 3).join(', ')}`);
            }
          } else {
            console.log(`      └─ Error: ${grok.error || grok.message || 'Unknown'}`);
            console.log(`      └─ Using fallback: neutral (50%)`);
          }
        } else {
          console.log(`   🤖 Grok Sentiment: NOT PRESENT IN DATA`);
        }
        
        console.log(`   🎯 Combined Confidence: ${(rec.decision.confidence * 100).toFixed(1)}%`);
        console.log(`   🔗 Kalshi: ${rec.market.url}`);
      });
      
      console.log(`\n${'='.repeat(80)}`);
      console.log(`✅ Successfully converted and set ${converted.length} recommendations`);
      console.log(`📅 Last updated: ${data.lastUpdated || 'just now'}`);
      console.log(`${'='.repeat(80)}\n`);
      
      setRecommendations(converted);
      setLastUpdated(data.lastUpdated ? new Date(data.lastUpdated) : new Date());
      
    } catch (error) {
      console.error(`\n❌ Error fetching from Python backend:`);
      console.error(error);
      console.error(`\n⚠️  Keeping existing recommendations\n`);
      // Don't clear existing recommendations on error
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
   * Manually trigger re-fetch
   */
  const refresh = () => {
    fetchRecommendations();
  };

  return {
    recommendations: recommendations.filter((r) => r.status === "pending"),
    loading,
    processing,
    lastUpdated,
    acceptRecommendation,
    snoozeRecommendation,
    dismissRecommendation,
    refresh,
  };
}

