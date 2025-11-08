"""
Moving Average Strategy

Analyzes price trends using moving averages to identify mean reversion
and momentum opportunities.
"""

from typing import Dict, Any
from datetime import datetime

from strategies.base import Strategy, StrategyResult
from strategies.kalshi_data import (
    fetch_market_history,
    get_current_price,
    calculate_sma,
    calculate_ema,
    process_history_to_daily,
    get_price_series,
)


class MovingAverageStrategy(Strategy):
    """
    Moving Average Strategy
    
    Uses moving averages to identify:
    - Mean reversion: Price far from MA → expect reversal
    - Trend following: Price crossing MA → expect continuation
    - Momentum: Rate of change in price
    
    Configurable parameters:
    - ma_period: Moving average window (default: 7 days)
    - ma_type: 'sma' or 'ema' (default: 'sma')
    - signal_type: 'mean_reversion' or 'trend_following' (default: 'mean_reversion')
    - lookback_days: Days of history to fetch (default: 30)
    """
    
    def __init__(self, category: str, **config):
        super().__init__(category, **config)
        
        # Configuration with defaults
        self.ma_period = config.get('ma_period', 7)
        self.ma_type = config.get('ma_type', 'sma')  # 'sma' or 'ema'
        self.signal_type = config.get('signal_type', 'mean_reversion')  # or 'trend_following'
        self.lookback_days = config.get('lookback_days', 30)
    
    def get_name(self) -> str:
        return "moving_average"
    
    def get_description(self) -> str:
        return f"{self.ma_type.upper()}({self.ma_period}) {self.signal_type} strategy"
    
    def analyze(self, market: Dict[str, Any]) -> StrategyResult:
        """
        Analyze market using moving averages
        
        Args:
            market: Market dictionary with ticker, title, prices, etc.
        
        Returns:
            StrategyResult with p_quant, confidence, and MA signals
        """
        if not self.validate_market(market):
            raise ValueError("Invalid market data")
        
        ticker = market['ticker']
        
        # Fetch historical data
        history = fetch_market_history(ticker, days=self.lookback_days)
        
        if not history:
            # No historical data available
            return StrategyResult(
                p_quant=0.5,
                confidence=0.3,
                signals={
                    'error': 'No historical data available',
                    'ma_period': self.ma_period,
                    'signal_type': self.signal_type,
                },
                sources={},
                strategy_name=self.get_name(),
                timestamp=datetime.now().isoformat()
            )
        
        # Process to daily data
        daily_history = process_history_to_daily(history)
        
        if len(daily_history) < self.ma_period:
            return StrategyResult(
                p_quant=0.5,
                confidence=0.3,
                signals={
                    'error': f'Insufficient data: {len(daily_history)} days, need {self.ma_period}',
                    'days_available': len(daily_history),
                    'ma_period': self.ma_period,
                },
                sources={},
                strategy_name=self.get_name(),
                timestamp=datetime.now().isoformat()
            )
        
        # Get price series
        prices = get_price_series(daily_history, use_close=True)
        
        # Calculate moving average
        if self.ma_type == 'ema':
            ma_value = calculate_ema(prices, self.ma_period)
        else:
            ma_value = calculate_sma(prices, self.ma_period)
        
        if ma_value is None:
            return StrategyResult(
                p_quant=0.5,
                confidence=0.3,
                signals={'error': 'Could not calculate MA'},
                sources={},
                strategy_name=self.get_name(),
                timestamp=datetime.now().isoformat()
            )
        
        # Get current price
        current_price = get_current_price(market)
        
        # Calculate signals
        deviation = current_price - ma_value
        deviation_pct = (deviation / ma_value) * 100 if ma_value > 0 else 0
        
        # Calculate price volatility (standard deviation)
        if len(prices) >= self.ma_period:
            recent_prices = prices[-self.ma_period:]
            mean_price = sum(recent_prices) / len(recent_prices)
            variance = sum((p - mean_price) ** 2 for p in recent_prices) / len(recent_prices)
            std_dev = variance ** 0.5
        else:
            std_dev = 0.1  # Default
        
        # Generate probability based on signal type
        if self.signal_type == 'mean_reversion':
            p_quant = self._mean_reversion_signal(current_price, ma_value, std_dev)
        else:  # trend_following
            p_quant = self._trend_following_signal(current_price, ma_value, prices)
        
        # Calculate confidence based on:
        # 1. Amount of historical data
        # 2. Strength of signal
        # 3. Volatility (lower volatility = higher confidence)
        
        data_confidence = min(1.0, len(daily_history) / (self.ma_period * 3))
        signal_strength = min(1.0, abs(deviation) / (std_dev * 2)) if std_dev > 0 else 0.5
        volatility_factor = max(0.3, 1.0 - min(1.0, std_dev * 2))
        
        confidence = (data_confidence * 0.4 + signal_strength * 0.3 + volatility_factor * 0.3)
        confidence = max(0.3, min(0.85, confidence))
        
        # Build signals dictionary
        signals = {
            'ma_value': round(ma_value, 4),
            'current_price': round(current_price, 4),
            'deviation': round(deviation, 4),
            'deviation_pct': round(deviation_pct, 2),
            'std_dev': round(std_dev, 4),
            'days_of_data': len(daily_history),
            'ma_period': self.ma_period,
            'ma_type': self.ma_type,
            'signal_type': self.signal_type,
        }
        
        # Add trend info
        if len(prices) >= 3:
            recent_trend = prices[-1] - prices[-3]
            signals['recent_trend'] = 'up' if recent_trend > 0 else 'down'
            signals['trend_strength'] = round(abs(recent_trend), 4)
        
        return StrategyResult(
            p_quant=p_quant,
            confidence=confidence,
            signals=signals,
            sources={
                f'{self.ma_type.upper()}({self.ma_period})': ma_value,
                'Current Price': current_price,
            },
            strategy_name=self.get_name(),
            timestamp=datetime.now().isoformat()
        )
    
    def _mean_reversion_signal(self, current_price: float, ma_value: float, std_dev: float) -> float:
        """
        Generate probability for mean reversion strategy
        
        Logic:
        - If price >> MA: Expect price to drop → P(YES) lower
        - If price << MA: Expect price to rise → P(YES) higher
        - Use z-score to normalize deviation
        """
        if std_dev == 0:
            return 0.5
        
        # Calculate z-score (how many std devs away from MA)
        z_score = (current_price - ma_value) / std_dev
        
        # Convert z-score to probability adjustment
        # z > 0: price above MA → expect reversion down → lower P
        # z < 0: price below MA → expect reversion up → higher P
        
        # Use sigmoid-like function for smooth transition
        # Range: ~0.2 to ~0.8 for z-scores between -2 and +2
        adjustment = -z_score * 0.15  # Negative because we expect reversion
        
        p = 0.5 + adjustment
        
        # Clamp to reasonable range
        return max(0.2, min(0.8, p))
    
    def _trend_following_signal(self, current_price: float, ma_value: float, prices: list) -> float:
        """
        Generate probability for trend following strategy
        
        Logic:
        - If price > MA and rising: Expect continuation → P(YES) higher
        - If price < MA and falling: Expect continuation → P(YES) lower
        - Check for crossover events (price crossing MA)
        """
        # Check if price recently crossed MA
        if len(prices) >= 2:
            prev_price = prices[-2]
            
            # Bullish crossover: prev below MA, current above MA
            if prev_price < ma_value and current_price > ma_value:
                return 0.65  # Bullish signal
            
            # Bearish crossover: prev above MA, current below MA
            if prev_price > ma_value and current_price < ma_value:
                return 0.35  # Bearish signal
        
        # No crossover: use position relative to MA
        if current_price > ma_value:
            # Price above MA: bullish
            distance = (current_price - ma_value) / ma_value
            return 0.5 + min(0.25, distance * 2)  # Up to 0.75
        else:
            # Price below MA: bearish
            distance = (ma_value - current_price) / ma_value
            return 0.5 - min(0.25, distance * 2)  # Down to 0.25

