import { SourceComponent } from "@/lib/types";

// News API (free tier: 100 requests/day)
export async function fetchHeadlines(ticker: string, title: string): Promise<SourceComponent> {
  try {
    // Extract topic from title
    const keywords = title.toLowerCase();
    let searchQuery = "";
    
    if (keywords.includes("election") || keywords.includes("president")) {
      searchQuery = "election president politics";
    } else if (keywords.includes("congress") || keywords.includes("senate")) {
      searchQuery = "congress senate politics";
    } else {
      searchQuery = "politics government";
    }

    const response = await fetch(
      `https://newsapi.org/v2/everything?q=${encodeURIComponent(searchQuery)}&sortBy=publishedAt&pageSize=50&language=en&apiKey=${process.env.NEXT_PUBLIC_NEWS_API_KEY || 'demo'}`
    );

    if (!response.ok) {
      throw new Error(`NewsAPI failed: ${response.status}`);
    }

    const data = await response.json();
    const articles = data.articles || [];

    if (articles.length === 0) {
      throw new Error("No news articles found");
    }

    // Simple sentiment analysis based on title/description keywords
    const positiveWords = ["win", "lead", "ahead", "strong", "support", "victory", "success", "positive", "favorable", "boost"];
    const negativeWords = ["lose", "behind", "weak", "oppose", "defeat", "fail", "negative", "unfavorable", "decline", "drop"];

    let sentimentScore = 0;
    articles.slice(0, 30).forEach((article: any) => {
      const text = `${article.title} ${article.description || ""}`.toLowerCase();
      
      positiveWords.forEach(word => {
        if (text.includes(word)) sentimentScore += 1;
      });
      
      negativeWords.forEach(word => {
        if (text.includes(word)) sentimentScore -= 1;
      });
    });

    // Normalize sentiment (-1 to 1)
    const normalizedSentiment = sentimentScore / Math.max(1, articles.slice(0, 30).length);
    
    // Map to probability (0.3 - 0.7)
    const probability = Math.max(0.2, Math.min(0.8, 0.5 + normalizedSentiment * 0.2));

    return {
      source: "News Headlines",
      probability,
      confidence: 0.70,
      data: {
        sentiment: normalizedSentiment > 0.1 ? "positive" : normalizedSentiment < -0.1 ? "negative" : "neutral",
        articles: articles.length,
        sentimentScore: normalizedSentiment.toFixed(2),
        topSources: [...new Set(articles.slice(0, 5).map((a: any) => a.source.name))].slice(0, 3),
      },
    };
  } catch (error) {
    console.error("News Headlines API error:", error);
    throw error;
  }
}

// Polling Data (using FiveThirtyEight or RealClearPolitics - note: these don't have public APIs)
// We'll use a web scraping proxy or fallback to a news-based signal
export async function fetchPollingData(ticker: string, title: string): Promise<SourceComponent> {
  try {
    // Since 538 and RCP don't have official APIs, we'll use news sentiment as a proxy
    // In a production system, you'd scrape their websites or use a third-party aggregator
    
    // For now, we'll fetch Google Trends data as a proxy for public interest/momentum
    // Note: Google Trends doesn't have an official API, but we can use a proxy service
    
    // Extract candidate/topic names from title
    const keywords = title.match(/\b[A-Z][a-z]+\b/g) || ["politics"];
    const searchTerm = keywords.slice(0, 2).join(" ");

    // Using SerpAPI for Google Trends (requires API key)
    const response = await fetch(
      `https://serpapi.com/search.json?engine=google_trends&q=${encodeURIComponent(searchTerm)}&data_type=TIMESERIES&api_key=${process.env.NEXT_PUBLIC_SERPAPI_KEY || 'demo'}`
    );

    if (!response.ok) {
      // Fallback: use a middle probability with low confidence
      return {
        source: "Polling Aggregate",
        probability: 0.5,
        confidence: 0.50,
        data: {
          note: "API unavailable, using neutral baseline",
        },
      };
    }

    const data = await response.json();
    const timeline = data.interest_over_time?.timeline_data || [];

    if (timeline.length === 0) {
      throw new Error("No polling data available");
    }

    // Calculate momentum from recent trend
    const recent = timeline.slice(-7); // Last week
    const older = timeline.slice(-14, -7); // Week before

    const recentAvg = recent.reduce((sum: number, item: any) => sum + (item.values?.[0]?.value || 0), 0) / recent.length;
    const olderAvg = older.length > 0 ? older.reduce((sum: number, item: any) => sum + (item.values?.[0]?.value || 0), 0) / older.length : recentAvg;

    const momentum = olderAvg > 0 ? (recentAvg - olderAvg) / olderAvg : 0;

    // Map momentum to probability
    const probability = Math.max(0.2, Math.min(0.8, 0.5 + momentum * 0.3));

    return {
      source: "Polling Aggregate",
      probability,
      confidence: 0.75,
      data: {
        momentum: momentum > 0.05 ? "rising" : momentum < -0.05 ? "falling" : "stable",
        recentInterest: recentAvg.toFixed(1),
        change: `${(momentum * 100).toFixed(1)}%`,
      },
    };
  } catch (error) {
    console.error("Polling Data API error:", error);
    
    // Fallback to news sentiment
    try {
      const newsSignal = await fetchHeadlines(ticker, title);
      return {
        source: "Polling Aggregate",
        probability: newsSignal.probability,
        confidence: 0.60,
        data: {
          fallback: "Using news sentiment as proxy",
          ...newsSignal.data,
        },
      };
    } catch {
      throw error;
    }
  }
}

// Social Mentions (using Twitter API alternative or Reddit)
export async function fetchSocialMentions(ticker: string, title: string): Promise<SourceComponent> {
  try {
    // Use Reddit API (no auth needed for read-only)
    const keywords = title.toLowerCase();
    let subreddit = "politics";
    
    if (keywords.includes("election")) subreddit = "politics";
    else if (keywords.includes("president")) subreddit = "politics";

    const searchQuery = title.split(' ').slice(0, 3).join(' ');

    const response = await fetch(
      `https://www.reddit.com/r/${subreddit}/search.json?q=${encodeURIComponent(searchQuery)}&restrict_sr=1&sort=hot&limit=100`,
      { headers: { "User-Agent": "KalshiDecisionDashboard/1.0" } }
    );

    if (!response.ok) {
      throw new Error(`Reddit API failed: ${response.status}`);
    }

    const data = await response.json();
    const posts = data.data?.children || [];

    if (posts.length === 0) {
      throw new Error("No social mentions found");
    }

    // Analyze post scores and sentiment
    let totalScore = 0;
    let totalComments = 0;

    posts.forEach((post: any) => {
      const postData = post.data;
      totalScore += postData.score || 0;
      totalComments += postData.num_comments || 0;
    });

    const avgScore = totalScore / posts.length;
    const avgComments = totalComments / posts.length;

    // High engagement = higher confidence in market direction
    const engagement = Math.min(1, (avgScore + avgComments) / 100);

    // Simple sentiment from upvote ratio
    const upvoteRatios = posts.map((p: any) => p.data.upvote_ratio || 0.5);
    const avgUpvoteRatio = upvoteRatios.reduce((a: number, b: number) => a + b, 0) / upvoteRatios.length;

    const probability = Math.max(0.25, Math.min(0.75, 0.3 + avgUpvoteRatio * 0.4));

    return {
      source: "Social Momentum",
      probability,
      confidence: 0.65,
      data: {
        mentions: posts.length,
        avgScore: avgScore.toFixed(0),
        avgComments: avgComments.toFixed(0),
        engagement: engagement > 0.5 ? "high" : "moderate",
        trend: avgUpvoteRatio > 0.6 ? "positive" : avgUpvoteRatio < 0.4 ? "negative" : "neutral",
        platforms: ["Reddit"],
      },
    };
  } catch (error) {
    console.error("Social Mentions API error:", error);
    throw error;
  }
}

export async function getPoliticsSources(ticker: string, title: string): Promise<SourceComponent[]> {
  const [polling, headlines, social] = await Promise.all([
    fetchPollingData(ticker, title).catch(e => {
      console.warn("Polling fetch failed:", e.message);
      return null;
    }),
    fetchHeadlines(ticker, title).catch(e => {
      console.warn("Headlines fetch failed:", e.message);
      return null;
    }),
    fetchSocialMentions(ticker, title).catch(e => {
      console.warn("Social Mentions fetch failed:", e.message);
      return null;
    }),
  ]);

  const sources = [polling, headlines, social].filter((s): s is SourceComponent => s !== null && s.confidence > 0);

  if (sources.length === 0) {
    throw new Error("All politics providers failed");
  }

  return sources;
}
