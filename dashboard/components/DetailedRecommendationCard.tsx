"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RecommendationWithMarket } from "@/lib/useRecommendations";
import { formatPercent } from "@/lib/utils";
import {
  Check,
  X,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronDown,
  ChevronUp,
  ExternalLink,
} from "lucide-react";

interface Props {
  recommendation: RecommendationWithMarket;
  onAccept: () => void;
  onSnooze: () => void;
  onDismiss: () => void;
}

export function DetailedRecommendationCard({
  recommendation,
  onAccept,
  onSnooze,
  onDismiss,
}: Props) {
  const { market, decision } = recommendation;
  const [showSources, setShowSources] = useState(false);

  const getActionIcon = () => {
    if (decision.action === "BUY_YES") return TrendingUp;
    if (decision.action === "BUY_NO") return TrendingDown;
    return Minus;
  };

  const getActionColor = () => {
    if (decision.action === "BUY_YES")
      return "text-green-600 dark:text-green-400";
    if (decision.action === "BUY_NO") return "text-red-600 dark:text-red-400";
    return "text-muted-foreground";
  };

  const getEdgeColor = () => {
    if (Math.abs(decision.edge) >= 0.2) return "bg-purple-600 text-white";
    if (Math.abs(decision.edge) >= 0.1) return "bg-blue-600 text-white";
    return "bg-green-600 text-white";
  };

  const ActionIcon = getActionIcon();

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ type: "spring", damping: 25, stiffness: 300 }}
    >
      <Card className="p-4 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" className="text-xs">
              {market.domain}
            </Badge>
            <Badge className={getEdgeColor()}>
              {formatPercent(Math.abs(decision.edge))} edge
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {formatPercent(decision.confidence)} conf
            </Badge>
          </div>
          <span className="text-xs text-muted-foreground shrink-0">
            {decision.timestamp.toLocaleTimeString()}
          </span>
        </div>

        {/* Market Info */}
        <div>
          <p className="font-medium text-sm line-clamp-2">{market.title}</p>
          <div className="flex items-center gap-2 mt-1.5">
            <p className="text-xs text-muted-foreground">{market.ticker}</p>
            <a
              href={market.url || `https://kalshi.com/markets/${market.ticker}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-2 py-1 text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/30 hover:bg-blue-100 dark:hover:bg-blue-950/50 rounded-md border border-blue-200 dark:border-blue-800 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
              onClick={(e) => e.stopPropagation()}
            >
              <span>View on Kalshi</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </div>
        </div>

        {/* Decision Action */}
        <div className="flex items-center gap-2 p-3 rounded-lg bg-muted/50">
          <ActionIcon className={`h-5 w-5 ${getActionColor()}`} />
          <div className="flex-1">
            <span className={`font-semibold text-sm ${getActionColor()}`}>
              {decision.action.replace("_", " ")}
            </span>
          </div>
        </div>

        {/* Probabilities Grid */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="space-y-1">
            <p className="text-muted-foreground">Market Price</p>
            <p className="font-mono font-semibold">
              {formatPercent(decision.pMarket)}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-muted-foreground">Combined Model</p>
            <p className="font-mono font-semibold">
              {formatPercent(decision.pCombined)}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-muted-foreground">Quant Signal</p>
            <p className="font-mono font-semibold">
              {formatPercent(decision.pQuant)}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-muted-foreground">Sentiment</p>
            <p className="font-mono font-semibold">
              {formatPercent(decision.pSent)}
            </p>
          </div>
        </div>

        {/* Source Chips */}
        <div className="flex flex-wrap gap-1.5">
          {decision.sources.map((source, idx) => (
            <Badge key={idx} variant="outline" className="text-xs px-2 py-0.5">
              {source}
            </Badge>
          ))}
        </div>

        {/* Rationale */}
        <div className="rounded-lg bg-muted/50 p-3">
          <p className="text-xs leading-relaxed">{decision.rationale}</p>
        </div>

        {/* Sentiment Sources Expandable */}
        {decision.sentimentSignal?.rawData && (
          <div className="border-t pt-3">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-2 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors w-full"
            >
              {showSources ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
              <span>
                Sentiment Sources ({decision.sentimentSignal.nSamples} samples)
              </span>
            </button>

            {showSources && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 space-y-3"
              >
                {/* Kalshi Comments */}
                {decision.sentimentSignal.rawData.comments.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs font-semibold text-muted-foreground">
                      📝 Kalshi Comments (
                      {decision.sentimentSignal.rawData.comments.length})
                    </p>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {decision.sentimentSignal.rawData.comments.map(
                        (comment, idx) => (
                          <div
                            key={idx}
                            className="rounded-md bg-muted/30 p-2 space-y-1 text-xs"
                          >
                            <p className="leading-relaxed">
                              &quot;{comment.text}&quot;
                            </p>
                            <div className="flex items-center gap-2 text-muted-foreground">
                              <span>👤 {comment.author}</span>
                              <span>•</span>
                              <a
                                href={comment.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 hover:text-foreground transition-colors"
                              >
                                View
                                <ExternalLink className="h-3 w-3" />
                              </a>
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {/* Twitter Posts */}
                {decision.sentimentSignal.rawData.tweets.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs font-semibold text-muted-foreground">
                      🐦 Twitter Posts (
                      {decision.sentimentSignal.rawData.tweets.length})
                    </p>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {decision.sentimentSignal.rawData.tweets.map(
                        (tweet, idx) => (
                          <div
                            key={idx}
                            className="rounded-md bg-muted/30 p-2 space-y-1 text-xs"
                          >
                            <p className="leading-relaxed">
                              &quot;{tweet.text}&quot;
                            </p>
                            <div className="flex items-center gap-2 text-muted-foreground">
                              <span>👤 {tweet.author}</span>
                              <span>•</span>
                              <span>❤️ {tweet.likes}</span>
                              <span>•</span>
                              <a
                                href={tweet.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 hover:text-foreground transition-colors"
                              >
                                View
                                <ExternalLink className="h-3 w-3" />
                              </a>
                            </div>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2">
          <Button size="sm" className="flex-1" onClick={onAccept}>
            <Check className="h-3 w-3 mr-1" />
            Accept
          </Button>
          <Button size="sm" variant="outline" onClick={onSnooze}>
            <Clock className="h-3 w-3 mr-1" />
            Snooze
          </Button>
          <Button size="sm" variant="ghost" onClick={onDismiss}>
            <X className="h-3 w-3" />
          </Button>
        </div>
      </Card>
    </motion.div>
  );
}
