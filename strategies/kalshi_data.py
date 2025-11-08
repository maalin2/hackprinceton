"""
Kalshi Historical Data Fetcher

Utilities for fetching historical price and volume data from Kalshi API.
"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

KALSHI_API = "https://api.elections.kalshi.com/trade-api/v2"
USER_AGENT = {"User-Agent": "kalshi-strategy/0.1 (trading analysis)"}


def fetch_market_history(ticker: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch historical price data for a market
    
    Args:
        ticker: Market ticker
        days: Number of days of history to fetch
    
    Returns:
        List of historical data points with prices, volume, timestamp
    """
    # Try to fetch candlestick/OHLC data first
    try:
        url = f"{KALSHI_API}/markets/{ticker}/history"
        params = {
            "limit": days * 24,  # Hourly data
            "min_ts": int((datetime.now() - timedelta(days=days)).timestamp())
        }
        
        r = requests.get(url, headers=USER_AGENT, params=params, timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            if "history" in data:
                return data["history"]
    except Exception as e:
        print(f"  ⚠️  Could not fetch history from /history endpoint: {e}")
    
    # Fallback: Try trades endpoint
    try:
        url = f"{KALSHI_API}/markets/{ticker}/trades"
        params = {
            "limit": 1000,
            "min_ts": int((datetime.now() - timedelta(days=days)).timestamp())
        }
        
        r = requests.get(url, headers=USER_AGENT, params=params, timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            if "trades" in data:
                # Convert trades to price points
                history = []
                for trade in data["trades"]:
                    history.append({
                        "timestamp": trade.get("created_time"),
                        "price": trade.get("yes_price", trade.get("price", 50)) / 100.0,  # Convert to 0-1
                        "volume": trade.get("count", 1),
                    })
                return history
    except Exception as e:
        print(f"  ⚠️  Could not fetch trades: {e}")
    
    # If both fail, return empty list
    return []


def get_current_price(market: Dict[str, Any]) -> float:
    """
    Get current market price from market data
    
    Args:
        market: Market dictionary
    
    Returns:
        Current price (0-1)
    """
    # Try last_price first
    if "last_price" in market and market["last_price"] is not None:
        price = market["last_price"]
        if isinstance(price, (int, float)):
            return price / 100.0 if price > 1 else price
    
    # Fallback to mid price
    yes_bid = market.get("yes_bid", 0)
    yes_ask = market.get("yes_ask", 100)
    
    if yes_bid > 0 or yes_ask < 100:
        mid_price = (yes_bid + yes_ask) / 2
        return mid_price / 100.0 if mid_price > 1 else mid_price
    
    # Default
    return 0.5


def calculate_sma(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate Simple Moving Average
    
    Args:
        prices: List of prices (most recent last)
        period: Number of periods for MA
    
    Returns:
        SMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    return sum(prices[-period:]) / period


def calculate_ema(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate Exponential Moving Average
    
    Args:
        prices: List of prices (most recent last)
        period: Number of periods for MA
    
    Returns:
        EMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    # Start with SMA
    sma = sum(prices[:period]) / period
    multiplier = 2 / (period + 1)
    
    ema = sma
    for price in prices[period:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema


def process_history_to_daily(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert high-frequency history to daily data points
    
    Args:
        history: List of historical data points
    
    Returns:
        List of daily data points (OHLC + volume)
    """
    if not history:
        return []
    
    # Group by day
    daily_data = {}
    
    for point in history:
        timestamp = point.get("timestamp")
        if not timestamp:
            continue
        
        # Parse timestamp
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                dt = datetime.fromtimestamp(timestamp)
            
            day = dt.date()
            
            price = point.get("price", 0.5)
            if isinstance(price, (int, float)) and price > 1:
                price = price / 100.0
            
            volume = point.get("volume", 0)
            
            if day not in daily_data:
                daily_data[day] = {
                    "date": day,
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": volume,
                }
            else:
                daily_data[day]["high"] = max(daily_data[day]["high"], price)
                daily_data[day]["low"] = min(daily_data[day]["low"], price)
                daily_data[day]["close"] = price
                daily_data[day]["volume"] += volume
        
        except Exception:
            continue
    
    # Sort by date
    sorted_days = sorted(daily_data.keys())
    return [daily_data[day] for day in sorted_days]


def get_price_series(history: List[Dict[str, Any]], use_close: bool = True) -> List[float]:
    """
    Extract price series from history
    
    Args:
        history: Daily history data
        use_close: If True, use close prices. If False, use mid (high+low)/2
    
    Returns:
        List of prices
    """
    if not history:
        return []
    
    prices = []
    for day in history:
        if use_close:
            price = day.get("close", 0.5)
        else:
            high = day.get("high", 0.5)
            low = day.get("low", 0.5)
            price = (high + low) / 2
        
        prices.append(price)
    
    return prices

