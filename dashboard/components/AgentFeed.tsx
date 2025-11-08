"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAgentFeed } from "@/lib/useAgentFeed";
import { useToast } from "@/components/ui/use-toast";
import { formatPercent } from "@/lib/utils";
import { Check, X, Clock, TrendingUp, TrendingDown } from "lucide-react";
import { AgentRecommendation } from "@/lib/types";

function RecommendationCard({ rec }: { rec: AgentRecommendation }) {
  const { acceptRecommendation, snoozeRecommendation, dismissRecommendation } =
    useAgentFeed();
  const { toast } = useToast();

  const handleAccept = () => {
    acceptRecommendation(rec.id);
    toast({
      title: "Order Queued",
      description: `${rec.action} on ${rec.ticker} (paper trading)`,
    });
  };

  const handleSnooze = () => {
    snoozeRecommendation(rec.id);
    toast({
      title: "Snoozed",
      description: "Recommendation will reappear in 10 seconds",
    });
  };

  const handleDismiss = () => {
    dismissRecommendation(rec.id);
  };

  const getActionColor = () => {
    if (rec.action.includes("BUY")) return "text-green-600 dark:text-green-400";
    if (rec.action.includes("SELL")) return "text-red-600 dark:text-red-400";
    return "text-muted-foreground";
  };

  const getActionIcon = () => {
    if (rec.action.includes("BUY")) return TrendingUp;
    if (rec.action.includes("SELL")) return TrendingDown;
    return Clock;
  };

  const ActionIcon = getActionIcon();

  if (rec.status !== "pending") return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ type: "spring", damping: 25, stiffness: 300 }}
    >
      <Card className="p-4 space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {rec.domain}
            </Badge>
            <Badge
              variant={rec.priority === "high" ? "destructive" : "secondary"}
              className="text-xs"
            >
              {rec.priority}
            </Badge>
          </div>
          <span className="text-xs text-muted-foreground">
            {rec.timestamp.toLocaleTimeString()}
          </span>
        </div>

        <div>
          <p className="font-medium text-sm truncate">{rec.market}</p>
          <p className="text-xs text-muted-foreground">{rec.ticker}</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <ActionIcon className={`h-4 w-4 ${getActionColor()}`} />
            <span className={`font-semibold text-sm ${getActionColor()}`}>
              {rec.action.replace("_", " ")}
            </span>
          </div>
          <div className="text-xs">
            <span className="text-muted-foreground">Edge: </span>
            <span className="font-mono font-semibold">
              {formatPercent(rec.edge)}
            </span>
          </div>
          <div className="text-xs">
            <span className="text-muted-foreground">Conf: </span>
            <span className="font-mono font-semibold">
              {formatPercent(rec.confidence)}
            </span>
          </div>
        </div>

        <p className="text-xs text-muted-foreground">{rec.rationale}</p>

        <div className="flex gap-2">
          <Button size="sm" className="flex-1" onClick={handleAccept}>
            <Check className="h-3 w-3 mr-1" />
            Accept
          </Button>
          <Button size="sm" variant="outline" onClick={handleSnooze}>
            <Clock className="h-3 w-3 mr-1" />
            Snooze
          </Button>
          <Button size="sm" variant="ghost" onClick={handleDismiss}>
            <X className="h-3 w-3" />
          </Button>
        </div>
      </Card>
    </motion.div>
  );
}

export function AgentFeed() {
  const { recommendations, loading, wsConnected } = useAgentFeed();

  const pendingRecs = recommendations.filter((r) => r.status === "pending");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">Agent Recommendations</h3>
          <div
            className={`h-2 w-2 rounded-full ${
              wsConnected ? "bg-green-500" : "bg-gray-400"
            }`}
            title={wsConnected ? "Connected" : "Disconnected"}
          />
        </div>
        <Badge variant="secondary">{pendingRecs.length} pending</Badge>
      </div>

      {loading ? (
        <div className="text-sm text-muted-foreground">Loading feed...</div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {pendingRecs.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-sm text-muted-foreground text-center py-8"
              >
                No pending recommendations. The agent is monitoring markets...
              </motion.div>
            ) : (
              pendingRecs.map((rec) => (
                <RecommendationCard key={rec.id} rec={rec} />
              ))
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
