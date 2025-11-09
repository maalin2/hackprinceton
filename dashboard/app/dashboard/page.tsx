"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { SummaryCards } from "@/components/SummaryCards";
import { WeeklyTradingChart } from "@/components/WeeklyTradingChart";
import { TradingCardDeck } from "@/components/TradingCardDeck";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  consumeSkipOnboardingRedirect,
  useUserPreferences,
} from "@/lib/useUserPreferences";
import { useUIStore } from "@/store/ui";
import { Target, X } from "lucide-react";

// Import test API utility (makes window.testAPI() available in console)
import "@/lib/testAPI";

export default function DashboardPage() {
  const router = useRouter();
  const { preferences, loading } = useUserPreferences();
  const skipRedirectRef = useRef(false);
  const [showTradingDeck, setShowTradingDeck] = useState(false);
  const { setTradingDeckMode } = useUIStore();

  useEffect(() => {
    if (!loading && !preferences) {
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
  }, [loading, preferences, router]);

  useEffect(() => {
    if (preferences) {
      skipRedirectRef.current = false;
    }
  }, [preferences]);

  // Update trading deck mode state
  useEffect(() => {
    setTradingDeckMode(showTradingDeck);
    return () => {
      setTradingDeckMode(false);
    };
  }, [showTradingDeck, setTradingDeckMode]);

  if (loading || !preferences) {
    return (
      <div className="container py-6">
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (showTradingDeck) {
    return (
      <div className="container py-6 max-w-4xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Trading Picks</h1>
            <p className="text-muted-foreground">
              Swipe through AI-curated trading opportunities
            </p>
          </div>
          <Button variant="outline" onClick={() => setShowTradingDeck(false)}>
            <X className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
        <TradingCardDeck />
      </div>
    );
  }

  return (
    <div className="container py-6">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Main Content */}
        <div className="flex-1 space-y-6 min-w-0">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome back, {preferences.name}!
            </h1>
          </div>

          {/* Start Trading CTA */}
          <Card className="p-6 bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-primary" />
                  <h2 className="text-xl font-semibold">Start Trading</h2>
                </div>
                <p className="text-sm text-muted-foreground">
                  New live picks ready for review!
                </p>
              </div>
              <Button
                size="lg"
                onClick={() => setShowTradingDeck(true)}
                className="shrink-0"
              >
                <Target className="h-4 w-4 mr-2" />
                Review Picks
              </Button>
            </div>
          </Card>

          <SummaryCards />

          <WeeklyTradingChart />
        </div>
      </div>
    </div>
  );
}
