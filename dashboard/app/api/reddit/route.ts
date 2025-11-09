import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const subreddit = searchParams.get('subreddit') || 'all';
  const query = searchParams.get('q') || '';
  const limit = searchParams.get('limit') || '20';

  if (!query) {
    return NextResponse.json({ error: 'Query parameter required' }, { status: 400 });
  }

  try {
    const url = `https://www.reddit.com/r/${subreddit}/search.json?q=${encodeURIComponent(query)}&restrict_sr=1&sort=hot&limit=${limit}`;
    
    console.log(`[Reddit API] Fetching: ${url}`);
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; KalshiDecisionDashboard/1.0; +https://kalshi.com)',
        'Accept': 'application/json',
      },
    });

    console.log(`[Reddit API] Response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[Reddit API] Error response: ${errorText}`);
      throw new Error(`Reddit API failed: ${response.status} - ${errorText.substring(0, 200)}`);
    }

    const data = await response.json();
    
    if (!data || !data.data) {
      console.error('[Reddit API] Invalid response structure:', data);
      throw new Error('Invalid Reddit API response structure');
    }
    
    // Transform to simpler format
    const posts = (data.data?.children || []).map((child: any) => {
      const post = child.data;
      return {
        id: post.id,
        title: post.title,
        text: post.selftext || '',
        author: post.author,
        score: post.score || 0,
        numComments: post.num_comments || 0,
        upvoteRatio: post.upvote_ratio || 0.5,
        created: post.created_utc,
        permalink: post.permalink,
      };
    });

    console.log(`[Reddit API] Successfully fetched ${posts.length} posts`);
    return NextResponse.json({ posts });
  } catch (error) {
    console.error('[Reddit API] Proxy error:', error);
    
    // Return empty array instead of error to allow graceful degradation
    // This way sentiment agent can still work with just Kalshi comments
    return NextResponse.json(
      { 
        posts: [], 
        error: error instanceof Error ? error.message : 'Failed to fetch from Reddit',
        fallback: true 
      },
      { status: 200 } // Return 200 with empty results instead of 500
    );
  }
}

