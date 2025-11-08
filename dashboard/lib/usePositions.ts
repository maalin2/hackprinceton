import { useState, useEffect } from "react";
import { Position } from "./types";

const mockPositions: Position[] = [
  {
    id: "1",
    ticker: "KXHIGHPHIL-25NOV08-T71",
    market: "Will Philadelphia hit >71°F on Nov 8?",
    domain: "Weather",
    side: "YES",
    entry: 0.02,
    mark: 0.023,
    size: 1000,
    pnl: 3.0,
    edge: 0.611,
    status: "open",
    openedAt: new Date("2025-11-07T10:30:00"),
    rationale: "NOAA forecast shows 63% probability vs 2% market price. Strong edge.",
    fills: [
      { timestamp: new Date("2025-11-07T10:30:00"), price: 0.02, quantity: 1000 },
    ],
  },
  {
    id: "2",
    ticker: "KXBTCD-25NOV1417-T99749.99",
    market: "Bitcoin price >$99,749.99 on Nov 14?",
    domain: "Crypto",
    side: "YES",
    entry: 0.67,
    mark: 0.72,
    size: 500,
    pnl: 25.0,
    edge: 0.18,
    status: "open",
    openedAt: new Date("2025-11-06T14:20:00"),
    rationale: "Strong momentum + institutional buying pressure. Quant model 85% confidence.",
    fills: [
      { timestamp: new Date("2025-11-06T14:20:00"), price: 0.67, quantity: 500 },
    ],
  },
  {
    id: "3",
    ticker: "KX2028DRUN-28-JOSS",
    market: "Will Josh Shapiro run for 2028 Dem nomination?",
    domain: "Politics",
    side: "YES",
    entry: 0.30,
    mark: 0.35,
    size: 800,
    pnl: 40.0,
    edge: 0.25,
    status: "open",
    openedAt: new Date("2025-11-05T09:15:00"),
    rationale: "Recent polling + insider sentiment indicates high likelihood. Edge vs market.",
    fills: [
      { timestamp: new Date("2025-11-05T09:15:00"), price: 0.30, quantity: 800 },
    ],
  },
  {
    id: "4",
    ticker: "KXNFLEXACTWINSHOU-25-9",
    market: "Houston Texans exact 9 wins this season?",
    domain: "Sports",
    side: "NO",
    entry: 0.18,
    mark: 0.12,
    size: 600,
    pnl: -36.0,
    edge: 0.08,
    status: "open",
    openedAt: new Date("2025-11-04T16:45:00"),
    rationale: "Team underperforming expectations. Model predicts 7-8 wins more likely.",
    fills: [
      { timestamp: new Date("2025-11-04T16:45:00"), price: 0.18, quantity: 600 },
    ],
  },
  {
    id: "5",
    ticker: "KXHIGHLAX-25NOV08-T81",
    market: "Will LA hit >81°F on Nov 8?",
    domain: "Weather",
    side: "YES",
    entry: 0.01,
    mark: 0.631,
    size: 1500,
    pnl: 931.50,
    edge: 0.621,
    status: "open",
    openedAt: new Date("2025-11-07T11:00:00"),
    rationale: "Massive edge opportunity. NOAA forecast 63.1% vs 1% market. Heat wave incoming.",
    fills: [
      { timestamp: new Date("2025-11-07T11:00:00"), price: 0.01, quantity: 1500 },
    ],
  },
];

export function usePositions(filter: "all" | "open" | "closed" = "all") {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    
    setTimeout(() => {
      let filtered = mockPositions;
      if (filter !== "all") {
        filtered = mockPositions.filter((p) => p.status === filter);
      }
      setPositions(filtered);
      setLoading(false);
    }, 200);
  }, [filter]);

  return { positions, loading };
}

