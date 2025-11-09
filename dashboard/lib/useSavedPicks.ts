import { useState, useEffect, useCallback } from "react";
import { createClient } from "@/lib/supabase/client";
import { TradingPick } from "./types";

export function useSavedPicks() {
  const [savedPicks, setSavedPicks] = useState<TradingPick[]>([]);
  const [loading, setLoading] = useState(true);
  const supabase = createClient();

  const loadSavedPicks = useCallback(async () => {
    setLoading(true);
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        setSavedPicks([]);
        return;
      }

      const { data, error } = await supabase
        .from("saved_picks")
        .select("*")
        .eq("user_id", user.id)
        .order("saved_at", { ascending: false });

      if (error) {
        console.error("Error loading saved picks:", error);
        setSavedPicks([]);
        return;
      }

      if (data) {
        // Convert database format to TradingPick format
        const picks: TradingPick[] = data.map((row) => ({
          ticker: row.ticker,
          market_question: row.market_question || undefined,
          decision: row.decision as "BUY" | "SHORT" | "PASS",
          technical_direction: row.technical_direction as "buy" | "short" | null,
          market_p: parseFloat(row.market_p),
          volatility_confidence: parseFloat(row.volatility_confidence),
          volume_confidence: parseFloat(row.volume_confidence),
          momentum: row.momentum as "bullish" | "bearish" | "neutral",
          final_confidence: parseFloat(row.final_confidence),
          reasoning: row.reasoning,
          sentiment: {
            label: row.sentiment_label as "positive" | "negative" | "neutral",
            score: row.sentiment_score,
            confidence: row.sentiment_confidence as "high" | "medium" | "low",
          },
          key_themes: row.key_themes || [],
          market_impact: row.market_impact || "",
        }));
        setSavedPicks(picks);
      } else {
        setSavedPicks([]);
      }
    } catch (error) {
      console.error("Error loading saved picks:", error);
      setSavedPicks([]);
    } finally {
      setLoading(false);
    }
  }, [supabase]);

  useEffect(() => {
    loadSavedPicks();

    // Listen for auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      loadSavedPicks();
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [loadSavedPicks, supabase]);

  const savePick = useCallback(
    async (pick: TradingPick) => {
      try {
        const {
          data: { user },
        } = await supabase.auth.getUser();

        if (!user) {
          console.error("No user logged in");
          return false;
        }

        const { error } = await supabase.from("saved_picks").insert({
          user_id: user.id,
          ticker: pick.ticker,
          market_question: pick.market_question || null,
          decision: pick.decision,
          technical_direction: pick.technical_direction || null,
          market_p: pick.market_p,
          volatility_confidence: pick.volatility_confidence,
          volume_confidence: pick.volume_confidence,
          momentum: pick.momentum,
          final_confidence: pick.final_confidence,
          reasoning: pick.reasoning,
          sentiment_label: pick.sentiment.label,
          sentiment_score: pick.sentiment.score,
          sentiment_confidence: pick.sentiment.confidence,
          key_themes: pick.key_themes,
          market_impact: pick.market_impact,
        });

        if (error) {
          // If it's a unique constraint violation, the pick is already saved
          if (error.code === "23505") {
            console.log("Pick already saved");
            return true;
          }
          console.error("Error saving pick:", error);
          return false;
        }

        // Reload saved picks
        await loadSavedPicks();
        return true;
      } catch (error) {
        console.error("Error saving pick:", error);
        return false;
      }
    },
    [supabase, loadSavedPicks]
  );

  const removePick = useCallback(
    async (ticker: string) => {
      try {
        const {
          data: { user },
        } = await supabase.auth.getUser();

        if (!user) {
          console.error("No user logged in");
          return false;
        }

        const { error } = await supabase
          .from("saved_picks")
          .delete()
          .eq("user_id", user.id)
          .eq("ticker", ticker);

        if (error) {
          console.error("Error removing pick:", error);
          return false;
        }

        // Reload saved picks
        await loadSavedPicks();
        return true;
      } catch (error) {
        console.error("Error removing pick:", error);
        return false;
      }
    },
    [supabase, loadSavedPicks]
  );

  return {
    savedPicks,
    loading,
    savePick,
    removePick,
    refreshSavedPicks: loadSavedPicks,
  };
}

