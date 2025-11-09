"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { usePositions } from "@/lib/usePositions";
import { useUIStore } from "@/store/ui";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { Position } from "@/lib/types";
import { Search, Info } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { EdgeBadge } from "./EdgeBadge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export function PositionsTable() {
  const [search, setSearch] = useState("");
  const { positions, loading } = usePositions("open");
  const { setSelectedPositionId } = useUIStore();

  const filteredPositions = positions.filter(
    (p) =>
      p.market.toLowerCase().includes(search.toLowerCase()) ||
      p.ticker.toLowerCase().includes(search.toLowerCase())
  );

  // Helper to get status emoji
  const getStatusEmoji = (pnl: number) => {
    if (pnl > 0.5) return "🟢";
    if (pnl < -0.5) return "🔴";
    return "⚪";
  };

  // Helper to get status text
  const getStatusText = (pnl: number) => {
    if (pnl > 0.5) return "Winning";
    if (pnl < -0.5) return "Losing";
    return "Break-even";
  };

  // Helper to shorten market names
  const shortenMarket = (market: string) => {
    // Limit to 60 characters
    if (market.length <= 60) return market;
    return market.substring(0, 57) + "...";
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-8 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[400px] w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg">Active Trades</CardTitle>
            <Dialog>
              <DialogTrigger asChild>
                <button className="text-muted-foreground hover:text-foreground transition-colors">
                  <Info className="h-3.5 w-3.5" />
                  <span className="sr-only">More info about Active Trades</span>
                </button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Active Trades</DialogTitle>
                  <DialogDescription>
                    These are the bets you've placed that haven't been sold off yet. Think of them like stocks you currently own in your portfolio. Their value changes in real-time as market prices move up or down. You can click on any position to see more details or decide whether to hold or sell.
                  </DialogDescription>
                </DialogHeader>
              </DialogContent>
            </Dialog>
          </div>
          <div className="relative w-56">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search markets..."
              className="pl-8 h-9 text-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow className="h-10">
                <TableHead className="py-2">Market</TableHead>
                <TableHead className="py-2">Side</TableHead>
                <TableHead className="text-right font-mono py-2">Current Price</TableHead>
                <TableHead className="text-right font-mono py-2">Size</TableHead>
                <TableHead className="text-right font-mono py-2">Profit/Loss</TableHead>
                <TableHead className="text-right py-2">Opportunity Score</TableHead>
                <TableHead className="text-center py-2">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredPositions.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={7}
                    className="text-center text-muted-foreground"
                  >
                    No open positions yet—browse Markets to add your first.
                  </TableCell>
                </TableRow>
              ) : (
                filteredPositions.map((position) => (
                  <TableRow
                    key={position.id}
                    className="cursor-pointer hover:bg-muted/50 h-12"
                    onClick={() => setSelectedPositionId(position.id)}
                  >
                    <TableCell className="max-w-md truncate font-medium py-2">
                      {shortenMarket(position.market)}
                    </TableCell>
                    <TableCell className="py-2">
                      <Badge
                        variant={
                          position.side === "YES" ? "default" : "secondary"
                        }
                        className="text-xs"
                      >
                        {position.side}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono py-2 text-sm">
                      {formatPercent(position.mark)}
                    </TableCell>
                    <TableCell className="text-right font-mono py-2 text-sm">
                      {position.size}
                    </TableCell>
                    <TableCell
                      className={`text-right font-mono font-semibold py-2 text-sm ${
                        position.pnl >= 0
                          ? "text-green-600 dark:text-green-400"
                          : "text-red-600 dark:text-red-400"
                      }`}
                    >
                      {formatCurrency(position.pnl)}
                    </TableCell>
                    <TableCell className="text-right py-2">
                      <EdgeBadge edge={position.edge} />
                    </TableCell>
                    <TableCell className="text-center py-2">
                      <span title={getStatusText(position.pnl)}>
                        {getStatusEmoji(position.pnl)}
                      </span>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
