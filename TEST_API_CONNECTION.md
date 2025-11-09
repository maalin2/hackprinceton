# 🧪 Test API Connection - Quick Guide

## How to Test Python Backend from Dashboard

### Step 1: Start Python Backend

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton
python3 api_server.py
```

Wait for:

```
🚀 KALSHI HYBRID ANALYSIS API STARTING
Docs: http://localhost:8000/docs
```

### Step 2: Start Dashboard

```bash
cd dashboard
npm run dev
```

### Step 3: Open Dashboard & Console

1. Open http://localhost:3000/dashboard in browser
2. Open browser console (Press F12 or Right-click → Inspect → Console)

### Step 4: Run Test

In the browser console, type:

```javascript
window.testAPI();
```

Press Enter.

---

## 📺 What You'll See

### Console Output (Success):

```
================================================================================
🧪 TESTING PYTHON API CONNECTION
================================================================================
API Base URL: http://localhost:8000
Time: 11/9/2025, 2:30:45 PM
================================================================================

📡 Test 1: Health Check
   Calling: GET /
   ✅ Status: 200
   📦 Response: {
     "status": "online",
     "service": "Kalshi Hybrid Analysis API",
     "version": "1.0.0"
   }

📡 Test 2: Status Check
   Calling: GET /api/status
   ✅ Status: 200
   📦 Response: {
     "status": "ready",
     "isAnalyzing": false,
     "lastUpdated": "2025-11-09T14:30:52.123Z",
     "count": 12,
     "error": null
   }

📡 Test 3: Get Recommendations
   Calling: GET /api/recommendations
   ✅ Status: 200
   📊 Response Status: success
   📦 Opportunities Count: 12

   🎯 SAMPLE RECOMMENDATION:
   --------------------------------------------------------------------------------
   Ticker: KXHIGHCHI-25NOV09-T38
   Title: Will the high temp in Chicago be <38° on Nov 9, 2025?
   Category: Weather
   Action: BUY_YES
   Quant Edge: 79.0%
   Market Prob: 0.5%
   Combined Confidence: 88.0%

   🤖 GROK SENTIMENT:
   Label: positive
   Score: 82%
   Confidence: high
   Key Themes: cold front, arctic blast, freezing

   💡 REASONING:
   Statistical analysis shows a 79.0% edge. Models predict 79.5% probability vs
   market price of 0.5%. Grok AI sentiment analysis: positive (82%). Key themes:
   cold front, arctic blast, freezing. ✅ Both quantitative and sentiment signals
   AGREE, increasing confidence.
   --------------------------------------------------------------------------------

   📊 ALL RECOMMENDATIONS:
   1. KXHIGHCHI-25NOV09-T38 - BUY_YES (Edge: 79.0%)
   2. KXHIGHDEN-25NOV08-B53.5 - BUY_NO (Edge: -90.9%)
   3. KXHIGHCHI-25NOV09-B40.5 - BUY_NO (Edge: -77.5%)
   4. KXHIGHDEN-25NOV08-T51 - BUY_YES (Edge: 63.7%)
   5. KXHIGHNY-25NOV09-T59 - BUY_YES (Edge: 62.8%)
   ... (7 more)

================================================================================
✅ API CONNECTION TEST COMPLETE
================================================================================
```

### Console Output (Backend Analyzing):

```
📡 Test 3: Get Recommendations
   Calling: GET /api/recommendations
   ✅ Status: 200
   📊 Response Status: analyzing
   📦 Opportunities Count: 0

   ⏳ Backend is currently analyzing markets
   💡 Wait 30-60 seconds and try again

================================================================================
✅ API CONNECTION TEST COMPLETE
================================================================================
```

### Console Output (Error):

```
================================================================================
❌ API CONNECTION TEST FAILED
================================================================================

🔥 Error: Failed to fetch

💡 Troubleshooting:
   1. Is Python backend running? (python3 api_server.py)
   2. Is it running on port 8000?
   3. Check Terminal 1 for backend errors
   4. Try: curl http://localhost:8000/api/status
================================================================================
```

---

## 🔍 What Gets Tested

1. **Health Check** (`GET /`)

   - Verifies backend is online
   - Returns service info

2. **Status Check** (`GET /api/status`)

   - Checks if analysis is running
   - Shows last update time
   - Shows recommendation count

3. **Get Recommendations** (`GET /api/recommendations`)
   - Fetches actual recommendations
   - Shows full details of first recommendation
   - Shows list of all recommendations

---

## 🐛 Troubleshooting

### Problem: "Failed to fetch"

**Cause:** Backend not running or wrong port

**Fix:**

1. Check Terminal 1 - is `python3 api_server.py` running?
2. Should show: `Docs: http://localhost:8000/docs`
3. Try: `curl http://localhost:8000/api/status`

### Problem: "Response Status: empty"

**Cause:** Backend hasn't finished first analysis yet

**Fix:** Wait 30-60 seconds, run `window.testAPI()` again

### Problem: "Response Status: analyzing"

**Cause:** Backend is currently analyzing (normal!)

**Fix:** Wait 30-60 seconds, run `window.testAPI()` again

### Problem: CORS error

**Cause:** Backend and dashboard on different domains

**Fix:**

1. Ensure backend is on `localhost:8000`
2. Ensure dashboard is on `localhost:3000`
3. Restart both if needed

---

## 📊 Python Backend Terminal Output

When you run `window.testAPI()`, you'll see this in Terminal 1:

```
📥 GET / - Request received at 14:31:20

📥 GET /api/status - Request received at 14:31:20
   ✅ Returning status: ready

📥 GET /api/recommendations - Request received at 14:31:20
   ✅ Returning 12 recommendations
   📅 Last updated: 14:30:52
```

This confirms the backend is receiving and responding to requests!

---

## 🎯 Success Criteria

Your API connection is working if:

- ✅ All 3 tests pass (Health, Status, Recommendations)
- ✅ You see recommendations in console
- ✅ Backend terminal shows incoming requests
- ✅ No error messages

---

## 🔄 Alternative: Test with curl

You can also test the API directly from terminal:

```bash
# Health check
curl http://localhost:8000/

# Status check
curl http://localhost:8000/api/status

# Get recommendations
curl http://localhost:8000/api/recommendations | jq
```

(Install `jq` for pretty JSON: `brew install jq`)

---

## 📝 What This Proves

Running `window.testAPI()` proves:

1. ✅ Dashboard can reach Python backend
2. ✅ Backend is responding correctly
3. ✅ API endpoints are working
4. ✅ Data is flowing correctly
5. ✅ Recommendations are being generated

Perfect for showing judges: "Here's the live API connection!" 🎓

---

## 🎬 For Demo

During HackPrinceton demo:

1. Open dashboard
2. Open console (F12)
3. Type: `window.testAPI()`
4. Show judges the output
5. Point out:
   - Real-time API calls
   - Python backend responding
   - Actual recommendations with Grok sentiment
   - All the data flowing through

**This is EXTREMELY impressive!** Shows both pretty UI AND technical depth. 🚀
