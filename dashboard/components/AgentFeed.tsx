"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAgentFeed } from "@/lib/useAgentFeed";
import { useToast } from "@/components/ui/use-toast";
import { formatPercent } from "@/lib/utils";
import { Check, X, Clock, TrendingUp, TrendingDown, Info } from "lucide-react";
import { AgentRecommendation } from "@/lib/types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

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

  const getActionText = () => {
    if (rec.action === "BUY_YES") return "Bet YES";
    if (rec.action === "BUY_NO") return "Bet NO";
    if (rec.action === "SELL_YES") return "Sell YES position";
    if (rec.action === "SELL_NO") return "Sell NO position";
    return "Wait - don't trade yet";
  };

  // Calculate current market odds (inverse of AI confidence for display)
  const currentOdds = rec.action.includes("YES") 
    ? Math.max(0.05, 1 - rec.edge - 0.1) 
    : Math.max(0.05, rec.edge + 0.1);

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
          <Badge variant="outline" className="text-xs">
            {rec.domain}
          </Badge>
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
              {getActionText()}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-muted/50 rounded p-2">
            <span className="text-muted-foreground block mb-1">AI thinks:</span>
            <span className="font-mono font-semibold text-sm">
              {formatPercent(rec.confidence)} likely
            </span>
          </div>
          <div className="bg-muted/50 rounded p-2">
            <span className="text-muted-foreground block mb-1">Current odds:</span>
            <span className="font-mono font-semibold text-sm">
              {formatPercent(currentOdds)}
            </span>
          </div>
        </div>

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
          <h3 className="text-lg font-semibold">Active Trade Recs</h3>
          <Dialog>
            <DialogTrigger asChild>
              <button className="text-muted-foreground hover:text-foreground transition-colors">
                <Info className="h-4 w-4" />
                <span className="sr-only">More info about Trade Recommendations</span>
              </button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Trade Recommendations</DialogTitle>
                <DialogDescription className="space-y-3">
                  <p>
                    Our AI analyzes markets in real-time and suggests next actions for the trades you are currently invested in. Here's what each part means:
                  </p>
                  <div className="space-y-2">
                    <div>
                      <strong className="text-foreground">AI thinks:</strong> This shows how confident our AI is that the event will happen. For example, "85% likely" means the AI believes there's an 85% chance this outcome will occur.
                    </div>
                    <div>
                      <strong className="text-foreground">Current odds:</strong> This is what the market is currently pricing the event at. If there's a big difference between what the AI thinks and the current odds, that could be a good trading opportunity.
                    </div>
                    <div>
                      <strong className="text-foreground">Actions:</strong>
                      <ul className="list-disc list-inside ml-2 mt-1">
                        <li><strong>Bet YES:</strong> Buy shares betting the event will happen</li>
                        <li><strong>Bet NO:</strong> Buy shares betting against the event</li>
                        <li><strong>Sell position:</strong> Close out an existing trade</li>
                      </ul>
                    </div>
                  </div>
                </DialogDescription>
              </DialogHeader>
            </DialogContent>
          </Dialog>
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
