"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { useUIStore } from "@/store/ui";
import { usePositions } from "@/lib/usePositions";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { Position } from "@/lib/types";

export function PositionDrawer() {
  const { selectedPositionId, setSelectedPositionId } = useUIStore();
  const { positions } = usePositions("all");
  const [position, setPosition] = useState<Position | null>(null);

  useEffect(() => {
    if (selectedPositionId) {
      const found = positions.find((p) => p.id === selectedPositionId);
      setPosition(found || null);
    } else {
      setPosition(null);
    }
  }, [selectedPositionId, positions]);

  return (
    <AnimatePresence>
      {position && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/80"
            onClick={() => setSelectedPositionId(null)}
          />
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 z-50 h-full w-full max-w-lg border-l bg-background p-6 shadow-lg overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold">Position Details</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSelectedPositionId(null)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-6">
              {/* Market Info */}
              <div>
                <p className="text-sm text-muted-foreground mb-1">Market</p>
                <p className="font-medium">{position.market}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {position.ticker}
                </p>
              </div>

              {/* Position Details */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Side</p>
                  <Badge
                    variant={position.side === "YES" ? "default" : "secondary"}
                    className="mt-1"
                  >
                    {position.side}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <Badge variant="outline" className="mt-1 capitalize">
                    {position.status}
                  </Badge>
                </div>
              </div>

              {/* Pricing */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Entry Price</p>
                  <p className="text-lg font-mono font-semibold">
                    {formatPercent(position.entry)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Mark Price</p>
                  <p className="text-lg font-mono font-semibold">
                    {formatPercent(position.mark)}
                  </p>
                </div>
              </div>

              {/* Size & P&L */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Position Size</p>
                  <p className="text-lg font-mono font-semibold">
                    {position.size}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">P&L</p>
                  <p
                    className={`text-lg font-mono font-semibold ${
                      position.pnl >= 0
                        ? "text-green-600 dark:text-green-400"
                        : "text-red-600 dark:text-red-400"
                    }`}
                  >
                    {formatCurrency(position.pnl)}
                  </p>
                </div>
              </div>

              {/* Edge */}
              <div>
                <p className="text-sm text-muted-foreground">Edge</p>
                <p className="text-lg font-mono font-semibold">
                  {formatPercent(position.edge)}
                </p>
              </div>

              {/* Rationale */}
              {position.rationale && (
                <div>
                  <p className="text-sm text-muted-foreground mb-2">
                    Entry Rationale
                  </p>
                  <div className="rounded-lg bg-muted p-4">
                    <p className="text-sm">{position.rationale}</p>
                  </div>
                </div>
              )}

              {/* Fills */}
              <div>
                <p className="text-sm text-muted-foreground mb-2">Fills</p>
                <div className="space-y-2">
                  {position.fills.map((fill, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between rounded-lg bg-muted p-3 text-sm"
                    >
                      <span className="text-muted-foreground">
                        {fill.timestamp.toLocaleString()}
                      </span>
                      <div className="font-mono">
                        <span className="font-semibold">{fill.quantity}</span>
                        <span className="text-muted-foreground"> @ </span>
                        <span className="font-semibold">
                          {formatPercent(fill.price)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Timestamps */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-muted-foreground">Opened</p>
                  <p className="text-sm font-mono">
                    {position.openedAt.toLocaleString()}
                  </p>
                </div>
                {position.closedAt && (
                  <div>
                    <p className="text-sm text-muted-foreground">Closed</p>
                    <p className="text-sm font-mono">
                      {position.closedAt.toLocaleString()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
