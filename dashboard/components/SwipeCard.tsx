"use client";

import { useState, useRef, useEffect } from "react";
import { motion, useMotionValue, useTransform, PanInfo } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { TradingPick } from "@/lib/types";
import { formatPercent } from "@/lib/utils";
import { ArrowLeft, ArrowRight, ArrowUp, ArrowDown, X, Bookmark } from "lucide-react";
import { cn } from "@/lib/utils";
import { PREFERENCE_TOPICS } from "@/lib/preferenceTopics";

interface SwipeCardProps {
  pick: TradingPick;
  onSwipe: (action: "pass" | "trade" | "save" | "dismiss") => void;
  index: number;
  total: number;
  tradeModalOpen?: boolean; // Track if trade modal is open
}

const SWIPE_THRESHOLD = 100;
const ROTATION_MULTIPLIER = 0.1;

export function SwipeCard({ pick, onSwipe, index, total, tradeModalOpen = false }: SwipeCardProps) {
  const [isExiting, setIsExiting] = useState(false);
  const [wasModalOpen, setWasModalOpen] = useState(false);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotate = useTransform(x, [-300, 300], [-30, 30]);
  const opacity = useTransform(x, [-300, -SWIPE_THRESHOLD, 0, SWIPE_THRESHOLD, 300], [0, 1, 1, 1, 0]);

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

  const handleDragEnd = (_: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const swipeDistance = Math.abs(info.offset.x);
    const verticalDistance = Math.abs(info.offset.y);

    if (isExiting) return;

    // Vertical swipes (up/down) take priority
    if (verticalDistance > SWIPE_THRESHOLD) {
      if (info.offset.y < 0) {
        // Swipe up - Save
        setIsExiting(true);
        onSwipe("save");
      } else {
        // Swipe down - Dismiss
        setIsExiting(true);
        onSwipe("dismiss");
      }
      return;
    }

    // Horizontal swipes
    if (swipeDistance > SWIPE_THRESHOLD) {
      if (info.offset.x > 0) {
        // Swipe right - Trade (don't exit yet, wait for confirmation)
        onSwipe("trade");
        // Don't set isExiting - card will exit only after trade is confirmed
      } else {
        // Swipe left - Pass
        setIsExiting(true);
        onSwipe("pass");
      }
    } else {
      // Spring back to center
      x.set(0);
      y.set(0);
    }
  };

  const handleButtonClick = (action: "pass" | "trade" | "save" | "dismiss") => {
    if (isExiting) return;
    if (action === "trade") {
      // Don't exit for trade - wait for confirmation
      onSwipe("trade");
    } else {
      setIsExiting(true);
      onSwipe(action);
    }
  };

  // Reset position when pick changes
  useEffect(() => {
    x.set(0);
    y.set(0);
    setIsExiting(false);
  }, [pick.ticker, x, y]);

  // Track modal state changes
  useEffect(() => {
    if (tradeModalOpen) {
      setWasModalOpen(true);
    } else if (wasModalOpen) {
      // Modal was open and now closed - reset card position
      x.set(0);
      y.set(0);
      setIsExiting(false);
      setWasModalOpen(false);
    }
  }, [tradeModalOpen, wasModalOpen, x, y]);

  // Handle keyboard arrow keys
  useEffect(() => {
    if (tradeModalOpen || isExiting) return; // Don't handle keys when modal is open or card is exiting

    const handleKeyDown = (event: KeyboardEvent) => {
      // Only handle arrow keys
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) {
        return;
      }

      // Prevent default scrolling behavior
      event.preventDefault();

      switch (event.key) {
        case "ArrowLeft":
          // Pass
          setIsExiting(true);
          onSwipe("pass");
          break;
        case "ArrowRight":
          // Trade
          onSwipe("trade");
          break;
        case "ArrowUp":
          // Save
          setIsExiting(true);
          onSwipe("save");
          break;
        case "ArrowDown":
          // Dismiss
          setIsExiting(true);
          onSwipe("dismiss");
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [tradeModalOpen, isExiting, onSwipe]);

  return (
    <motion.div
      className="relative w-full mx-auto"
      style={{
        x,
        y,
        rotate,
        opacity,
        zIndex: total - index,
      }}
      drag={!tradeModalOpen} // Disable dragging when modal is open
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0.2}
      onDragEnd={handleDragEnd}
      animate={isExiting ? { scale: 0.8, opacity: 0 } : { scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <Card className="p-6 pt-5 space-y-5 cursor-grab active:cursor-grabbing touch-none min-h-[480px]">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              💡 AI Pick #{index + 1} of {total}
            </Badge>
          </div>
          {topicInfo && (
            <Badge variant="secondary" className="text-xs">
              {topicInfo.emoji} {topicInfo.name}
            </Badge>
          )}
        </div>

        {/* Market Question */}
        <div className="space-y-3">
          <h3 className="text-2xl font-bold leading-tight">
            {pick.market_question || pick.ticker}
          </h3>
          {pick.market_question && (
            <p className="text-sm text-muted-foreground font-mono">
              {pick.ticker}
            </p>
          )}
        </div>

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
            {pick.decision === "BUY" && pick.technical_direction === "buy" && "📈 Recommended: BUY YES"}
            {pick.decision === "SHORT" && pick.technical_direction === "short" && "📉 Recommended: BUY NO"}
            {pick.decision === "BUY" && !pick.technical_direction && "📈 Recommended: BUY"}
            {pick.decision === "SHORT" && !pick.technical_direction && "📉 Recommended: SHORT"}
            {pick.decision === "PASS" && "⏸️ Recommendation: PASS"}
          </Badge>
        </div>
        
        {/* Grok Sentiment Display */}
        {pick.sentiment && (
          <div className="bg-muted/50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">🤖 Grok Sentiment:</span>
              <div className="flex items-center gap-2">
                {pick.sentiment.label !== "none" ? (
                  <>
                    <Badge 
                      variant={pick.sentiment.label === "positive" ? "default" : pick.sentiment.label === "negative" ? "destructive" : "outline"}
                      className="text-xs"
                    >
                      {pick.sentiment.label} ({pick.sentiment.score}%)
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {pick.sentiment.confidence} confidence
                    </Badge>
                  </>
                ) : (
                  <Badge variant="outline" className="text-xs text-muted-foreground">
                    Not available
                  </Badge>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Reasoning */}
        <div className="space-y-3">
          <h4 className="text-base font-semibold flex items-center gap-2">
            📊 Why this pick?
          </h4>
          <p className="text-base text-muted-foreground line-clamp-4">
            {pick.reasoning}
          </p>
        </div>

        {/* Swipe Hints (Desktop) */}
        <div className="hidden md:flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
          <div className="flex items-center gap-1">
            <ArrowLeft className="h-3 w-3" />
            <span>Pass</span>
          </div>
          <div className="flex items-center gap-1">
            <ArrowUp className="h-3 w-3" />
            <span>Save</span>
          </div>
          <div className="flex items-center gap-1">
            <ArrowDown className="h-3 w-3" />
            <span>Dismiss</span>
          </div>
          <div className="flex items-center gap-1">
            <ArrowRight className="h-3 w-3" />
            <span>Trade</span>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}

