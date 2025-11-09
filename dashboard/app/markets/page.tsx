"use client";

import { useEffect, useRef, useState } from "react";
import { useMarkets } from "@/lib/useMarkets";
import { MarketCard } from "@/components/MarketCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Domain } from "@/lib/types";
import { useUIStore } from "@/store/ui";
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter } from "next/navigation";
import { Info } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  consumeSkipOnboardingRedirect,
  useUserPreferences,
} from "@/lib/useUserPreferences";

const domains: (Domain | "all")[] = [
  "all",
  "Politics",
  "Weather",
  "Crypto",
  "Sports",
  "Economics",
  "Technology",
  "Entertainment",
];

export default function MarketsPage() {
  const { selectedDomain, setSelectedDomain } = useUIStore();
  const router = useRouter();
  const { preferences, loading: prefsLoading } = useUserPreferences();
  const skipRedirectRef = useRef(false);

  const { markets, loading } = useMarkets({
    domain: selectedDomain === "all" ? undefined : selectedDomain,
  });

  useEffect(() => {
    if (!prefsLoading && !preferences) {
      if (!skipRedirectRef.current) {
        const shouldSkip = consumeSkipOnboardingRedirect();
        if (shouldSkip) {
          skipRedirectRef.current = true;
          return;
        }
      } else {
        return;
      }
      router.replace("/onboarding");
    }
  }, [prefsLoading, preferences, router]);

  useEffect(() => {
    if (preferences) {
      skipRedirectRef.current = false;
    }
  }, [preferences]);

  if (prefsLoading || !preferences) {
    return (
      <div className="container py-6">
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">
            Loading personalized markets...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-6">
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <h1 className="text-3xl font-bold">Markets</h1>
          <Dialog>
            <DialogTrigger asChild>
              <button className="text-muted-foreground hover:text-foreground transition-colors">
                <Info className="h-5 w-5" />
                <span className="sr-only">Market card information</span>
              </button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Understanding Market Cards</DialogTitle>
                <DialogDescription asChild>
                  <div className="space-y-4 pt-2">
                    <div>
                      <h4 className="font-semibold text-foreground mb-1">Market Title & Ticker</h4>
                      <p className="text-sm">The prediction market question and its unique identifier code.</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-foreground mb-1">Category Badge</h4>
                      <p className="text-sm">The market category (Politics, Weather, Crypto, Sports, Economics, Technology, or Entertainment).</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-foreground mb-1">YES / NO Prices</h4>
                      <p className="text-sm">Bid/Ask prices in cents (¢). Purple shows the bid (what you can sell for), red shows the ask (what you can buy for). For example, "45¢ / 47¢" means you can sell at 45¢ or buy at 47¢.</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-foreground mb-1">Market Probability</h4>
                      <p className="text-sm">The implied probability based on current market prices. This represents what the market believes is the likelihood of the event occurring.</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-foreground mb-1">Edge Badge</h4>
                      <p className="text-sm">The trading edge or advantage, shown as a percentage. A higher edge indicates a potentially more profitable trading opportunity based on our analysis compared to market pricing.</p>
                    </div>
                  </div>
                </DialogDescription>
              </DialogHeader>
            </DialogContent>
          </Dialog>
        </div>
        <p className="text-muted-foreground">
          Browse active prediction markets and find trading opportunities
        </p>
      </div>

      {/* Category Buttons */}
      <div className="flex flex-wrap gap-2 mb-6">
        {domains.map((domain) => (
          <Button
            key={domain}
            variant={selectedDomain === domain ? "default" : "outline"}
            size="sm"
            onClick={() => setSelectedDomain(domain)}
          >
            {domain === "all" ? "All Markets" : domain}
          </Button>
        ))}
      </div>

      {/* Markets Grid */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      ) : markets.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">
            No markets found in this category.
          </p>
          <Button
            variant="link"
            onClick={() => {
              setSelectedDomain("all");
            }}
          >
            View all markets
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {markets.map((market) => (
            <MarketCard key={market.id} market={market} />
          ))}
        </div>
      )}
    </div>
  );
}
