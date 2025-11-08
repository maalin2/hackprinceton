# Kalshi AI Trading Dashboard

A modern, minimal trading dashboard for an agentic AI system built for Kalshi prediction markets.

## Tech Stack

- **Framework**: Next.js 14 (App Router) + TypeScript
- **UI**: Tailwind CSS + shadcn/ui components
- **Icons**: lucide-react
- **Animations**: Framer Motion
- **Charts**: Recharts
- **State**: Zustand
- **Fonts**: Inter (text) + JetBrains Mono (numbers)

## Features

- 📊 **Portfolio Performance Chart** - Real-time equity curve with 1D/1W/1M/All range filters
- 📈 **Live Trading Positions** - Sortable, searchable table with detailed position drawer
- 🤖 **Agent Feed** - Streaming recommendations with Accept/Snooze/Dismiss actions
- 🎯 **Markets Browser** - Filterable grid by domain, edge, and spread
- ⚙️ **Settings** - Configurable strategy weights and risk parameters
- 🌓 **Dark Mode** - System-aware theme with persistence
- ♿ **Accessible** - Full keyboard navigation and screen reader support
- 📱 **Responsive** - Mobile-first design that scales to desktop

## Getting Started

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
dashboard/
├── app/                      # Next.js App Router pages
│   ├── dashboard/            # Main dashboard view
│   ├── markets/              # Markets browser
│   ├── settings/             # Configuration
│   ├── layout.tsx            # Root layout with theme provider
│   └── globals.css           # Global styles
├── components/               # React components
│   ├── ui/                   # shadcn/ui primitives
│   ├── PerformanceChart.tsx  # Portfolio equity chart
│   ├── PositionsTable.tsx    # Trading positions table
│   ├── PositionDrawer.tsx    # Detailed position view
│   ├── AgentFeed.tsx         # AI recommendation feed
│   ├── MarketCard.tsx        # Market display card
│   ├── SummaryCards.tsx      # KPI summary cards
│   ├── EdgeBadge.tsx         # Edge indicator badge
│   └── TopNav.tsx            # Navigation header
├── lib/                      # Data hooks & utilities
│   ├── usePortfolio.ts       # Portfolio data hook
│   ├── usePositions.ts       # Positions data hook
│   ├── useMarkets.ts         # Markets data hook
│   ├── useAgentFeed.ts       # Agent recommendations hook
│   ├── types.ts              # TypeScript types
│   └── utils.ts              # Utility functions
└── store/                    # Zustand stores
    └── ui.ts                 # UI state management
```

## Key Components

### Dashboard (`/dashboard`)

- Summary KPI cards (Total Equity, 24h P&L, Win Rate, Open Risk)
- Performance chart with time range selection
- Open positions table with search and sort
- Live agent recommendation feed

### Markets (`/markets`)

- Grid view of active markets
- Filter by domain (Politics, Weather, Crypto, Sports)
- Filter by minimum edge and maximum spread
- Real-time edge calculations

### Settings (`/settings`)

- Strategy weight sliders (Quant vs Sentiment)
- Risk parameters (edge threshold, max spread, position size)
- Theme toggle
- API key configuration (placeholder)

## Mock Data

All data is currently mocked via hooks in `/lib`:

- `usePortfolio.ts` - Generates mock equity curve and KPIs
- `usePositions.ts` - Returns sample open positions
- `useMarkets.ts` - Provides filterable mock markets
- `useAgentFeed.ts` - Simulates streaming recommendations

To connect real data, simply replace the mock implementations with actual API calls. The UI components are data-agnostic and will work seamlessly.

## Customization

### Theme Colors

Edit `app/globals.css` to customize color palette:

- Dark mode is the default
- HSL color variables for easy customization

### Edge Thresholds

Modify `EdgeBadge.tsx` to adjust edge color coding:

- High edge (≥30%): Green
- Medium edge (≥10%): Blue
- Low edge (≥0%): Outline
- Negative edge: Red

### Agent Feed Interval

Adjust recommendation frequency in `lib/useAgentFeed.ts`:

```typescript
// New recommendation every 8-15 seconds
const interval = Math.random() * 7000 + 8000;
```

## Keyboard Shortcuts

- `Tab` - Navigate between controls
- `Escape` - Close drawers and dialogs
- `Enter` - Activate buttons and links

## Accessibility

- ARIA labels on all interactive elements
- Focus rings on keyboard navigation
- Screen reader optimized
- Color contrast meets WCAG AA standards

## Future Enhancements

- [ ] WebSocket connection for live market data
- [ ] Order execution interface
- [ ] Position history and trade analytics
- [ ] Real-time P&L tracking
- [ ] Portfolio risk metrics
- [ ] Alert notifications
- [ ] Export to CSV

## License

MIT
