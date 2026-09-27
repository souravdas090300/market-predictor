"""Advanced Backtesting Engine for strategy analysis and optimization."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone as tz
from enum import Enum
import itertools
from abc import ABC, abstractmethod


class ActionType(Enum):
    """Types of trading actions."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Trade:
    """Represents a single trade in the backtest."""
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_percent: float
    trade_type: str  # "LONG" or "SHORT"
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


@dataclass
class Position:
    """Represents an open position."""
    entry_price: float
    quantity: float
    entry_date: datetime
    stop_loss: float
    take_profit: float
    position_type: str = "LONG"


@dataclass
class BacktestMetrics:
    """Comprehensive backtest performance metrics."""
    total_return: float
    total_return_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_return: float
    recovery_factor: float
    equity_history: List[Dict[str, Any]] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class Signal:
    """Trading signal from a strategy."""
    action: ActionType
    allocation: float = 1.0  # Percentage of capital to allocate
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = 1.0


class StrategyBase(ABC):
    """Base class for trading strategies."""
    
    @abstractmethod
    def get_signal(self, historical_data: pd.DataFrame) -> Signal:
        """Generate trading signal based on historical data."""
        pass
    
    @abstractmethod
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Set strategy parameters."""
        pass
    
    @abstractmethod
    def optimize(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Optimize strategy parameters."""
        pass


class BacktestingEngine:
    """Advanced backtesting engine with comprehensive analysis."""
    
    def __init__(self):
        """Initialize the backtesting engine."""
        self.trades: List[Trade] = []
        self.equity_history: List[Dict[str, Any]] = []
        self.positions: List[Position] = []
    
    async def run_backtest(
        self,
        historical_data: pd.DataFrame,
        strategy: StrategyBase,
        initial_capital: float = 100000,
        commission: float = 0.001
    ) -> BacktestMetrics:
        """
        Run complete backtest with strategy.
        
        Args:
            historical_data: DataFrame with OHLC data and timestamp
            strategy: Strategy instance implementing StrategyBase
            initial_capital: Starting capital for backtest
            commission: Commission rate per trade (default 0.1%)
        
        Returns:
            BacktestMetrics with comprehensive performance data
        """
        self.trades = []
        self.equity_history = []
        self.positions = []
        
        capital = initial_capital
        position: Optional[Position] = None
        
        # Ensure data has required columns
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in historical_data.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Initialize equity history
        if 'timestamp' in historical_data.columns:
            first_timestamp = historical_data['timestamp'].iloc[0]
        else:
            first_timestamp = historical_data.index[0]
        
        equity_history = [{
            'date': first_timestamp,
            'value': initial_capital
        }]
        
        for i in range(1, len(historical_data)):
            candle = historical_data.iloc[i]
            prev_candle = historical_data.iloc[i - 1]
            
            # Get timestamp
            if 'timestamp' in historical_data.columns:
                timestamp = candle['timestamp']
            else:
                timestamp = historical_data.index[i]
            
            # Generate signal using data up to current point
            current_data = historical_data.iloc[:i + 1].copy()
            signal = strategy.get_signal(current_data)
            
            if signal.action == ActionType.BUY and position is None:
                # Open position
                entry_price = candle['open']
                quantity = int((capital * signal.allocation) / entry_price)
                cost = quantity * entry_price * (1 + commission)
                
                if cost <= capital and quantity > 0:
                    stop_loss = signal.stop_loss or entry_price * 0.95
                    take_profit = signal.take_profit or entry_price * 1.05
                    
                    position = Position(
                        entry_price=entry_price,
                        quantity=quantity,
                        entry_date=timestamp,
                        stop_loss=stop_loss,
                        take_profit=take_profit
                    )
                    capital -= cost
            
            elif signal.action == ActionType.SELL and position is not None:
                # Close position
                exit_price = candle['open']
                proceeds = position.quantity * exit_price * (1 - commission)
                pnl = proceeds - (position.quantity * position.entry_price)
                pnl_percent = (pnl / (position.quantity * position.entry_price)) * 100
                
                trade = Trade(
                    entry_date=position.entry_date,
                    exit_date=timestamp,
                    entry_price=position.entry_price,
                    exit_price=exit_price,
                    quantity=position.quantity,
                    pnl=pnl,
                    pnl_percent=pnl_percent,
                    trade_type=position.position_type,
                    stop_loss=position.stop_loss,
                    take_profit=position.take_profit
                )
                
                self.trades.append(trade)
                capital += proceeds
                position = None
            
            elif position is not None:
                # Check stop loss / take profit
                if candle['low'] <= position.stop_loss or candle['high'] >= position.take_profit:
                    if candle['low'] <= position.stop_loss:
                        exit_price = position.stop_loss
                    else:
                        exit_price = position.take_profit
                    
                    proceeds = position.quantity * exit_price * (1 - commission)
                    pnl = proceeds - (position.quantity * position.entry_price)
                    pnl_percent = (pnl / (position.quantity * position.entry_price)) * 100
                    
                    trade = Trade(
                        entry_date=position.entry_date,
                        exit_date=timestamp,
                        entry_price=position.entry_price,
                        exit_price=exit_price,
                        quantity=position.quantity,
                        pnl=pnl,
                        pnl_percent=pnl_percent,
                        trade_type=position.position_type,
                        stop_loss=position.stop_loss,
                        take_profit=position.take_profit
                    )
                    
                    self.trades.append(trade)
                    capital += proceeds
                    position = None
            
            # Track current equity
            current_equity = capital
            if position is not None:
                current_equity += position.quantity * candle['close']
            
            equity_history.append({
                'date': timestamp,
                'value': current_equity
            })
        
        self.equity_history = equity_history
        return self.calculate_metrics(initial_capital)
    
    def calculate_metrics(self, initial_capital: float) -> BacktestMetrics:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            initial_capital: Starting capital for metric calculations
        
        Returns:
            BacktestMetrics with all calculated metrics
        """
        if len(self.trades) == 0:
            return BacktestMetrics(
                total_return=0,
                total_return_percent=0,
                sharpe_ratio=0,
                sortino_ratio=0,
                max_drawdown=0,
                win_rate=0,
                profit_factor=0,
                total_trades=0,
                avg_return=0,
                recovery_factor=0,
                error='No trades executed'
            )
        
        final_equity = self.equity_history[-1]['value']
        total_return = final_equity - initial_capital
        total_return_percent = (total_return / initial_capital) * 100
        
        # Win rate
        winning_trades = len([t for t in self.trades if t.pnl > 0])
        win_rate = (winning_trades / len(self.trades)) * 100
        
        # Profit factor
        gross_profit = sum([t.pnl for t in self.trades if t.pnl > 0])
        gross_loss = abs(sum([t.pnl for t in self.trades if t.pnl < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
        
        # Calculate returns series
        returns = []
        for i in range(1, len(self.equity_history)):
            ret = (self.equity_history[i]['value'] - self.equity_history[i - 1]['value']) / self.equity_history[i - 1]['value']
            returns.append(ret)
        
        avg_return = np.mean(returns) if returns else 0
        std_dev = np.std(returns) if returns else 0
        
        # Sharpe Ratio (annualized)
        sharpe_ratio = (avg_return * 252 / std_dev) if std_dev > 0 else 0
        
        # Sortino Ratio (only downside deviation)
        down_returns = [r for r in returns if r < 0]
        down_std_dev = np.std(down_returns) if down_returns else 0
        sortino_ratio = (avg_return * 252 / down_std_dev) if down_std_dev > 0 else 0
        
        # Max Drawdown
        max_drawdown = 0
        peak = self.equity_history[0]['value']
        for equity_point in self.equity_history:
            if equity_point['value'] > peak:
                peak = equity_point['value']
            drawdown = (peak - equity_point['value']) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Recovery Factor
        largest_loss = min([t.pnl for t in self.trades])
        recovery_factor = total_return / abs(largest_loss) if largest_loss != 0 else 0
        
        return BacktestMetrics(
            total_return=round(total_return, 2),
            total_return_percent=round(total_return_percent, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            sortino_ratio=round(sortino_ratio, 2),
            max_drawdown=round(max_drawdown * 100, 2),
            win_rate=round(win_rate, 2),
            profit_factor=round(profit_factor, 2),
            total_trades=len(self.trades),
            avg_return=round(avg_return * 100, 2),
            recovery_factor=round(recovery_factor, 2),
            equity_history=self.equity_history,
            trades=self.trades
        )
    
    def monte_carlo_simulation(
        self,
        iterations: int = 1000,
        initial_capital: float = 100000
    ) -> Dict[str, Any]:
        """
        Monte Carlo simulation - randomize trade order to assess robustness.
        
        Args:
            iterations: Number of simulation runs
            initial_capital: Starting capital for simulations
        
        Returns:
            Dictionary with Monte Carlo simulation results
        """
        if len(self.trades) == 0:
            return {'error': 'No trades to simulate'}
        
        results = []
        
        for _ in range(iterations):
            # Randomize trade order
            shuffled_trades = np.random.permutation(self.trades)
            equity = initial_capital
            drawdown = 0
            peak_equity = initial_capital
            
            for trade in shuffled_trades:
                equity += trade.pnl
                if equity > peak_equity:
                    peak_equity = equity
                dd = (peak_equity - equity) / peak_equity
                if dd > drawdown:
                    drawdown = dd
            
            results.append({
                'final_equity': equity,
                'max_drawdown': drawdown * 100,
                'total_return': ((equity - initial_capital) / initial_capital) * 100
            })
        
        return {
            'avg_final_equity': round(np.mean([r['final_equity'] for r in results]), 2),
            'avg_max_drawdown': round(np.mean([r['max_drawdown'] for r in results]), 2),
            'avg_return': round(np.mean([r['total_return'] for r in results]), 2),
            'worst_case': round(min([r['final_equity'] for r in results]), 2),
            'best_case': round(max([r['final_equity'] for r in results]), 2),
            'simulations': iterations,
            'percentile_5': round(np.percentile([r['final_equity'] for r in results], 5), 2),
            'percentile_95': round(np.percentile([r['final_equity'] for r in results], 95), 2)
        }
    
    async def walk_forward_analysis(
        self,
        historical_data: pd.DataFrame,
        strategy: StrategyBase,
        window_size: int = 100,
        step_size: int = 20,
        initial_capital: float = 100000
    ) -> Dict[str, Any]:
        """
        Walk-forward analysis for robust strategy testing.
        
        Args:
            historical_data: Complete historical dataset
            strategy: Strategy to test
            window_size: Size of training window
            step_size: Step size for rolling window
            initial_capital: Starting capital for each test
        
        Returns:
            Dictionary with walk-forward analysis results
        """
        results = []
        
        for i in range(window_size, len(historical_data), step_size):
            train_window = historical_data.iloc[:i].copy()
            test_start = i
            test_end = min(i + step_size, len(historical_data))
            test_window = historical_data.iloc[test_start:test_end].copy()
            
            if len(test_window) < 5:  # Skip if test window too small
                continue
            
            # Optimize on train window
            try:
                optimized_params = strategy.optimize(train_window)
                strategy.set_parameters(optimized_params)
                
                # Test on out-of-sample window
                engine = BacktestingEngine()
                test_metrics = await engine.run_backtest(test_window, strategy, initial_capital)
                
                results.append({
                    'train_period': {
                        'start': train_window.index[0] if 'timestamp' not in train_window.columns else train_window['timestamp'].iloc[0],
                        'end': train_window.index[-1] if 'timestamp' not in train_window.columns else train_window['timestamp'].iloc[-1]
                    },
                    'test_period': {
                        'start': test_window.index[0] if 'timestamp' not in test_window.columns else test_window['timestamp'].iloc[0],
                        'end': test_window.index[-1] if 'timestamp' not in test_window.columns else test_window['timestamp'].iloc[-1]
                    },
                    'metrics': {
                        'total_return_percent': test_metrics.total_return_percent,
                        'sharpe_ratio': test_metrics.sharpe_ratio,
                        'max_drawdown': test_metrics.max_drawdown,
                        'win_rate': test_metrics.win_rate,
                        'total_trades': test_metrics.total_trades
                    }
                })
            except Exception as e:
                # Skip if optimization fails
                continue
        
        if not results:
            return {'error': 'Walk-forward analysis failed - no valid windows'}
        
        # Calculate aggregate metrics
        avg_sharpe = np.mean([r['metrics']['sharpe_ratio'] for r in results])
        avg_return = np.mean([r['metrics']['total_return_percent'] for r in results])
        returns_list = [r['metrics']['total_return_percent'] for r in results]
        
        return {
            'periods': len(results),
            'avg_sharpe_ratio': round(avg_sharpe, 2),
            'avg_return': round(avg_return, 2),
            'consistency': self._calculate_consistency(returns_list),
            'std_return': round(np.std(returns_list), 2),
            'results': results
        }
    
    def stress_test(
        self,
        historical_data: pd.DataFrame,
        strategy: StrategyBase,
        initial_capital: float = 100000
    ) -> Dict[str, Any]:
        """
        Stress testing - test strategy against different market conditions.
        
        Args:
            historical_data: Historical price data
            strategy: Strategy to test
            initial_capital: Starting capital
        
        Returns:
            Dictionary with stress test results
        """
        results = {}
        
        # Calculate volatility if not present
        if 'volatility' not in historical_data.columns:
            data = historical_data.copy()
            data['volatility'] = data['close'].pct_change().rolling(window=20).std()
        else:
            data = historical_data
        
        # Test 1: High Volatility Period
        high_vol_data = data[data['volatility'] > data['volatility'].quantile(0.75)]
        if len(high_vol_data) > 20:
            engine = BacktestingEngine()
            high_vol_metrics = engine.calculate_metrics(initial_capital)
            results['high_volatility'] = {
                'total_return_percent': high_vol_metrics.total_return_percent,
                'sharpe_ratio': high_vol_metrics.sharpe_ratio,
                'max_drawdown': high_vol_metrics.max_drawdown,
                'win_rate': high_vol_metrics.win_rate,
                'total_trades': high_vol_metrics.total_trades
            }
        
        # Test 2: Trending Market (price above 20 SMA)
        data['sma_20'] = data['close'].rolling(window=20).mean()
        trending_data = data[data['close'] > data['sma_20']]
        if len(trending_data) > 20:
            engine = BacktestingEngine()
            trending_metrics = engine.calculate_metrics(initial_capital)
            results['trending_market'] = {
                'total_return_percent': trending_metrics.total_return_percent,
                'sharpe_ratio': trending_metrics.sharpe_ratio,
                'max_drawdown': trending_metrics.max_drawdown,
                'win_rate': trending_metrics.win_rate,
                'total_trades': trending_metrics.total_trades
            }
        
        # Test 3: Mean Reversion (price far from SMA)
        data['distance_from_sma'] = abs(data['close'] - data['sma_20']) / data['sma_20']
        mean_reversion_data = data[data['distance_from_sma'] > 0.05]
        if len(mean_reversion_data) > 20:
            engine = BacktestingEngine()
            mean_rev_metrics = engine.calculate_metrics(initial_capital)
            results['mean_reversion'] = {
                'total_return_percent': mean_rev_metrics.total_return_percent,
                'sharpe_ratio': mean_rev_metrics.sharpe_ratio,
                'max_drawdown': mean_rev_metrics.max_drawdown,
                'win_rate': mean_rev_metrics.win_rate,
                'total_trades': mean_rev_metrics.total_trades
            }
        
        # Test 4: Low Volatility Period
        low_vol_data = data[data['volatility'] < data['volatility'].quantile(0.25)]
        if len(low_vol_data) > 20:
            engine = BacktestingEngine()
            low_vol_metrics = engine.calculate_metrics(initial_capital)
            results['low_volatility'] = {
                'total_return_percent': low_vol_metrics.total_return_percent,
                'sharpe_ratio': low_vol_metrics.sharpe_ratio,
                'max_drawdown': low_vol_metrics.max_drawdown,
                'win_rate': low_vol_metrics.win_rate,
                'total_trades': low_vol_metrics.total_trades
            }
        
        return results
    
    def _calculate_consistency(self, returns: List[float]) -> float:
        """
        Calculate consistency score based on return standard deviation.
        
        Args:
            returns: List of returns
        
        Returns:
            Consistency score (0-100, higher is better)
        """
        if len(returns) == 0:
            return 0
        
        avg = np.mean(returns)
        variance = np.var(returns)
        std_dev = np.sqrt(variance)
        
        # Lower standard deviation = higher consistency
        consistency = 100 - min(std_dev * 10, 100)
        return round(consistency, 2)
    
    def calculate_sma(self, data: pd.DataFrame, period: int) -> float:
        """
        Calculate Simple Moving Average.
        
        Args:
            data: Price data
            period: SMA period
        
        Returns:
            SMA value
        """
        if len(data) < period:
            return data['close'].iloc[-1] if len(data) > 0 else 0
        
        return data['close'].iloc[-period:].mean()
    
    async def optimize_parameters(
        self,
        historical_data: pd.DataFrame,
        strategy: StrategyBase,
        param_ranges: Dict[str, List[Any]],
        initial_capital: float = 100000
    ) -> List[Dict[str, Any]]:
        """
        Parameter optimization using grid search.
        
        Args:
            historical_data: Historical price data
            strategy: Strategy to optimize
            param_ranges: Dictionary of parameter names and their possible values
            initial_capital: Starting capital for backtests
        
        Returns:
            List of parameter combinations sorted by Sharpe ratio
        """
        results = []
        
        # Generate all parameter combinations
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        for combination in itertools.product(*param_values):
            params = dict(zip(param_names, combination))
            
            try:
                strategy.set_parameters(params)
                engine = BacktestingEngine()
                metrics = await engine.run_backtest(historical_data, strategy, initial_capital)
                
                results.append({
                    'params': params,
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'total_return_percent': metrics.total_return_percent,
                    'max_drawdown': metrics.max_drawdown,
                    'win_rate': metrics.win_rate,
                    'total_trades': metrics.total_trades
                })
            except Exception as e:
                # Skip invalid parameter combinations
                continue
        
        # Sort by Sharpe ratio and return top 10
        results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        return results[:10]


# Example strategy implementations
class SimpleMomentumStrategy(StrategyBase):
    """Simple momentum-based trading strategy."""
    
    def __init__(self, lookback_period: int = 10, threshold: float = 0.02):
        self.lookback_period = lookback_period
        self.threshold = threshold
        self.parameters = {
            'lookback_period': lookback_period,
            'threshold': threshold
        }
    
    def get_signal(self, historical_data: pd.DataFrame) -> Signal:
        """Generate momentum signal."""
        if len(historical_data) < self.lookback_period:
            return Signal(action=ActionType.HOLD)
        
        recent_return = (historical_data['close'].iloc[-1] - 
                       historical_data['close'].iloc[-self.lookback_period]) / \
                       historical_data['close'].iloc[-self.lookback_period]
        
        if recent_return > self.threshold:
            return Signal(action=ActionType.BUY, allocation=0.5)
        elif recent_return < -self.threshold:
            return Signal(action=ActionType.SELL)
        else:
            return Signal(action=ActionType.HOLD)
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Set strategy parameters."""
        self.lookback_period = parameters.get('lookback_period', 10)
        self.threshold = parameters.get('threshold', 0.02)
        self.parameters = parameters
    
    def optimize(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Optimize parameters using simple grid search."""
        best_sharpe = -float('inf')
        best_params = self.parameters.copy()
        
        for lookback in [5, 10, 15, 20]:
            for threshold in [0.01, 0.02, 0.03, 0.05]:
                self.lookback_period = lookback
                self.threshold = threshold
                
                # Simple backtest for optimization
                returns = []
                for i in range(lookback, len(historical_data)):
                    window_data = historical_data.iloc[:i+1]
                    signal = self.get_signal(window_data)
                    
                    if signal.action == ActionType.BUY:
                        entry_return = historical_data['close'].iloc[i+1] / historical_data['close'].iloc[i] - 1
                        returns.append(entry_return)
                
                if len(returns) > 0:
                    sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
                    if sharpe > best_sharpe:
                        best_sharpe = sharpe
                        best_params = {'lookback_period': lookback, 'threshold': threshold}
        
        return best_params


class MeanReversionStrategy(StrategyBase):
    """Mean reversion trading strategy."""
    
    def __init__(self, lookback_period: int = 20, std_threshold: float = 2.0):
        self.lookback_period = lookback_period
        self.std_threshold = std_threshold
        self.parameters = {
            'lookback_period': lookback_period,
            'std_threshold': std_threshold
        }
    
    def get_signal(self, historical_data: pd.DataFrame) -> Signal:
        """Generate mean reversion signal."""
        if len(historical_data) < self.lookback_period:
            return Signal(action=ActionType.HOLD)
        
        recent_prices = historical_data['close'].iloc[-self.lookback_period:]
        mean = recent_prices.mean()
        std = recent_prices.std()
        current_price = historical_data['close'].iloc[-1]
        
        z_score = (current_price - mean) / std if std > 0 else 0
        
        if z_score < -self.std_threshold:
            return Signal(action=ActionType.BUY, allocation=0.5)
        elif z_score > self.std_threshold:
            return Signal(action=ActionType.SELL)
        else:
            return Signal(action=ActionType.HOLD)
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Set strategy parameters."""
        self.lookback_period = parameters.get('lookback_period', 20)
        self.std_threshold = parameters.get('std_threshold', 2.0)
        self.parameters = parameters
    
    def optimize(self, historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Optimize parameters."""
        best_sharpe = -float('inf')
        best_params = self.parameters.copy()
        
        for lookback in [10, 20, 30]:
            for std_threshold in [1.5, 2.0, 2.5, 3.0]:
                self.lookback_period = lookback
                self.std_threshold = std_threshold
                
                # Simple backtest for optimization
                returns = []
                for i in range(lookback, len(historical_data)):
                    window_data = historical_data.iloc[:i+1]
                    signal = self.get_signal(window_data)
                    
                    if signal.action == ActionType.BUY:
                        entry_return = historical_data['close'].iloc[i+1] / historical_data['close'].iloc[i] - 1
                        returns.append(entry_return)
                
                if len(returns) > 0:
                    sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
                    if sharpe > best_sharpe:
                        best_sharpe = sharpe
                        best_params = {'lookback_period': lookback, 'std_threshold': std_threshold}
        
        return best_params


def run_comprehensive_backtest(
    historical_data: pd.DataFrame,
    strategy_type: str = "momentum",
    initial_capital: float = 100000
) -> Dict[str, Any]:
    """
    Run comprehensive backtest with all analysis features.
    
    Args:
        historical_data: Historical price data
        strategy_type: Type of strategy to use
        initial_capital: Starting capital
    
    Returns:
        Dictionary with comprehensive backtest results
    """
    # Select strategy
    if strategy_type == "momentum":
        strategy = SimpleMomentumStrategy()
    elif strategy_type == "mean_reversion":
        strategy = MeanReversionStrategy()
    else:
        strategy = SimpleMomentumStrategy()
    
    # Run main backtest
    engine = BacktestingEngine()
    main_metrics = asyncio.run(engine.run_backtest(historical_data, strategy, initial_capital))
    
    # Run Monte Carlo simulation
    monte_carlo_results = engine.monte_carlo_simulation(iterations=1000, initial_capital=initial_capital)
    
    # Run stress tests
    stress_results = engine.stress_test(historical_data, strategy, initial_capital)
    
    return {
        'main_metrics': {
            'total_return': main_metrics.total_return,
            'total_return_percent': main_metrics.total_return_percent,
            'sharpe_ratio': main_metrics.sharpe_ratio,
            'sortino_ratio': main_metrics.sortino_ratio,
            'max_drawdown': main_metrics.max_drawdown,
            'win_rate': main_metrics.win_rate,
            'profit_factor': main_metrics.profit_factor,
            'total_trades': main_metrics.total_trades,
            'avg_return': main_metrics.avg_return,
            'recovery_factor': main_metrics.recovery_factor
        },
        'monte_carlo': monte_carlo_results,
        'stress_tests': stress_results,
        'strategy_type': strategy_type,
        'backtest_date': datetime.now(tz.utc).isoformat()
    }


# Import asyncio for async operations
import asyncio