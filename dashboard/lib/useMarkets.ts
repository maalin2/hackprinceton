import { useState, useEffect } from "react";
import { Market, Domain } from "./types";

const KALSHI_API = "https://api.elections.kalshi.com/trade-api/v2";

// Domain mapping for Kalshi categories
const DOMAIN_TO_CATEGORY: Record<Domain, string> = {
  Weather: "Climate and Weather",
  Politics: "Politics",
  Crypto: "Crypto",
  Sports: "Sports",
};

interface UseMarketsOptions {
  domain?: Domain;
  minEdge?: number;
  maxSpread?: number;
  limit?: number;
}

export function useMarkets(options: UseMarketsOptions = {}) {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMarkets = async () => {
      setLoading(true);

      try {
        // Fetch markets from Kalshi API
        const params = new URLSearchParams({
          status: "open",
          limit: String(options.limit || 200),
        });

        const response = await fetch(`${KALSHI_API}/markets?${params}`, {
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Kalshi API failed: ${response.status}`);
        }

        const data = await response.json();
        const kalshiMarkets = data.markets || [];

        // Transform Kalshi markets to our Market format
        let transformed: Market[] = kalshiMarkets.map((km: any) => {
          const yesBid = km.yes_bid || 0;
          const yesAsk = km.yes_ask || 0;
          const noBid = km.no_bid || 0;
          const noAsk = km.no_ask || 0;
          const lastPrice = km.last_price || 0;

          // Calculate implied probability from mid-market price
          const yesMid = yesBid && yesAsk ? (yesBid + yesAsk) / 2 : lastPrice;
          const impliedProb = yesMid / 100;

          // Calculate spread
          const spread = yesAsk && yesBid ? yesAsk - yesBid : 0;

          // Map category to domain
          let domain: Domain = "Weather";
          const category = km.category || "";
          if (category === "Politics") domain = "Politics";
          else if (category === "Crypto") domain = "Crypto";
          else if (category === "Sports") domain = "Sports";
          else if (category === "Climate and Weather") domain = "Weather";

          // Extract series from ticker
          const series = km.ticker?.split('-')[0] || km.series_ticker || "";

          // Generate Kalshi market URL
          const marketUrl = `https://kalshi.com/markets/${km.ticker}`;

          return {
            id: km.id || km.ticker,
            ticker: km.ticker,
            title: km.title || km.subtitle || "Untitled Market",
            domain,
            series,
            yesBid,
            yesAsk,
            noBid,
            noAsk,
            spread,
            impliedProb,
            combinedProb: impliedProb, // Will be updated by agent analysis
            edge: 0, // Will be calculated by agent analysis
            volume24h: km.volume || km.volume_24h || 0,
            openInterest: km.open_interest || 0,
            closeTime: km.close_time ? new Date(km.close_time) : new Date(),
            lastPrice: km.last_price,
            url: marketUrl,
          };
        });

        // Apply filters
        if (options.domain) {
          transformed = transformed.filter((m) => m.domain === options.domain);
        }

        if (options.minEdge !== undefined) {
          transformed = transformed.filter((m) => m.edge >= options.minEdge);
        }

        if (options.maxSpread !== undefined) {
          transformed = transformed.filter((m) => m.spread <= options.maxSpread);
        }

        // Sort by volume (most liquid first)
        transformed.sort((a, b) => b.volume24h - a.volume24h);

        setMarkets(transformed);
      } catch (error) {
        console.error("Failed to fetch markets from Kalshi:", error);
        
        // Fallback to empty array or cached data
        setMarkets([]);
      } finally {
        setLoading(false);
      }
    };

    fetchMarkets();

    // Refresh every 60 seconds
    const interval = setInterval(fetchMarkets, 60000);

    return () => clearInterval(interval);
  }, [options.domain, options.minEdge, options.maxSpread, options.limit]);

  return { markets, loading };
}
