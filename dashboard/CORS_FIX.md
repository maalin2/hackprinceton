# CORS Fix: Server-Side API Routes

## Problem

Browser-based API calls to Reddit and other services were blocked by CORS (Cross-Origin Resource Sharing) policies. You'd see errors like:

```
Access to fetch at 'https://www.reddit.com/r/cryptocurrency/search.json'
from origin 'http://localhost:3000' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present
```

## Solution

Created **Next.js API routes** that act as server-side proxies. These routes:

- Run on the server (no CORS restrictions)
- Make requests to external APIs
- Return data to the client

### Architecture

```
Browser → Next.js API Route → External API (Reddit, etc.)
         (localhost:3000/api/*)    (reddit.com, etc.)

✅ No CORS issues
✅ Can add authentication
✅ Can cache responses
✅ Can transform data
```

## Implementation

### 1. Created API Route: `/app/api/reddit/route.ts`

```typescript
export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.get("q");
  const subreddit = request.nextUrl.searchParams.get("subreddit");

  // Server-side fetch (no CORS issues)
  const response = await fetch(
    `https://www.reddit.com/r/${subreddit}/search.json?q=${query}...`,
    { headers: { "User-Agent": "KalshiDashboard/1.0" } }
  );

  return NextResponse.json(data);
}
```

### 2. Updated Client Code

**Before (❌ CORS errors):**

```typescript
const response = await fetch(
  "https://www.reddit.com/r/cryptocurrency/search.json?q=..."
);
```

**After (✅ Works):**

```typescript
const response = await fetch("/api/reddit?subreddit=cryptocurrency&q=...");
```

## Files Changed

1. **`app/api/reddit/route.ts`** (new)

   - Server-side Reddit API proxy
   - Handles search requests
   - Returns clean JSON data

2. **`lib/agents/sentiment/twitter.ts`**

   - Removed Nitter scraper (CORS issues)
   - Now uses Reddit API route as fallback
   - Twitter API → Reddit (both CORS-free)

3. **`lib/agents/quant/providers/politics.ts`**
   - Updated `fetchSocialMentions()` to use API route
   - No more direct Reddit calls

## Benefits

### ✅ Fixed Issues

- No more CORS errors
- Reddit data works reliably
- Twitter fallback (Reddit) works

### 🚀 New Capabilities

- Can add rate limiting
- Can cache Reddit responses
- Can add authentication headers
- Can transform/filter data server-side

### 🔒 Security

- API keys stay on server (not exposed to browser)
- Can validate requests before forwarding
- Can sanitize responses

## Usage

### Client-Side (in agents)

```typescript
// Search Reddit via our API
const response = await fetch(
  `/api/reddit?subreddit=${subreddit}&q=${encodeURIComponent(query)}&limit=20`
);

const data = await response.json();
const posts = data.posts; // Clean, transformed data
```

### Available Parameters

| Parameter   | Required | Default | Description         |
| ----------- | -------- | ------- | ------------------- |
| `q`         | ✅ Yes   | -       | Search query        |
| `subreddit` | No       | `all`   | Subreddit to search |
| `limit`     | No       | `20`    | Max results (1-100) |

### Response Format

```json
{
  "posts": [
    {
      "id": "abc123",
      "title": "Post title",
      "text": "Post body (if any)",
      "author": "username",
      "score": 42,
      "numComments": 15,
      "upvoteRatio": 0.87,
      "created": 1699564800,
      "permalink": "/r/cryptocurrency/comments/..."
    }
  ]
}
```

## Testing

### 1. Test the API Route Directly

```bash
# Start the dev server
cd dashboard
npm run dev

# In another terminal, test the endpoint
curl "http://localhost:3000/api/reddit?subreddit=cryptocurrency&q=bitcoin&limit=5"
```

Expected: JSON response with Reddit posts

### 2. Test in Browser

1. Open DevTools Console (F12)
2. Run:

```javascript
fetch("/api/reddit?subreddit=cryptocurrency&q=bitcoin&limit=5")
  .then((r) => r.json())
  .then((d) => console.log(d.posts));
```

Expected: Array of Reddit posts logged to console

### 3. Test Through Agents

1. Go to `/dashboard`
2. Wait for recommendations to load
3. Check console for:

```
📝 Kalshi Comments (1): ...
🐦 Twitter Posts (12): ...  ← Should show Reddit posts as fallback
```

## Future API Routes

Can add more routes for other CORS-blocked services:

### Potential Routes

```
/api/news          → NewsAPI proxy
/api/weather       → Weather API aggregator
/api/crypto        → CoinGecko/CryptoPanic proxy
/api/twitter       → Twitter API proxy
/api/kalshi        → Kalshi API proxy with caching
```

### Benefits

1. **Caching**: Cache responses server-side
2. **Rate Limiting**: Implement request throttling
3. **Authentication**: Hide API keys from client
4. **Aggregation**: Combine multiple APIs in one request
5. **Transformation**: Clean/filter data before sending to client

## Performance Considerations

### Current Setup

- Each request goes: Client → Next.js API → Reddit → Next.js API → Client
- Adds ~50-100ms latency vs direct call
- But necessary to avoid CORS

### Optimization Options

1. **Edge Functions**: Deploy API routes to edge (Vercel Edge)

   - Lower latency (geographically distributed)
   - Faster cold starts

2. **Caching**: Add Redis/KV cache

   ```typescript
   // Cache Reddit results for 5 minutes
   const cached = await redis.get(`reddit:${subreddit}:${query}`);
   if (cached) return NextResponse.json(cached);
   ```

3. **Response Streaming**: Stream large responses
   ```typescript
   return new Response(stream, {
     headers: { "Content-Type": "text/event-stream" },
   });
   ```

## Troubleshooting

### API route returns 500 error

**Cause**: Reddit API failed or rate limited

**Solution**:

1. Check server logs (terminal running `npm run dev`)
2. Test Reddit API directly in browser
3. Wait if rate limited (Reddit: 60 requests/minute)

### Still seeing CORS errors

**Cause**: Client code still calling external API directly

**Solution**:

1. Search codebase for direct Reddit URLs:
   ```bash
   grep -r "reddit.com" lib/
   ```
2. Replace with `/api/reddit` calls

### Empty results from API

**Cause**: Search query too specific or no matches

**Solution**:

1. Check query parameters
2. Try broader search terms
3. Test query on reddit.com directly

## Development vs Production

### Development (Current)

```
localhost:3000 → localhost:3000/api/reddit → reddit.com
```

### Production (Vercel)

```
yourdomain.com → yourdomain.com/api/reddit → reddit.com
                 ↑ Edge function (fast!)
```

Same code, better performance in production!

## Migration Checklist

- [x] Created `/app/api/reddit/route.ts`
- [x] Updated `lib/agents/sentiment/twitter.ts`
- [x] Updated `lib/agents/quant/providers/politics.ts`
- [x] Removed Nitter scraper (unreliable + CORS issues)
- [x] Tested API route works
- [x] Verified no CORS errors in console

## Result

✅ **No more CORS errors!**
✅ **Reddit sentiment data works**
✅ **Twitter fallback (Reddit) works**
✅ **Ready to add more API routes as needed**

---

**You now have a production-ready API proxy system!** 🎉
