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
 * 2. Reddit as fallback (similar sentiment signal)
 */
export async function fetchTwitterPosts(searchQuery: string): Promise<Tweet[]> {
  // Try Twitter API first if key is available
  if (process.env.NEXT_PUBLIC_TWITTER_BEARER_TOKEN) {
    try {
      return await fetchFromTwitterAPI(searchQuery);
    } catch (error) {
      console.error("Twitter API failed, trying Reddit fallback:", error);
    }
  }

  // Use Reddit posts as sentiment proxy (via our API to avoid CORS)
  try {
    return await fetchFromReddit(searchQuery);
  } catch (error) {
    console.error("All social fetch methods failed:", error);
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

// Method 2: Reddit fallback (similar sentiment signal)
async function fetchFromReddit(searchQuery: string): Promise<Tweet[]> {
  // Search multiple relevant subreddits via our API proxy (avoids CORS)
  const subreddits = ['wallstreetbets', 'cryptocurrency', 'politics', 'news', 'sports'];
  const allPosts: Tweet[] = [];

  for (const subreddit of subreddits) {
    try {
      // Use our Next.js API route to avoid CORS
      const response = await fetch(
        `/api/reddit?subreddit=${subreddit}&q=${encodeURIComponent(searchQuery)}&limit=20`
      );

      if (!response.ok) {
        console.warn(`Reddit ${subreddit} returned ${response.status}`);
        continue;
      }

      const data = await response.json();
      
      // Check if this is a fallback response (Reddit API failed but returned 200)
      if (data.fallback) {
        console.warn(`Reddit ${subreddit} fallback:`, data.error);
        continue;
      }
      
      const posts = data.posts || [];

      if (posts.length === 0) {
        console.warn(`Reddit ${subreddit} returned no posts`);
        continue;
      }

      posts.forEach((post: any) => {
        const text = post.title + (post.text ? ` ${post.text.substring(0, 200)}` : '');

        if (text.length > 10) {
          allPosts.push({
            id: post.id,
            text: text.substring(0, 280),
            timestamp: new Date(post.created * 1000),
            author: `u/${post.author}`,
            likes: post.score || 0,
            url: `https://reddit.com${post.permalink}`,
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
