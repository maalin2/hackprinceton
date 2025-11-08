import { SourceComponent } from "@/lib/types";

interface SportsMarket {
  ticker: string;
  sport: string;
  team: string;
  opponent?: string;
  date: Date;
}

function parseSportsMarket(ticker: string, title: string): SportsMarket | null {
  // Extract sport type
  let sport = "unknown";
  const titleLower = title.toLowerCase();
  
  if (titleLower.includes("nfl") || titleLower.includes("football")) sport = "nfl";
  else if (titleLower.includes("nba") || titleLower.includes("basketball")) sport = "nba";
  else if (titleLower.includes("mlb") || titleLower.includes("baseball")) sport = "mlb";
  else if (titleLower.includes("nhl") || titleLower.includes("hockey")) sport = "nhl";
  else if (titleLower.includes("soccer") || titleLower.includes("mls")) sport = "soccer";

  // Extract team names (look for capitalized words)
  const teams = title.match(/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b/g) || [];
  const team = teams[0] || "Unknown";
  const opponent = teams[1];

  return {
    ticker,
    sport,
    team,
    opponent,
    date: new Date(),
  };
}

// Injury Reports (using ESPN or similar)
export async function fetchInjuryReports(ticker: string, title: string): Promise<SourceComponent> {
  try {
    const parsed = parseSportsMarket(ticker, title);
    if (!parsed) throw new Error("Could not parse sports market");

    // ESPN has a public-ish API (not officially documented but stable)
    let espnSport = "football/nfl";
    if (parsed.sport === "nba") espnSport = "basketball/nba";
    else if (parsed.sport === "mlb") espnSport = "baseball/mlb";
    else if (parsed.sport === "nhl") espnSport = "hockey/nhl";

    const response = await fetch(
      `https://site.api.espn.com/apis/site/v2/sports/${espnSport}/news`
    );

    if (!response.ok) {
      throw new Error(`ESPN API failed: ${response.status}`);
    }

    const data = await response.json();
    const articles = data.articles || [];

    // Count injury-related articles
    const injuryArticles = articles.filter((a: any) => 
      a.headline?.toLowerCase().includes("injury") ||
      a.headline?.toLowerCase().includes("injured") ||
      a.headline?.toLowerCase().includes("out") ||
      a.description?.toLowerCase().includes("injury")
    );

    const injuryCount = injuryArticles.length;
    
    // More injuries = lower probability of winning
    const impactScore = Math.max(0, 1 - (injuryCount / 10));
    
    // Base probability influenced by injury news
    const probability = Math.max(0.3, Math.min(0.8, 0.5 + (impactScore - 0.5) * 0.3));

    return {
      source: "Injury Reports",
      probability,
      confidence: 0.75,
      data: {
        injuryCount,
        impactLevel: injuryCount > 3 ? "high" : injuryCount > 1 ? "medium" : "low",
        recentNews: injuryArticles.slice(0, 3).map((a: any) => a.headline),
        lastUpdate: new Date().toISOString(),
      },
    };
  } catch (error) {
    console.error("Injury Reports API error:", error);
    throw error;
  }
}

// Team Form & ELO ratings
export async function fetchTeamForm(ticker: string, title: string): Promise<SourceComponent> {
  try {
    const parsed = parseSportsMarket(ticker, title);
    if (!parsed) throw new Error("Could not parse sports market");

    // Use ESPN Standings/Scores API
    let espnSport = "football/nfl";
    if (parsed.sport === "nba") espnSport = "basketball/nba";
    else if (parsed.sport === "mlb") espnSport = "baseball/mlb";
    else if (parsed.sport === "nhl") espnSport = "hockey/nhl";

    const response = await fetch(
      `https://site.api.espn.com/apis/site/v2/sports/${espnSport}/scoreboard`
    );

    if (!response.ok) {
      throw new Error(`ESPN Standings API failed: ${response.status}`);
    }

    const data = await response.json();
    const events = data.events || [];

    // Find team in recent games
    const teamGames = events.filter((e: any) => {
      const competitors = e.competitions?.[0]?.competitors || [];
      return competitors.some((c: any) => 
        c.team.displayName?.toLowerCase().includes(parsed.team.toLowerCase()) ||
        c.team.abbreviation?.toLowerCase().includes(parsed.team.toLowerCase())
      );
    });

    if (teamGames.length === 0) {
      // No recent games, use neutral probability
      return {
        source: "Team Form (ELO)",
        probability: 0.5,
        confidence: 0.50,
        data: {
          note: "No recent games found",
        },
      };
    }

    // Calculate win rate from recent games
    let wins = 0;
    let total = 0;

    teamGames.slice(0, 5).forEach((game: any) => {
      const competitors = game.competitions?.[0]?.competitors || [];
      const teamCompetitor = competitors.find((c: any) => 
        c.team.displayName?.toLowerCase().includes(parsed.team.toLowerCase())
      );

      if (teamCompetitor && game.status?.type?.completed) {
        total++;
        if (teamCompetitor.winner) wins++;
      }
    });

    const winRate = total > 0 ? wins / total : 0.5;
    
    // Adjust probability based on recent form
    const probability = Math.max(0.3, Math.min(0.8, winRate * 0.6 + 0.2));

    return {
      source: "Team Form (ELO)",
      probability,
      confidence: 0.82,
      data: {
        winRate: `${(winRate * 100).toFixed(0)}%`,
        recentRecord: `${wins}-${total - wins}`,
        gamesAnalyzed: total,
        form: winRate > 0.6 ? "strong" : winRate > 0.4 ? "average" : "poor",
      },
    };
  } catch (error) {
    console.error("Team Form API error:", error);
    throw error;
  }
}

// Sports News Sentiment
export async function fetchSportsNews(ticker: string, title: string): Promise<SourceComponent> {
  try {
    const parsed = parseSportsMarket(ticker, title);
    if (!parsed) throw new Error("Could not parse sports market");

    // Use NewsAPI for sports news
    const searchQuery = `${parsed.team} ${parsed.sport}`;

    const response = await fetch(
      `https://newsapi.org/v2/everything?q=${encodeURIComponent(searchQuery)}&sortBy=publishedAt&pageSize=30&language=en&apiKey=${process.env.NEXT_PUBLIC_NEWS_API_KEY || 'demo'}`
    );

    if (!response.ok) {
      throw new Error(`NewsAPI failed: ${response.status}`);
    }

    const data = await response.json();
    const articles = data.articles || [];

    if (articles.length === 0) {
      throw new Error("No sports news found");
    }

    // Sentiment analysis
    const positiveWords = ["win", "victory", "dominate", "strong", "best", "star", "excel", "lead", "ahead", "favorite"];
    const negativeWords = ["lose", "defeat", "struggle", "weak", "worst", "injury", "problem", "behind", "underdog", "poor"];

    let sentimentScore = 0;

    articles.slice(0, 20).forEach((article: any) => {
      const text = `${article.title} ${article.description || ""}`.toLowerCase();
      
      positiveWords.forEach(word => {
        if (text.includes(word)) sentimentScore += 1;
      });
      
      negativeWords.forEach(word => {
        if (text.includes(word)) sentimentScore -= 1;
      });
    });

    const normalizedSentiment = sentimentScore / Math.max(1, articles.slice(0, 20).length);
    
    const probability = Math.max(0.3, Math.min(0.75, 0.5 + normalizedSentiment * 0.15));

    return {
      source: "Sports News",
      probability,
      confidence: 0.70,
      data: {
        sentiment: normalizedSentiment > 0.1 ? "favorable" : normalizedSentiment < -0.1 ? "unfavorable" : "neutral",
        articles: articles.length,
        sentimentScore: normalizedSentiment.toFixed(2),
        topHeadlines: articles.slice(0, 3).map((a: any) => a.title),
      },
    };
  } catch (error) {
    console.error("Sports News API error:", error);
    throw error;
  }
}

export async function getSportsSources(ticker: string, title: string): Promise<SourceComponent[]> {
  const [injuries, form, news] = await Promise.all([
    fetchInjuryReports(ticker, title).catch(e => {
      console.warn("Injury Reports fetch failed:", e.message);
      return null;
    }),
    fetchTeamForm(ticker, title).catch(e => {
      console.warn("Team Form fetch failed:", e.message);
      return null;
    }),
    fetchSportsNews(ticker, title).catch(e => {
      console.warn("Sports News fetch failed:", e.message);
      return null;
    }),
  ]);

  const sources = [injuries, form, news].filter((s): s is SourceComponent => s !== null && s.confidence > 0);

  if (sources.length === 0) {
    throw new Error("All sports providers failed");
  }

  return sources;
}
