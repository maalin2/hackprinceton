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
import { Search } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { EdgeBadge } from "./EdgeBadge";

export function PositionsTable() {
  const [search, setSearch] = useState("");
  const { positions, loading } = usePositions("open");
  const { setSelectedPositionId } = useUIStore();

  const filteredPositions = positions.filter(
    (p) =>
      p.market.toLowerCase().includes(search.toLowerCase()) ||
      p.ticker.toLowerCase().includes(search.toLowerCase())
  );

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
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Open Positions</CardTitle>
          <div className="relative w-64">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search markets..."
              className="pl-8"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Market</TableHead>
                <TableHead>Side</TableHead>
                <TableHead className="text-right font-mono">Entry</TableHead>
                <TableHead className="text-right font-mono">Mark</TableHead>
                <TableHead className="text-right font-mono">Size</TableHead>
                <TableHead className="text-right font-mono">P&L</TableHead>
                <TableHead className="text-right">Edge</TableHead>
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
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => setSelectedPositionId(position.id)}
                  >
                    <TableCell className="max-w-md truncate font-medium">
                      {position.market}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          position.side === "YES" ? "default" : "secondary"
                        }
                      >
                        {position.side}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatPercent(position.entry)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatPercent(position.mark)}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {position.size}
                    </TableCell>
                    <TableCell
                      className={`text-right font-mono font-semibold ${
                        position.pnl >= 0
                          ? "text-green-600 dark:text-green-400"
                          : "text-red-600 dark:text-red-400"
                      }`}
                    >
                      {formatCurrency(position.pnl)}
                    </TableCell>
                    <TableCell className="text-right">
                      <EdgeBadge edge={position.edge} />
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
