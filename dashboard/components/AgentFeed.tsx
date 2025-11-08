"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useRecommendations } from "@/lib/useRecommendations";
import { useToast } from "@/components/ui/use-toast";
import { DetailedRecommendationCard } from "./DetailedRecommendationCard";
import { RefreshCw, Loader2 } from "lucide-react";

export function AgentFeed() {
  const {
    recommendations,
    loading,
    processing,
    acceptRecommendation,
    snoozeRecommendation,
    dismissRecommendation,
    refresh,
  } = useRecommendations();
  const { toast } = useToast();

  const handleAccept = (id: string, marketTitle: string) => {
    acceptRecommendation(id);
    toast({
      title: "Position Queued",
      description: `Paper trade queued for: ${marketTitle}`,
    });
  };

  const handleSnooze = (id: string) => {
    snoozeRecommendation(id);
    toast({
      title: "Snoozed",
      description: "Recommendation will reappear in 30 seconds",
    });
  };

  const handleDismiss = (id: string) => {
    dismissRecommendation(id);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">Agent Recommendations</h3>
          <div
            className={`h-2 w-2 rounded-full ${
              processing ? "bg-yellow-500 animate-pulse" : "bg-green-500"
            }`}
            title={processing ? "Analyzing..." : "Ready"}
          />
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{recommendations.length} pending</Badge>
          <Button
            variant="ghost"
            size="icon"
            onClick={refresh}
            disabled={processing}
            title="Refresh analysis"
          >
            {processing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="text-sm text-muted-foreground text-center py-8">
          <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
          Analyzing markets...
        </div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {recommendations.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-sm text-muted-foreground text-center py-8"
              >
                <p className="mb-2">
                  No actionable recommendations at the moment.
                </p>
                <p className="text-xs">
                  The agents are monitoring markets continuously. Click refresh
                  to re-analyze.
                </p>
              </motion.div>
            ) : (
              recommendations.map((rec) => (
                <DetailedRecommendationCard
                  key={rec.id}
                  recommendation={rec}
                  onAccept={() => handleAccept(rec.id, rec.market.title)}
                  onSnooze={() => handleSnooze(rec.id)}
                  onDismiss={() => handleDismiss(rec.id)}
                />
              ))
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Agent Status Info */}
      <div className="text-xs text-muted-foreground pt-4 border-t space-y-1">
        <p>
          <span className="font-semibold">Multi-Agent System:</span> Quant +
          Sentiment Analysis
        </p>
        <p>
          <span className="font-semibold">Auto-refresh:</span> Every 60 seconds
        </p>
        <p>
          <span className="font-semibold">Action threshold:</span> ±8% edge
          minimum
        </p>
      </div>
    </div>
  );
}
