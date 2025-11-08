#!/usr/bin/env python3
"""
Quantitative Market Analysis Agent

Standalone agent that can be used with MCP or as a CLI tool.
Provides quantitative analysis for Kalshi markets using statistical methods only.
"""

import json
import sys
import argparse
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import weather_test
    import politics_test
    import economics_test
except ImportError as e:
    print(f"Error: Could not import test modules: {e}", file=sys.stderr)
    sys.exit(1)

# Try to import strategy system
try:
    from strategies import get_strategy
    STRATEGIES_AVAILABLE = True
except ImportError:
    STRATEGIES_AVAILABLE = False
    print("Warning: Strategy system not available", file=sys.stderr)


class QuantitativeAgent:
    """Quantitative Market Analysis Agent with Strategy Support"""
    
    def __init__(self, strategy: str = "statistical_arbitrage", **strategy_config):
        """
        Initialize agent with strategy selection
        
        Args:
            strategy: Strategy name ('statistical_arbitrage', 'moving_average')
            **strategy_config: Additional strategy configuration (e.g., ma_period=7)
        """
        self.strategy_name = strategy
        self.strategy_config = strategy_config
        
        self.categories = {
            "weather": {
                "sources": ["NOAA (GFS)", "Open-Meteo (ECMWF)", "Climatology"],
                "module": weather_test,
                "get_markets": weather_test.get_open_weather_markets,
                "analyze": weather_test.enrich_with_weather_probs,
            },
            "politics": {
                "sources": ["Kalshi Market Consensus", "Historical Voting Patterns", "Betting Market Model"],
                "module": politics_test,
                "get_markets": politics_test.get_open_politics_markets,
                "analyze": politics_test.enrich_with_politics_probs,
            },
            "economics": {
                "sources": ["FRED", "Economic Indicators", "Kalshi Market Consensus"],
                "module": economics_test,
                "get_markets": economics_test.get_open_economics_markets,
                "analyze": economics_test.enrich_with_economics_probs,
            },
        }
    
    def analyze_category(self, category: str, limit: int = 10) -> dict:
        """Analyze markets in a specific category"""
        if category not in self.categories:
            return {
                "status": "error",
                "error": f"Unknown category: {category}",
                "message": f"Available categories: {', '.join(self.categories.keys())}"
            }
        
        try:
            config = self.categories[category]
            df = config["get_markets"]()
            
            if df.empty:
                return {
                    "status": "no_markets",
                    "message": f"No open {category} markets found",
                    "markets_analyzed": 0
                }
            
            # Limit markets
            df = df.head(limit)
            
            # Analyze markets
            df_out = config["analyze"](df)
            
            if df_out.empty:
                return {
                    "status": "analysis_failed",
                    "message": "Could not analyze markets",
                    "markets_analyzed": 0
                }
            
            # Convert to JSON-serializable format
            results = []
            for _, row in df_out.iterrows():
                results.append(self._format_market_result(row, category))
            
            # Calculate summary statistics
            summary = self._calculate_summary(df_out)
            
            return {
                "status": "success",
                "category": category,
                "sources": config["sources"],
                "summary": summary,
                "markets": results
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Error analyzing {category} markets: {e}"
            }
    
    def analyze_single_market(self, ticker: str) -> dict:
        """Analyze a single market by ticker"""
        # Determine category from ticker
        category = self._detect_category(ticker)
        
        if category not in self.categories:
            return {
                "status": "error",
                "error": f"Could not determine category for ticker: {ticker}"
            }
        
        try:
            config = self.categories[category]
            df = config["get_markets"]()
            
            if df.empty:
                return {
                    "status": "no_markets",
                    "message": f"No open {category} markets found"
                }
            
            # Find market
            market_df = df[df["ticker"] == ticker]
            if market_df.empty:
                return {
                    "status": "not_found",
                    "message": f"Market {ticker} not found"
                }
            
            # Analyze market
            df_out = config["analyze"](market_df)
            if df_out.empty:
                return {
                    "status": "analysis_failed",
                    "message": f"Could not analyze market {ticker}"
                }
            
            row = df_out.iloc[0]
            return self._format_market_result(row, category)
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Error analyzing market {ticker}: {e}"
            }
    
    def get_categories(self) -> dict:
        """Get available categories and their sources"""
        return {
            "categories": [
                {
                    "name": name,
                    "sources": config["sources"],
                    "methodology": "Statistical/Quantitative methods only (no sentiment analysis)"
                }
                for name, config in self.categories.items()
            ]
        }
    
    def _detect_category(self, ticker: str) -> str:
        """Detect category from ticker"""
        ticker_upper = ticker.upper()
        
        if ticker.startswith(("KXHIGH", "KXRAIN")):
            return "weather"
        elif any(keyword in ticker_upper for keyword in ["GDP", "INFLATION", "UNEMPLOYMENT", "INTEREST", "STOCK"]):
            return "economics"
        else:
            return "politics"  # Default
    
    def _format_market_result(self, row, category: str) -> dict:
        """Format a single market result"""
        return {
            "ticker": str(row.get("ticker", "")),
            "title": str(row.get("title", "")),
            "combined_p": float(row.get("combined_p", 0)) if pd.notnull(row.get("combined_p")) else None,
            "market_p": float(row.get("market_p", 0)) if pd.notnull(row.get("market_p")) else None,
            "edge": float(row.get("edge", 0)) if pd.notnull(row.get("edge")) else None,
            "edge_pct": float(row.get("edge_pct", 0)) if pd.notnull(row.get("edge_pct")) else None,
            "sources": int(row.get("sources", 0)),
            "confidence": float(row.get("confidence", 0)) if pd.notnull(row.get("confidence")) else None,
            "source_breakdown": str(row.get("source_breakdown", "")),
            "recommendation": self._get_recommendation(row.get("edge_pct"))
        }
    
    def _calculate_summary(self, df_out) -> dict:
        """Calculate summary statistics"""
        return {
            "markets_analyzed": len(df_out),
            "average_edge": float(df_out["edge_pct"].mean()) if df_out["edge_pct"].notna().any() else None,
            "max_edge": float(df_out["edge_pct"].max()) if df_out["edge_pct"].notna().any() else None,
            "markets_with_edge_gt_8": int((df_out["edge_pct"].abs() > 8).sum()) if df_out["edge_pct"].notna().any() else 0,
            "average_confidence": float(df_out["confidence"].mean()) if df_out["confidence"].notna().any() else None
        }
    
    def _get_recommendation(self, edge_pct) -> str:
        """Get trading recommendation based on edge"""
        if pd.isna(edge_pct):
            return "HOLD (no edge data)"
        
        edge_pct = float(edge_pct)
        if edge_pct > 8:
            return "BUY YES"
        elif edge_pct < -8:
            return "BUY NO"
        else:
            return "HOLD"


def main():
    """CLI interface for the quantitative agent"""
    parser = argparse.ArgumentParser(description="Quantitative Market Analysis Agent with Strategy Support")
    parser.add_argument("command", choices=["analyze", "categories", "market", "strategies"], help="Command to execute")
    parser.add_argument("--category", choices=["weather", "politics", "economics"], help="Category to analyze")
    parser.add_argument("--ticker", help="Market ticker to analyze")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of markets to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Strategy options
    parser.add_argument("--strategy", default="statistical_arbitrage", choices=["statistical_arbitrage", "moving_average"], help="Analysis strategy to use")
    parser.add_argument("--ma-period", type=int, default=7, help="Moving average period (for moving_average strategy)")
    parser.add_argument("--ma-type", choices=["sma", "ema"], default="sma", help="Moving average type")
    parser.add_argument("--signal-type", choices=["mean_reversion", "trend_following"], default="mean_reversion", help="Signal type for MA")
    
    args = parser.parse_args()
    
    # Build strategy config
    strategy_config = {}
    if args.strategy == "moving_average":
        strategy_config = {
            "ma_period": args.ma_period,
            "ma_type": args.ma_type,
            "signal_type": args.signal_type,
        }
    
    agent = QuantitativeAgent(strategy=args.strategy, **strategy_config)
    
    if args.command == "strategies":
        strategies_info = {
            "available_strategies": [
                {
                    "name": "statistical_arbitrage",
                    "description": "Multi-source comparison to find statistical arbitrage",
                    "best_for": ["weather", "politics", "economics"],
                    "requires": "External data sources (NOAA, FRED, etc.)"
                },
                {
                    "name": "moving_average",
                    "description": "Price trend analysis using moving averages",
                    "best_for": ["politics", "economics"],
                    "requires": "Historical price data from Kalshi",
                    "parameters": {
                        "ma_period": "Moving average window (default: 7 days)",
                        "ma_type": "sma or ema (default: sma)",
                        "signal_type": "mean_reversion or trend_following (default: mean_reversion)"
                    }
                }
            ],
            "current_strategy": args.strategy,
            "current_config": strategy_config
        }
        
        if args.json:
            print(json.dumps(strategies_info, indent=2))
        else:
            print("=" * 60)
            print("AVAILABLE STRATEGIES")
            print("=" * 60)
            for strat in strategies_info["available_strategies"]:
                marker = "✅" if strat["name"] == args.strategy else "  "
                print(f"\n{marker} {strat['name'].upper()}")
                print(f"  Description: {strat['description']}")
                print(f"  Best for: {', '.join(strat['best_for'])}")
                print(f"  Requires: {strat['requires']}")
                if "parameters" in strat:
                    print(f"  Parameters:")
                    for param, desc in strat["parameters"].items():
                        print(f"    --{param.replace('_', '-')}: {desc}")
            print(f"\nCurrent Strategy: {args.strategy}")
            if strategy_config:
                print(f"Current Config: {strategy_config}")
    
    elif args.command == "categories":
        result = agent.get_categories()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Available Categories:")
            for cat in result["categories"]:
                print(f"\n{cat['name'].upper()}:")
                print(f"  Sources: {', '.join(cat['sources'])}")
                print(f"  Methodology: {cat['methodology']}")
    
    elif args.command == "analyze":
        if not args.category:
            print("Error: --category is required for analyze command", file=sys.stderr)
            sys.exit(1)
        
        result = agent.analyze_category(args.category, args.limit)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_analysis_result(result, args.strategy, strategy_config)
    
    elif args.command == "market":
        if not args.ticker:
            print("Error: --ticker is required for market command", file=sys.stderr)
            sys.exit(1)
        
        result = agent.analyze_single_market(args.ticker)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_market_result(result)


def print_analysis_result(result: dict, strategy_name: str = "statistical_arbitrage", strategy_config: dict = None):
    """Print analysis result in human-readable format"""
    if result["status"] != "success":
        print(f"Status: {result['status']}")
        print(f"Message: {result.get('message', 'Unknown error')}")
        return
    
    print(f"Category: {result['category'].upper()}")
    print(f"Strategy: {strategy_name}")
    if strategy_config:
        print(f"Strategy Config: {strategy_config}")
    print(f"Sources: {', '.join(result['sources'])}")
    print(f"\nSummary:")
    summary = result["summary"]
    print(f"  Markets Analyzed: {summary['markets_analyzed']}")
    if summary.get('average_edge') is not None:
        print(f"  Average Edge: {summary['average_edge']:.2f}%")
    if summary.get('max_edge') is not None:
        print(f"  Max Edge: {summary['max_edge']:.2f}%")
    print(f"  Markets with >8% Edge: {summary['markets_with_edge_gt_8']}")
    if summary.get('average_confidence') is not None:
        print(f"  Average Confidence: {summary['average_confidence']:.2f}")
    
    print(f"\nMarkets:")
    for market in result["markets"]:
        print(f"  {market['ticker']}: {market['title'][:60]}")
        if market.get('edge_pct') is not None:
            print(f"    Edge: {market['edge_pct']:+.1f}% | Recommendation: {market['recommendation']}")
        print(f"    Sources: {market['source_breakdown']}")


def print_market_result(result: dict):
    """Print single market result in human-readable format"""
    if result["status"] != "success":
        print(f"Status: {result['status']}")
        print(f"Message: {result.get('message', 'Unknown error')}")
        return
    
    print(f"Ticker: {result['ticker']}")
    print(f"Title: {result['title']}")
    print(f"Category: {result['category'].upper()}")
    if result.get('combined_p') is not None:
        print(f"Combined Probability: {result['combined_p']:.3f}")
    if result.get('market_p') is not None:
        print(f"Market Probability: {result['market_p']:.3f}")
    if result.get('edge_pct') is not None:
        print(f"Edge: {result['edge_pct']:+.1f}%")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Confidence: {result.get('confidence', 'N/A')}")
    print(f"Sources: {result['source_breakdown']}")


if __name__ == "__main__":
    main()

