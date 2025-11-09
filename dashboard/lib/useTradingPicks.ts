import { useState, useEffect } from "react";
import { TradingPick } from "./types";
import { useUserPreferences } from "./useUserPreferences";

// Mock data generator - replace with actual API call
const generateMockPicks = (): TradingPick[] => {
  return [
    {
      ticker: "KXBTCD-25NOV1417-T99749",
      market_question: "Will Bitcoin hit >$99,749.99 on Nov 14, 2025?",
      topic: "crypto",
      decision: "BUY",
      technical_direction: "buy",
      market_p: 0.65,
      volatility_confidence: 0.78,
      volume_confidence: 0.82,
      momentum: "bullish",
      final_confidence: 0.78,
      reasoning: "Bitcoin shows strong technical indicators with RSI at 68 and breaking above key resistance. Market sentiment is positive with institutional buying pressure. Current odds at 65% are undervalued compared to our 78% confidence.",
      sentiment: {
        label: "positive",
        score: 75,
        confidence: "high",
      },
      key_themes: ["crypto", "institutional adoption", "technical breakout"],
      market_impact: "High - Major market event expected",
    },
    {
      ticker: "KXHIGHPHIL-25NOV08-T71",
      market_question: "Will Philadelphia hit >71°F on Nov 8, 2025?",
      topic: "weather",
      decision: "BUY",
      technical_direction: "buy",
      market_p: 0.42,
      volatility_confidence: 0.65,
      volume_confidence: 0.58,
      momentum: "bullish",
      final_confidence: 0.72,
      reasoning: "Weather models show consistent warming trend. Historical data suggests 72% probability of hitting 71°F. Market is pricing at only 42%, creating a significant edge opportunity.",
      sentiment: {
        label: "positive",
        score: 68,
        confidence: "medium",
      },
      key_themes: ["weather", "climate patterns", "seasonal trends"],
      market_impact: "Medium - Regional weather event",
    },
    {
      ticker: "KX2028DRUN-28-JOSS",
      market_question: "Will Josh Shapiro run for 2028 Democratic nomination?",
      topic: "politics",
      decision: "PASS",
      technical_direction: null,
      market_p: 0.55,
      volatility_confidence: 0.45,
      volume_confidence: 0.52,
      momentum: "neutral",
      final_confidence: 0.48,
      reasoning: "Political markets are highly uncertain this far out. While Shapiro has strong credentials, 2028 is too distant for reliable prediction. Market pricing seems fair.",
      sentiment: {
        label: "neutral",
        score: 50,
        confidence: "low",
      },
      key_themes: ["politics", "elections", "long-term"],
      market_impact: "High - Major political event",
    },
    {
      ticker: "KXETHMAX M-25DEC01-5200",
      market_question: "Will Ethereum hit >$5,200 by Dec 1, 2025?",
      topic: "crypto",
      decision: "BUY",
      technical_direction: "buy",
      market_p: 0.38,
      volatility_confidence: 0.72,
      volume_confidence: 0.68,
      momentum: "bullish",
      final_confidence: 0.81,
      reasoning: "Ethereum showing strong fundamentals with upcoming upgrades. Technical analysis indicates bullish momentum. Market odds of 38% significantly undervalue the 81% probability we calculate.",
      sentiment: {
        label: "positive",
        score: 82,
        confidence: "high",
      },
      key_themes: ["crypto", "ethereum", "upgrades"],
      market_impact: "High - Major crypto market event",
    },
    {
      ticker: "SENATEFL-28-R",
      market_question: "Will Republicans win FL Senate seat in 2028?",
      topic: "politics",
      decision: "SHORT",
      technical_direction: "short",
      market_p: 0.68,
      volatility_confidence: 0.58,
      volume_confidence: 0.62,
      momentum: "bearish",
      final_confidence: 0.35,
      reasoning: "Market is overpricing Republican chances at 68%. Recent polling and demographic shifts suggest lower probability. Good short opportunity with 35% actual probability.",
      sentiment: {
        label: "negative",
        score: 32,
        confidence: "medium",
      },
      key_themes: ["politics", "elections", "senate"],
      market_impact: "High - Major political event",
    },
  ];
};

export type CardAction = "pass" | "trade" | "save" | "dismiss";

export interface CardState {
  pick: TradingPick;
  action: CardAction | null;
  index: number;
}

export function useTradingPicks() {
  const { preferences } = useUserPreferences();
  const [picks, setPicks] = useState<TradingPick[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [reviewedCount, setReviewedCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [savedPicks, setSavedPicks] = useState<TradingPick[]>([]);
  const [dismissedTickers, setDismissedTickers] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Simulate API call
    setLoading(true);
    setTimeout(() => {
      const allPicks = generateMockPicks();
      
      // Filter picks based on user's selected topics
      const filteredPicks = preferences?.topics && preferences.topics.length > 0
        ? allPicks.filter(pick => pick.topic && preferences.topics.includes(pick.topic))
        : allPicks;
      
      setPicks(filteredPicks);
      setLoading(false);
    }, 500);
  }, [preferences]);

  const handleSwipe = (action: CardAction) => {
    if (currentIndex >= picks.length) return;

    const currentPick = picks[currentIndex];

    switch (action) {
      case "pass":
        // Just move to next card
        break;
      case "trade":
        // Will be handled by TradeModal
        break;
      case "save":
        setSavedPicks((prev) => [...prev, currentPick]);
        break;
      case "dismiss":
        setDismissedTickers((prev) => {
          const newSet = new Set(prev);
          newSet.add(currentPick.ticker);
          return newSet;
        });
        break;
    }

    setCurrentIndex((prev) => prev + 1);
    setReviewedCount((prev) => prev + 1);
  };

  const getCurrentPick = (): TradingPick | null => {
    if (currentIndex >= picks.length) return null;
    return picks[currentIndex];
  };

  const hasMorePicks = currentIndex < picks.length;
  const totalPicks = picks.length;
  const progress = totalPicks > 0 ? (reviewedCount / totalPicks) * 100 : 0;

  return {
    currentPick: getCurrentPick(),
    hasMorePicks,
    totalPicks,
    reviewedCount,
    progress,
    loading,
    savedPicks,
    handleSwipe,
    reset: () => {
      setCurrentIndex(0);
      setReviewedCount(0);
      const allPicks = generateMockPicks();
      const filteredPicks = preferences?.topics && preferences.topics.length > 0
        ? allPicks.filter(pick => pick.topic && preferences.topics.includes(pick.topic))
        : allPicks;
      setPicks(filteredPicks);
    },
  };
}

