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
        <h1 className="text-3xl font-bold mb-2">Markets</h1>
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
