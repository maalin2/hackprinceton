# API Setup Guide

This dashboard uses real data from multiple sources. Most APIs have free tiers that are sufficient for development and demo purposes.

## Required APIs

### 1. Kalshi Markets (✅ No Key Required)

- **Purpose**: Fetch live prediction market data
- **Setup**: No API key needed for read-only access
- **Rate Limit**: Reasonable rate limits for public endpoints
- **Docs**: https://trading-api.readme.io/reference/getting-started

### 2. Weather APIs

#### NOAA Weather API (✅ No Key Required)

- **Purpose**: U.S. weather forecasts
- **Setup**: No API key needed
- **Rate Limit**: Reasonable
- **Docs**: https://www.weather.gov/documentation/services-web-api
- **Note**: Requires User-Agent header

#### Open-Meteo (✅ No Key Required)

- **Purpose**: Global weather forecasts (ECMWF model)
- **Setup**: No API key needed
- **Rate Limit**: 10,000 requests/day (free)
- **Docs**: https://open-meteo.com/en/docs

#### Visual Crossing (🔑 Key Required)

- **Purpose**: Historical weather data for climatology
- **Setup**:
  1. Sign up at: https://www.visualcrossing.com/weather-api
  2. Free tier: 1,000 requests/day
  3. Add to `.env.local`:
     ```
     NEXT_PUBLIC_VISUAL_CROSSING_KEY=your_key_here
     ```
- **Fallback**: System uses climatological averages if API fails

### 3. Crypto APIs

#### CoinGecko (✅ No Key Required)

- **Purpose**: Cryptocurrency prices, market data, on-chain proxies
- **Setup**: No API key needed for basic endpoints
- **Rate Limit**: 10-50 calls/minute (free)
- **Docs**: https://www.coingecko.com/en/api/documentation

#### CryptoPanic (🔑 Key Recommended)

- **Purpose**: Crypto news sentiment
- **Setup**:
  1. Sign up at: https://cryptopanic.com/developers/api/
  2. Free tier: 50 requests/hour
  3. Add to `.env.local`:
     ```
     NEXT_PUBLIC_CRYPTOPANIC_KEY=your_key_here
     ```
- **Fallback**: Works with demo key (limited)

### 4. News APIs

#### NewsAPI (🔑 Key Required)

- **Purpose**: News headlines for politics and sports sentiment
- **Setup**:
  1. Sign up at: https://newsapi.org/register
  2. Free tier: 100 requests/day
  3. Add to `.env.local`:
     ```
     NEXT_PUBLIC_NEWS_API_KEY=your_key_here
     ```
- **Note**: Essential for politics and sports categories

#### ESPN API (✅ No Key Required)

- **Purpose**: Sports scores, standings, injury reports
- **Setup**: No API key needed (unofficial public API)
- **Rate Limit**: Reasonable
- **Docs**: Unofficial - https://site.api.espn.com/

### 5. Social/Search APIs

#### Reddit API (✅ No Key Required)

- **Purpose**: Social sentiment, discussions
- **Setup**: No API key needed for read-only JSON endpoints
- **Rate Limit**: ~60 requests/minute
- **Docs**: https://www.reddit.com/dev/api

#### Twitter/X API (🔑 Key Optional)

- **Purpose**: Twitter sentiment analysis
- **Setup**:
  1. Apply at: https://developer.twitter.com/en/portal/dashboard
  2. Free tier: 500k tweets/month (v2 API)
  3. Add to `.env.local`:
     ```
     NEXT_PUBLIC_TWITTER_BEARER_TOKEN=your_token_here
     ```
- **Fallback**: Uses Nitter (Twitter scraper) or Reddit as proxy

#### SerpAPI for Google Trends (🔑 Key Optional)

- **Purpose**: Public interest/momentum signals for politics
- **Setup**:
  1. Sign up at: https://serpapi.com/
  2. Free tier: 100 searches/month
  3. Add to `.env.local`:
     ```
     NEXT_PUBLIC_SERPAPI_KEY=your_key_here
     ```
- **Fallback**: Uses news sentiment as proxy

## Quick Start (Minimum Setup)

For basic functionality, you only need:

1. **No keys at all!** The system works with:

   - Kalshi markets (no key)
   - Open-Meteo weather (no key)
   - CoinGecko crypto (no key)
   - ESPN sports (no key)
   - Reddit sentiment (no key)

2. **For full functionality**, add these keys (all have free tiers):

   ```bash
   # Copy the example file
   cp env.example .env.local

   # Add your keys to .env.local
   NEXT_PUBLIC_NEWS_API_KEY=your_newsapi_key        # Free: 100 req/day
   NEXT_PUBLIC_VISUAL_CROSSING_KEY=your_vc_key      # Free: 1000 req/day
   NEXT_PUBLIC_CRYPTOPANIC_KEY=your_cp_key          # Free: 50 req/hour
   ```

3. **Optional enhancements**:
   ```bash
   NEXT_PUBLIC_TWITTER_BEARER_TOKEN=your_token      # Free: 500k tweets/month
   NEXT_PUBLIC_SERPAPI_KEY=your_serpapi_key         # Free: 100 searches/month
   ```

## Testing Without Keys

The system gracefully degrades when APIs are unavailable:

- **Weather**: Falls back to NOAA + Open-Meteo + climatology
- **Crypto**: Uses CoinGecko only (no key needed)
- **Politics**: Uses Reddit sentiment if news API unavailable
- **Sports**: Uses ESPN (no key) + Reddit fallback
- **Sentiment**: Uses Reddit as fallback for Twitter

## Rate Limits & Best Practices

### Current Usage Estimates (per hour)

- **Weather markets**: ~10 requests/market (3 providers)
- **Crypto markets**: ~5 requests/market (CoinGecko + news)
- **Politics markets**: ~8 requests/market (news + social)
- **Sports markets**: ~6 requests/market (ESPN + news)
- **Sentiment**: ~2 requests/market (Reddit/Twitter)

### Optimization Tips

1. **Caching**: Results are cached within 60-second window
2. **Parallel requests**: All providers fetch concurrently
3. **Graceful degradation**: Failed sources don't block analysis
4. **Intelligent fallbacks**: System uses best available data

### Recommended Free Tier Setup

With these free APIs, you can analyze ~50 markets/hour comfortably:

```
✅ Kalshi (unlimited)
✅ Open-Meteo (10,000/day = 416/hour)
✅ CoinGecko (600/hour)
✅ ESPN (unlimited-ish)
✅ Reddit (3,600/hour)
🔑 NewsAPI (100/day = 4/hour) ← Main bottleneck
🔑 Visual Crossing (1,000/day = 41/hour)
🔑 CryptoPanic (50/hour)
```

**Total sustainable rate**: ~50-100 market analyses per hour

## Production Considerations

For higher volumes, consider:

1. **Upgrade API plans**:

   - NewsAPI Pro: $449/mo → 250k requests/day
   - Visual Crossing: $35/mo → 10k requests/day
   - CryptoPanic: $29/mo → unlimited

2. **Add caching layer** (Redis):

   - Cache weather forecasts: 1 hour
   - Cache crypto prices: 5 minutes
   - Cache news sentiment: 30 minutes

3. **Rate limit management**:

   - Implement request queuing
   - Distribute across multiple API keys
   - Use exponential backoff

4. **Alternative providers**:
   - WeatherAPI.com (10k free/day)
   - Polygon.io for crypto (free tier)
   - Finnhub for market news

## Troubleshooting

### "All providers failed" error

**Cause**: No API keys configured or rate limits exceeded

**Solution**:

1. Check `.env.local` file exists and has correct keys
2. Verify keys are valid (test individually)
3. Check console for specific API errors
4. Wait if rate limited (errors show 429 status)

### Markets not loading

**Cause**: Kalshi API issue or network problem

**Solution**:

1. Check Kalshi API status: https://kalshi.com/
2. Verify network connection
3. Check browser console for CORS errors
4. Try clearing browser cache

### Weather forecasts incorrect

**Cause**: Location parsing failed or API returned old data

**Solution**:

1. Check market ticker format in console
2. Verify location coordinates in `weather.ts` LOCATION_COORDS
3. Add new locations as needed

### Sentiment analysis empty

**Cause**: No Twitter key + Reddit fallback failed

**Solution**:

1. Add Twitter API key (most reliable)
2. Check Reddit isn't blocked in your region
3. System will work with partial sentiment data

## API Key Security

**Important**: Never commit API keys to git!

```bash
# .env.local is already in .gitignore
# Always use NEXT_PUBLIC_ prefix for client-side keys
# For sensitive keys, use server-side API routes
```

For production:

- Use environment variables in hosting platform (Vercel, Netlify)
- Rotate keys periodically
- Monitor usage in API dashboards
- Set up usage alerts

## Cost Estimates

### Free Tier (Current Setup)

- **Monthly cost**: $0
- **Capacity**: ~50-100 markets/hour
- **Limitations**: NewsAPI 100/day bottleneck

### Starter Paid ($35/month)

- Visual Crossing: $35/mo (10k/day)
- **Capacity**: ~200-300 markets/hour
- **Recommended for**: Personal projects, demos

### Production ($500/month)

- NewsAPI Pro: $449/mo
- Visual Crossing: $35/mo
- CryptoPanic: $29/mo
- **Capacity**: Thousands of markets/hour
- **Recommended for**: Commercial deployment

---

**Questions?** Check the documentation in each provider's TypeScript file or open an issue.
