"""
Statistical Arbitrage Strategy

Compares multiple independent data sources to find mispricing.
Works by fetching data from external sources and comparing to market price.
"""

import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add parent directory to path to import test modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.base import Strategy, StrategyResult

# Import the existing analysis modules
try:
    import weather_test
    import politics_test
    import economics_test
except ImportError as e:
    print(f"Warning: Could not import test modules: {e}")
    weather_test = None
    politics_test = None
    economics_test = None


class StatisticalArbitrageStrategy(Strategy):
    """
    Statistical Arbitrage Strategy
    
    Uses multiple independent data sources to find mispricing:
    - Weather: NOAA, Open-Meteo, Climatology
    - Politics: Kalshi consensus, historical patterns, betting models
    - Economics: FRED, economic indicators, Kalshi consensus
    """
    
    def get_name(self) -> str:
        return "statistical_arbitrage"
    
    def get_description(self) -> str:
        return "Multi-source comparison to find statistical arbitrage opportunities"
    
    def analyze(self, market: Dict[str, Any]) -> StrategyResult:
        """
        Analyze market using statistical arbitrage
        
        Args:
            market: Market dictionary with ticker, title, prices, etc.
        
        Returns:
            StrategyResult with p_quant, confidence, and source breakdown
        """
        if not self.validate_market(market):
            raise ValueError("Invalid market data")
        
        # Route to appropriate category analyzer
        if self.category == "weather":
            return self._analyze_weather(market)
        elif self.category == "politics":
            return self._analyze_politics(market)
        elif self.category == "economics":
            return self._analyze_economics(market)
        else:
            raise ValueError(f"Unknown category: {self.category}")
    
    def _analyze_weather(self, market: Dict[str, Any]) -> StrategyResult:
        """Analyze weather market using existing weather_test logic"""
        if weather_test is None:
            raise ImportError("weather_test module not available")
        
        import pandas as pd
        
        # Create a single-row DataFrame (what the existing function expects)
        df = pd.DataFrame([market])
        
        # Use the existing enrich_with_weather_probs function
        try:
            df_enriched = weather_test.enrich_with_weather_probs(df)
            
            if df_enriched.empty or len(df_enriched) == 0:
                return StrategyResult(
                    p_quant=0.5,
                    confidence=0.3,
                    signals={'error': 'Analysis failed'},
                    sources={},
                    strategy_name=self.get_name(),
                    timestamp=datetime.now().isoformat()
                )
            
            row = df_enriched.iloc[0]
            
            # Extract results
            p_quant = row.get('combined_p', 0.5)
            confidence = row.get('conf', 0.5)
            
            # Build source breakdown (if available)
            sources = {}
            if 'noaa_p' in row and pd.notna(row['noaa_p']):
                sources['NOAA'] = row['noaa_p']
            if 'om_p' in row and pd.notna(row['om_p']):
                sources['Open-Meteo'] = row['om_p']
            if 'clim_p' in row and pd.notna(row['clim_p']):
                sources['Climatology'] = row['clim_p']
            
            # Build signals
            signals = {
                'num_sources': len(sources),
            }
            
            if 'lead_days' in row:
                signals['lead_days'] = row['lead_days']
            
            return StrategyResult(
                p_quant=p_quant,
                confidence=confidence,
                signals=signals,
                sources=sources,
                strategy_name=self.get_name(),
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            return StrategyResult(
                p_quant=0.5,
                confidence=0.3,
                signals={'error': str(e)},
                sources={},
                strategy_name=self.get_name(),
                timestamp=datetime.now().isoformat()
            )
    
    def _analyze_politics(self, market: Dict[str, Any]) -> StrategyResult:
        """Analyze politics market using existing politics_test logic"""
        if politics_test is None:
            raise ImportError("politics_test module not available")
        
        ticker = market['ticker']
        title = market.get('title', '')
        series = market.get('series', ticker.split('-')[0])
        
        # Parse market
        parsed = politics_test.parse_politics_market(ticker, title)
        
        # For politics, we need the full DataFrame to calculate consensus
        # This is a simplified version - in practice, we'd pass the full df
        sources = []
        
        # Source 1: Kalshi market consensus (simplified - would need full df)
        # Skip for now as it requires the full DataFrame
        
        # Source 2: Historical patterns
        try:
            hist = politics_test.fetch_historical_patterns(parsed)
            if hist:
                sources.append(hist)
        except Exception:
            pass
        
        # Source 3: Betting market model
        try:
            betting = politics_test.fetch_betting_model_prob(parsed)
            if betting:
                sources.append(betting)
        except Exception:
            pass
        
        if not sources:
            return StrategyResult(
                p_quant=0.5,
                confidence=0.3,
                signals={'error': 'No sources available'},
                sources={},
                strategy_name=self.get_name(),
                timestamp=datetime.now().isoformat()
            )
        
        # Combine sources
        result = politics_test.combine_sources(sources)
        
        # Build source breakdown
        source_probs = {}
        for src in sources:
            source_name = src.get('source', 'unknown')
            source_probs[source_name] = src.get('prob', 0.5)
        
        return StrategyResult(
            p_quant=result['prob'],
            confidence=result['confidence'],
            signals={
                'event_type': parsed.get('event_type', 'unknown'),
                'num_sources': len(sources),
            },
            sources=source_probs,
            strategy_name=self.get_name(),
            timestamp=datetime.now().isoformat()
        )
    
    def _analyze_economics(self, market: Dict[str, Any]) -> StrategyResult:
        """Analyze economics market using existing economics_test logic"""
        if economics_test is None:
            raise ImportError("economics_test module not available")
        
        ticker = market['ticker']
        title = market.get('title', '')
        series = market.get('series', ticker.split('-')[0])
        
        # Parse market
        parsed = economics_test.parse_economics_market(ticker, title)
        
        sources = []
        
        # Source 1: FRED
        try:
            fred = economics_test.fetch_fred_data(
                parsed.get('indicator_type'),
                parsed.get('target_date')
            )
            if fred:
                # Convert to probability using the market's threshold
                value = fred.get('forecast')
                if value is not None:
                    prob = economics_test.economic_value_to_probability(
                        value,
                        parsed.get('threshold'),
                        parsed.get('comparison', '>'),
                        parsed.get('indicator_type'),
                        fred.get('volatility', 0.02)
                    )
                    sources.append({
                        'source': 'FRED',
                        'prob': prob,
                        'confidence': 0.85,
                    })
        except Exception:
            pass
        
        # Source 2: Economic Indicators
        try:
            indicators = economics_test.fetch_economic_indicators(
                parsed.get('indicator_type'),
                parsed.get('target_date')
            )
            if indicators:
                value = indicators.get('current_value')
                if value is not None:
                    prob = economics_test.economic_value_to_probability(
                        value,
                        parsed.get('threshold'),
                        parsed.get('comparison', '>'),
                        parsed.get('indicator_type'),
                        indicators.get('volatility', 0.02)
                    )
                    sources.append({
                        'source': 'Economic Indicators',
                        'prob': prob,
                        'confidence': indicators.get('confidence', 0.70),
                    })
        except Exception:
            pass
        
        if not sources:
            return StrategyResult(
                p_quant=0.5,
                confidence=0.3,
                signals={'error': 'No sources available'},
                sources={},
                strategy_name=self.get_name(),
                timestamp=datetime.now().isoformat()
            )
        
        # Combine sources
        result = economics_test.combine_sources(sources)
        
        # Build source breakdown
        source_probs = {}
        for src in sources:
            source_name = src.get('source', 'unknown')
            source_probs[source_name] = src.get('prob', 0.5)
        
        return StrategyResult(
            p_quant=result['prob'],
            confidence=result['confidence'],
            signals={
                'indicator_type': parsed.get('indicator_type', 'unknown'),
                'threshold': parsed.get('threshold'),
                'comparison': parsed.get('comparison'),
                'num_sources': len(sources),
            },
            sources=source_probs,
            strategy_name=self.get_name(),
            timestamp=datetime.now().isoformat()
        )

