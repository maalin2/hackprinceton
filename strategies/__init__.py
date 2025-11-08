"""
Strategy Module for Kalshi Market Analysis

Provides different technical analysis strategies:
- Statistical Arbitrage: Multi-source comparison
- Moving Average: Price trend analysis
- Momentum: Price momentum indicators
- Hybrid: Combination of strategies
"""

from .base import Strategy, StrategyResult
from .statistical_arbitrage import StatisticalArbitrageStrategy
from .moving_average import MovingAverageStrategy

__all__ = [
    'Strategy',
    'StrategyResult',
    'StatisticalArbitrageStrategy',
    'MovingAverageStrategy',
    'get_strategy',
]

def get_strategy(strategy_name: str, category: str, **kwargs):
    """
    Factory function to get strategy instance
    
    Args:
        strategy_name: Name of strategy ('statistical_arbitrage', 'moving_average')
        category: Market category ('weather', 'politics', 'economics')
        **kwargs: Additional configuration for the strategy
    
    Returns:
        Strategy instance
    """
    strategies = {
        'statistical_arbitrage': StatisticalArbitrageStrategy,
        'moving_average': MovingAverageStrategy,
    }
    
    if strategy_name not in strategies:
        raise ValueError(
            f"Unknown strategy: {strategy_name}. "
            f"Available: {', '.join(strategies.keys())}"
        )
    
    return strategies[strategy_name](category=category, **kwargs)

