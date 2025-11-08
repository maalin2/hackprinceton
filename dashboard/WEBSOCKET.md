# WebSocket Configuration Guide

The Agent Feed now uses WebSocket for real-time updates instead of polling/intervals.

## Current Mode: Mock WebSocket

By default, the app runs in **mock mode** to simulate WebSocket behavior for demo purposes.

### How to Switch to Real WebSocket

1. **Open** `lib/useAgentFeed.ts`
2. **Find** line 68:
   ```typescript
   const MOCK_WS_MODE = true; // Set to false when using real WebSocket
   ```
3. **Change** to:

   ```typescript
   const MOCK_WS_MODE = false;
   ```

4. **Set WebSocket URL** (optional):

   - Create `.env.local` in the dashboard root
   - Add: `NEXT_PUBLIC_WS_URL=wss://your-websocket-server.com/agent-feed`
   - Default: `ws://localhost:8080/agent-feed`

5. **Restart** dev server:
   ```bash
   npm run dev
   ```

## WebSocket Message Format

The real WebSocket server should send messages in this JSON format:

```json
{
  "type": "recommendation",
  "id": "rec-123-1699999999999",
  "timestamp": "2025-11-08T10:30:00.000Z",
  "domain": "Weather",
  "ticker": "KXHIGHPHIL-25NOV08-T71",
  "market": "Will Philadelphia hit >71°F on Nov 8?",
  "action": "BUY_YES",
  "edge": 0.611,
  "confidence": 0.85,
  "rationale": "NOAA forecast divergence from market price. High edge opportunity.",
  "priority": "high"
}
```

### Message Fields

- `type`: Always "recommendation"
- `id`: Unique identifier (string)
- `timestamp`: ISO 8601 datetime string
- `domain`: "Politics" | "Weather" | "Crypto" | "Sports"
- `ticker`: Market ticker (string)
- `market`: Human-readable market description
- `action`: "BUY_YES" | "BUY_NO" | "SELL_YES" | "SELL_NO" | "HOLD"
- `edge`: Number between 0 and 1 (0.611 = 61.1% edge)
- `confidence`: Number between 0 and 1 (0.85 = 85% confidence)
- `rationale`: AI explanation string
- `priority`: "high" | "medium" | "low"

## Features

### ✅ Auto-Reconnection

If the WebSocket connection drops, it will automatically attempt to reconnect every 5 seconds.

### ✅ Connection Status Indicator

A small green/gray dot appears next to "Agent Recommendations" title:

- 🟢 Green = Connected
- ⚪ Gray = Disconnected

### ✅ Console Logging

All WebSocket events are logged to the browser console:

- `📡 Agent Feed: Connecting to WebSocket...`
- `✅ Agent Feed: WebSocket connected`
- `📨 Agent Feed: Message received`
- `❌ Agent Feed: WebSocket error`

### ✅ Automatic Cleanup

WebSocket connections are properly closed when:

- Component unmounts
- Page navigation
- Browser tab closes

## Example: Python WebSocket Server

Here's a simple example WebSocket server using Python:

```python
import asyncio
import json
import websockets
import random
from datetime import datetime

async def agent_feed(websocket):
    print(f"Client connected: {websocket.remote_address}")

    try:
        while True:
            # Generate recommendation
            recommendation = {
                "type": "recommendation",
                "id": f"rec-{random.randint(1000, 9999)}-{int(datetime.now().timestamp() * 1000)}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "domain": random.choice(["Politics", "Weather", "Crypto", "Sports"]),
                "ticker": "KXHIGHPHIL-25NOV08-T71",
                "market": "Will Philadelphia hit >71°F on Nov 8?",
                "action": random.choice(["BUY_YES", "BUY_NO", "SELL_YES", "SELL_NO", "HOLD"]),
                "edge": round(random.uniform(0.05, 0.65), 3),
                "confidence": round(random.uniform(0.65, 0.95), 2),
                "rationale": "NOAA forecast divergence detected. High edge opportunity.",
                "priority": random.choice(["high", "medium", "low"])
            }

            # Send to client
            await websocket.send(json.dumps(recommendation))
            print(f"Sent recommendation: {recommendation['ticker']}")

            # Wait 10-15 seconds before next recommendation
            await asyncio.sleep(random.uniform(10, 15))

    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    async with websockets.serve(agent_feed, "localhost", 8080):
        print("WebSocket server running on ws://localhost:8080")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
```

### To run:

```bash
pip install websockets
python websocket_server.py
```

Then set `MOCK_WS_MODE = false` in `useAgentFeed.ts`.

## Example: Node.js WebSocket Server

Using the `ws` library:

```javascript
const WebSocket = require("ws");

const wss = new WebSocket.Server({ port: 8080 });

wss.on("connection", (ws) => {
  console.log("Client connected");

  const sendRecommendation = () => {
    const recommendation = {
      type: "recommendation",
      id: `rec-${Math.random().toString(36).substr(2, 9)}-${Date.now()}`,
      timestamp: new Date().toISOString(),
      domain: ["Politics", "Weather", "Crypto", "Sports"][
        Math.floor(Math.random() * 4)
      ],
      ticker: "KXHIGHPHIL-25NOV08-T71",
      market: "Will Philadelphia hit >71°F on Nov 8?",
      action: ["BUY_YES", "BUY_NO", "SELL_YES", "SELL_NO", "HOLD"][
        Math.floor(Math.random() * 5)
      ],
      edge: Math.random() * 0.6 + 0.05,
      confidence: Math.random() * 0.3 + 0.65,
      rationale: "NOAA forecast divergence detected.",
      priority: ["high", "medium", "low"][Math.floor(Math.random() * 3)],
    };

    ws.send(JSON.stringify(recommendation));
    console.log("Sent recommendation:", recommendation.ticker);
  };

  // Send recommendation every 10-15 seconds
  const interval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      sendRecommendation();
    }
  }, Math.random() * 5000 + 10000);

  ws.on("close", () => {
    console.log("Client disconnected");
    clearInterval(interval);
  });
});

console.log("WebSocket server running on ws://localhost:8080");
```

### To run:

```bash
npm install ws
node websocket_server.js
```

## Connecting to Real Kalshi API

When Kalshi provides a WebSocket endpoint, simply:

1. Set `MOCK_WS_MODE = false`
2. Set `NEXT_PUBLIC_WS_URL=wss://api.kalshi.com/trade-api/ws/...`
3. Add authentication if needed (modify `ws.onopen` to send auth token)

Example with authentication:

```typescript
ws.onopen = () => {
  console.log("✅ WebSocket connected");
  setWsConnected(true);

  // Send authentication
  ws.send(
    JSON.stringify({
      type: "auth",
      token: "your-api-key",
    })
  );
};
```

## Troubleshooting

### Connection Refused

- Ensure WebSocket server is running on specified port
- Check firewall settings
- Verify URL format (ws:// for local, wss:// for production)

### No Recommendations Appearing

- Check browser console for error messages
- Verify message format matches expected schema
- Ensure `type: "recommendation"` is included in messages

### Frequent Disconnections

- Check network stability
- Verify server isn't timing out idle connections
- Consider implementing ping/pong heartbeat

## Current Status

🔴 **Mock Mode Active** - Using simulated WebSocket with intervals  
🟢 **Ready for Production** - Switch `MOCK_WS_MODE = false` to enable real WebSocket

The UI is fully functional in both modes!
