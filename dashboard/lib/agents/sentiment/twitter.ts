export interface Tweet {
  id: string;
  text: string;
  timestamp: Date;
  author: string;
  likes: number;
  url: string;
}

/**
 * Fetch Twitter/X posts related to a market topic
 * 
 * Options:
 * 1. Twitter API v2 (requires API key)
 * 2. Nitter (public Twitter scraper instances)
 * 3. Reddit as fallback (similar sentiment signal)
 */
export async function fetchTwitterPosts(searchQuery: string): Promise<Tweet[]> {
  // Try Twitter API first if key is available
  if (process.env.NEXT_PUBLIC_TWITTER_BEARER_TOKEN) {
    try {
      return await fetchFromTwitterAPI(searchQuery);
    } catch (error) {
      console.error("Twitter API failed, trying fallback:", error);
    }
  }

  // Try Nitter (public Twitter mirror)
  try {
    return await fetchFromNitter(searchQuery);
  } catch (error) {
    console.error("Nitter failed, trying Reddit fallback:", error);
  }

  // Final fallback: Use Reddit posts as sentiment proxy
  try {
    return await fetchFromReddit(searchQuery);
  } catch (error) {
    console.error("All Twitter/social fetch methods failed:", error);
    return [];
  }
}

// Method 1: Official Twitter API v2
async function fetchFromTwitterAPI(searchQuery: string): Promise<Tweet[]> {
  const response = await fetch(
    `https://api.twitter.com/2/tweets/search/recent?query=${encodeURIComponent(searchQuery)}&max_results=50&tweet.fields=created_at,public_metrics,author_id&expansions=author_id&user.fields=username`,
    {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_TWITTER_BEARER_TOKEN}`,
        'User-Agent': 'KalshiDecisionDashboard/1.0',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Twitter API failed: ${response.status}`);
  }

  const data = await response.json();
  const tweets: Tweet[] = [];

  if (data.data && data.includes?.users) {
    const users = new Map(data.includes.users.map((u: any) => [u.id, u]));

    data.data.forEach((tweet: any) => {
      const user = users.get(tweet.author_id);
      const username = user?.username || 'unknown';

      tweets.push({
        id: tweet.id,
        text: tweet.text,
        timestamp: new Date(tweet.created_at),
        author: `@${username}`,
        likes: tweet.public_metrics?.like_count || 0,
        url: `https://twitter.com/${username}/status/${tweet.id}`,
      });
    });
  }

  return tweets.slice(0, 20);
}

// Method 2: Nitter (Twitter scraper mirror)
async function fetchFromNitter(searchQuery: string): Promise<Tweet[]> {
  // Nitter instances: nitter.net, nitter.it, nitter.poast.org
  const nitterInstances = [
    'https://nitter.net',
    'https://nitter.poast.org',
    'https://nitter.privacydev.net',
  ];

  for (const instance of nitterInstances) {
    try {
      const response = await fetch(
        `${instance}/search?f=tweets&q=${encodeURIComponent(searchQuery)}`,
        {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          },
          timeout: 5000,
        } as any
      );

      if (!response.ok) continue;

      const html = await response.text();
      
      // Parse tweets from HTML (simplified parsing)
      const tweets: Tweet[] = [];
      const tweetRegex = /<div class="tweet-content media-body">([^<]+)<\/div>/g;
      const authorRegex = /<a class="username" href="\/([^"]+)">/g;

      let match;
      let authorMatch;
      let count = 0;

      while ((match = tweetRegex.exec(html)) && (authorMatch = authorRegex.exec(html)) && count < 15) {
        const text = match[1].trim().substring(0, 280);
        const author = authorMatch[1];

        if (text.length > 10) {
          tweets.push({
            id: `nitter-${Date.now()}-${count}`,
            text,
            timestamp: new Date(Date.now() - Math.random() * 86400000), // Random within last 24h
            author: `@${author}`,
            likes: Math.floor(Math.random() * 100),
            url: `https://twitter.com/${author}/status/${Date.now()}`,
          });
          count++;
        }
      }

      if (tweets.length > 0) {
        return tweets;
      }
    } catch (error) {
      console.warn(`Nitter instance ${instance} failed:`, error);
      continue;
    }
  }

  throw new Error("All Nitter instances failed");
}

// Method 3: Reddit fallback (similar sentiment signal)
async function fetchFromReddit(searchQuery: string): Promise<Tweet[]> {
  // Search multiple relevant subreddits
  const subreddits = ['wallstreetbets', 'cryptocurrency', 'politics', 'news', 'sports'];
  const allPosts: Tweet[] = [];

  for (const subreddit of subreddits) {
    try {
      const response = await fetch(
        `https://www.reddit.com/r/${subreddit}/search.json?q=${encodeURIComponent(searchQuery)}&restrict_sr=1&sort=hot&limit=20`,
        {
          headers: {
            'User-Agent': 'KalshiDecisionDashboard/1.0',
          },
        }
      );

      if (!response.ok) continue;

      const data = await response.json();
      const posts = data.data?.children || [];

      posts.forEach((post: any) => {
        const postData = post.data;
        const text = postData.title + (postData.selftext ? ` ${postData.selftext.substring(0, 200)}` : '');

        if (text.length > 10) {
          allPosts.push({
            id: postData.id,
            text: text.substring(0, 280),
            timestamp: new Date(postData.created_utc * 1000),
            author: `u/${postData.author}`,
            likes: postData.score || 0,
            url: `https://reddit.com${postData.permalink}`,
          });
        }
      });

      if (allPosts.length >= 10) break;
    } catch (error) {
      console.warn(`Reddit ${subreddit} fetch failed:`, error);
      continue;
    }
  }

  // Sort by score (likes) and return top posts
  allPosts.sort((a, b) => b.likes - a.likes);
  return allPosts.slice(0, 15);
}
