# Kalshi Market Links

All markets now include direct links to their Kalshi pages for verification.

## Implementation

### 1. **URL Generation**

Every market automatically gets a Kalshi URL:

```typescript
// Format: https://kalshi.com/markets/{ticker}
const marketUrl = `https://kalshi.com/markets/${ticker}`;
```

**Example:**

- Ticker: `KXHIGHPHIL-25NOV08-T71`
- URL: `https://kalshi.com/markets/KXHIGHPHIL-25NOV08-T71`

### 2. **Data Structure Updates**

#### Market Interface

```typescript
export interface Market {
  // ... other fields
  url: string; // Link to Kalshi market page
  lastPrice?: number; // Last trade price (optional)
}
```

#### MarketLite Interface

```typescript
export interface MarketLite {
  // ... other fields
  url: string; // Link to Kalshi market page
  lastPrice: number;
}
```

### 3. **UI Components**

#### MarketCard (`/markets` page)

- **Entire card is clickable** → Opens Kalshi market in new tab
- Shows "View on Kalshi →" link below ticker
- External link icon next to title

#### DetailedRecommendationCard (`/dashboard` page)

- **"View on Kalshi" link** below ticker
- Opens in new tab with `target="_blank"`
- Prevents event propagation (doesn't trigger card click)

### 4. **Real Markets Integration**

The `useRecommendations` hook now:

- ✅ Uses **real markets** from `useMarkets` (not mock data)
- ✅ Fetches up to 50 markets from Kalshi API
- ✅ Converts to `MarketLite` with URLs included
- ✅ Analyzes top 20 markets for recommendations

## Usage

### View Market on Kalshi

1. **From Markets Page** (`/markets`):

   - Click anywhere on the market card
   - Opens Kalshi market page in new tab

2. **From Dashboard** (`/dashboard`):
   - Click "View on Kalshi" link in recommendation card
   - Opens Kalshi market page in new tab

### Verify Market Data

1. Click the link to open Kalshi
2. Compare:
   - ✅ Market title matches
   - ✅ Ticker matches
   - ✅ Prices are within a few cents (due to timing)
   - ✅ Domain/category matches

## URL Format

```
https://kalshi.com/markets/{TICKER}
```

**Examples:**

- `https://kalshi.com/markets/KXHIGHPHIL-25NOV08-T71`
- `https://kalshi.com/markets/KXBTCD-25NOV1417-T99749`
- `https://kalshi.com/markets/KX2028DRUN-28-JOSS`

## Files Changed

1. **`lib/types.ts`**

   - Added `url: string` to `Market` interface
   - Added `url: string` to `MarketLite` interface
   - Added `lastPrice?: number` to `Market` interface

2. **`lib/useMarkets.ts`**

   - Generates Kalshi URL for each market: `https://kalshi.com/markets/${ticker}`
   - Includes URL in returned Market objects

3. **`lib/useRecommendations.ts`**

   - Now uses **real markets** from `useMarkets` hook
   - Converts Market → MarketLite with URLs
   - Analyzes real Kalshi markets (not mock data)

4. **`components/MarketCard.tsx`**

   - Wrapped entire card in Next.js `Link` component
   - Shows "View on Kalshi →" text
   - External link icon next to title
   - Opens in new tab

5. **`components/DetailedRecommendationCard.tsx`**
   - Added "View on Kalshi" link below ticker
   - External link icon
   - Opens in new tab with proper event handling

## Benefits

### ✅ Verification

- Users can verify markets are real
- Compare prices/data with Kalshi
- Build trust in the system

### ✅ Transparency

- Full transparency into data sources
- Direct links to source markets
- Easy fact-checking

### ✅ User Experience

- Quick access to trade on Kalshi
- No need to manually search for markets
- One-click verification

## Testing

### Test Market Links

1. **Go to `/markets` page**
2. **Click any market card**
3. **Verify:**
   - Opens Kalshi in new tab
   - URL matches ticker
   - Market data matches dashboard

### Test Recommendation Links

1. **Go to `/dashboard` page**
2. **Wait for recommendations to load**
3. **Click "View on Kalshi" link**
4. **Verify:**
   - Opens Kalshi in new tab
   - Market exists on Kalshi
   - Prices are similar (within timing window)

## Future Enhancements

### Potential Additions

1. **Series Links**

   - Link to series page: `https://kalshi.com/series/{series}`
   - Show all markets in a series

2. **Category Links**

   - Link to category page: `https://kalshi.com/category/{category}`
   - Browse similar markets

3. **Trading Links**

   - Deep links to trade directly
   - Pre-filled order forms
   - Requires Kalshi API integration

4. **Share Links**
   - Copy market link to clipboard
   - Share recommendations via link
   - Social media integration

## Error Handling

If a market URL fails:

- Link still works (Kalshi will show 404 if market doesn't exist)
- User can verify market doesn't exist (helps debug)
- System continues to work normally

## Security

- ✅ Links open in new tab (`target="_blank"`)
- ✅ `rel="noopener noreferrer"` prevents security issues
- ✅ No user data sent to Kalshi
- ✅ Read-only links (no trading actions)

---

**All markets now have verifiable links to Kalshi!** 🎉

Users can click any market or recommendation to see the real market on Kalshi's website.
