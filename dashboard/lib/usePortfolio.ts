import { useState, useEffect } from "react";
import { PortfolioSnapshot, PortfolioKPIs } from "./types";

const generateMockData = (days: number): PortfolioSnapshot[] => {
  const data: PortfolioSnapshot[] = [];
  let equity = 10000;
  const now = new Date();

  for (let i = days; i >= 0; i--) {
    const timestamp = new Date(now);
    timestamp.setDate(timestamp.getDate() - i);
    
    const change = (Math.random() - 0.45) * 200;
    equity += change;
    
    data.push({
      timestamp,
      equity,
      pnl: change,
    });
  }

  return data;
};

const mockKPIs: PortfolioKPIs = {
  totalEquity: 12458.32,
  pnl24h: 342.15,
  winRate: 0.64,
  openRisk: 2840.00,
};

export function usePortfolio(range: "1D" | "1W" | "1M" | "All" = "1W") {
  const [data, setData] = useState<PortfolioSnapshot[]>([]);
  const [kpis, setKpis] = useState<PortfolioKPIs>(mockKPIs);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    
    setTimeout(() => {
      const days = range === "1D" ? 1 : range === "1W" ? 7 : range === "1M" ? 30 : 90;
      setData(generateMockData(days));
      setKpis(mockKPIs);
      setLoading(false);
    }, 300);
  }, [range]);

  return { data, kpis, loading };
}

