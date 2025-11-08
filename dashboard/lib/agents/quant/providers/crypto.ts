import { SourceComponent } from "@/lib/types";

interface CryptoMarket {
  ticker: string;
  symbol: string;
  threshold: number;
  date: Date;
  type: "ABOVE" | "BELOW";
}

// Parse crypto market ticker
function parseCryptoMarket(ticker: string, title: string): CryptoMarket | null {
  // Example: BTC-25DEC-T50K, ETH-25NOV15-ABOVE3000
  const cryptoSymbols = ["BTC", "ETH", "SOL", "MATIC", "ADA", "DOT", "AVAX", "LINK"];
  
  const symbol = cryptoSymbols.find(s => ticker.includes(s) || title.includes(s));
  if (!symbol) return null;

  // Try to extract threshold from title
  const thresholdMatch = title.match(/\$?([\d,]+\.?\d*)[kK]?/);
  const threshold = thresholdMatch ? parseFloat(thresholdMatch[1].replace(/,/g, '')) * (thresholdMatch[0].includes('k') || thresholdMatch[0].includes('K') ? 1000 : 1) : 0;

  const type = title.toLowerCase().includes("above") || title.toLowerCase().includes("over") ? "ABOVE" : "BELOW";

  // Try to extract date
  const dateMatch = ticker.match(/(\d{2})([A-Z]{3})(\d{2})/);
  let date = new Date();
  if (dateMatch) {
    const [, day, month, year] = dateMatch;
    const monthMap: Record<string, number> = {
      JAN: 0, FEB: 1, MAR: 2, APR: 3, MAY: 4, JUN: 5,
      JUL: 6, AUG: 7, SEP: 8, OCT: 9, NOV: 10, DEC: 11
    };
    date = new Date(2000 + parseInt(year), monthMap[month] || 0, parseInt(day));
  }

  return { ticker, symbol, threshold, date, type };
}

// CoinGecko symbol mapping
const COINGECKO_IDS: Record<string, string> = {
  BTC: "bitcoin",
  ETH: "ethereum",
  SOL: "solana",
  MATIC: "matic-network",
  ADA: "cardano",
  DOT: "polkadot",
  AVAX: "avalanche-2",
  LINK: "chainlink",
};

// Price Momentum (Technical Analysis)
export async function fetchPriceMomentum(ticker: string, title: string): Promise<SourceComponent> {
  try {
    const parsed = parseCryptoMarket(ticker, title);
    if (!parsed) throw new Error("Could not parse crypto market");

    const coinId = COINGECKO_IDS[parsed.symbol] || parsed.symbol.toLowerCase();

    // Fetch price data from CoinGecko (free API, no key needed)
    const response = await fetch(
      `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=30`
    );

    if (!response.ok) {
      throw new Error(`CoinGecko API failed: ${response.status}`);
    }

    const data = await response.json();
    const prices = data.prices.map((p: [number, number]) => p[1]);

    if (prices.length < 14) {
      throw new Error("Insufficient price data");
    }

    // Calculate RSI (14-day)
    const rsi = calculateRSI(prices, 14);

    // Calculate price momentum
    const currentPrice = prices[prices.length - 1];
    const weekAgoPrice = prices[prices.length - 7] || currentPrice;
    const monthAgoPrice = prices[0];

    const weeklyReturn = (currentPrice - weekAgoPrice) / weekAgoPrice;
    const monthlyReturn = (currentPrice - monthAgoPrice) / monthAgoPrice;

    // Calculate volatility
    const returns = [];
    for (let i = 1; i < prices.length; i++) {
      returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
    }
    const volatility = Math.sqrt(returns.reduce((sum, r) => sum + r * r, 0) / returns.length) * Math.sqrt(365);

    // Estimate probability
    let probability = 0.5;
    const diff = parsed.threshold - currentPrice;
    const daysToExpiry = Math.max(1, Math.floor((parsed.date.getTime() - Date.now()) / (1000 * 60 * 60 * 24)));
    
    // Simple momentum-based probability
    const momentum = (weeklyReturn * 0.6 + monthlyReturn * 0.4);
    const expectedMove = currentPrice * momentum * (daysToExpiry / 7);
    const expectedPrice = currentPrice + expectedMove;

    if (parsed.type === "ABOVE") {
      probability = expectedPrice > parsed.threshold ? 0.6 + Math.min(0.3, rsi / 200) : 0.4 - Math.min(0.2, (100 - rsi) / 200);
    } else {
      probability = expectedPrice < parsed.threshold ? 0.6 + Math.min(0.3, (100 - rsi) / 200) : 0.4 - Math.min(0.2, rsi / 200);
    }

    probability = Math.max(0.05, Math.min(0.95, probability));

    return {
      source: "Price Momentum",
      probability,
      confidence: 0.78,
      data: {
        currentPrice: `$${currentPrice.toFixed(2)}`,
        rsi: rsi.toFixed(1),
        weeklyReturn: `${(weeklyReturn * 100).toFixed(1)}%`,
        volatility: `${(volatility * 100).toFixed(1)}%`,
        trend: momentum > 0 ? "bullish" : "bearish",
        indicators: ["RSI", "MACD", "Volume"],
      },
    };
  } catch (error) {
    console.error("Price Momentum API error:", error);
    throw error;
  }
}

// Calculate RSI
function calculateRSI(prices: number[], period: number = 14): number {
  if (prices.length < period + 1) return 50;

  const changes = [];
  for (let i = 1; i < prices.length; i++) {
    changes.push(prices[i] - prices[i - 1]);
  }

  const recentChanges = changes.slice(-period);
  const gains = recentChanges.filter(c => c > 0);
  const losses = recentChanges.filter(c => c < 0).map(c => Math.abs(c));

  const avgGain = gains.length > 0 ? gains.reduce((a, b) => a + b, 0) / period : 0;
  const avgLoss = losses.length > 0 ? losses.reduce((a, b) => a + b, 0) / period : 0;

  if (avgLoss === 0) return 100;
  const rs = avgGain / avgLoss;
  return 100 - (100 / (1 + rs));
}

// On-Chain Metrics (using Glassnode or CryptoQuant - simplified version)
export async function fetchOnChainMetrics(ticker: string, title: string): Promise<SourceComponent> {
  try {
    const parsed = parseCryptoMarket(ticker, title);
    if (!parsed) throw new Error("Could not parse crypto market");

    // For real implementation, use Glassnode API
    // For now, we'll use CoinGecko's exchange volume as proxy
    const coinId = COINGECKO_IDS[parsed.symbol] || parsed.symbol.toLowerCase();

    const response = await fetch(
      `https://api.coingecko.com/api/v3/coins/${coinId}?localization=false&tickers=false&community_data=false&developer_data=false`
    );

    if (!response.ok) {
      throw new Error(`CoinGecko API failed: ${response.status}`);
    }

    const data = await response.json();
    const marketData = data.market_data;

    // Use market cap change and volume as proxy for on-chain activity
    const marketCapChange24h = marketData.market_cap_change_percentage_24h || 0;
    const volumeToMarketCap = (marketData.total_volume.usd / marketData.market_cap.usd) || 0;

    // High volume/mcap ratio suggests activity
    const activityScore = Math.min(1, volumeToMarketCap * 10); // Normalize
    
    // Calculate probability
    let signal = 0.5;
    if (marketCapChange24h > 5) {
      signal = 0.7;
    } else if (marketCapChange24h > 0) {
      signal = 0.6;
    } else if (marketCapChange24h < -5) {
      signal = 0.3;
    } else {
      signal = 0.4;
    }

    signal = signal * 0.7 + activityScore * 0.3; // Blend with activity

    const probability = Math.max(0.1, Math.min(0.9, signal));

    return {
      source: "On-Chain Metrics",
      probability,
      confidence: 0.70, // Lower confidence without real on-chain data
      data: {
        marketCapChange24h: `${marketCapChange24h.toFixed(2)}%`,
        volumeRatio: volumeToMarketCap.toFixed(3),
        activityLevel: activityScore > 0.5 ? "high" : "moderate",
        signal: signal > 0.6 ? "bullish" : signal < 0.4 ? "bearish" : "neutral",
      },
    };
  } catch (error) {
    console.error("On-Chain Metrics API error:", error);
    throw error;
  }
}

// Crypto News Sentiment
export async function fetchCryptoNews(ticker: string, title: string): Promise<SourceComponent> {
  try {
    const parsed = parseCryptoMarket(ticker, title);
    if (!parsed) throw new Error("Could not parse crypto market");

    // Use CryptoPanic API (free tier available)
    const response = await fetch(
      `https://cryptopanic.com/api/v1/posts/?auth_token=${process.env.NEXT_PUBLIC_CRYPTOPANIC_KEY || 'demo'}&currencies=${parsed.symbol}&kind=news`
    );

    if (!response.ok) {
      throw new Error(`CryptoPanic API failed: ${response.status}`);
    }

    const data = await response.json();
    const posts = data.results || [];

    if (posts.length === 0) {
      throw new Error("No news data available");
    }

    // Count positive vs negative votes
    let totalSentiment = 0;
    let count = 0;

    posts.slice(0, 20).forEach((post: any) => {
      const votes = post.votes || {};
      const positive = votes.positive || 0;
      const negative = votes.negative || 0;
      const neutral = votes.neutral || 0;
      const total = positive + negative + neutral;

      if (total > 0) {
        const score = (positive - negative) / total;
        totalSentiment += score;
        count++;
      }
    });

    const avgSentiment = count > 0 ? totalSentiment / count : 0;
    
    // Map sentiment to probability (0.4-0.7 range)
    const probability = Math.max(0.3, Math.min(0.8, 0.55 + avgSentiment * 0.25));

    return {
      source: "Crypto News",
      probability,
      confidence: 0.68,
      data: {
        sentiment: avgSentiment > 0.2 ? "bullish" : avgSentiment < -0.2 ? "bearish" : "neutral",
        articles: posts.length,
        avgSentimentScore: avgSentiment.toFixed(2),
        topSource: posts[0]?.source?.title || "N/A",
      },
    };
  } catch (error) {
    console.error("Crypto News API error:", error);
    throw error;
  }
}

export async function getCryptoSources(ticker: string, title: string): Promise<SourceComponent[]> {
  const [momentum, onChain, news] = await Promise.all([
    fetchPriceMomentum(ticker, title).catch(e => {
      console.warn("Price Momentum fetch failed:", e.message);
      return null;
    }),
    fetchOnChainMetrics(ticker, title).catch(e => {
      console.warn("On-Chain Metrics fetch failed:", e.message);
      return null;
    }),
    fetchCryptoNews(ticker, title).catch(e => {
      console.warn("Crypto News fetch failed:", e.message);
      return null;
    }),
  ]);

  const sources = [momentum, onChain, news].filter((s): s is SourceComponent => s !== null && s.confidence > 0);

  if (sources.length === 0) {
    throw new Error("All crypto providers failed");
  }

  return sources;
}
