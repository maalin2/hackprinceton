import { useState, useEffect } from "react";
import { Market, Domain } from "./types";

const mockMarkets: Market[] = [
  {
    id: "1",
    ticker: "KXHIGHPHIL-25NOV08-T71",
    title: "Will Philadelphia hit >71°F on Nov 8, 2025?",
    domain: "Weather",
    series: "KXHIGHPHIL",
    yesBid: 1,
    yesAsk: 3,
    noBid: 97,
    noAsk: 99,
    spread: 2,
    impliedProb: 0.02,
    combinedProb: 0.631,
    edge: 0.611,
    volume24h: 1200,
    openInterest: 5400,
    closeTime: new Date("2025-11-09T04:59:00"),
  },
  {
    id: "2",
    ticker: "KXBTCD-25NOV1417-T99749.99",
    title: "Bitcoin price >$99,749.99 on Nov 14, 2025?",
    domain: "Crypto",
    series: "KXBTCD",
    yesBid: 67,
    yesAsk: 74,
    noBid: 26,
    noAsk: 33,
    spread: 7,
    impliedProb: 0.705,
    combinedProb: 0.82,
    edge: 0.115,
    volume24h: 8500,
    openInterest: 24000,
    closeTime: new Date("2025-11-14T17:00:00"),
  },
  {
    id: "3",
    ticker: "KX2028DRUN-28-JOSS",
    title: "Will Josh Shapiro run for 2028 Democratic nomination?",
    domain: "Politics",
    series: "KX2028DRUN",
    yesBid: 30,
    yesAsk: 40,
    noBid: 60,
    noAsk: 70,
    spread: 10,
    impliedProb: 0.35,
    combinedProb: 0.52,
    edge: 0.17,
    volume24h: 3200,
    openInterest: 15000,
    closeTime: new Date("2028-01-01T00:00:00"),
  },
  {
    id: "4",
    ticker: "KXNFLEXACTWINSHOU-25-9",
    title: "Will Houston Texans win exactly 9 games this season?",
    domain: "Sports",
    series: "KXNFLEXACTWINSHOU",
    yesBid: 8,
    yesAsk: 39,
    noBid: 61,
    noAsk: 92,
    spread: 31,
    impliedProb: 0.235,
    combinedProb: 0.18,
    edge: -0.055,
    volume24h: 420,
    openInterest: 2100,
    closeTime: new Date("2026-01-05T00:00:00"),
  },
  {
    id: "5",
    ticker: "KXHIGHLAX-25NOV08-T81",
    title: "Will Los Angeles hit >81°F on Nov 8, 2025?",
    domain: "Weather",
    series: "KXHIGHLAX",
    yesBid: 0,
    yesAsk: 2,
    noBid: 98,
    noAsk: 100,
    spread: 2,
    impliedProb: 0.01,
    combinedProb: 0.631,
    edge: 0.621,
    volume24h: 800,
    openInterest: 3200,
    closeTime: new Date("2025-11-09T04:59:00"),
  },
  {
    id: "6",
    ticker: "KXETHMAX M-25DEC01-5200",
    title: "Will Ethereum reach above $5200 by Dec 1, 2025?",
    domain: "Crypto",
    series: "KXETHMAXM",
    yesBid: 2,
    yesAsk: 6,
    noBid: 94,
    noAsk: 98,
    spread: 4,
    impliedProb: 0.04,
    combinedProb: 0.12,
    edge: 0.08,
    volume24h: 2500,
    openInterest: 12000,
    closeTime: new Date("2025-12-01T00:00:00"),
  },
  {
    id: "7",
    ticker: "SENATEFL-28-R",
    title: "Will Republicans win the Florida Senate race in 2028?",
    domain: "Politics",
    series: "SENATEFL",
    yesBid: 81,
    yesAsk: 90,
    noBid: 10,
    noAsk: 19,
    spread: 9,
    impliedProb: 0.855,
    combinedProb: 0.91,
    edge: 0.055,
    volume24h: 5600,
    openInterest: 28000,
    closeTime: new Date("2028-11-08T00:00:00"),
  },
  {
    id: "8",
    ticker: "KXLEADERNFLSACKS-26JAN05-MCRO",
    title: "Will Maxx Crosby lead NFL in sacks for 2025 season?",
    domain: "Sports",
    series: "KXLEADERNFLSACKS",
    yesBid: 5,
    yesAsk: 23,
    noBid: 77,
    noAsk: 95,
    spread: 18,
    impliedProb: 0.14,
    combinedProb: 0.22,
    edge: 0.08,
    volume24h: 180,
    openInterest: 890,
    closeTime: new Date("2026-01-05T00:00:00"),
  },
];

interface UseMarketsOptions {
  domain?: Domain;
  minEdge?: number;
  maxSpread?: number;
}

export function useMarkets(options: UseMarketsOptions = {}) {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    
    setTimeout(() => {
      let filtered = mockMarkets;
      
      if (options.domain) {
        filtered = filtered.filter((m) => m.domain === options.domain);
      }
      
      if (options.minEdge !== undefined) {
        filtered = filtered.filter((m) => m.edge >= options.minEdge);
      }
      
      if (options.maxSpread !== undefined) {
        filtered = filtered.filter((m) => m.spread <= options.maxSpread);
      }
      
      setMarkets(filtered);
      setLoading(false);
    }, 250);
  }, [options.domain, options.minEdge, options.maxSpread]);

  return { markets, loading };
}

