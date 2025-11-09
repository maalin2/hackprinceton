"use client";

import { useState, useMemo } from "react";
import { SwipeCard } from "./SwipeCard";
import { TradeModal } from "./TradeModal";
import { useRecommendations } from "@/lib/useRecommendations";
import { useSavedPicks } from "@/lib/useSavedPicks";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { Target, CheckCircle2 } from "lucide-react";
import { TradingPick } from "@/lib/types";

export function TradingCardDeck() {
  // Use real recommendations from Python backend (no mock data!)
  const {
    recommendations,
    loading,
    processing,
    acceptRecommendation,
    dismissRecommendation,
    getMoreRecommendations,
  } = useRecommendations();

  const [currentIndex, setCurrentIndex] = useState(0);

  // Convert recommendations to TradingPick format
  const picks: TradingPick[] = useMemo(() => {
    if (recommendations.length > 0) {
      console.log(
        `\n🎴 TradingCardDeck: Converting ${recommendations.length} REAL recommendations from Python API`
      );
      console.log("   Source: Python Backend (hybrid_analysis.py)");
      console.log("   Data: Statistical + Grok AI Sentiment");
      console.log("   NO MOCK DATA - All events are real from Kalshi!\n");
    }
    const allPicks = recommendations.map((rec) => {
      // Determine decision type
      let decision: "BUY" | "SHORT" | "PASS";
      if (rec.decision.action === "BUY_YES") {
        decision = "BUY";
      } else if (rec.decision.action === "BUY_NO") {
        decision = "SHORT";
      } else {
        decision = "PASS";
      }

      // Get Grok sentiment if available
      const grokSentiment = rec.decision.sentimentSignal;
      const hasGrokData = grokSentiment !== undefined && grokSentiment !== null;
      const grokScore = hasGrokData ? grokSentiment.pSent : rec.decision.pSent;

      // Determine if we have real Grok data (not just fallback)
      // If pSent is exactly 0.5 and no sentimentSignal, it's likely a fallback
      const isGrokFallback = !hasGrokData && rec.decision.pSent === 0.5;

      console.log(`   🔍 Grok check for ${rec.market.ticker}:`, {
        hasGrokData,
        sentimentSignal: rec.decision.sentimentSignal,
        pSent: rec.decision.pSent,
        isGrokFallback,
      });

      return {
        ticker: rec.market.ticker,
        market_question: rec.market.title,
        topic: rec.market.domain.toLowerCase(),
        decision: decision,
        technical_direction: (rec.decision.action === "BUY_YES"
          ? "buy"
          : rec.decision.action === "BUY_NO"
          ? "short"
          : null) as "buy" | "short" | null,
        market_p: rec.decision.pMarket,
        volatility_confidence: rec.decision.confidence,
        volume_confidence: rec.decision.confidence,
        momentum: (rec.decision.edge > 0
          ? "bullish"
          : rec.decision.edge < 0
          ? "bearish"
          : "neutral") as "bullish" | "bearish" | "neutral",
        final_confidence: rec.decision.confidence,
        reasoning: rec.decision.rationale,
        sentiment:
          hasGrokData && !isGrokFallback
            ? {
                label: (grokScore > 0.6
                  ? "positive"
                  : grokScore < 0.4
                  ? "negative"
                  : "neutral") as "positive" | "negative" | "neutral",
                score: Math.round(grokScore * 100),
                confidence: (grokSentiment.confidence > 0.7
                  ? "high"
                  : grokSentiment.confidence > 0.5
                  ? "medium"
                  : "low") as "high" | "medium" | "low",
              }
            : {
                label: "neutral" as const,
                score: 0,
                confidence: "low" as const,
              },
        key_themes: rec.decision.sources || [],
        market_impact:
          Math.abs(rec.decision.edge) > 0.2
            ? "High - Significant edge opportunity"
            : "Medium - Moderate edge opportunity",
      };
    });

    // Sort by final_confidence (descending) and take top 5
    const topPicks = allPicks
      .sort((a, b) => b.final_confidence - a.final_confidence)
      .slice(0, 5);

    if (topPicks.length > 0) {
      console.log(`\n✨ Filtered to top ${topPicks.length} highest confidence picks`);
      console.log("   Confidence range:", {
        highest: topPicks[0]?.final_confidence.toFixed(2),
        lowest: topPicks[topPicks.length - 1]?.final_confidence.toFixed(2),
      });
    }

    return topPicks;
  }, [recommendations]);

  const currentPick = picks[currentIndex] || null;
  const hasMorePicks = currentIndex < picks.length;
  const totalPicks = picks.length;
  const reviewedCount = currentIndex;
  const progress = totalPicks > 0 ? (reviewedCount / totalPicks) * 100 : 0;

  const handleSwipe = (action: "pass" | "trade" | "save" | "dismiss") => {
    if (currentIndex < picks.length && action === "trade") {
      // Accept the recommendation
      const rec = recommendations[currentIndex];
      if (rec) {
        acceptRecommendation(rec.id);
      }
    } else if (currentIndex < picks.length && action === "dismiss") {
      // Dismiss the recommendation
      const rec = recommendations[currentIndex];
      if (rec) {
        dismissRecommendation(rec.id);
      }
    }

    // Move to next card
    setCurrentIndex((prev) => prev + 1);
  };

  const reset = () => {
    setCurrentIndex(0);
  };
  const { savePick } = useSavedPicks();
  const [tradeModalOpen, setTradeModalOpen] = useState(false);
  const { toast } = useToast();

  const handleSwipeAction = async (
    action: "pass" | "trade" | "save" | "dismiss"
  ) => {
    if (action === "trade") {
      setTradeModalOpen(true);
    } else {
      handleSwipe(action);
      if (action === "save" && currentPick) {
        const success = await savePick(currentPick);
        if (success) {
          toast({
            title: "Saved",
            description: "Pick saved for later review",
          });
        } else {
          toast({
            title: "Error",
            description: "Failed to save pick. Please try again.",
            variant: "destructive",
          });
        }
      } else if (action === "dismiss") {
        toast({
          title: "Dismissed",
          description: "Won't show this topic again",
        });
      }
    }
  };

  const handleTradeConfirm = (amount: number) => {
    // Close modal first, then handle swipe (which will exit the card)
    setTradeModalOpen(false);
    handleSwipe("trade");
    toast({
      title: "Trade Queued",
      description: `Trade order for $${amount.toFixed(
        2
      )} has been queued (paper trading)`,
    });
  };

  if (loading) {
    console.log(
      "🔄 TradingCardDeck: Fetching REAL recommendations from Python backend..."
    );
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">
            {processing
              ? "Waiting for new recommendations..."
              : "Loading real picks from API..."}
          </p>
        </div>
      </div>
    );
  }

  if (!hasMorePicks && reviewedCount === 0) {
    console.log(
      "⚠️  TradingCardDeck: No recommendations available from Python backend"
    );
    console.log("   Make sure api_server.py is running!");
    return (
      <Card className="p-8 text-center">
        <Target className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-lg font-semibold mb-2">No picks available</h3>
        <p className="text-muted-foreground mb-4">
          Waiting for recommendations from Python backend...
        </p>
        <Button onClick={reset} variant="outline">
          Refresh
        </Button>
      </Card>
    );
  }

  if (!hasMorePicks) {
    return (
      <Card className="p-8 text-center">
        <CheckCircle2 className="h-12 w-12 mx-auto mb-4 text-purple-600" />
        <h3 className="text-lg font-semibold mb-2">All done! 🎉</h3>
        <p className="text-muted-foreground mb-4">
          You've reviewed all {totalPicks} picks for today
        </p>
        <div className="flex gap-2 justify-center">
          <Button
            onClick={() => {
              reset();
              getMoreRecommendations();
            }}
            variant="outline"
          >
            Get More Recommendations
          </Button>
          <Button onClick={() => (window.location.href = "/markets")}>
            Browse Markets
          </Button>
        </div>
      </Card>
    );
  }

  // Log current card being displayed
  if (currentPick && currentIndex < recommendations.length) {
    const rec = recommendations[currentIndex];
    console.log(`\n📇 Displaying Card ${currentIndex + 1}/${totalPicks}`);
    console.log(`   Ticker: ${currentPick.ticker}`);
    console.log(`   Market: ${currentPick.market_question}`);
    console.log(
      `   Action: ${rec.decision.action} → Display: ${currentPick.decision}`
    );
    console.log(
      `   🤖 Grok Sentiment: ${currentPick.sentiment.label} (${currentPick.sentiment.score}%)`
    );
    if (rec.decision.sentimentSignal) {
      console.log(
        `      ✅ Grok data available: ${JSON.stringify(
          rec.decision.sentimentSignal,
          null,
          2
        )}`
      );
    } else {
      console.log(`      ❌ No Grok sentimentSignal in decision object`);
      console.log(`      pSent value: ${rec.decision.pSent}`);
    }
    console.log(`   Source: Python Backend - REAL DATA`);
    console.log(
      `   🔗 Kalshi: https://kalshi.com/markets/${currentPick.ticker}`
    );
  }

  return (
    <div>
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            {reviewedCount} of {totalPicks} picks reviewed
          </span>
          <span className="font-medium">{Math.round(progress)}%</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Swipe Card Stack */}
      <div className="relative min-h-[600px] flex items-start justify-center pt-4">
        {currentPick && (
          <SwipeCard
            pick={currentPick}
            onSwipe={handleSwipeAction}
            index={reviewedCount}
            total={totalPicks}
            tradeModalOpen={tradeModalOpen}
          />
        )}
      </div>

      {/* Trade Modal */}
      {currentPick && (
        <TradeModal
          pick={currentPick}
          open={tradeModalOpen}
          onOpenChange={setTradeModalOpen}
          onConfirm={handleTradeConfirm}
        />
      )}
    </div>
  );
}
