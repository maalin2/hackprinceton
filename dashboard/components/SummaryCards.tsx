"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { usePortfolio } from "@/lib/usePortfolio";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { TrendingUp, TrendingDown, Activity, DollarSign } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

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
      title: "Total Equity",
      value: formatCurrency(kpis.totalEquity),
      icon: DollarSign,
      description: "Current portfolio value",
    },
    {
      title: "24h P&L",
      value: formatCurrency(kpis.pnl24h),
      icon: kpis.pnl24h >= 0 ? TrendingUp : TrendingDown,
      description: `${kpis.pnl24h >= 0 ? "+" : ""}${formatPercent(
        kpis.pnl24h / (kpis.totalEquity - kpis.pnl24h)
      )}`,
      positive: kpis.pnl24h >= 0,
    },
    {
      title: "Win Rate",
      value: formatPercent(kpis.winRate),
      icon: Activity,
      description: "All-time win percentage",
    },
    {
      title: "Open Risk",
      value: formatCurrency(kpis.openRisk),
      icon: TrendingUp,
      description: "Capital in open positions",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => (
        <Card key={index} className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
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
            <p className="text-xs text-muted-foreground">{card.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
