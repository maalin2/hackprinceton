"use client";

import { useState } from "react";
import { useMarkets } from "@/lib/useMarkets";
import { MarketCard } from "@/components/MarketCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Domain } from "@/lib/types";
import { useUIStore } from "@/store/ui";
import { Filter, X } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

const domains: (Domain | "all")[] = [
  "all",
  "Politics",
  "Weather",
  "Crypto",
  "Sports",
];

export default function MarketsPage() {
  const { selectedDomain, setSelectedDomain, settings } = useUIStore();
  const [minEdge, setMinEdge] = useState<number>(0);
  const [maxSpread, setMaxSpread] = useState<number>(20);
  const [showFilters, setShowFilters] = useState(false);

  const { markets, loading } = useMarkets({
    domain: selectedDomain === "all" ? undefined : selectedDomain,
    minEdge,
    maxSpread,
  });

  return (
    <div className="container py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Markets</h1>
        <p className="text-muted-foreground">
          Browse active prediction markets and find trading opportunities
        </p>
      </div>

      {/* Domain Filters */}
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
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div className="mb-6 p-4 border rounded-lg bg-card space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="min-edge">Minimum Edge (%)</Label>
              <Input
                id="min-edge"
                type="number"
                min="0"
                max="100"
                step="1"
                value={minEdge * 100}
                onChange={(e) => setMinEdge(Number(e.target.value) / 100)}
                className="font-mono"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="max-spread">Maximum Spread (¢)</Label>
              <Input
                id="max-spread"
                type="number"
                min="0"
                max="100"
                step="1"
                value={maxSpread}
                onChange={(e) => setMaxSpread(Number(e.target.value))}
                className="font-mono"
              />
            </div>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">
              {markets.length} market{markets.length !== 1 ? "s" : ""} found
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setMinEdge(0);
                setMaxSpread(20);
              }}
            >
              <X className="h-4 w-4 mr-2" />
              Clear Filters
            </Button>
          </div>
        </div>
      )}

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
            No markets found matching your filters.
          </p>
          <Button
            variant="link"
            onClick={() => {
              setMinEdge(0);
              setMaxSpread(20);
              setSelectedDomain("all");
            }}
          >
            Clear all filters
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
