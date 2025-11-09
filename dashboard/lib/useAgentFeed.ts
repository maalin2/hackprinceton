import { useState, useEffect, useRef } from "react";
import { AgentRecommendation } from "./types";
import { useRecommendations, RecommendationWithMarket } from "./useRecommendations";

// Convert RecommendationWithMarket to AgentRecommendation format for compatibility
function convertToAgentRecommendation(rec: RecommendationWithMarket): AgentRecommendation {
  const getPriority = (edge: number): "high" | "medium" | "low" => {
    const absEdge = Math.abs(edge);
    if (absEdge >= 0.15) return "high";
    if (absEdge >= 0.08) return "medium";
    return "low";
  };

  return {
    id: rec.id,
    timestamp: rec.decision.timestamp,
    domain: rec.market.domain,
    ticker: rec.market.ticker,
    market: rec.market.title,
    action: rec.decision.action,
    edge: rec.decision.edge,
    confidence: rec.decision.confidence,
    rationale: rec.decision.rationale,
    priority: getPriority(rec.decision.edge),
    status: rec.status,
  };
}

export function useAgentFeed() {
  const [recommendations, setRecommendations] = useState<AgentRecommendation[]>([]);
  const [wsConnected, setWsConnected] = useState(true); // Always connected for real-time analysis
  const previousIdsRef = useRef<string>("");
  
  // Use the real multi-agent recommendation system
  const {
    recommendations: realRecommendations,
    loading,
    acceptRecommendation: acceptRec,
    snoozeRecommendation: snoozeRec,
    dismissRecommendation: dismissRec,
  } = useRecommendations();

  // Convert and update recommendations only when IDs actually change
  useEffect(() => {
    // Create a stable ID string from recommendation IDs
    const currentIds = realRecommendations.map(r => r.id).sort().join(",");
    
    // Only update if recommendations actually changed
    if (currentIds === previousIdsRef.current) {
      return; // Skip if same recommendations
    }
    
    previousIdsRef.current = currentIds;
    
    // First, log the raw data from useRecommendations
    if (realRecommendations.length > 0) {
      console.log("\n🔍 RAW DATA from useRecommendations:");
      console.log("   Received", realRecommendations.length, "raw recommendations");
      realRecommendations.forEach((raw, idx) => {
        console.log(`   [${idx + 1}] Ticker: ${raw.market.ticker}, Title: ${raw.market.title.substring(0, 50)}...`);
        console.log(`       Decision: ${raw.decision.action}, Edge: ${(raw.decision.edge * 100).toFixed(1)}%`);
        console.log(`       Market URL: ${raw.market.url}`);
      });
    }
    
    const converted = realRecommendations.map(convertToAgentRecommendation);
    
    if (converted.length > 0) {
      console.log("\n📨 Agent Feed: Updated with", converted.length, "real recommendations");
      console.log("=" .repeat(80));
      converted.forEach((rec, idx) => {
        console.log(`\n🎯 Recommendation #${idx + 1}:`);
        console.log(`   Ticker: ${rec.ticker}`);
        console.log(`   Market: ${rec.market}`);
        console.log(`   Domain: ${rec.domain}`);
        console.log(`   Action: ${rec.action}`);
        console.log(`   Edge: ${(rec.edge * 100).toFixed(1)}%`);
        console.log(`   Confidence: ${(rec.confidence * 100).toFixed(1)}%`);
        console.log(`   🔗 Kalshi Link: https://kalshi.com/markets/${rec.ticker}`);
        console.log(`   📝 Rationale: ${rec.rationale || "N/A"}`);
      });
      console.log("=" .repeat(80) + "\n");
    }
    
    setRecommendations(converted);
  }, [realRecommendations]);

  useEffect(() => {
    console.log("✅ Agent Feed: Using REAL multi-agent system (Quant + Sentiment + Decision)");
    console.log("📡 Agent Feed: Auto-refresh every 5 minutes");
    
    // No cleanup needed - useRecommendations handles it
  }, []);

  // Wrap the recommendation handlers to work with string IDs
  const acceptRecommendation = (id: string) => {
    acceptRec(id);
    setRecommendations((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: "accepted" as const } : r))
    );
  };

  const snoozeRecommendation = (id: string) => {
    snoozeRec(id);
    setRecommendations((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: "snoozed" as const } : r))
    );
  };

  const dismissRecommendation = (id: string) => {
    dismissRec(id);
    setRecommendations((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: "dismissed" as const } : r))
    );
  };

  return {
    recommendations,
    loading,
    wsConnected,
    acceptRecommendation,
    snoozeRecommendation,
    dismissRecommendation,
  };
}

