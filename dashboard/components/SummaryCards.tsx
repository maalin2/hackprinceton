"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { usePortfolio } from "@/lib/usePortfolio";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { TrendingUp, TrendingDown, Activity, DollarSign, Info } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export function SummaryCards() {
  const { kpis, loading } = usePortfolio();

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-32" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: "Account Worth",
      value: formatCurrency(kpis.totalEquity),
      icon: DollarSign,
      infoTitle: "Account Value",
      infoDescription: "This is the total current value of your trading account, including all open positions and available cash. It represents your portfolio's worth at this moment.",
    },
    {
      title: "Today's Profit",
      value: formatCurrency(kpis.pnl24h),
      icon: kpis.pnl24h >= 0 ? TrendingUp : TrendingDown,
      positive: kpis.pnl24h >= 0,
      infoTitle: "Today's Profit",
      infoDescription: "The profit or loss generated in the last 24 hours. A positive value (green) indicates gains, while a negative value (red) indicates losses. The percentage shows the change relative to yesterday's account value.",
    },
    {
      title: "Success Rate",
      value: formatPercent(kpis.winRate),
      icon: Activity,
      infoTitle: "Success Rate",
      infoDescription: "The percentage of your trades that were profitable across your entire trading history. A higher success rate indicates more consistent winning trades, though it doesn't account for the size of wins versus losses.",
    },
    {
      title: "Invested Now",
      value: formatCurrency(kpis.openRisk),
      icon: TrendingUp,
      infoTitle: "Invested Now",
      infoDescription: "The total amount of capital currently allocated to active trading positions. This shows how much of your account value is actively invested in the market right now versus sitting in cash.",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => (
        <Card key={index} className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div className="flex items-center gap-2">
              <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
              <Dialog>
                <DialogTrigger asChild>
                  <button className="text-muted-foreground hover:text-foreground transition-colors">
                    <Info className="h-3.5 w-3.5" />
                    <span className="sr-only">More info about {card.title}</span>
                  </button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>{card.infoTitle}</DialogTitle>
                    <DialogDescription>
                      {card.infoDescription}
                    </DialogDescription>
                  </DialogHeader>
                </DialogContent>
              </Dialog>
            </div>
            <card.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-mono font-bold ${
                card.positive !== undefined
                  ? card.positive
                    ? "text-green-600 dark:text-green-400"
                    : "text-red-600 dark:text-red-400"
                  : ""
              }`}
            >
              {card.value}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
