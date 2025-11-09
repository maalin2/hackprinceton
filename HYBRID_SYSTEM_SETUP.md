# 🤖 Hybrid Analysis System - Setup & Usage Guide

**Statistical Screening + Grok AI Sentiment** → Dashboard

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────┐
│  PYTHON BACKEND (Port 8000)                                │
│                                                             │
│  api_server.py (FastAPI)                                   │
│      ↓                                                      │
│  hybrid_analysis.py                                        │
│      ├─→ Statistical Screening (weather/politics/economics)│
│      ├─→ Grok Sentiment Analysis (for filtered bets)      │
│      └─→ Combined Decision (75% quant, 25% sentiment)     │
└────────────────────────────────────────────────────────────┘
                            ↓ HTTP API
┌────────────────────────────────────────────────────────────┐
│  NEXT.JS DASHBOARD (Port 3000)                             │
│                                                             │
│  useRecommendations.ts                                     │
│      ├─→ Fetches from http://localhost:8000/api/recommendations
│      ├─→ Displays in TradingCardDeck (card swipe UI)      │
│      └─→ Displays in AgentFeed (sidebar list)             │
└────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** installed
3. **X API Key** (for Grok sentiment analysis)
4. **API Keys** (optional):
   - `FRED_API_KEY` (for economics)
   - `ALPHA_VANTAGE_API_KEY` (for economics)

---

## 🚀 Installation

### Step 1: Install Python Dependencies

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton

# Install API server dependencies
pip3 install --break-system-packages -r api_requirements.txt

# Verify installation
python3 -c "import fastapi; print('FastAPI installed ✅')"
python3 -c "import uvicorn; print('Uvicorn installed ✅')"
```

### Step 2: Set Up Environment Variables

Create or update `.env` file in the project root:

```bash
# Required for Grok sentiment analysis
X_API_KEY=your_xai_api_key_here

# Optional for economics analysis
FRED_API_KEY=your_fred_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

**Get your X API key:**

1. Go to https://x.ai
2. Sign up / Log in
3. Get your API key
4. Add to `.env`

### Step 3: Install Dashboard Dependencies

```bash
cd dashboard
npm install
```

---

## 🎮 Running the System

### Terminal 1: Start Python Backend

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton

# Run the API server
python3 api_server.py

# Expected output:
# 🚀 KALSHI HYBRID ANALYSIS API STARTING
# Docs: http://localhost:8000/docs
# API: http://localhost:8000/api/recommendations
# 🔄 Running initial analysis...
```

**Server will:**

- Run initial analysis on startup
- Auto-refresh every 5 minutes
- Cache results for fast dashboard access
- Expose REST API on port 8000

### Terminal 2: Start Dashboard

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton/dashboard

npm run dev

# Expected output:
# ▲ Next.js 14.x.x
# - Local:   http://localhost:3000
# - Ready in 2.3s
```

### Terminal 3: (Optional) Monitor Logs

```bash
# Watch Python backend logs
tail -f /path/to/logs

# Or just watch Terminal 1 for analysis progress
```

---

## 🌐 Accessing the System

### Dashboard UI

Open http://localhost:3000/dashboard

You'll see:

- **Card Swipe UI** (Tinder-style) - swipe through recommendations
- **Sidebar Feed** - list of all recommendations
- **Real-time updates** - refreshes every 60 seconds

### API Endpoints

**Interactive API Docs:**
http://localhost:8000/docs

**Get Recommendations:**

```bash
curl http://localhost:8000/api/recommendations
```

**Check Status:**

```bash
curl http://localhost:8000/api/status
```

**Trigger New Analysis:**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "edge_threshold": 0.10,
    "max_recommendations": 20
  }'
```

---

## 📊 How It Works

### 1. Statistical Screening (Fast, Cheap)

The system first filters ~150 markets to ~10-20 high-edge opportunities:

```python
# Runs weather_test.py, politics_test.py, economics_test.py
# Filters for edge > 10%
# Returns top opportunities by absolute edge
```

**Data Sources:**

- Weather: NOAA, Open-Meteo, Climatology
- Politics: Kalshi Consensus, Historical Patterns, Betting Models
- Economics: FRED, Economic Indicators, Market Consensus

### 2. Grok Sentiment Verification (Slow, Costs $)

For each filtered bet, calls Grok AI:

```python
# Analyzes Twitter sentiment
# Returns label (positive/negative/neutral)
# Returns key themes
# Returns confidence score
```

**Cost:** ~$0.01-0.05 per market analyzed

### 3. Combine Signals

Weighted combination:

- **75%** Quantitative edge
- **25%** Grok sentiment

**Decision Logic:**

- If both agree → HIGH CONFIDENCE ✅
- If disagree → MEDIUM CONFIDENCE ⚠️
- If low confidence → SKIP ❌

### 4. Display on Dashboard

Results shown in real-time with:

- Quantitative edge
- Grok sentiment analysis
- Combined confidence
- Detailed reasoning
- Action buttons (Accept, Snooze, Dismiss)

---

## 🎯 Usage Examples

### Example 1: View Current Recommendations

1. Open dashboard: http://localhost:3000/dashboard
2. See recommendations in card format
3. Swipe right to accept, left to dismiss
4. OR use sidebar to see full list

### Example 2: Manually Trigger Analysis

```bash
# Trigger with custom parameters
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "edge_threshold": 0.15,
    "max_recommendations": 10,
    "quant_weight": 0.8,
    "sentiment_weight": 0.2
  }'

# Wait ~30-60 seconds for analysis to complete

# Fetch results
curl http://localhost:8000/api/recommendations
```

### Example 3: Run CLI Analysis

```bash
# Run hybrid analysis from command line
python3 hybrid_analysis.py --edge 0.10 --max 20

# Output JSON format
python3 hybrid_analysis.py --json > recommendations.json
```

---

## 🔧 Configuration

### Adjust Analysis Parameters

Edit `api_server.py` or pass parameters via API:

```python
# Edge threshold (default: 10%)
edge_threshold = 0.10  # Filter for opportunities with >10% edge

# Max recommendations (default: 20)
max_recommendations = 20  # Limit to top 20 to avoid too many Grok calls

# Signal weights (default: 75% quant, 25% sentiment)
quant_weight = 0.75
sentiment_weight = 0.25

# Auto-refresh interval (default: 5 minutes)
# Edit in api_server.py: auto_refresh_loop()
```

### Adjust Dashboard Refresh

Edit `dashboard/lib/useRecommendations.ts`:

```typescript
// Change refresh interval (default: 60 seconds)
const interval = setInterval(() => {
  fetchRecommendations();
}, 60000); // 60000 = 1 minute
```

---

## 🐛 Troubleshooting

### Problem: Python backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**

```bash
pip3 install --break-system-packages fastapi uvicorn
```

### Problem: Grok sentiment failing

**Error:** `X_API_KEY environment variable is not set`

**Solution:**

1. Check `.env` file has `X_API_KEY=...`
2. Restart Python backend
3. Verify key is valid at https://x.ai

### Problem: Dashboard shows "No recommendations"

**Possible Causes:**

1. Python backend not running → Start it in Terminal 1
2. Analysis still in progress → Wait 30-60 seconds
3. No high-edge opportunities found → Lower edge threshold

**Check Status:**

```bash
curl http://localhost:8000/api/status
```

### Problem: CORS errors in browser console

**Error:** `Access-Control-Allow-Origin`

**Solution:**

- Ensure Python backend is running on port 8000
- Check `api_server.py` has correct CORS settings
- Verify dashboard is on port 3000

### Problem: Slow analysis

**Cause:** Grok API calls take time (~2-3 seconds each)

**Solutions:**

1. Reduce `max_recommendations` to analyze fewer markets
2. Increase `edge_threshold` to filter more aggressively
3. Results are cached for 5 minutes, so subsequent requests are instant

---

## 📈 Performance Metrics

### Analysis Speed

- **Statistical screening:** ~5-10 seconds (150 markets)
- **Grok sentiment (per market):** ~2-3 seconds
- **Total for 10 markets:** ~30-40 seconds
- **Total for 20 markets:** ~50-70 seconds

### Cost Estimates

- **Grok API:** ~$0.01-0.05 per market
- **10 markets:** ~$0.10-0.50
- **20 markets:** ~$0.20-1.00
- **Per day (auto-refresh every 5 min):** ~$5-20

### Caching

- Results cached for 5 minutes
- Dashboard can fetch cached results instantly
- Auto-refresh triggers new analysis every 5 minutes

---

## 🎯 What You'll See

### Dashboard Recommendation Card Example

```
┌──────────────────────────────────────────────────────┐
│ 🌡️ Chicago Temperature - Nov 9                      │
│                                                      │
│ 📊 QUANTITATIVE ANALYSIS                             │
│    Edge: 79.0%                                       │
│    Sources: NOAA (40°F), Open-Meteo (39°F)          │
│    Model thinks: 79.5% likely                       │
│    Market price: 0.5%                                │
│                                                      │
│ 🤖 GROK AI SENTIMENT                                 │
│    Label: Positive (82%)                             │
│    Confidence: High                                  │
│    Key Themes: cold front, arctic blast, freezing   │
│                                                      │
│ ✅ BOTH SIGNALS AGREE → High Confidence!             │
│                                                      │
│ 🎯 RECOMMENDATION: BUY YES                           │
│    Combined Confidence: 88%                          │
│                                                      │
│ 💡 Both weather models and social sentiment confirm │
│    unseasonably cold weather. Strong statistical    │
│    edge combined with positive sentiment creates    │
│    high-confidence opportunity.                     │
│                                                      │
│ [✓ Accept]  [⏰ Snooze]  [✗ Dismiss]                │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Checklist

- [ ] Install Python dependencies (`pip3 install -r api_requirements.txt`)
- [ ] Set `X_API_KEY` in `.env`
- [ ] Start Python backend (`python3 api_server.py`)
- [ ] Start dashboard (`cd dashboard && npm run dev`)
- [ ] Open http://localhost:3000/dashboard
- [ ] Wait 30-60 seconds for first analysis
- [ ] See hybrid recommendations! 🎉

---

## 📝 Files Created

- ✅ `hybrid_analysis.py` - Main analysis pipeline
- ✅ `api_server.py` - FastAPI backend
- ✅ `api_requirements.txt` - Python dependencies
- ✅ `dashboard/lib/useRecommendations.ts` - Updated to call Python API
- ✅ `HYBRID_SYSTEM_SETUP.md` - This guide

---

## 🎓 For HackPrinceton Demo

**What to show judges:**

1. **Open dashboard** - Show real-time recommendations
2. **Show Python terminal** - Show analysis happening in real-time
3. **Click a recommendation** - Show detailed breakdown:
   - Quantitative sources (NOAA, FRED, etc.)
   - Grok AI sentiment
   - Combined reasoning
4. **Show API docs** - http://localhost:8000/docs
5. **Explain hybrid approach** - Stats filter, AI verify, combine signals

**Key talking points:**

- ✅ Real data from NOAA, FRED, Open-Meteo
- ✅ AI-powered sentiment with Grok
- ✅ Statistical arbitrage detection
- ✅ Production-ready architecture (backend + frontend)
- ✅ Auto-refresh for real-time updates

---

**Built with ❤️ for HackPrinceton**

Questions? Check logs in Terminal 1 (Python) and browser console (Dashboard).

Happy trading! 🎲
