#!/usr/bin/env python3
"""Test economics markets analysis"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import economics_test

# Get all economics markets
df = economics_test.get_open_economics_markets()
print(f"Total economics markets found: {len(df)}")
print()

# Test enrichment with first 10 markets
print("Testing enrichment with first 10 markets...")
print("=" * 80)
df_out = economics_test.enrich_with_economics_probs(df.head(10))

print()
print(f"Markets successfully enriched: {len(df_out)}/10")
print(f"Success rate: {len(df_out)/10*100:.1f}%")
print()

if not df_out.empty:
    print("Enriched markets:")
    print("-" * 80)
    for _, row in df_out.iterrows():
        print(f"Ticker: {row['ticker']}")
        print(f"  Title: {row['title']}")
        print(f"  Combined P: {row['combined_p']:.3f}")
        print(f"  Market P: {row['market_p']:.3f}")
        print(f"  Edge: {row['edge_pct']:.1f}%")
        print(f"  Sources: {row['sources']}")
        print(f"  Source breakdown: {row['source_breakdown']}")
        print()
else:
    print("No markets were successfully enriched!")
