import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Domain, UISettings } from "@/lib/types";

interface UIState {
  // Theme
  theme: "dark" | "light" | "system";
  setTheme: (theme: "dark" | "light" | "system") => void;

  // Drawers
  selectedPositionId: string | null;
  setSelectedPositionId: (id: string | null) => void;

  // Agent feed
  agentFeedCollapsed: boolean;
  toggleAgentFeed: () => void;

  // Filters
  selectedDomain: Domain | "all";
  setSelectedDomain: (domain: Domain | "all") => void;

  // Chart range
  chartRange: "1D" | "1W" | "1M" | "All";
  setChartRange: (range: "1D" | "1W" | "1M" | "All") => void;

  // Settings
  settings: UISettings;
  updateSettings: (settings: Partial<UISettings>) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      // Theme
      theme: "dark",
      setTheme: (theme) => set({ theme }),

      // Drawers
      selectedPositionId: null,
      setSelectedPositionId: (id) => set({ selectedPositionId: id }),

      // Agent feed
      agentFeedCollapsed: false,
      toggleAgentFeed: () =>
        set((state) => ({ agentFeedCollapsed: !state.agentFeedCollapsed })),

      // Filters
      selectedDomain: "all",
      setSelectedDomain: (domain) => set({ selectedDomain: domain }),

      // Chart range
      chartRange: "1W",
      setChartRange: (range) => set({ chartRange: range }),

      // Settings
      settings: {
        quantWeight: 0.6,
        sentimentWeight: 0.4,
        minEdgeThreshold: 0.05,
        maxSpread: 15,
        maxPositionSize: 2000,
      },
      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        })),
    }),
    {
      name: "kalshi-ui-storage",
      partialize: (state) => ({
        theme: state.theme,
        settings: state.settings,
      }),
    }
  )
);

