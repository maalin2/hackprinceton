"use client";

import { useState } from "react";
import { SwipeCard } from "./SwipeCard";
import { TradeModal } from "./TradeModal";
import { useTradingPicks } from "@/lib/useTradingPicks";
import { useSavedPicks } from "@/lib/useSavedPicks";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useToast } from "@/components/ui/use-toast";
import { Target, CheckCircle2 } from "lucide-react";

export function TradingCardDeck() {
  const {
    currentPick,
    hasMorePicks,
    totalPicks,
    reviewedCount,
    progress,
    loading,
    handleSwipe,
    reset,
  } = useTradingPicks();
  const { savePick } = useSavedPicks();
  const [tradeModalOpen, setTradeModalOpen] = useState(false);
  const { toast } = useToast();

  const handleSwipeAction = async (action: "pass" | "trade" | "save" | "dismiss") => {
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
      description: `Trade order for $${amount.toFixed(2)} has been queued (paper trading)`,
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading your picks...</p>
        </div>
      </div>
    );
  }

  if (!hasMorePicks && reviewedCount === 0) {
    return (
      <Card className="p-8 text-center">
        <Target className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-lg font-semibold mb-2">No picks available</h3>
        <p className="text-muted-foreground mb-4">
          Check back later for new trading opportunities
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
        <CheckCircle2 className="h-12 w-12 mx-auto mb-4 text-green-600" />
        <h3 className="text-lg font-semibold mb-2">All done! 🎉</h3>
        <p className="text-muted-foreground mb-4">
          You've reviewed all {totalPicks} picks for today
        </p>
        <div className="flex gap-2 justify-center">
          <Button onClick={reset} variant="outline">
            Review Again
          </Button>
          <Button onClick={() => window.location.href = "/markets"}>
            Browse Markets
          </Button>
        </div>
      </Card>
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

