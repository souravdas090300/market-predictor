"""Strategy optimization and backtesting module."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class StrategyType(Enum):
    """Types of trading strategies."""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    TREND_FOLLOWING = "trend_following"
    GRID_TRADING = "grid_trading"


@dataclass
class StrategyResult:
    """Result of strategy optimization."""
    strategy_name: str
    parameters: Dict
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    average_win: float
    average_loss: float


class StrategyOptimizer:
    """Optimize trading strategies based on historical data."""
    
    def __init__(self, data: pd.DataFrame, initial_capital: float = 100000):
        """
        Initialize strategy optimizer.
        
        Args:
            data: Historical price data with OHLC
            initial_capital: Starting capital for backtesting
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
    
    def calculate_returns(self, price_column: str = 'close') -> pd.Series:
        """Calculate daily returns."""
        return self.data[price_column].pct_change().dropna()
    
    def optimize_momentum_strategy(
        self,
        lookback_range: Tuple[int, int] = (5, 20),
        holding_period_range: Tuple[int, int] = (1, 10)
    ) -> StrategyResult:
        """
        Optimize momentum strategy parameters.
        
        Args:
            lookback_range: Range of lookback periods to test
            holding_period_range: Range of holding periods to test
        
        Returns:
            StrategyResult with optimal parameters
        """
        best_result = None
        best_sharpe = -float('inf')
        
        returns = self.calculate_returns()
        
        for lookback in range(lookback_range[0], lookback_range[1] + 1):
            for holding in range(holding_period_range[0], holding_period_range[1] + 1):
                # Generate signals
                signals = self._generate_momentum_signals(returns, lookback)
                
                # Backtest
                result = self._backtest_strategy(signals, holding)
                
                if result['sharpe_ratio'] > best_sharpe:
                    best_sharpe = result['sharpe_ratio']
                    best_result = StrategyResult(
                        strategy_name="Momentum",
                        parameters={
                            'lookback_period': lookback,
                            'holding_period': holding
                        },
                        total_return=result['total_return'],
                        annualized_return=result['annualized_return'],
                        sharpe_ratio=result['sharpe_ratio'],
                        max_drawdown=result['max_drawdown'],
                        win_rate=result['win_rate'],
                        profit_factor=result['profit_factor'],
                        total_trades=result['total_trades'],
                        winning_trades=result['winning_trades'],
                        average_win=result['average_win'],
                        average_loss=result['average_loss']
                    )
        
        return best_result
    
    def optimize_mean_reversion_strategy(
        self,
        lookback_range: Tuple[int, int] = (10, 30),
        std_threshold_range: Tuple[float, float] = (1.5, 3.0)
    ) -> StrategyResult:
        """
        Optimize mean reversion strategy parameters.
        
        Args:
            lookback_range: Range of lookback periods
            std_threshold_range: Range of standard deviation thresholds
        
        Returns:
            StrategyResult with optimal parameters
        """
        best_result = None
        best_sharpe = -float('inf')
        
        returns = self.calculate_returns()
        
        for lookback in range(lookback_range[0], lookback_range[1] + 1):
            for std_threshold in np.arange(std_threshold_range[0], std_threshold_range[1] + 0.5, 0.5):
                # Generate signals
                signals = self._generate_mean_reversion_signals(returns, lookback, std_threshold)
                
                # Backtest with fixed holding period
                result = self._backtest_strategy(signals, 5)
                
                if result['sharpe_ratio'] > best_sharpe:
                    best_sharpe = result['sharpe_ratio']
                    best_result = StrategyResult(
                        strategy_name="Mean Reversion",
                        parameters={
                            'lookback_period': lookback,
                            'std_threshold': std_threshold
                        },
                        total_return=result['total_return'],
                        annualized_return=result['annualized_return'],
                        sharpe_ratio=result['sharpe_ratio'],
                        max_drawdown=result['max_drawdown'],
                        win_rate=result['win_rate'],
                        profit_factor=result['profit_factor'],
                        total_trades=result['total_trades'],
                        winning_trades=result['winning_trades'],
                        average_win=result['average_win'],
                        average_loss=result['average_loss']
                    )
        
        return best_result
    
    def _generate_momentum_signals(self, returns: pd.Series, lookback: int) -> pd.Series:
        """Generate momentum signals based on lookback period."""
        momentum = returns.rolling(window=lookback).mean()
        signals = (momentum > 0).astype(int)
        return signals
    
    def _generate_mean_reversion_signals(
        self,
        returns: pd.Series,
        lookback: int,
        std_threshold: float
    ) -> pd.Series:
        """Generate mean reversion signals."""
        mean = returns.rolling(window=lookback).mean()
        std = returns.rolling(window=lookback).std()
        z_score = (returns - mean) / std
        
        # Buy when price is below mean by threshold
        signals = (z_score < -std_threshold).astype(int)
        return signals
    
    def _backtest_strategy(
        self,
        signals: pd.Series,
        holding_period: int
    ) -> Dict:
        """
        Backtest a trading strategy.
        
        Args:
            signals: Series of buy/sell signals (1=buy, 0=sell/hold)
            holding_period: Number of periods to hold position
        
        Returns:
            Dictionary with backtest results
        """
        capital = self.initial_capital
        position = 0
        trades = []
        equity_curve = [capital]
        
        for i in range(len(signals)):
            if signals.iloc[i] == 1 and position == 0:
                # Buy signal
                position = capital / self.data['close'].iloc[i]
                entry_price = self.data['close'].iloc[i]
                entry_idx = i
                
            elif position > 0 and (i - entry_idx) >= holding_period:
                # Sell after holding period
                exit_price = self.data['close'].iloc[i]
                profit = (exit_price - entry_price) * position
                capital = capital + profit
                
                trades.append(profit)
                position = 0
            
            equity_curve.append(capital)
        
        # Calculate metrics
        if len(trades) > 0:
            equity_series = pd.Series(equity_curve)
            returns = equity_series.pct_change().dropna()
            
            total_return = (capital - self.initial_capital) / self.initial_capital
            annualized_return = (1 + total_return) ** (252 / len(equity_curve)) - 1
            
            if len(returns) > 0:
                sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            else:
                sharpe_ratio = 0
            
            max_drawdown = (equity_series / equity_series.cummax() - 1).min()
            
            winning_trades = len([t for t in trades if t > 0])
            win_rate = winning_trades / len(trades)
            
            average_win = np.mean([t for t in trades if t > 0]) if winning_trades > 0 else 0
            average_loss = abs(np.mean([t for t in trades if t < 0])) if len(trades) - winning_trades > 0 else 0
            
            profit_factor = average_win / average_loss if average_loss > 0 else 0
        else:
            total_return = 0
            annualized_return = 0
            sharpe_ratio = 0
            max_drawdown = 0
            win_rate = 0
            profit_factor = 0
            winning_trades = 0
            average_win = 0
            average_loss = 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(trades),
            'winning_trades': winning_trades,
            'average_win': average_win,
            'average_loss': average_loss
        }
    
    def compare_strategies(self) -> Dict[str, StrategyResult]:
        """Compare multiple strategies and return the best."""
        results = {}
        
        # Test momentum
        momentum_result = self.optimize_momentum_strategy()
        if momentum_result:
            results['momentum'] = momentum_result
        
        # Test mean reversion
        mean_reversion_result = self.optimize_mean_reversion_strategy()
        if mean_reversion_result:
            results['mean_reversion'] = mean_reversion_result
        
        return results


def optimize_strategy_for_symbol(
    symbol: str,
    data: pd.DataFrame,
    strategy_type: str = "momentum"
) -> Dict:
    """
    Optimize a specific strategy for a symbol.
    
    Args:
        symbol: Asset symbol
        data: Historical price data
        strategy_type: Type of strategy to optimize
    
    Returns:
        Dictionary with optimization results
    """
    optimizer = StrategyOptimizer(data)
    
    if strategy_type == "momentum":
        result = optimizer.optimize_momentum_strategy()
    elif strategy_type == "mean_reversion":
        result = optimizer.optimize_mean_reversion_strategy()
    else:
        # Compare all strategies
        results = optimizer.compare_strategies()
        if results:
            # Return the best strategy
            best_strategy = max(results.items(), key=lambda x: x[1].sharpe_ratio)
            result = best_strategy[1]
        else:
            result = None
    
    return {
        'symbol': symbol,
        'strategy_type': strategy_type,
        'result': result,
        'recommendation': _generate_strategy_recommendation(result) if result else "No suitable strategy found"
    }


def _generate_strategy_recommendation(result: StrategyResult) -> str:
    """Generate strategy recommendation."""
    if result.sharpe_ratio > 2.0:
        return f"EXCELLENT: {result.strategy_name} strategy shows Sharpe ratio of {result.sharpe_ratio:.2f}. Consider implementing with recommended parameters."
    elif result.sharpe_ratio > 1.0:
        return f"GOOD: {result.strategy_name} strategy shows Sharpe ratio of {result.sharpe_ratio:.2f}. Viable for trading."
    elif result.sharpe_ratio > 0.5:
        return f"ACCEPTABLE: {result.strategy_name} strategy shows Sharpe ratio of {result.sharpe_ratio:.2f}. Consider with additional filters."
    else:
        return f"POOR: {result.strategy_name} strategy shows Sharpe ratio of {result.sharpe_ratio:.2f}. Not recommended without additional edge."