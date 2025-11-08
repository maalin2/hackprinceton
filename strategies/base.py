"""
Base Strategy Class

Defines the interface that all strategies must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class StrategyResult:
    """Result from a strategy analysis"""
    
    # Core probability and confidence
    p_quant: float  # 0-1 probability
    confidence: float  # 0-1 confidence in the prediction
    
    # Strategy-specific data
    signals: Dict[str, Any]  # Strategy-specific signals/indicators
    sources: Dict[str, float]  # Source name -> probability (for multi-source)
    
    # Metadata
    strategy_name: str
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'p_quant': self.p_quant,
            'confidence': self.confidence,
            'signals': self.signals,
            'sources': self.sources,
            'strategy_name': self.strategy_name,
            'timestamp': self.timestamp,
        }


class Strategy(ABC):
    """Base class for all analysis strategies"""
    
    def __init__(self, category: str, **config):
        """
        Initialize strategy
        
        Args:
            category: Market category ('weather', 'politics', 'economics')
            **config: Strategy-specific configuration
        """
        self.category = category
        self.config = config
    
    @abstractmethod
    def analyze(self, market: Dict[str, Any]) -> StrategyResult:
        """
        Analyze a market and return probability + confidence
        
        Args:
            market: Market data (ticker, title, prices, etc.)
        
        Returns:
            StrategyResult with p_quant, confidence, and signals
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return strategy name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return strategy description"""
        pass
    
    def validate_market(self, market: Dict[str, Any]) -> bool:
        """
        Validate that market has required fields
        
        Args:
            market: Market data dictionary
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['ticker', 'title']
        return all(field in market for field in required_fields)

