export interface Comment {
  id: string;
  text: string;
  timestamp: Date;
  author: string;
  url: string;
}

/**
 * Fetch Kalshi discussion comments for a market/series
 */
export async function fetchKalshiComments(series: string): Promise<Comment[]> {
  try {
    // Kalshi API doesn't have a public comments/discussion endpoint yet
    // For now, we'll need to scrape the website or wait for API support
    
    // Temporary: Try to fetch from Kalshi's GraphQL endpoint (if available)
    const response = await fetch(`https://kalshi.com/api/markets/${series}/comments`, {
      headers: {
        'User-Agent': 'KalshiDecisionDashboard/1.0',
      },
    });

    if (!response.ok) {
      console.warn(`Kalshi comments not available for ${series}: ${response.status}`);
      return [];
    }

    const data = await response.json();
    const comments: Comment[] = [];

    // Parse response (format may vary)
    if (Array.isArray(data)) {
      data.forEach((comment: any) => {
        comments.push({
          id: comment.id || `comment-${Date.now()}`,
          text: comment.text || comment.content || comment.message || "",
          timestamp: comment.timestamp ? new Date(comment.timestamp) : new Date(),
          author: comment.author || comment.username || "Anonymous",
          url: `https://kalshi.com/markets/${series}/comments/${comment.id}`,
        });
      });
    }

    return comments.slice(0, 20); // Limit to 20 most recent
  } catch (error) {
    console.error(`Failed to fetch Kalshi comments for ${series}:`, error);
    
    // Fallback: Try to get general market sentiment from market description
    // This is a workaround until Kalshi provides a proper comments API
    try {
      const marketResponse = await fetch(
        `https://api.elections.kalshi.com/trade-api/v2/markets/${series}`,
        { timeout: 5000 } as any
      );

      if (marketResponse.ok) {
        const marketData = await marketResponse.json();
        const market = marketData.market;

        if (market) {
          // Generate a synthetic comment from market data
          const syntheticComment: Comment = {
            id: `synthetic-${Date.now()}`,
            text: `Market currently at ${market.yes_bid || market.last_price || 50}¢. ` +
                  `Volume: ${market.volume || 0} contracts. ` +
                  `This market ${market.yes_bid > 60 ? 'looks bullish' : market.yes_bid < 40 ? 'looks bearish' : 'seems balanced'}.`,
            timestamp: new Date(),
            author: "Market Data",
            url: `https://kalshi.com/markets/${series}`,
          };

          return [syntheticComment];
        }
      }
    } catch (fallbackError) {
      console.error("Fallback market data fetch failed:", fallbackError);
    }

    return []; // Return empty if all attempts fail
  }
}
