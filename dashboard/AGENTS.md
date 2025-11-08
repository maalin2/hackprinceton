# Multi-Agent Workflow System

Production-grade multi-agent decision system for Kalshi prediction markets.

## Architecture

```
┌─────────────┐
│   Market    │
└──────┬──────┘
       │
   ┌───▼────┐     ┌──────────────┐
   │ Quant  ├────►│              │
   │ Agent  │     │   Decision   │     ┌──────────────┐
   └────────┘     │    Engine    ├────►│ Recommendation│
                  │              │     └──────────────┘
   ┌────────┐     │  (Combines   │
   │Sentiment├────►│   signals)   │
   │ Agent  │     │              │
   └────────┘     └──────────────┘
```

## Components

### 1. Quant Agent (`lib/agents/quant/`)

Fetches ≥3 credible sources per category and computes `P_quant`.

#### Providers by Category:

**Weather** (`providers/weather.ts`):

- NOAA (GFS model)
- Open-Meteo (ECMWF model)
- Meteostat (climatology)

**Politics** (`providers/politics.ts`):

- Polling Aggregate (538-style)
- News Headlines sentiment
- Social Mention momentum

**Crypto** (`providers/crypto.ts`):

- Price Momentum (RSI, MACD, Volume)
- On-Chain Metrics (whale activity, exchange flows)
- Crypto News sentiment

**Sports** (`providers/sports.ts`):

- Injury Reports
- Team Form (ELO ratings)
- Sports News sentiment

#### Output: `QuantSignal`

```typescript
{
  pQuant: number,          // 0-1 probability
  confidence: number,      // 0-1 confidence
  sources: SourceComponent[], // Per-source breakdown
  timestamp: Date
}
```

#### Combining Sources

- Weighted average by confidence
- Harmonic mean for overall confidence
- Penalty if < 3 sources
- Caps extremes (0.01 - 0.99)

### 2. Sentiment Agent (`lib/agents/sentiment/`)

Gathers Kalshi comments + Twitter posts and computes `P_sentiment`.

#### Data Sources:

**Kalshi Comments** (`sentiment/kalshi.ts`):

- Fetches discussion threads for series/market
- Returns 5-12 recent comments

**Twitter/X** (`sentiment/twitter.ts`):

- Searches recent posts for market topic
- Returns 8-15 tweets
- Supports snscrape for keyless mode

#### Sentiment Analysis (`sentiment/vader.ts`):

- Simplified VADER implementation
- Compound score: -1 (negative) to +1 (positive)
- Handles intensifiers ("very", "extremely")
- Handles negations ("not", "never")
- Domain-specific terms (bullish/bearish, win/lose)

#### Probability Conversion:

```
P_sentiment = 0.5 + 0.3 * compound_score
```

Maps compound [-1, 1] → probability [0.2, 0.8]

#### Output: `SentimentSignal`

```typescript
{
  pSent: number,           // 0-1 probability
  confidence: number,      // Based on sample size & agreement
  nSamples: number,        // Total texts analyzed
  sources: {
    kalshi: number,        // Kalshi comment count
    twitter: number        // Twitter post count
  },
  timestamp: Date
}
```

#### Confidence Calculation:

- Sample size factor (more samples = higher confidence)
- Agreement factor (lower variance = higher confidence)
- Caps: 0.3 - 0.85

### 3. Decision Engine (`lib/agents/decision/`)

Combines signals and generates trading decisions.

#### Algorithm:

1. **Compute Market Probability**:

   ```
   P_market = (yesBid + yesAsk) / 200
   ```

   Fallback to `lastPrice / 100` if no quotes.

2. **Adjust Weights** (if sentiment samples < 20):

   ```
   penalty = nSamples / 20
   ws_adjusted = ws * penalty
   wq_adjusted = 1 - ws_adjusted
   ```

3. **Combine Signals**:

   ```
   P_combined = wq * P_quant + ws * P_sent
   ```

   Default weights: `wq=0.8`, `ws=0.2`

4. **Compute Edge**:

   ```
   edge = P_combined - P_market
   ```

5. **Determine Action**:

   - If `edge >= threshold` → **BUY YES**
   - If `edge <= -threshold` → **BUY NO**
   - Else → **HOLD**

   Default threshold: ±8%

6. **Compute Confidence**:

   ```
   confidence = 0.6 * (0.5 + |edge|) + 0.4 * avg_signal_confidence
   ```

7. **Generate Rationale**:
   - Action summary with edge magnitude
   - Top quant source with probability
   - Sentiment breakdown (samples, sources)
   - Market vs model comparison

#### Output: `Decision`

```typescript
{
  action: "BUY_YES" | "BUY_NO" | "HOLD",
  pMarket: number,
  pQuant: number,
  pSent: number,
  pCombined: number,
  edge: number,
  confidence: number,
  rationale: string,
  sources: string[],
  timestamp: Date
}
```

## Usage

### Hook: `useRecommendations()`

Coordinates all agents and generates recommendations.

```typescript
const {
  recommendations, // Array of RecommendationWithMarket
  loading, // Initial load state
  processing, // Analysis in progress
  acceptRecommendation,
  snoozeRecommendation,
  dismissRecommendation,
  refresh, // Manual re-analysis
} = useRecommendations();
```

#### Auto-Refresh

- Analyzes markets every 60 seconds
- Runs agents in parallel for speed
- Filters out HOLD actions
- Only shows actionable recommendations

### UI Component: `DetailedRecommendationCard`

Displays full agent analysis:

- Market info + domain badge
- Decision action (BUY YES/NO)
- Edge + confidence badges
- Probability grid (Market, Combined, Quant, Sentiment)
- Source chips (NOAA, Polls, Twitter, etc.)
- Full rationale text
- Action buttons (Accept, Snooze, Dismiss)

### Settings Integration

Decision engine automatically syncs with `/settings`:

- **Quant Weight** (default: 80%)
- **Sentiment Weight** (default: 20%)
- **Min Edge Threshold** (default: 8%)

Changes update immediately on next analysis cycle.

## Mock Mode

All providers use mock data by default for demo purposes.

### Enable Mock Mode:

```typescript
// In provider files:
const USE_MOCK = process.env.NEXT_PUBLIC_MOCK_QUANT !== "false";
const USE_MOCK = process.env.NEXT_PUBLIC_MOCK_SENTIMENT !== "false";
```

### Disable for Production:

Create `.env.local`:

```bash
NEXT_PUBLIC_MOCK_QUANT=false
NEXT_PUBLIC_MOCK_SENTIMENT=false
```

Then implement real API calls in providers.

## Testing

### Run Tests:

```bash
npm test
```

### Test Coverage:

**Decision Engine** (`__tests__/decision.test.ts`):

- ✅ Market probability computation
- ✅ Signal combination (weighted)
- ✅ Sentiment downweighting (low samples)
- ✅ Edge calculation & thresholds
- ✅ Action determination (BUY_YES/BUY_NO/HOLD)
- ✅ Confidence calculation
- ✅ Rationale generation
- ✅ Source collection
- ✅ Dynamic weight updates

**Sentiment Analysis** (`__tests__/vader.test.ts`):

- ✅ Positive/negative/neutral detection
- ✅ Intensifiers & negations
- ✅ Domain-specific terms (bullish/bearish)
- ✅ Compound score normalization
- ✅ Probability conversion
- ✅ End-to-end text → probability

## Performance

### Parallel Execution:

- Quant sources fetched in parallel (3+ concurrent requests)
- Sentiment sources fetched in parallel (Kalshi + Twitter)
- All markets analyzed concurrently
- Typical analysis time: **2-3 seconds** per market (mock mode)

### Optimization:

- Results cached within 60-second window
- Failed sources don't block analysis
- Automatic retry with exponential backoff (production)

## Example Recommendation

```json
{
  "market": {
    "ticker": "KXHIGHPHIL-25NOV08-T71",
    "title": "Will Philadelphia hit >71°F on Nov 8?",
    "domain": "Weather"
  },
  "decision": {
    "action": "BUY_YES",
    "pMarket": 0.02,
    "pQuant": 0.631,
    "pSent": 0.55,
    "pCombined": 0.615,
    "edge": 0.595,
    "confidence": 0.89,
    "rationale": "Strong YES signal with 59.5% edge. Quant model (63.1%) led by NOAA at 63.0%. Sentiment (55.0%) from 12 samples across Kalshi (7) + Twitter (5). Market pricing: 2.0%. Combined model: 61.5%.",
    "sources": ["NOAA", "Open-Meteo", "Meteostat", "Kalshi Comments", "Twitter"]
  }
}
```

## Future Enhancements

- [ ] Real-time WebSocket for live updates
- [ ] Backtesting framework with historical data
- [ ] Machine learning model calibration
- [ ] Portfolio optimization (Kelly Criterion)
- [ ] Risk management (position sizing, diversification)
- [ ] Performance tracking (Sharpe, Sortino, win rate)
- [ ] Alert system for high-confidence signals
- [ ] Integration with actual Kalshi trading API

## Architecture Benefits

1. **Modular**: Each agent is independent and testable
2. **Extensible**: Easy to add new providers or categories
3. **Transparent**: Full breakdown of decision rationale
4. **Configurable**: Weights and thresholds adjustable via UI
5. **Robust**: Graceful degradation when sources fail
6. **Fast**: Parallel execution for sub-3s analysis
7. **Testable**: Comprehensive unit tests for core logic

---

Built with ❤️ for HackPrinceton
