#!/usr/bin/env python3
"""
Margin of Error Calculation for Hybrid AI Betting Agent

This script calculates a data-driven margin of error for the agent's predictions
based on:
1. Quantitative model uncertainties
2. Sentiment analysis uncertainties
3. Market data quality
4. Source reliability
5. Historical calibration data (if available)
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ErrorComponents:
    """Breakdown of error sources"""
    quant_model_error: float  # Error from quantitative models
    sentiment_error: float     # Error from Grok sentiment analysis
    market_data_error: float   # Error from market price estimation
    source_reliability_error: float  # Error from source quality
    combined_error: float      # Total margin of error

class MarginOfErrorCalculator:
    """
    Calculates margin of error for hybrid AI betting predictions
    
    Based on:
    - Weather: Normal distribution with sigma (3-5°F), model RMSE (2-4°F)
    - Politics: Market efficiency assumptions, polling error margins
    - Economics: Data revision errors, reporting lags
    - Grok: LLM uncertainty, no ground truth
    - Market: Bid-ask spread, liquidity
    """
    
    # Weather model uncertainties (based on forecast skill)
    WEATHER_ERRORS = {
        "1day": {"sigma": 3.0, "rmse": 2.5, "model_error": 0.08},  # ±8% for 1-day forecasts
        "2day": {"sigma": 4.0, "rmse": 3.0, "model_error": 0.12},  # ±12% for 2-day forecasts
        "3+day": {"sigma": 5.0, "rmse": 4.0, "model_error": 0.15},  # ±15% for 3+ day forecasts
    }
    
    # Politics model uncertainties (based on polling and market efficiency)
    POLITICS_ERRORS = {
        "polling_error": 0.05,      # Typical polling margin of error: ±5%
        "market_efficiency": 0.10,  # Markets are ~90% efficient: ±10% error
        "model_error": 0.12,        # Combined model error: ±12%
    }
    
    # Economics model uncertainties (based on data quality)
    ECONOMICS_ERRORS = {
        "data_revision": 0.08,      # Economic data gets revised: ±8%
        "reporting_lag": 0.10,      # Data is lagged: ±10%
        "model_error": 0.12,        # Combined model error: ±12%
    }
    
    # Grok sentiment uncertainties (based on LLM performance)
    GROK_ERRORS = {
        "llm_uncertainty": 0.15,    # LLMs have ~15% uncertainty
        "sentiment_error": 0.12,    # Sentiment analysis error: ±12%
        "sample_size_penalty": 0.05,  # Small sample penalty: ±5%
    }
    
    # Market data uncertainties
    MARKET_ERRORS = {
        "spread_error": 0.02,       # Bid-ask spread uncertainty: ±2%
        "liquidity_error": 0.03,    # Low liquidity penalty: ±3%
        "market_efficiency": 0.05,  # Market can be wrong: ±5%
    }
    
    def calculate_quant_error(self, category: str, lead_days: int = None, 
                            num_sources: int = 3, source_confidence: float = 0.8) -> float:
        """
        Calculate quantitative model error based on category and parameters
        
        Args:
            category: "Weather", "Politics", "Economics"
            lead_days: Days until event (for weather)
            num_sources: Number of sources used
            source_confidence: Average source confidence (0-1)
        
        Returns:
            Error margin (0-1)
        """
        if category == "Weather":
            # Weather error depends on lead time
            if lead_days is None:
                lead_days = 3  # Default to 3+ days (worst case)
            
            if lead_days <= 1:
                base_error = self.WEATHER_ERRORS["1day"]["model_error"]
            elif lead_days == 2:
                base_error = self.WEATHER_ERRORS["2day"]["model_error"]
            else:
                base_error = self.WEATHER_ERRORS["3+day"]["model_error"]
            
            # Multiple sources reduce error (but not linearly)
            # 3 sources → reduce error by ~20%, 2 sources → reduce by ~10%
            source_reduction = 1.0 - (min(num_sources - 1, 2) * 0.1)
            
            # Confidence adjustment: lower confidence = higher error
            confidence_factor = 1.0 + (1.0 - source_confidence) * 0.3
            
            quant_error = base_error * source_reduction * confidence_factor
            
        elif category == "Politics":
            base_error = self.POLITICS_ERRORS["model_error"]
            # Politics models are less reliable than weather
            source_reduction = 1.0 - (min(num_sources - 1, 2) * 0.08)
            confidence_factor = 1.0 + (1.0 - source_confidence) * 0.4
            quant_error = base_error * source_reduction * confidence_factor
            
        elif category == "Economics":
            base_error = self.ECONOMICS_ERRORS["model_error"]
            # Economics has data lags and revisions
            source_reduction = 1.0 - (min(num_sources - 1, 2) * 0.08)
            confidence_factor = 1.0 + (1.0 - source_confidence) * 0.4
            quant_error = base_error * source_reduction * confidence_factor
            
        else:
            # Unknown category: use conservative estimate
            quant_error = 0.15
        
        # Cap at reasonable bounds
        return min(0.25, max(0.05, quant_error))
    
    def calculate_sentiment_error(self, grok_available: bool = True, 
                                 grok_confidence: str = "medium",
                                 sample_size: int = 1) -> float:
        """
        Calculate Grok sentiment analysis error
        
        Args:
            grok_available: Whether Grok analysis succeeded
            grok_confidence: "high", "medium", "low"
            sample_size: Number of samples analyzed (usually 1 for Grok)
        
        Returns:
            Error margin (0-1)
        """
        if not grok_available:
            # If Grok failed, sentiment error is high (we don't use it)
            return 0.20  # 20% error when unavailable
        
        # Base LLM uncertainty
        base_error = self.GROK_ERRORS["llm_uncertainty"]
        
        # Confidence adjustment
        if grok_confidence == "high":
            confidence_factor = 0.8  # Reduce error by 20%
        elif grok_confidence == "medium":
            confidence_factor = 1.0  # No adjustment
        else:  # low
            confidence_factor = 1.3  # Increase error by 30%
        
        # Sample size penalty (Grok is single analysis, so small sample)
        sample_penalty = self.GROK_ERRORS["sample_size_penalty"]
        
        sentiment_error = base_error * confidence_factor + sample_penalty
        
        return min(0.30, max(0.10, sentiment_error))
    
    def calculate_market_error(self, spread: float = 4.0, volume: float = 1000) -> float:
        """
        Calculate market price estimation error
        
        Args:
            spread: Bid-ask spread in cents
            volume: 24h volume
        
        Returns:
            Error margin (0-1)
        """
        # Spread error: wider spread = more uncertainty
        spread_error = (spread / 100.0) * 0.5  # Convert to probability error
        
        # Liquidity error: low volume = less reliable price
        if volume < 100:
            liquidity_error = self.MARKET_ERRORS["liquidity_error"] * 2
        elif volume < 500:
            liquidity_error = self.MARKET_ERRORS["liquidity_error"]
        else:
            liquidity_error = self.MARKET_ERRORS["liquidity_error"] * 0.5
        
        # Market efficiency error (markets can be wrong)
        market_efficiency_error = self.MARKET_ERRORS["market_efficiency"]
        
        # Combined market error
        market_error = spread_error + liquidity_error + market_efficiency_error
        
        return min(0.15, max(0.02, market_error))
    
    def calculate_combined_error(self, quant_error: float, sentiment_error: float,
                               market_error: float, quant_weight: float = 0.75,
                               sentiment_weight: float = 0.25) -> float:
        """
        Combine errors using weighted propagation
        
        For weighted combination: error = sqrt(w1^2 * e1^2 + w2^2 * e2^2)
        Then add market error (which affects the final edge calculation)
        """
        # Weighted error propagation (assuming independent errors)
        combined_model_error = np.sqrt(
            (quant_weight ** 2) * (quant_error ** 2) +
            (sentiment_weight ** 2) * (sentiment_error ** 2)
        )
        
        # Market error is separate (affects edge, not model prediction)
        # Total error = model error + market error (additive, not multiplicative)
        total_error = combined_model_error + market_error * 0.5  # Market error is less impactful
        
        return min(0.30, max(0.08, total_error))
    
    def calculate_margin_of_error(self, category: str, quant_confidence: float = 0.8,
                                 grok_available: bool = True, grok_confidence: str = "medium",
                                 spread: float = 4.0, volume: float = 1000,
                                 lead_days: int = None, num_sources: int = 3,
                                 quant_weight: float = 0.75, sentiment_weight: float = 0.25) -> ErrorComponents:
        """
        Calculate comprehensive margin of error for a prediction
        
        Args:
            category: "Weather", "Politics", "Economics"
            quant_confidence: Quantitative model confidence (0-1)
            grok_available: Whether Grok analysis is available
            grok_confidence: Grok confidence level ("high", "medium", "low")
            spread: Bid-ask spread in cents
            volume: 24h trading volume
            lead_days: Days until event (for weather)
            num_sources: Number of quantitative sources
            quant_weight: Weight for quantitative signal (default: 0.75)
            sentiment_weight: Weight for sentiment signal (default: 0.25)
        
        Returns:
            ErrorComponents with breakdown of error sources
        """
        # Calculate individual error components
        quant_error = self.calculate_quant_error(
            category=category,
            lead_days=lead_days,
            num_sources=num_sources,
            source_confidence=quant_confidence
        )
        
        sentiment_error = self.calculate_sentiment_error(
            grok_available=grok_available,
            grok_confidence=grok_confidence,
            sample_size=1
        )
        
        market_error = self.calculate_market_error(
            spread=spread,
            volume=volume
        )
        
        # Source reliability error (based on number of sources and confidence)
        if num_sources < 3:
            source_reliability_error = 0.05 * (3 - num_sources)  # +5% per missing source
        else:
            source_reliability_error = 0.0
        
        # Combined error
        combined_error = self.calculate_combined_error(
            quant_error=quant_error,
            sentiment_error=sentiment_error,
            market_error=market_error,
            quant_weight=quant_weight,
            sentiment_weight=sentiment_weight
        )
        
        # Add source reliability error
        combined_error += source_reliability_error
        combined_error = min(0.35, combined_error)  # Cap at 35%
        
        return ErrorComponents(
            quant_model_error=quant_error,
            sentiment_error=sentiment_error,
            market_data_error=market_error,
            source_reliability_error=source_reliability_error,
            combined_error=combined_error
        )


def get_recommended_margin_of_error(category: str, confidence: float = 0.8,
                                   grok_available: bool = True) -> Dict[str, float]:
    """
    Get recommended margin of error for typical use cases
    
    Returns a simple recommendation based on category and confidence level
    """
    calculator = MarginOfErrorCalculator()
    
    # Default parameters
    if category == "Weather":
        lead_days = 2  # Typical 2-day forecast
        num_sources = 3
    elif category == "Politics":
        lead_days = None
        num_sources = 3
    elif category == "Economics":
        lead_days = None
        num_sources = 3
    else:
        lead_days = None
        num_sources = 2
    
    # Calculate error
    errors = calculator.calculate_margin_of_error(
        category=category,
        quant_confidence=confidence,
        grok_available=grok_available,
        grok_confidence="medium",
        spread=4.0,
        volume=1000,
        lead_days=lead_days,
        num_sources=num_sources
    )
    
    return {
        "recommended_margin": errors.combined_error,
        "quant_error": errors.quant_model_error,
        "sentiment_error": errors.sentiment_error,
        "market_error": errors.market_data_error,
        "total_error_range": f"±{errors.combined_error * 100:.1f}%",
        "interpretation": get_error_interpretation(errors.combined_error)
    }


def get_error_interpretation(error: float) -> str:
    """Interpret error margin in human-readable terms"""
    if error < 0.10:
        return "High precision - Model is highly confident"
    elif error < 0.15:
        return "Medium-high precision - Model is reasonably confident"
    elif error < 0.20:
        return "Medium precision - Model has moderate uncertainty"
    elif error < 0.25:
        return "Medium-low precision - Model has significant uncertainty"
    else:
        return "Low precision - Model has high uncertainty, use with caution"


if __name__ == "__main__":
    # Example calculations
    calculator = MarginOfErrorCalculator()
    
    print("=" * 80)
    print("MARGIN OF ERROR CALCULATION FOR HYBRID AI BETTING AGENT")
    print("=" * 80)
    print()
    
    # Example 1: Weather (1-day forecast, high confidence)
    print("Example 1: Weather Market (1-day forecast, high confidence)")
    print("-" * 80)
    errors1 = calculator.calculate_margin_of_error(
        category="Weather",
        quant_confidence=0.85,
        grok_available=True,
        grok_confidence="high",
        spread=2.0,
        volume=5000,
        lead_days=1,
        num_sources=3
    )
    print(f"Quantitative Model Error: ±{errors1.quant_model_error * 100:.1f}%")
    print(f"Sentiment Error: ±{errors1.sentiment_error * 100:.1f}%")
    print(f"Market Data Error: ±{errors1.market_data_error * 100:.1f}%")
    print(f"Source Reliability Error: ±{errors1.source_reliability_error * 100:.1f}%")
    print(f"Combined Margin of Error: ±{errors1.combined_error * 100:.1f}%")
    print(f"Interpretation: {get_error_interpretation(errors1.combined_error)}")
    print()
    
    # Example 2: Weather (3-day forecast, medium confidence)
    print("Example 2: Weather Market (3-day forecast, medium confidence)")
    print("-" * 80)
    errors2 = calculator.calculate_margin_of_error(
        category="Weather",
        quant_confidence=0.70,
        grok_available=True,
        grok_confidence="medium",
        spread=4.0,
        volume=1000,
        lead_days=3,
        num_sources=3
    )
    print(f"Quantitative Model Error: ±{errors2.quant_model_error * 100:.1f}%")
    print(f"Sentiment Error: ±{errors2.sentiment_error * 100:.1f}%")
    print(f"Market Data Error: ±{errors2.market_data_error * 100:.1f}%")
    print(f"Combined Margin of Error: ±{errors2.combined_error * 100:.1f}%")
    print(f"Interpretation: {get_error_interpretation(errors2.combined_error)}")
    print()
    
    # Example 3: Politics (high confidence)
    print("Example 3: Politics Market (high confidence)")
    print("-" * 80)
    errors3 = calculator.calculate_margin_of_error(
        category="Politics",
        quant_confidence=0.80,
        grok_available=True,
        grok_confidence="high",
        spread=3.0,
        volume=3000,
        num_sources=3
    )
    print(f"Quantitative Model Error: ±{errors3.quant_model_error * 100:.1f}%")
    print(f"Sentiment Error: ±{errors3.sentiment_error * 100:.1f}%")
    print(f"Market Data Error: ±{errors3.market_data_error * 100:.1f}%")
    print(f"Combined Margin of Error: ±{errors3.combined_error * 100:.1f}%")
    print(f"Interpretation: {get_error_interpretation(errors3.combined_error)}")
    print()
    
    # Example 4: Economics (medium confidence, Grok unavailable)
    print("Example 4: Economics Market (medium confidence, Grok unavailable)")
    print("-" * 80)
    errors4 = calculator.calculate_margin_of_error(
        category="Economics",
        quant_confidence=0.75,
        grok_available=False,
        grok_confidence="low",
        spread=5.0,
        volume=800,
        num_sources=3
    )
    print(f"Quantitative Model Error: ±{errors4.quant_model_error * 100:.1f}%")
    print(f"Sentiment Error: ±{errors4.sentiment_error * 100:.1f}%")
    print(f"Market Data Error: ±{errors4.market_data_error * 100:.1f}%")
    print(f"Combined Margin of Error: ±{errors4.combined_error * 100:.1f}%")
    print(f"Interpretation: {get_error_interpretation(errors4.combined_error)}")
    print()
    
    # Summary: Recommended margins
    print("=" * 80)
    print("RECOMMENDED MARGINS OF ERROR BY CATEGORY")
    print("=" * 80)
    print()
    
    for category in ["Weather", "Politics", "Economics"]:
        rec = get_recommended_margin_of_error(category, confidence=0.8, grok_available=True)
        print(f"{category}:")
        print(f"  Recommended Margin: {rec['total_error_range']}")
        print(f"  Breakdown: Quant ±{rec['quant_error']*100:.1f}%, Sentiment ±{rec['sentiment_error']*100:.1f}%, Market ±{rec['market_error']*100:.1f}%")
        print(f"  Interpretation: {rec['interpretation']}")
        print()

