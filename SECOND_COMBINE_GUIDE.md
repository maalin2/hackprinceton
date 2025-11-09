# second_combine Branch - Integration Guide

## ✅ What You Have Now

This branch combines:
- ✅ **mcp_quantitative_agent/** (from `markets`) - Real analysis backend
- ✅ **dashboard/** (from `card-interfaces`) - Card swipe UI
- ✅ **Python analysis scripts** (weather_test.py, politics_test.py, economics_test.py)
- ✅ **Agent system** (lib/agents/ still exists!)

## 📊 Current Status

### What's Working:
- ✅ MCP server (server.py) - can run independently
- ✅ Python quantitative analysis - fully functional
- ✅ Dashboard UI - card swipe interface installed
- ✅ **Agent system code still exists** in `dashboard/lib/agents/`

### What's NOT Connected:
- ⚠️ Dashboard uses `useTradingPicks.ts` (mock data)
- ⚠️ Real agent system (`useRecommendations.ts`, `useAgentFeed.ts`) not integrated with card UI
- ⚠️ Card swipe UI doesn't call real agents yet

## 🎯 Two Paths Forward

### Option 1: Keep Mock Data (Quick Demo)
**Time**: No changes needed  
**Best for**: Fast demo, UI showcase

Just use the card interface as-is with mock data:
```bash
cd dashboard
npm run dev
```

Dashboard will show pretty cards with fake data.

---

### Option 2: Connect Cards to Real Agents (Recommended)
**Time**: ~30 minutes  
**Best for**: Real analysis with pretty UI

Connect the card UI to your real agent system.

## 🔧 How to Connect Real Agents to Card UI

### Step 1: Update useTradingPicks.ts

Currently it generates mock data. Replace with real agent calls:

**File**: `dashboard/lib/useTradingPicks.ts`

```typescript
import { useState, useEffect } from "react";
import { TradingPick } from "./types";
import { useRecommendations } from "./useRecommendations"; // Real agent system!

export function useTradingPicks() {
  const [picks, setPicks] = useState<TradingPick[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Use REAL recommendations instead of mock data
  const {
    recommendations,
    loading: agentLoading,
    processing,
  } = useRecommendations();
  
  useEffect(() => {
    // Convert real recommendations to TradingPick format
    if (!agentLoading) {
      const converted = recommendations.map(rec => ({
        ticker: rec.market.ticker,
        market_question: rec.market.title,
        topic: rec.market.domain.toLowerCase(),
        decision: rec.decision.action === "BUY_YES" ? "BUY" : 
                  rec.decision.action === "BUY_NO" ? "SHORT" : "PASS",
        technical_direction: rec.decision.action === "BUY_YES" ? "buy" : 
                            rec.decision.action === "BUY_NO" ? "short" : null,
        market_p: rec.decision.pMarket,
        volatility_confidence: rec.decision.confidence,
        volume_confidence: rec.decision.confidence,
        momentum: rec.decision.edge > 0 ? "bullish" : "bearish",
        final_confidence: rec.decision.confidence,
        reasoning: rec.decision.rationale,
        sentiment: {
          label: rec.decision.pSent > 0.5 ? "positive" : "negative",
          score: Math.round(rec.decision.pSent * 100),
          confidence: rec.decision.confidence > 0.7 ? "high" : "medium",
        },
        key_themes: rec.decision.sources,
        market_impact: rec.decision.edge > 0.15 ? "High" : "Medium",
      }));
      
      setPicks(converted);
      setLoading(false);
    }
  }, [recommendations, agentLoading]);
  
  // ... rest of the hook (save, unsave, etc.)
  
  return {
    picks,
    loading: loading || processing,
    refreshPicks: () => {}, // Could trigger re-analysis
    savePick,
    unsavePick,
  };
}
```

### Step 2: Verify Dependencies

Check that `useRecommendations` still exists:
```bash
ls dashboard/lib/useRecommendations.ts
```

If it exists → great!  
If not → it was deleted by card-interfaces merge. Need to restore it.

### Step 3: Test the Integration

```bash
cd dashboard
npm run dev
```

Open http://localhost:3000/dashboard

Expected behavior:
- ✅ Real markets from Kalshi
- ✅ Real analysis from agents
- ✅ Pretty card swipe UI
- ✅ Auto-refresh every 60s

## 📁 File Structure

```
second_combine/
├── mcp_quantitative_agent/    ← Real Python backend
│   ├── server.py               ← MCP server
│   ├── quantitative_agent.py  ← CLI tool
│   └── ...
│
├── weather_test.py             ← Real weather analysis
├── politics_test.py            ← Real politics analysis
├── economics_test.py           ← Real economics analysis
│
└── dashboard/                  ← Card swipe UI
    ├── lib/
    │   ├── agents/             ← Real agent system (still here!)
    │   ├── useRecommendations.ts  ← Real agent orchestrator
    │   └── useTradingPicks.ts  ← Currently mock, needs update
    │
    └── components/
        ├── TradingCardDeck.tsx ← Card swipe interface
        ├── SwipeCard.tsx       ← Individual cards
        └── AgentFeed.tsx       ← Old sidebar (still exists)
```

## 🎨 UI Options

You now have BOTH UI styles available:

### Option A: Card Swipe (from card-interfaces)
- Component: `TradingCardDeck.tsx`
- Style: Tinder-like swipe
- Location: Full screen modal

### Option B: Sidebar List (from markets)
- Component: `AgentFeed.tsx`
- Style: List view
- Location: Right sidebar

### Option C: Both!
Show cards in main view, keep sidebar for quick reference:
```typescript
<div className="flex flex-col lg:flex-row gap-6">
  {/* Card Swipe (main) */}
  <div className="flex-1">
    <TradingCardDeck />
  </div>
  
  {/* Agent Feed (sidebar) */}
  <div className="lg:w-96 shrink-0">
    <AgentFeed />
  </div>
</div>
```

## 🚀 Quick Start

### Just Want to See It Work?

1. **Start Dashboard**:
   ```bash
   cd dashboard
   npm run dev
   ```
   Opens http://localhost:3000/dashboard
   
   Shows card swipe UI with **mock data** (fast demo)

2. **Start MCP Server** (optional, for AI assistants):
   ```bash
   cd mcp_quantitative_agent
   python server.py --http
   ```
   Opens http://localhost:8000
   
   Allows Claude Desktop/Cline to use your analysis

### Want Real Data in Cards?

Follow "Option 2" instructions above to connect `useTradingPicks` to `useRecommendations`.

## 🔄 Auto-Refresh Status

- **markets branch**: Had 60s auto-refresh ✅
- **card-interfaces**: No auto-refresh ❌
- **second_combine**: Depends on which hook you use
  - If using `useRecommendations`: Auto-refresh ✅
  - If using mock `useTradingPicks`: No auto-refresh ❌

## 📊 Comparison

| Feature | markets | card-interfaces | second_combine |
|---------|---------|-----------------|----------------|
| **MCP Server** | ✅ Yes | ❌ No | ✅ Yes |
| **Python Analysis** | ✅ Yes | ❌ No | ✅ Yes |
| **Agent System** | ✅ Full | ❌ None | ✅ Full (in code) |
| **Card Swipe UI** | ❌ No | ✅ Yes | ✅ Yes |
| **Sidebar UI** | ✅ Yes | ❌ No | ✅ Yes (still exists) |
| **Real Data** | ✅ Connected | ❌ Mock only | ⚠️ Not connected yet |
| **Auto-refresh** | ✅ 60s | ❌ No | ⚠️ Not connected yet |

## ✅ What to Do Next

### Immediate (Keep Mock Data):
```bash
cd dashboard
npm run dev
```
Demo the card swipe UI with fast-loading mock data.

### Short Term (30 min):
1. Update `useTradingPicks.ts` to use `useRecommendations`
2. Test that cards show real Kalshi markets
3. Verify auto-refresh works

### Long Term (Optional):
1. Add view toggle (cards vs list)
2. Improve card UI with real data
3. Add trade execution
4. Deploy both dashboard + MCP server

## 🎯 Recommended Approach for Demo

**For HackPrinceton judges:**

1. **Show card swipe UI first** (instant load, pretty)
   - "Here's our trading interface with AI recommendations"
   
2. **Open browser console** (show it's real)
   - "Behind the scenes, our multi-agent system is running"
   - Show logs from `useRecommendations`
   
3. **Switch to sidebar view** (show technical depth)
   - "Here's the full analysis breakdown"
   - Show NOAA, FRED data sources
   
4. **Demo MCP server** (if time)
   - "AI assistants can also use our analysis"
   - Run a Claude Desktop query

## 🐛 Potential Issues

### Issue 1: Cards show no data
**Cause**: `useTradingPicks` still using mock data, but mock generator broken

**Fix**: Either:
- Keep mock data working (quick fix)
- Connect to `useRecommendations` (proper fix)

### Issue 2: Real data is slow
**Cause**: Agents take 2-3s to analyze markets

**Fix**: Show loading state with:
```typescript
{loading && <div>Analyzing markets...</div>}
```

### Issue 3: Cards and agents conflict
**Cause**: Both trying to render

**Fix**: Choose one primary view

## 📝 Summary

**You now have:**
- ✅ Best backend (real Python analysis)
- ✅ Best frontend (card swipe UI)
- ⚠️ Not connected yet (but all pieces exist!)

**Next step:**
- Connect `useTradingPicks` to `useRecommendations`
- Or just demo with mock data for speed

**Best of both worlds is possible!** 🎉

---

**Branch**: `second_combine`  
**Created**: From `markets` + `card-interfaces` dashboard  
**Status**: Ready to connect or demo as-is

