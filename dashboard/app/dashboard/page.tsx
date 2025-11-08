"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { SummaryCards } from "@/components/SummaryCards";
import { PositionsTable } from "@/components/PositionsTable";
import { PositionDrawer } from "@/components/PositionDrawer";
import { AgentFeed } from "@/components/AgentFeed";
import {
  consumeSkipOnboardingRedirect,
  useUserPreferences,
} from "@/lib/useUserPreferences";

export default function DashboardPage() {
  const router = useRouter();
  const { preferences, loading } = useUserPreferences();
  const skipRedirectRef = useRef(false);

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

  if (loading || !preferences) {
    return (
      <div className="container py-6">
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-6">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Main Content */}
        <div className="flex-1 space-y-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome back, {preferences.name}! 👋
            </h1>
            <p className="text-muted-foreground">
              Monitor your portfolio performance and active positions
            </p>
          </div>

          <SummaryCards />
          <PositionsTable />
        </div>

        {/* Agent Feed Sidebar */}
        <div className="lg:w-96 shrink-0">
          <div className="sticky top-20">
            <AgentFeed />
          </div>
        </div>
      </div>

      <PositionDrawer />
    </div>
  );
}
