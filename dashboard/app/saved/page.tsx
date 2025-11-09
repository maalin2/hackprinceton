"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useSavedPicks } from "@/lib/useSavedPicks";
import { TradingPick } from "@/lib/types";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { TradeModal } from "@/components/TradeModal";
import { formatPercent } from "@/lib/utils";
import { Bookmark, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  consumeSkipOnboardingRedirect,
  useUserPreferences,
} from "@/lib/useUserPreferences";
import { useToast } from "@/components/ui/use-toast";
import { PREFERENCE_TOPICS } from "@/lib/preferenceTopics";

function SavedPickCard({ pick, onRemove }: { pick: TradingPick; onRemove: (ticker: string) => void }) {
  const { toast } = useToast();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tradeModalOpen, setTradeModalOpen] = useState(false);

  const getConfidenceLabel = (confidence: number): { label: string; color: string } => {
    if (confidence >= 0.7) return { label: "High", color: "text-green-600 dark:text-green-400" };
    if (confidence >= 0.5) return { label: "Medium", color: "text-yellow-600 dark:text-yellow-400" };
    return { label: "Low", color: "text-red-600 dark:text-red-400" };
  };

  const confidenceInfo = getConfidenceLabel(pick.final_confidence);

  const getTopicInfo = () => {
    if (!pick.topic) return null;
    return PREFERENCE_TOPICS.find(t => t.id === pick.topic);
  };

  const topicInfo = getTopicInfo();

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent opening dialog when clicking remove
    onRemove(pick.ticker);
    toast({
      title: "Removed",
      description: "Pick removed from saved list",
    });
  };

  const handleTrade = () => {
    setDialogOpen(false);
    setTradeModalOpen(true);
  };

  const handleTradeConfirm = (amount: number) => {
    setTradeModalOpen(false);
    toast({
      title: "Trade Queued",
      description: `Trade order for $${amount.toFixed(2)} has been queued (paper trading)`,
    });
  };

  return (
    <>
      <Card 
        className="hover:shadow-lg transition-shadow cursor-pointer"
        onClick={() => setDialogOpen(true)}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              {topicInfo && (
                <Badge variant="secondary" className="text-xs mb-2">
                  {topicInfo.emoji} {topicInfo.name}
                </Badge>
              )}
              <h3 className="font-semibold text-lg mb-1">
                {pick.market_question || pick.ticker}
              </h3>
              {pick.market_question && (
                <p className="text-xs text-muted-foreground font-mono">
                  {pick.ticker}
                </p>
              )}
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleRemove}
              className="shrink-0"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Odds and Confidence */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-muted/50 rounded-lg p-3">
              <p className="text-xs text-muted-foreground mb-1">Current odds</p>
              <p className="text-lg font-mono font-bold">
                {formatPercent(pick.market_p)}
              </p>
            </div>
            <div className="bg-muted/50 rounded-lg p-3">
              <p className="text-xs text-muted-foreground mb-1">AI confidence</p>
              <p className={cn("text-lg font-mono font-bold", confidenceInfo.color)}>
                {confidenceInfo.label} ({formatPercent(pick.final_confidence)})
              </p>
            </div>
          </div>

          {/* Decision Badge */}
          <div className="flex items-center justify-center">
            <Badge
              variant={pick.decision === "BUY" ? "default" : pick.decision === "SHORT" ? "destructive" : "outline"}
              className="text-sm px-4 py-1"
            >
              {pick.decision === "BUY" && "📈 Recommended: BUY"}
              {pick.decision === "SHORT" && "📉 Recommended: SHORT"}
              {pick.decision === "PASS" && "⏸️ Recommendation: PASS"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Detail Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
              </div>
              {topicInfo && (
                <Badge variant="secondary" className="text-xs">
                  {topicInfo.emoji} {topicInfo.name}
                </Badge>
              )}
            </div>
            <DialogTitle className="mt-4">
              {pick.market_question || pick.ticker}
            </DialogTitle>
            {pick.market_question && (
              <DialogDescription className="font-mono">
                {pick.ticker}
              </DialogDescription>
            )}
          </DialogHeader>

          <div className="space-y-5 py-4">
            {/* Odds and Confidence */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-muted/50 rounded-lg p-4">
                <p className="text-sm text-muted-foreground mb-2">Current odds</p>
                <p className="text-2xl font-mono font-bold">
                  {formatPercent(pick.market_p)}
                </p>
              </div>
              <div className="bg-muted/50 rounded-lg p-4">
                <p className="text-sm text-muted-foreground mb-2">AI confidence</p>
                <p className={cn("text-2xl font-mono font-bold", confidenceInfo.color)}>
                  {confidenceInfo.label} ({formatPercent(pick.final_confidence)})
                </p>
              </div>
            </div>

            {/* Decision Badge */}
            <div className="flex items-center justify-center">
              <Badge
                variant={pick.decision === "BUY" ? "default" : pick.decision === "SHORT" ? "destructive" : "outline"}
                className="text-sm px-4 py-1"
              >
                {pick.decision === "BUY" && "📈 Recommended: BUY"}
                {pick.decision === "SHORT" && "📉 Recommended: SHORT"}
                {pick.decision === "PASS" && "⏸️ Recommendation: PASS"}
              </Badge>
            </div>

            {/* Reasoning */}
            <div className="space-y-3">
              <h4 className="text-base font-semibold flex items-center gap-2">
                📊 Why this pick?
              </h4>
              <p className="text-base text-muted-foreground">
                {pick.reasoning}
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button onClick={handleTrade}>
              Trade
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Trade Modal */}
      <TradeModal
        pick={pick}
        open={tradeModalOpen}
        onOpenChange={setTradeModalOpen}
        onConfirm={handleTradeConfirm}
      />
    </>
  );
}

export default function SavedPicksPage() {
  const router = useRouter();
  const { preferences, loading: prefsLoading } = useUserPreferences();
  const { savedPicks, loading, removePick } = useSavedPicks();
  const skipRedirectRef = useRef(false);

  useEffect(() => {
    if (!prefsLoading && !preferences) {
      if (!skipRedirectRef.current) {
        const shouldSkip = consumeSkipOnboardingRedirect();
        if (shouldSkip) {
          skipRedirectRef.current = true;
          return;
        }
      } else {
        return;
      }
      router.replace("/onboarding");
    }
  }, [prefsLoading, preferences, router]);

  useEffect(() => {
    if (preferences) {
      skipRedirectRef.current = false;
    }
  }, [preferences]);

  if (prefsLoading || !preferences) {
    return (
      <div className="container py-6">
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Loading saved picks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Saved Picks</h1>
        <p className="text-muted-foreground">
          Review your saved trading opportunities
        </p>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-48" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : savedPicks.length === 0 ? (
        <Card className="p-12 text-center">
          <Bookmark className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-xl font-semibold mb-2">No saved picks yet</h3>
          <p className="text-muted-foreground mb-6">
            Swipe up on trading cards to save them for later review
          </p>
          <Button onClick={() => router.push("/dashboard")}>
            Go to Dashboard
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {savedPicks.map((pick) => (
            <SavedPickCard
              key={`${pick.ticker}-${pick.market_question}`}
              pick={pick}
              onRemove={removePick}
            />
          ))}
        </div>
      )}
    </div>
  );
}

