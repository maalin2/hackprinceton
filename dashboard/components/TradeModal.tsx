"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { TradingPick } from "@/lib/types";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { TrendingUp, TrendingDown } from "lucide-react";

interface TradeModalProps {
  pick: TradingPick | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (amount: number) => void;
}

export function TradeModal({ pick, open, onOpenChange, onConfirm }: TradeModalProps) {
  const [amount, setAmount] = useState("100");
  const [error, setError] = useState("");

  if (!pick) return null;

  const handleAmountChange = (value: string) => {
    const numValue = parseFloat(value);
    if (isNaN(numValue) || numValue < 1) {
      setError("Amount must be at least $1");
      setAmount(value);
      return;
    }
    if (numValue > 10000) {
      setError("Amount cannot exceed $10,000");
      setAmount(value);
      return;
    }
    setError("");
    setAmount(value);
  };

  const handleConfirm = () => {
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount < 1) {
      setError("Please enter a valid amount");
      return;
    }
    onConfirm(numAmount);
    onOpenChange(false);
    setAmount("100");
    setError("");
  };

  const isBuy = pick.decision === "BUY";
  const isShort = pick.decision === "SHORT";
  const estimatedPayout = isBuy
    ? parseFloat(amount) * (1 / pick.market_p - 1)
    : parseFloat(amount) * (1 / (1 - pick.market_p) - 1);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Place Trade</DialogTitle>
          <DialogDescription>
            Review your trade details before confirming
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Pick Info */}
          <div className="space-y-2">
            <Label className="text-sm font-semibold">Market</Label>
            <p className="text-sm">{pick.ticker}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label className="text-sm font-semibold">Decision</Label>
              <div className="flex items-center gap-2">
                {isBuy ? (
                  <TrendingUp className="h-4 w-4 text-green-600" />
                ) : isShort ? (
                  <TrendingDown className="h-4 w-4 text-red-600" />
                ) : null}
                <span className="text-sm font-medium">{pick.decision}</span>
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-sm font-semibold">Current Odds</Label>
              <p className="text-sm font-mono">{formatPercent(pick.market_p)}</p>
            </div>
          </div>

          {/* Trade Amount */}
          <div className="space-y-2">
            <Label htmlFor="amount">Trade Amount ($)</Label>
            <Input
              id="amount"
              type="number"
              min="1"
              max="10000"
              step="1"
              value={amount}
              onChange={(e) => handleAmountChange(e.target.value)}
              className="font-mono"
            />
            {error && <p className="text-xs text-red-600">{error}</p>}
            <p className="text-xs text-muted-foreground">
              Minimum: $1 | Maximum: $10,000
            </p>
          </div>

          {/* Estimated Payout */}
          {!isNaN(estimatedPayout) && (
            <div className="bg-muted/50 rounded-lg p-3 space-y-1">
              <p className="text-xs text-muted-foreground">Estimated payout if correct</p>
              <p className="text-lg font-mono font-bold">
                {formatCurrency(parseFloat(amount) + estimatedPayout)}
              </p>
              <p className="text-xs text-muted-foreground">
                Profit: {formatCurrency(estimatedPayout)}
              </p>
            </div>
          )}

          {/* Risk Warning */}
          <div className="bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
            <p className="text-xs text-yellow-800 dark:text-yellow-200">
              ⚠️ Trading involves risk. You may lose your entire investment.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={!!error || !amount}>
            Confirm Trade
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

