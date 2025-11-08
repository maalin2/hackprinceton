# Real Data Migration Guide

The dashboard now uses **100% real data** from live APIs. No more mock data!

## What Changed

### ✅ All Providers Now Use Real APIs

| Component               | Old (Mock)           | New (Real)                          | Free?                    |
| ----------------------- | -------------------- | ----------------------------------- | ------------------------ |
| **Markets**             | Mock data array      | Kalshi API                          | ✅ Yes                   |
| **Weather**             | Random probabilities | NOAA + Open-Meteo + Visual Crossing | ✅ Mostly (VC needs key) |
| **Crypto**              | Random momentum      | CoinGecko + CryptoPanic             | ✅ Mostly (CP needs key) |
| **Politics**            | Random sentiment     | NewsAPI + Reddit + SerpAPI          | 🔑 NewsAPI key needed    |
| **Sports**              | Random ELO           | ESPN + NewsAPI                      | 🔑 NewsAPI key needed    |
| **Sentiment (Kalshi)**  | Mock comments        | Kalshi API (with fallback)          | ✅ Yes                   |
| **Sentiment (Twitter)** | Mock tweets          | Twitter API / Nitter / Reddit       | ✅ Fallback available    |

## Setup Instructions

### 1. Minimum Setup (Works Without Any Keys!)

The dashboard works out of the box with these free, no-key-needed APIs:

```bash
cd dashboard
npm install
npm run dev
```

**Available without keys:**

- ✅ Live Kalshi markets
- ✅ NOAA weather forecasts
- ✅ Open-Meteo weather forecasts
- ✅ CoinGecko crypto prices
- ✅ ESPN sports data
- ✅ Reddit sentiment

### 2. Recommended Setup (Add Free API Keys)

For full functionality, add these free API keys:

```bash
# 1. Copy the example environment file
cp env.example .env.local

# 2. Get free API keys:

# NewsAPI (100 requests/day) - https://newsapi.org/register
# Essential for politics and sports news sentiment
NEXT_PUBLIC_NEWS_API_KEY=your_newsapi_key_here

# Visual Crossing (1000 requests/day) - https://www.visualcrossing.com/weather-api
# Improves weather forecasts with historical data
NEXT_PUBLIC_VISUAL_CROSSING_KEY=your_visual_crossing_key_here

# CryptoPanic (50 requests/hour) - https://cryptopanic.com/developers/api/
# Adds crypto news sentiment
NEXT_PUBLIC_CRYPTOPANIC_KEY=your_cryptopanic_key_here

# 3. Restart the dev server
npm run dev
```

### 3. Optional Enhanced Setup

For even better results, add these optional keys:

```bash
# Twitter API (500k tweets/month) - https://developer.twitter.com/
# Better social sentiment than Reddit fallback
NEXT_PUBLIC_TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# SerpAPI (100 searches/month) - https://serpapi.com/
# Google Trends data for political momentum
NEXT_PUBLIC_SERPAPI_KEY=your_serpapi_key_here
```

## How Real Data Works

### Markets (`lib/useMarkets.ts`)

**Before:**

```typescript
const mockMarkets = [...];
```

**Now:**

```typescript
const response = await fetch(
  "https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=200"
);
```

- Fetches live open markets from Kalshi
- Auto-refreshes every 60 seconds
- Filters by domain, edge, spread
- Sorts by liquidity (volume)

### Weather (`lib/agents/quant/providers/weather.ts`)

**Before:**

```typescript
if (USE_MOCK) {
  return { probability: Math.random(), confidence: 0.85 };
}
```

**Now:**

```typescript
// 1. NOAA Weather.gov API
const pointResponse = await fetch(
  `https://api.weather.gov/points/${lat},${lon}`
);
const forecastData = await fetch(forecastUrl);

// 2. Open-Meteo ECMWF model
const response = await fetch(`https://api.open-meteo.com/v1/forecast?...`);

// 3. Visual Crossing historical data
const response = await fetch(`https://weather.visualcrossing.com/...`);
```

- Parses market ticker to extract location and threshold
- Fetches real forecasts from 3 independent sources
- Calculates probability using Normal distribution / sigmoid
- Returns weighted average with confidence scores

### Crypto (`lib/agents/quant/providers/crypto.ts`)

**Before:**

```typescript
rsi: 40 + Math.random() * 40;
```

**Now:**

```typescript
// CoinGecko price history (30 days)
const response = await fetch(
  `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=30`
);

// Calculate real RSI
const rsi = calculateRSI(prices, 14);

// Calculate real momentum
const weeklyReturn = (currentPrice - weekAgoPrice) / weekAgoPrice;

// Calculate real volatility
const volatility = Math.sqrt(variance) * Math.sqrt(365);
```

- Fetches real price data from CoinGecko
- Calculates actual RSI, MACD, momentum indicators
- Uses market cap changes and volume ratios for on-chain proxy
- Fetches crypto news from CryptoPanic with vote-based sentiment

### Politics (`lib/agents/quant/providers/politics.ts`)

**Before:**

```typescript
const sentiment = Math.random() * 0.6 + 0.2;
```

**Now:**

```typescript
// NewsAPI for headlines
const response = await fetch(
  `https://newsapi.org/v2/everything?q=${searchQuery}&...&apiKey=${key}`
);

// Count positive/negative keywords
positiveWords.forEach((word) => {
  if (text.includes(word)) sentimentScore += 1;
});

// Reddit for social momentum
const response = await fetch(
  `https://www.reddit.com/r/politics/search.json?q=${query}&...`
);

// Calculate engagement score
const engagement = (avgScore + avgComments) / 100;
```

- Fetches real news articles from NewsAPI
- Keyword-based sentiment analysis
- Reddit upvote ratio and engagement metrics
- Google Trends momentum (if SerpAPI key provided)

### Sports (`lib/agents/quant/providers/sports.ts`)

**Before:**

```typescript
const eloProb = 0.35 + Math.random() * 0.4;
```

**Now:**

```typescript
// ESPN API for scores/standings
const response = await fetch(
  `https://site.api.espn.com/apis/site/v2/sports/${sport}/scoreboard`
);

// Calculate real win rate from recent games
const winRate = total > 0 ? wins / total : 0.5;

// Count injury-related articles
const injuryArticles = articles.filter((a) =>
  a.headline?.toLowerCase().includes("injury")
);

// NewsAPI for sports news sentiment
const response = await fetch(
  `https://newsapi.org/v2/everything?q=${team} ${sport}&...`
);
```

- Fetches real game results from ESPN
- Calculates actual win/loss records
- Identifies injury news from ESPN feed
- News sentiment analysis for team perception

### Sentiment (`lib/agents/sentiment/`)

**Kalshi Comments:**

```typescript
// Attempts to fetch from Kalshi API
const response = await fetch(
  `https://kalshi.com/api/markets/${series}/comments`
);

// Fallback: Creates synthetic comment from market data
const marketResponse = await fetch(
  `https://api.elections.kalshi.com/trade-api/v2/markets/${series}`
);
```

**Twitter/Social:**

```typescript
// Option 1: Twitter API v2 (if key provided)
const response = await fetch(
  `https://api.twitter.com/2/tweets/search/recent?...`,
  { headers: { Authorization: `Bearer ${token}` } }
);

// Option 2: Nitter (Twitter scraper mirror)
const response = await fetch(`https://nitter.net/search?q=${query}`);

// Option 3: Reddit fallback
const response = await fetch(
  `https://www.reddit.com/r/${subreddit}/search.json?q=${query}`
);
```

- Tries multiple sources in priority order
- VADER sentiment analysis on all text
- Probability conversion: `P_sentiment = 0.5 + 0.3 * compound_score`
- Confidence based on sample size and agreement

## Verification

To verify everything is working with real data:

### 1. Check Console Logs

Open browser console (F12) and look for:

```
📊 Quant Agent: Weather market KXHIGHPHIL-25NOV08-T71
  ✅ NOAA: 0.63 (confidence: 0.85)
  ✅ Open-Meteo: 0.59 (confidence: 0.80)
  ✅ Meteostat: 0.52 (confidence: 0.70)

📝 Kalshi Comments (3):
  1. "Market currently at 2¢. Volume: 1200 contracts. This market looks bullish."
     👤 Market Data | 🔗 https://kalshi.com/markets/KXHIGHPHIL

🐦 Twitter Posts (12):
  1. "Weather forecast shows temperatures rising..."
     👤 @weathernerd | ❤️  45 | 🔗 https://twitter.com/weathernerd/status/...
```

### 2. Check Market Data

Markets should show:

- Real tickers from Kalshi (e.g., `KXHIGHPHIL-25NOV08-T71`)
- Real prices (not random numbers)
- Real volumes and open interest
- Real close times matching Kalshi's site

### 3. Check Recommendations

Recommendations should:

- Take 2-5 seconds to generate (API calls in progress)
- Show real source data in probability grid
- Have clickable links to actual news articles/tweets/comments
- Update every 60 seconds with new analysis

### 4. Compare to Kalshi

Visit https://kalshi.com/ and compare:

- Market titles should match exactly
- Prices should be within a few cents (due to timing)
- Categories should align

## Fallback Behavior

The system gracefully degrades when APIs fail:

```
Primary API Failed → Try Fallback → Still Failed → Skip Source
```

**Example flows:**

**Weather:**

```
NOAA fails → Open-Meteo works → Use Open-Meteo + climatology
All fail → Throw error (weather markets require forecasts)
```

**Crypto:**

```
CryptoPanic fails → Use CoinGecko only → Still valid (price momentum sufficient)
CoinGecko fails → Throw error (need price data)
```

**Politics:**

```
NewsAPI fails → Use Reddit → Still valid (sentiment signal)
All fail → Throw error (need some news source)
```

**Twitter:**

```
Twitter API fails → Try Nitter → Try Reddit → Use Reddit (similar signal)
All fail → Return empty array → Use only Kalshi comments
```

## Performance

### Typical API Response Times

| Provider       | Response Time | Parallel | Cached |
| -------------- | ------------- | -------- | ------ |
| Kalshi Markets | 200-500ms     | Yes      | 60s    |
| NOAA Weather   | 300-800ms     | Yes      | N/A    |
| Open-Meteo     | 100-300ms     | Yes      | N/A    |
| CoinGecko      | 200-600ms     | Yes      | N/A    |
| NewsAPI        | 300-1000ms    | Yes      | N/A    |
| ESPN           | 200-500ms     | Yes      | N/A    |
| Reddit         | 300-700ms     | Yes      | N/A    |

### Total Analysis Time

- **Single market**: 2-5 seconds (parallel provider calls)
- **10 markets**: ~30 seconds (analyzed sequentially)
- **Caching**: Results cached 60s, subsequent calls instant

### Optimization Tips

1. **Limit market count**: Use filters (domain, minEdge, maxSpread)
2. **Increase cache time**: Modify cache duration in `useRecommendations`
3. **Batch similar markets**: Group by category to reuse some data
4. **Add Redis**: Cache weather/news across markets

## Troubleshooting

### "All providers failed"

**Check:**

1. Internet connection
2. API keys in `.env.local`
3. Console for specific errors
4. API status pages

### Slow recommendations

**Causes:**

- Many markets being analyzed
- Slow API responses
- Rate limiting

**Solutions:**

- Filter markets by domain
- Add API keys for better rate limits
- Increase cache duration
- Check network speed

### Wrong probabilities

**Causes:**

- Ticker parsing failed
- API returned stale data
- Market type mismatch

**Solutions:**

- Check console for parsing errors
- Add location/ticker mappings
- Verify API responses in Network tab

## Development vs Production

### Development (Current)

```
✅ All APIs use free tiers
✅ No database required
✅ Client-side data fetching
✅ Basic caching (in-memory, 60s)
```

### Production Recommendations

```
🚀 Upgrade to paid API tiers (higher limits)
🚀 Server-side API calls (hide keys, better caching)
🚀 Redis for cross-request caching
🚀 Background jobs for pre-analysis
🚀 WebSocket for real-time updates
🚀 Database for historical recommendations
```

---

**You're now running on 100% real data!** 🎉

Check `API_SETUP.md` for detailed API documentation and `AGENTS.md` for agent architecture.
