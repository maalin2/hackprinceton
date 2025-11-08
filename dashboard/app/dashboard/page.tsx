"use client";

import { SummaryCards } from "@/components/SummaryCards";
import { PerformanceChart } from "@/components/PerformanceChart";
import { PositionsTable } from "@/components/PositionsTable";
import { PositionDrawer } from "@/components/PositionDrawer";
import { AgentFeed } from "@/components/AgentFeed";

export default function DashboardPage() {
  return (
    <div className="container py-6">
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Main Content */}
        <div className="flex-1 space-y-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
            <p className="text-muted-foreground">
              Monitor your portfolio performance and active positions
            </p>
          </div>

          <SummaryCards />
          <PerformanceChart />
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
