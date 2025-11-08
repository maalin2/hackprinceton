import requests

# Categories to fetch bets from (case-insensitive match)
categories = ["Climate and Weather", "Politics", "Sports", "Crypto"]

for category in categories:
    print(f"\n{'='*80}")
    print(f"== {category.upper()} ==")
    print('='*80)
    
    # First, get series in this category
    r_series = requests.get(
        "https://api.elections.kalshi.com/trade-api/v2/series",
        params={"limit": 200},
        timeout=10,
    )
    r_series.raise_for_status()
    all_series = r_series.json().get("series", [])
    
    # Filter series by category (case-insensitive)
    matching_series = [s for s in all_series if s.get('category', '').lower() == category.lower()]
    
    print(f"Found {len(matching_series)} series in {category}")
    
    if not matching_series:
        print(f"No series found in category '{category}'")
        continue
    
    # Display first 10 series from this category
    series_to_show = matching_series[:10]
    
    print(f"\nShowing {len(series_to_show)} series:\n")
    for s in series_to_show:
        ticker = s.get('ticker', 'N/A')
        title = s.get('title', 'N/A')
        
        # Truncate long titles
        if len(title) > 80:
            title = title[:77] + "..."
        
        print(f"{ticker[:40]:<40} | {title}")
        print()
