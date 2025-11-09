# 🚀 QUICK START - Hybrid Analysis System

## ⚡ Start in 3 Steps

### 1️⃣ Set API Key (REQUIRED!)

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton

# Create .env file with your X API key
echo "X_API_KEY=your_xai_api_key_here" > .env

# Get your key from: https://x.ai
```

### 2️⃣ Start Backend (Terminal 1)

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton
python3 api_server.py
```

**Expected output:**

```
🚀 KALSHI HYBRID ANALYSIS API STARTING
Docs: http://localhost:8000/docs
API: http://localhost:8000/api/recommendations
🔄 Running initial analysis...
```

**Wait ~60 seconds for first analysis to complete!**

### 3️⃣ Start Dashboard (Terminal 2)

```bash
cd /Users/anshulmangalapalli/Documents/GitHub/hackprinceton/dashboard
npm run dev
```

**Then open:** http://localhost:3000/dashboard

---

## ✅ You're Done!

You should now see:

- **Backend analyzing** in Terminal 1
- **Dashboard displaying recommendations** in browser
- **Real-time updates** every 60 seconds

---

## 🎯 What You're Seeing

Each recommendation card shows:

- **📊 Quantitative Edge** (from NOAA, FRED, Open-Meteo)
- **🤖 Grok AI Sentiment** (from Twitter analysis)
- **✅ Combined Confidence** (75% quant + 25% sentiment)
- **💡 Detailed Reasoning** (why you should bet)
- **🔗 Kalshi Link** (to place actual bet)

---

## 🐛 Troubleshooting

### Problem: Backend fails

```bash
# Install dependencies
pip3 install --break-system-packages fastapi uvicorn pydantic

# Try again
python3 api_server.py
```

### Problem: "X_API_KEY not set"

```bash
# Check .env file exists
cat .env

# Should show: X_API_KEY=your_key_here
# If not, create it:
echo "X_API_KEY=your_actual_key" > .env
```

### Problem: Dashboard shows "No recommendations"

**Wait 60 seconds!** First analysis takes time.

Then check:

```bash
curl http://localhost:8000/api/status
```

---

## 📖 Full Documentation

- **Setup Guide:** `HYBRID_SYSTEM_SETUP.md`
- **Implementation:** `IMPLEMENTATION_COMPLETE.md`
- **API Docs:** http://localhost:8000/docs (when backend running)

---

## 🎓 For HackPrinceton Demo

Just run the 3 steps above and you're ready to demo!

Show judges:

1. Dashboard with real-time recommendations
2. Backend terminal showing analysis
3. Click a card to show detailed reasoning
4. Explain: Stats filter → AI verify → Combine signals

Good luck! 🚀
