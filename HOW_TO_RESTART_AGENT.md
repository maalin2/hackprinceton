# How to Restart the Agent

## Quick Commands

### Option 1: Full Server Restart (Clears Everything)

```bash
# Stop the server
cd dashboard
pkill -f "next dev"

# Start fresh
npm run dev
```

### Option 2: Just Restart Browser (Soft Restart)

- **Hard Refresh**: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Clears cache and reloads the page
- Agent will re-analyze on page load

### Option 3: Manual Trigger (In Browser Console)

```javascript
// Open browser console (F12) and run:
window.location.reload(true);
```

## What Each Option Does

### Full Server Restart

**When to use**: When you've changed code or need a complete fresh start

**What it clears**:

- ✅ All cached data
- ✅ WebSocket connections
- ✅ Agent state
- ✅ Market data
- ✅ Recommendations

**How long**: ~5-10 seconds to restart

**Steps**:

1. Kill the dev server
2. Restart with `npm run dev`
3. Wait for "Ready in Xs"
4. Open http://localhost:3000/dashboard

### Browser Hard Refresh

**When to use**: When the server is running but you want fresh recommendations

**What it clears**:

- ✅ Browser cache
- ✅ React component state
- ✅ Current recommendations
- ⚠️ Keeps server state

**How long**: Instant

**Steps**:

1. Press Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
2. Agent automatically re-analyzes on load

### Just Wait 60 Seconds

**When to use**: To see fresh market data without restarting

**What happens**:

- Agent auto-refreshes every 60 seconds
- Fetches latest market prices
- Re-analyzes with updated data
- New recommendations appear

**No action needed** - just watch!

## Current Status

✅ **Server is now restarting...**

Wait ~5-10 seconds, then:

1. Open http://localhost:3000/dashboard
2. Check browser console (F12) for:
   ```
   ✅ Agent Feed: Using REAL multi-agent system
   🔍 RAW DATA from useRecommendations:
   ```
3. See fresh recommendations in right sidebar

## Troubleshooting

### "Port 3000 is already in use"

```bash
# Kill any process on port 3000
lsof -ti:3000 | xargs kill -9

# Then restart
npm run dev
```

### "Recommendations not updating"

1. Hard refresh browser (Cmd+Shift+R)
2. Check console for errors
3. Verify auto-refresh is running (should see logs every 60s)

### "Agent shows old data"

1. Full server restart (Option 1 above)
2. Clear browser cache
3. Hard refresh

### "Too many Reddit errors"

This is **normal** - Reddit rate limits your IP. The agent still works because:

- Uses other sources (NOAA, Kalshi comments, etc.)
- Reddit is just ONE of many sources
- Recommendations generate successfully without it

## Quick Reference

| Action           | Command                              | Time    | Clears       |
| ---------------- | ------------------------------------ | ------- | ------------ |
| **Full Restart** | `pkill -f "next dev" && npm run dev` | 5-10s   | Everything   |
| **Hard Refresh** | Cmd+Shift+R                          | Instant | Browser only |
| **Auto-Refresh** | (Wait 60s)                           | 60s     | Updates data |
| **Kill Port**    | `lsof -ti:3000 \| xargs kill -9`     | Instant | Port only    |

## Monitoring Agent Status

### Check if agent is running:

```bash
# Should show "next dev" process
ps aux | grep "next dev"
```

### Check agent logs in browser console:

1. Open http://localhost:3000/dashboard
2. Press F12 (Developer Tools)
3. Go to Console tab
4. Look for:
   - ✅ "Agent Feed: Using REAL multi-agent system"
   - 📨 "Agent Feed: Updated with X recommendations"
   - 🎯 Individual recommendation details

### Check server logs in terminal:

- Should see "[Recommendations] Analyzing X markets"
- Should see market fetching logs
- Reddit 429 errors are normal (rate limiting)

## What Happens on Restart

1. **Server Stops** (if doing full restart)

   - Closes all connections
   - Clears cache
   - Stops agent analysis

2. **Server Starts**

   - Next.js compiles
   - Shows "Ready in Xs"
   - Server listens on http://localhost:3000

3. **Browser Loads Dashboard**

   - Fetches user preferences
   - Initializes agent system
   - Starts fetching markets

4. **Agent Analyzes**

   - Fetches top 50 markets by volume
   - Runs Quant + Sentiment agents on top 20
   - Generates recommendations
   - Displays in right sidebar

5. **Auto-Refresh Begins**
   - Every 60 seconds
   - Re-fetches markets
   - Re-analyzes with latest data
   - Updates recommendations

## Expected Behavior After Restart

✅ Green dot (●) next to "Agent Recommendations"  
✅ Shows "X pending" recommendation count  
✅ Displays recommendation cards in right sidebar  
✅ Tickers are blue and clickable  
✅ Console shows detailed logs  
✅ Auto-refresh every 60 seconds

## Common Issues After Restart

### No recommendations appearing

**Possible causes**:

- All markets returned HOLD (no edge > 8%)
- Markets are closed (weather markets are seasonal)
- Network issues

**Solution**:

- Check console for "Analyzing X markets"
- Wait for full analysis (2-3 seconds)
- Check if any errors in console

### Same recommendations as before

**This is NORMAL**:

- Markets haven't changed in 60 seconds
- Same opportunities still exist
- Wait 5-10 minutes for market shifts

### Infinite console logs

**If fixed properly**:

- Should only log once per update
- Should see "Updated with X recommendations"
- Should NOT continuously repeat

**If still happening**:

- Hard refresh browser
- Clear browser cache
- Full server restart

---

**Current Status**: Server restarting, will be ready in ~5-10 seconds  
**Test URL**: http://localhost:3000/dashboard  
**Next Step**: Open browser and check console logs
