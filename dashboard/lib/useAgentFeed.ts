import { useState, useEffect } from "react";
import { AgentRecommendation, Domain } from "./types";

const domains: Domain[] = ["Politics", "Weather", "Crypto", "Sports"];
const actions = ["BUY_YES", "BUY_NO", "SELL_YES", "SELL_NO", "HOLD"] as const;
const priorities = ["high", "medium", "low"] as const;

const rationales = [
  "Our AI model sees strong upward momentum with high confidence in this prediction.",
  "Weather forecast data shows a different outcome than what the market is pricing in.",
  "Recent polling data indicates a major shift. This could be a good entry point.",
  "Multiple technical signals are pointing in the same direction right now.",
  "Social media sentiment is way off from market pricing. Could be an opportunity.",
  "Several weather models agree on this outcome. Time to act on this signal.",
  "Large investors appear to be moving into this position based on blockchain data.",
  "Past patterns suggest this outcome is more likely than the market thinks.",
];

const tickers = [
  "KXHIGHPHIL-25NOV08-T71",
  "KXBTCD-25NOV1417-T99749",
  "KX2028DRUN-28-JOSS",
  "KXETHMAX M-25DEC01-5200",
  "SENATEFL-28-R",
  "KXNFLEXACTWINSHOU-25-9",
];

const markets = [
  "Philadelphia >71°F on Nov 8?",
  "Bitcoin >$99,749.99 on Nov 14?",
  "Josh Shapiro 2028 Dem run?",
  "Ethereum >$5200 by Dec 1?",
  "Republicans win FL Senate 2028?",
  "Houston Texans exact 9 wins?",
];

let idCounter = 0;

function generateRecommendation(): AgentRecommendation {
  const idx = Math.floor(Math.random() * tickers.length);
  return {
    id: `rec-${++idCounter}-${Date.now()}`,
    timestamp: new Date(),
    domain: domains[Math.floor(Math.random() * domains.length)],
    ticker: tickers[idx],
    market: markets[idx],
    action: actions[Math.floor(Math.random() * actions.length)],
    edge: Math.random() * 0.5 + 0.05,
    confidence: Math.random() * 0.3 + 0.65,
    rationale: rationales[Math.floor(Math.random() * rationales.length)],
    priority: priorities[Math.floor(Math.random() * priorities.length)],
    status: "pending",
  };
}

export function useAgentFeed() {
  const [recommendations, setRecommendations] = useState<AgentRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    // Initial load
    setRecommendations([generateRecommendation(), generateRecommendation()]);
    setLoading(false);

    // Mock WebSocket server (replace with real Kalshi WebSocket endpoint)
    // Example: wss://api.kalshi.com/trade-api/ws/recommendations
    const MOCK_WS_MODE = true; // Set to false when using real WebSocket
    
    if (MOCK_WS_MODE) {
      // Simulate WebSocket with interval for demo purposes
      console.log("📡 Agent Feed: Mock WebSocket connected");
      setWsConnected(true);
      
      const interval = setInterval(() => {
        const newRec = generateRecommendation();
        console.log("📨 Agent Feed: New recommendation received", newRec.ticker);
        
        setRecommendations((prev) => {
          const filtered = prev.filter(
            (r) => r.status === "pending" || Date.now() - r.timestamp.getTime() < 60000
          ).slice(-20);
          return [newRec, ...filtered];
        });
      }, Math.random() * 7000 + 8000);

      return () => {
        clearInterval(interval);
        console.log("📡 Agent Feed: Mock WebSocket disconnected");
      };
    }

    // Real WebSocket implementation (activate by setting MOCK_WS_MODE = false)
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8080/agent-feed";
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      try {
        console.log("📡 Agent Feed: Connecting to WebSocket...", WS_URL);
        ws = new WebSocket(WS_URL);

        ws.onopen = () => {
          console.log("✅ Agent Feed: WebSocket connected");
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log("📨 Agent Feed: Message received", data);
            
            // Handle different message types
            if (data.type === "recommendation") {
              const newRec: AgentRecommendation = {
                id: data.id,
                timestamp: new Date(data.timestamp),
                domain: data.domain,
                ticker: data.ticker,
                market: data.market,
                action: data.action,
                edge: data.edge,
                confidence: data.confidence,
                rationale: data.rationale,
                priority: data.priority,
                status: "pending",
              };

              setRecommendations((prev) => {
                const filtered = prev.filter(
                  (r) => r.status === "pending" || Date.now() - r.timestamp.getTime() < 60000
                ).slice(-20);
                return [newRec, ...filtered];
              });
            }
          } catch (error) {
            console.error("❌ Agent Feed: Error parsing message", error);
          }
        };

        ws.onerror = (error) => {
          console.error("❌ Agent Feed: WebSocket error", error);
        };

        ws.onclose = () => {
          console.log("📡 Agent Feed: WebSocket disconnected. Reconnecting in 5s...");
          setWsConnected(false);
          
          // Attempt to reconnect after 5 seconds
          reconnectTimeout = setTimeout(() => {
            connect();
          }, 5000);
        };
      } catch (error) {
        console.error("❌ Agent Feed: Connection failed", error);
        reconnectTimeout = setTimeout(() => {
          connect();
        }, 5000);
      }
    };

    connect();

    return () => {
      console.log("📡 Agent Feed: Cleaning up WebSocket connection");
      if (ws) {
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, []);

  const updateRecommendation = (id: string, status: AgentRecommendation["status"]) => {
    setRecommendations((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status } : r))
    );
  };

  const dismissRecommendation = (id: string) => {
    updateRecommendation(id, "dismissed");
    setTimeout(() => {
      setRecommendations((prev) => prev.filter((r) => r.id !== id));
    }, 300);
  };

  const snoozeRecommendation = (id: string) => {
    updateRecommendation(id, "snoozed");
    setTimeout(() => {
      setRecommendations((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status: "pending" } : r))
      );
    }, 10000);
  };

  const acceptRecommendation = (id: string) => {
    updateRecommendation(id, "accepted");
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

