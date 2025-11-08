# Quick Start Guide

Get the Kalshi AI Trading Dashboard running in 3 minutes.

## Prerequisites

- Node.js 18+ installed
- npm or yarn

## Step-by-Step

### 1. Navigate to the dashboard directory

```bash
cd dashboard
```

### 2. Install dependencies

```bash
npm install
```

This will install all required packages including:

- Next.js, React, TypeScript
- Tailwind CSS, shadcn/ui components
- Framer Motion, Recharts
- Zustand, next-themes

### 3. Start the development server

```bash
npm run dev
```

### 4. Open your browser

Navigate to [http://localhost:3000](http://localhost:3000)

You'll be automatically redirected to `/dashboard`.

## What You'll See

### Dashboard Page (Default)

- **Top**: 4 KPI summary cards (Total Equity, 24h P&L, Win Rate, Open Risk)
- **Center**: Interactive portfolio performance chart with range filters (1D/1W/1M/All)
- **Bottom**: Positions table with 5 mock open positions
- **Right Sidebar**: Live agent feed with streaming recommendations

Click on any position row to open a detailed drawer with fills, rationale, and timestamps.

### Markets Page

Click "Markets" in the top nav to browse:

- Grid of 8 mock markets across 4 domains
- Filter by domain chips (All/Politics/Weather/Crypto/Sports)
- Advanced filters for minimum edge and maximum spread
- Each card shows pricing, probabilities, edge badge

### Settings Page

Configure your trading parameters:

- **Strategy Weights**: Quant vs Sentiment sliders
- **Risk Parameters**: Edge threshold, max spread, position size
- **Appearance**: Dark/light theme toggle
- **API Config**: Placeholder for Kalshi API keys

## Features to Try

### Agent Feed Interactions

1. Wait for recommendations to stream in (every 8-15 seconds)
2. Click **Accept** → See toast notification
3. Click **Snooze** → Recommendation disappears and returns in 10s
4. Click **Dismiss** → Permanently remove

### Chart Range Filters

Click the range buttons (1D/1W/1M/All) above the performance chart to see animated transitions.

### Position Details

Click any row in the positions table to slide open a detailed drawer showing:

- Market info, pricing, P&L
- Entry rationale from the AI
- Fill history with timestamps
- Position metadata

### Market Filtering

1. Go to Markets page
2. Click domain chips to filter by category
3. Click "Filters" to show advanced options
4. Adjust edge/spread sliders to refine results

### Theme Toggle

Click the sun/moon icon in the top-right nav to toggle between light and dark modes. Theme preference is saved to localStorage.

### Settings Adjustments

1. Go to Settings
2. Adjust any slider or input
3. Click "Save Settings" to see toast confirmation
4. Changes are persisted via Zustand

## Mock Data

All data is simulated:

- **Portfolio**: Equity curve generated with random walk
- **Positions**: 5 realistic open positions with actual Kalshi tickers from your weather test
- **Markets**: 8 markets with realistic spreads and edges
- **Agent Feed**: New recommendations every 8-15 seconds

## Next Steps

### Connect Real Data

Replace mock hooks in `/lib` with actual Kalshi API calls:

```typescript
// Example: lib/usePortfolio.ts
export function usePortfolio() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("https://api.kalshi.com/...")
      .then((res) => res.json())
      .then(setData);
  }, []);

  return { data, loading: false };
}
```

UI components are data-agnostic and will work seamlessly with real data.

### Build for Production

```bash
npm run build
npm start
```

Optimized production build with:

- Static generation
- Code splitting
- Image optimization
- Font optimization

## Troubleshooting

### Port 3000 already in use

```bash
# Use a different port
PORT=3001 npm run dev
```

### Dependencies won't install

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Type errors

```bash
# Rebuild TypeScript
npm run build
```

## Tech Stack Quick Reference

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Accessible component primitives
- **Framer Motion**: Smooth animations
- **Recharts**: Portfolio chart
- **Zustand**: Lightweight state management
- **next-themes**: Theme persistence

## File Structure

```
dashboard/
├── app/              # Pages (dashboard, markets, settings)
├── components/       # React components + UI primitives
├── lib/              # Data hooks + utilities
├── store/            # Zustand stores
└── package.json      # Dependencies
```

## Support

For questions or issues:

1. Check the main README.md
2. Review component source code (all documented)
3. Inspect browser console for errors

Enjoy building with the Kalshi AI Trading Dashboard! 🚀
