import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Market } from "@/lib/types";
import { formatPercent } from "@/lib/utils";
import { EdgeBadge } from "./EdgeBadge";

interface MarketCardProps {
  market: Market;
}

export function MarketCard({ market }: MarketCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow cursor-pointer">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-sm line-clamp-2">{market.title}</h3>
            <p className="text-xs text-muted-foreground mt-1">
              {market.ticker}
            </p>
          </div>
          <Badge variant="outline" className="text-xs shrink-0">
            {market.domain}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Prices */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-xs text-muted-foreground mb-1">YES</p>
            <div className="flex gap-1 font-mono text-xs">
              <span className="text-green-600 dark:text-green-400">
                {market.yesBid}¢
              </span>
              <span className="text-muted-foreground">/</span>
              <span className="text-red-600 dark:text-red-400">
                {market.yesAsk}¢
              </span>
            </div>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">NO</p>
            <div className="flex gap-1 font-mono text-xs">
              <span className="text-green-600 dark:text-green-400">
                {market.noBid}¢
              </span>
              <span className="text-muted-foreground">/</span>
              <span className="text-red-600 dark:text-red-400">
                {market.noAsk}¢
              </span>
            </div>
          </div>
        </div>

        {/* Probabilities */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-muted-foreground">Market</span>
            <span className="font-mono font-semibold">
              {formatPercent(market.impliedProb)}
            </span>
          </div>
          <div className="flex justify-between text-xs mb-2">
            <span className="text-muted-foreground">Combined</span>
            <span className="font-mono font-semibold">
              {formatPercent(market.combinedProb)}
            </span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full bg-primary transition-all"
              style={{ width: `${market.combinedProb * 100}%` }}
            />
          </div>
        </div>

        {/* Edge & Stats */}
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex gap-2 text-xs text-muted-foreground">
            <span>Spread: {market.spread}¢</span>
            <span>Vol: {market.volume24h}</span>
          </div>
          <EdgeBadge edge={market.edge} />
        </div>
      </CardContent>
    </Card>
  );
}
