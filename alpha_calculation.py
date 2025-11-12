#!/usr/bin/env python3
"""
Alpha Calculation for Hybrid AI Betting Agent

Alpha = Excess return over market/benchmark
For prediction markets: Alpha = Expected Return - Market Return

This script calculates:
1. Expected Alpha (based on edge calculations)
2. Theoretical Alpha (if predictions are perfectly calibrated)
3. Required Win Rate for positive alpha
4. Risk-adjusted Alpha (Sharpe ratio equivalent)
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AlphaMetrics:
    """Alpha performance metrics"""
    expected_alpha: float  # Expected excess return (%)
    theoretical_alpha: float  # Alpha if perfectly calibrated
    required_win_rate: float  # Minimum win rate for positive alpha
    sharpe_equivalent: float  # Risk-adjusted alpha (Sharpe-like)
    kelly_fraction: float  # Optimal position size (Kelly Criterion)
    expected_return: float  # Expected return per bet (%)
    risk_free_rate: float  # Risk-free rate (assumed 0% for prediction markets)

class AlphaCalculator:
    """
    Calculate alpha for prediction market betting strategy
    
    Alpha = Expected Return - Benchmark Return
    For prediction markets, benchmark is typically 0% (break-even)
    """
    
    def __init__(self, risk_free_rate: float = 0.0):
        """
        Initialize alpha calculator
        
        Args:
            risk_free_rate: Risk-free rate (default: 0% for prediction markets)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_expected_return(self, edge: float, market_price: float, 
                                 prediction: float, bet_size: float = 1.0) -> float:
        """
        Calculate expected return for a single bet
        
        Args:
            edge: Edge in probability (prediction - market_price)
            market_price: Market-implied probability (0-1)
            prediction: Model prediction (0-1)
            bet_size: Size of bet (default: 1.0 = 100%)
        
        Returns:
            Expected return as decimal (e.g., 0.15 = 15%)
        """
        # If betting YES at market_price:
        # - Win: Get (1 - market_price) / market_price return
        # - Lose: Lose bet_size
        
        # Expected value = P(win) × Win_Return - P(lose) × Loss
        # P(win) = prediction (our model's probability)
        # P(lose) = 1 - prediction
        
        if edge > 0:  # BUY YES
            # Win return: (1 - market_price) / market_price
            win_return = (1.0 - market_price) / market_price if market_price > 0 else 0
            expected_return = (prediction * win_return) - ((1 - prediction) * bet_size)
        
        else:  # BUY NO (edge < 0)
            # Win return: market_price / (1 - market_price)
            win_return = market_price / (1.0 - market_price) if market_price < 1.0 else 0
            expected_return = ((1 - prediction) * win_return) - (prediction * bet_size)
        
        return expected_return
    
    def calculate_alpha(self, edge: float, market_price: float, 
                       prediction: float, market_return: float = 0.0) -> float:
        """
        Calculate alpha (excess return over market)
        
        Args:
            edge: Edge in probability
            market_price: Market-implied probability
            prediction: Model prediction
            market_return: Market benchmark return (default: 0% = break-even)
        
        Returns:
            Alpha as decimal (e.g., 0.10 = 10% alpha)
        """
        expected_return = self.calculate_expected_return(edge, market_price, prediction)
        alpha = expected_return - market_return - self.risk_free_rate
        return alpha
    
    def calculate_required_win_rate(self, edge: float, market_price: float) -> float:
        """
        Calculate minimum win rate required for positive alpha
        
        Args:
            edge: Edge in probability
            market_price: Market-implied probability
        
        Returns:
            Required win rate (0-1)
        """
        if edge > 0:  # BUY YES
            # Break-even: win_rate × (1-market_price)/market_price = (1-win_rate) × 1
            # Solving: win_rate = market_price
            # But we need positive alpha, so: win_rate > market_price
            # With edge, we predict: win_rate = market_price + edge
            required_win_rate = market_price + abs(edge) * 0.5  # Conservative estimate
        else:  # BUY NO
            # Break-even: win_rate × market_price/(1-market_price) = (1-win_rate) × 1
            # Solving: win_rate = 1 - market_price
            # With edge, we predict: win_rate = 1 - market_price + abs(edge) * 0.5
            required_win_rate = 1 - market_price + abs(edge) * 0.5
        
        return min(1.0, max(0.0, required_win_rate))
    
    def calculate_sharpe_equivalent(self, expected_alpha: float, 
                                   edge_std: float, num_bets: int = 100) -> float:
        """
        Calculate Sharpe ratio equivalent for prediction markets
        
        Sharpe = (Return - RiskFree) / StdDev
        For prediction markets: Sharpe = Alpha / StdDev
        
        Args:
            expected_alpha: Expected alpha per bet
            edge_std: Standard deviation of edges
            num_bets: Number of bets (for scaling)
        
        Returns:
            Sharpe ratio equivalent
        """
        if edge_std == 0:
            return 0.0
        
        # Annualized Sharpe (assuming daily bets)
        annual_alpha = expected_alpha * np.sqrt(365)  # Annualize
        annual_std = edge_std * np.sqrt(365)
        
        sharpe = annual_alpha / annual_std if annual_std > 0 else 0.0
        return sharpe
    
    def calculate_kelly_fraction(self, edge: float, market_price: float, 
                                prediction: float) -> float:
        """
        Calculate optimal position size using Kelly Criterion
        
        Kelly = (p × b - q) / b
        Where:
        - p = probability of winning
        - q = probability of losing (1-p)
        - b = odds (win return)
        
        Args:
            edge: Edge in probability
            market_price: Market-implied probability
            prediction: Model prediction
        
        Returns:
            Kelly fraction (0-1, recommended to use fraction of this)
        """
        if edge > 0:  # BUY YES
            p = prediction
            q = 1 - prediction
            b = (1.0 - market_price) / market_price if market_price > 0 else 0
        else:  # BUY NO
            p = 1 - prediction
            q = prediction
            b = market_price / (1.0 - market_price) if market_price < 1.0 else 0
        
        if b == 0:
            return 0.0
        
        kelly = (p * b - q) / b
        # Cap at reasonable bounds (0-1, but typically use 25-50% of Kelly)
        return max(0.0, min(1.0, kelly))
    
    def calculate_alpha_metrics(self, edge: float, market_price: float, 
                               prediction: float, edge_std: float = 0.10) -> AlphaMetrics:
        """
        Calculate comprehensive alpha metrics
        
        Args:
            edge: Edge in probability
            market_price: Market-implied probability
            prediction: Model prediction
            edge_std: Standard deviation of edges (for Sharpe calculation)
        
        Returns:
            AlphaMetrics with all calculated metrics
        """
        # Expected return
        expected_return = self.calculate_expected_return(edge, market_price, prediction)
        
        # Alpha
        expected_alpha = self.calculate_alpha(edge, market_price, prediction)
        
        # Theoretical alpha (if prediction is perfectly calibrated)
        # This assumes our prediction is correct
        theoretical_alpha = expected_alpha  # Same calculation, but assumes perfect calibration
        
        # Required win rate
        required_win_rate = self.calculate_required_win_rate(edge, market_price)
        
        # Sharpe equivalent
        sharpe_equivalent = self.calculate_sharpe_equivalent(expected_alpha, edge_std)
        
        # Kelly fraction
        kelly_fraction = self.calculate_kelly_fraction(edge, market_price, prediction)
        
        return AlphaMetrics(
            expected_alpha=expected_alpha,
            theoretical_alpha=theoretical_alpha,
            required_win_rate=required_win_rate,
            sharpe_equivalent=sharpe_equivalent,
            kelly_fraction=kelly_fraction,
            expected_return=expected_return,
            risk_free_rate=self.risk_free_rate
        )


def calculate_portfolio_alpha(edges: List[float], market_prices: List[float],
                             predictions: List[float], bet_sizes: List[float] = None) -> Dict:
    """
    Calculate portfolio-level alpha metrics
    
    Args:
        edges: List of edges for each bet
        market_prices: List of market prices for each bet
        predictions: List of predictions for each bet
        bet_sizes: List of bet sizes (default: equal weighting)
    
    Returns:
        Dictionary with portfolio alpha metrics
    """
    if bet_sizes is None:
        bet_sizes = [1.0] * len(edges)
    
    calculator = AlphaCalculator()
    
    # Calculate individual alphas
    alphas = []
    returns = []
    kelly_fractions = []
    
    for edge, market_price, prediction, bet_size in zip(edges, market_prices, predictions, bet_sizes):
        metrics = calculator.calculate_alpha_metrics(edge, market_price, prediction)
        alphas.append(metrics.expected_alpha * bet_size)
        returns.append(metrics.expected_return * bet_size)
        kelly_fractions.append(metrics.kelly_fraction)
    
    # Portfolio metrics
    portfolio_alpha = np.mean(alphas)
    portfolio_return = np.mean(returns)
    alpha_std = np.std(alphas)
    
    # Sharpe equivalent
    sharpe = calculator.calculate_sharpe_equivalent(portfolio_alpha, alpha_std, len(edges))
    
    # Average Kelly fraction
    avg_kelly = np.mean(kelly_fractions)
    
    return {
        'portfolio_alpha': portfolio_alpha,
        'portfolio_return': portfolio_return,
        'alpha_std': alpha_std,
        'sharpe_equivalent': sharpe,
        'avg_kelly_fraction': avg_kelly,
        'num_bets': len(edges),
        'avg_edge': np.mean(edges),
        'edge_std': np.std(edges),
    }


if __name__ == "__main__":
    calculator = AlphaCalculator()
    
    print("=" * 80)
    print("ALPHA CALCULATION FOR HYBRID AI BETTING AGENT")
    print("=" * 80)
    print()
    
    # Example 1: High-edge weather bet
    print("Example 1: High-Edge Weather Bet")
    print("-" * 80)
    edge1 = 0.25  # 25% edge
    market_price1 = 0.50  # Market prices at 50%
    prediction1 = 0.75  # We predict 75%
    
    metrics1 = calculator.calculate_alpha_metrics(edge1, market_price1, prediction1)
    print(f"Edge: {edge1:.1%}")
    print(f"Market Price: {market_price1:.1%}")
    print(f"Prediction: {prediction1:.1%}")
    print()
    print(f"Expected Alpha: {metrics1.expected_alpha:.2%}")
    print(f"Expected Return: {metrics1.expected_return:.2%}")
    print(f"Required Win Rate: {metrics1.required_win_rate:.1%}")
    print(f"Kelly Fraction: {metrics1.kelly_fraction:.1%} (use 25-50% of this)")
    print(f"Sharpe Equivalent: {metrics1.sharpe_equivalent:.2f}")
    print()
    
    # Example 2: Medium-edge politics bet
    print("Example 2: Medium-Edge Politics Bet")
    print("-" * 80)
    edge2 = 0.15  # 15% edge
    market_price2 = 0.60  # Market prices at 60%
    prediction2 = 0.75  # We predict 75%
    
    metrics2 = calculator.calculate_alpha_metrics(edge2, market_price2, prediction2)
    print(f"Edge: {edge2:.1%}")
    print(f"Market Price: {market_price2:.1%}")
    print(f"Prediction: {prediction2:.1%}")
    print()
    print(f"Expected Alpha: {metrics2.expected_alpha:.2%}")
    print(f"Expected Return: {metrics2.expected_return:.2%}")
    print(f"Required Win Rate: {metrics2.required_win_rate:.1%}")
    print(f"Kelly Fraction: {metrics2.kelly_fraction:.1%} (use 25-50% of this)")
    print(f"Sharpe Equivalent: {metrics2.sharpe_equivalent:.2f}")
    print()
    
    # Example 3: Low-edge economics bet
    print("Example 3: Low-Edge Economics Bet")
    print("-" * 80)
    edge3 = 0.10  # 10% edge (minimum threshold)
    market_price3 = 0.40  # Market prices at 40%
    prediction3 = 0.50  # We predict 50%
    
    metrics3 = calculator.calculate_alpha_metrics(edge3, market_price3, prediction3)
    print(f"Edge: {edge3:.1%}")
    print(f"Market Price: {market_price3:.1%}")
    print(f"Prediction: {prediction3:.1%}")
    print()
    print(f"Expected Alpha: {metrics3.expected_alpha:.2%}")
    print(f"Expected Return: {metrics3.expected_return:.2%}")
    print(f"Required Win Rate: {metrics3.required_win_rate:.1%}")
    print(f"Kelly Fraction: {metrics3.kelly_fraction:.1%} (use 25-50% of this)")
    print(f"Sharpe Equivalent: {metrics3.sharpe_equivalent:.2f}")
    print()
    
    # Portfolio analysis
    print("=" * 80)
    print("PORTFOLIO ALPHA ANALYSIS")
    print("=" * 80)
    print()
    
    # Simulate portfolio of 20 bets with varying edges
    edges_portfolio = [0.25, 0.20, 0.18, 0.15, 0.15, 0.12, 0.12, 0.10, 0.10, 0.10,
                      0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]
    market_prices_portfolio = [0.50, 0.45, 0.55, 0.60, 0.40, 0.50, 0.50, 0.50, 0.50, 0.50,
                               0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50]
    predictions_portfolio = [mp + edge for mp, edge in zip(market_prices_portfolio, edges_portfolio)]
    
    portfolio_metrics = calculate_portfolio_alpha(
        edges_portfolio, market_prices_portfolio, predictions_portfolio
    )
    
    print(f"Portfolio Alpha: {portfolio_metrics['portfolio_alpha']:.2%}")
    print(f"Portfolio Return: {portfolio_metrics['portfolio_return']:.2%}")
    print(f"Alpha Std Dev: {portfolio_metrics['alpha_std']:.2%}")
    print(f"Sharpe Equivalent: {portfolio_metrics['sharpe_equivalent']:.2f}")
    print(f"Average Kelly Fraction: {portfolio_metrics['avg_kelly_fraction']:.1%}")
    print(f"Number of Bets: {portfolio_metrics['num_bets']}")
    print(f"Average Edge: {portfolio_metrics['avg_edge']:.1%}")
    print(f"Edge Std Dev: {portfolio_metrics['edge_std']:.1%}")
    print()
    
    # Interpretation
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()
    print("Alpha > 0%: Strategy generates excess returns")
    print("Alpha < 0%: Strategy underperforms market")
    print()
    print("Sharpe Equivalent:")
    print("  > 1.0: Good risk-adjusted returns")
    print("  > 2.0: Excellent risk-adjusted returns")
    print("  > 3.0: Outstanding risk-adjusted returns")
    print()
    print("Kelly Fraction:")
    print("  Use 25-50% of Kelly for conservative position sizing")
    print("  Full Kelly is optimal but risky (high variance)")
    print()
    print("Required Win Rate:")
    print("  Minimum win rate needed for positive alpha")
    print("  If actual win rate > required → positive alpha")
    print("  If actual win rate < required → negative alpha")
    print()

