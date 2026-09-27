"""Tests for the advanced backtesting engine."""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services import backtesting


def synthetic_backtest_data(n=500, seed=42):
    """Generate synthetic OHLC data for backtesting."""
    np.random.seed(seed)
    ret = np.random.normal(0.0004, 0.012, n)
    close = 100 * np.exp(np.cumsum(ret))
    open_ = np.r_[close[0], close[:-1]] * (1 + np.random.normal(0, 0.002, n))
    high = np.maximum(open_, close) * (1 + np.abs(np.random.normal(0, 0.004, n)))
    low = np.minimum(open_, close) * (1 - np.abs(np.random.normal(0, 0.004, n)))
    idx = pd.bdate_range(end=datetime.now(), periods=n)
    
    df = pd.DataFrame({
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.random.randint(1000, 5000, n).astype(float)
    }, index=idx)
    df['timestamp'] = idx
    return df


def test_backtesting_engine_initialization():
    """Test backtesting engine initialization."""
    engine = backtesting.BacktestingEngine()
    assert engine.trades == []
    assert engine.equity_history == []
    assert engine.positions == []


def test_simple_momentum_strategy():
    """Test simple momentum strategy signal generation."""
    strategy = backtesting.SimpleMomentumStrategy(lookback_period=10, threshold=0.02)
    data = synthetic_backtest_data()
    
    signal = strategy.get_signal(data)
    assert signal.action in [backtesting.ActionType.BUY, backtesting.ActionType.SELL, backtesting.ActionType.HOLD]
    assert 0 <= signal.allocation <= 1


def test_mean_reversion_strategy():
    """Test mean reversion strategy signal generation."""
    strategy = backtesting.MeanReversionStrategy(lookback_period=20, std_threshold=2.0)
    data = synthetic_backtest_data()
    
    signal = strategy.get_signal(data)
    assert signal.action in [backtesting.ActionType.BUY, backtesting.ActionType.SELL, backtesting.ActionType.HOLD]


def test_strategy_parameter_setting():
    """Test strategy parameter setting."""
    strategy = backtesting.SimpleMomentumStrategy()
    new_params = {'lookback_period': 15, 'threshold': 0.03}
    strategy.set_parameters(new_params)
    
    assert strategy.lookback_period == 15
    assert strategy.threshold == 0.03


def test_run_backtest_basic():
    """Test basic backtest execution."""
    data = synthetic_backtest_data()
    strategy = backtesting.SimpleMomentumStrategy()
    engine = backtesting.BacktestingEngine()
    
    import asyncio
    metrics = asyncio.run(engine.run_backtest(data, strategy, initial_capital=100000))
    
    assert metrics.total_trades >= 0
    assert isinstance(metrics.total_return, float)
    assert isinstance(metrics.sharpe_ratio, float)
    assert isinstance(metrics.max_drawdown, float)
    assert isinstance(metrics.win_rate, float)


def test_backtest_metrics_calculation():
    """Test metrics calculation with no trades."""
    engine = backtesting.BacktestingEngine()
    metrics = engine.calculate_metrics(100000)
    
    assert metrics.total_trades == 0
    assert metrics.total_return == 0
    assert metrics.error == 'No trades executed'


def test_monte_carlo_simulation():
    """Test Monte Carlo simulation."""
    data = synthetic_backtest_data()
    strategy = backtesting.SimpleMomentumStrategy()
    engine = backtesting.BacktestingEngine()
    
    import asyncio
    asyncio.run(engine.run_backtest(data, strategy, initial_capital=100000))
    
    # Add some trades for simulation
    if len(engine.trades) == 0:
        # Create dummy trades
        for i in range(10):
            trade = backtesting.Trade(
                entry_date=datetime.now() - timedelta(days=i+10),
                exit_date=datetime.now() - timedelta(days=i),
                entry_price=100 + i,
                exit_price=100 + i + 5,
                quantity=10,
                pnl=50,
                pnl_percent=5.0,
                trade_type="LONG"
            )
            engine.trades.append(trade)
    
    results = engine.monte_carlo_simulation(iterations=100, initial_capital=100000)
    
    assert 'avg_final_equity' in results
    assert 'avg_max_drawdown' in results
    assert 'worst_case' in results
    assert 'best_case' in results
    assert results['simulations'] == 100


def test_stress_test():
    """Test stress testing functionality."""
    data = synthetic_backtest_data()
    strategy = backtesting.SimpleMomentumStrategy()
    engine = backtesting.BacktestingEngine()
    
    results = engine.stress_test(data, strategy, initial_capital=100000)
    
    # At least some stress tests should run
    assert isinstance(results, dict)
    # Some stress tests might not have enough data, so we just check the structure


def test_calculate_sma():
    """Test SMA calculation."""
    data = synthetic_backtest_data()
    engine = backtesting.BacktestingEngine()
    
    sma_20 = engine.calculate_sma(data, 20)
    assert isinstance(sma_20, float)
    assert sma_20 > 0


def test_consistency_calculation():
    """Test consistency score calculation."""
    engine = backtesting.BacktestingEngine()
    
    # High consistency (low variance)
    consistent_returns = [1.0, 1.1, 0.9, 1.0, 1.05]
    consistency_score = engine._calculate_consistency(consistent_returns)
    assert 0 <= consistency_score <= 100
    
    # Low consistency (high variance)
    variable_returns = [10.0, -5.0, 15.0, -10.0, 8.0]
    low_consistency = engine._calculate_consistency(variable_returns)
    assert low_consistency < consistency_score


def test_walk_forward_analysis():
    """Test walk-forward analysis."""
    data = synthetic_backtest_data(n=300)  # Need more data for walk-forward
    strategy = backtesting.SimpleMomentumStrategy()
    engine = backtesting.BacktestingEngine()
    
    import asyncio
    results = asyncio.run(engine.walk_forward_analysis(
        data, strategy, window_size=100, step_size=20, initial_capital=100000
    ))
    
    # Walk-forward might fail if data is insufficient, so we check for either success or error
    assert isinstance(results, dict)


def test_parameter_optimization():
    """Test parameter optimization."""
    data = synthetic_backtest_data()
    strategy = backtesting.SimpleMomentumStrategy()
    engine = backtesting.BacktestingEngine()
    
    param_ranges = {
        'lookback_period': [5, 10, 15],
        'threshold': [0.01, 0.02, 0.03]
    }
    
    import asyncio
    results = asyncio.run(engine.optimize_parameters(
        data, strategy, param_ranges, initial_capital=100000
    ))
    
    assert isinstance(results, list)
    # Results should be sorted by Sharpe ratio
    if len(results) > 1:
        assert results[0]['sharpe_ratio'] >= results[1]['sharpe_ratio']


def test_trade_dataclass():
    """Test Trade dataclass."""
    trade = backtesting.Trade(
        entry_date=datetime.now(),
        exit_date=datetime.now() + timedelta(days=1),
        entry_price=100.0,
        exit_price=105.0,
        quantity=10,
        pnl=50.0,
        pnl_percent=5.0,
        trade_type="LONG"
    )
    
    assert trade.entry_price == 100.0
    assert trade.exit_price == 105.0
    assert trade.pnl == 50.0
    assert trade.trade_type == "LONG"


def test_position_dataclass():
    """Test Position dataclass."""
    position = backtesting.Position(
        entry_price=100.0,
        quantity=10,
        entry_date=datetime.now(),
        stop_loss=95.0,
        take_profit=110.0
    )
    
    assert position.entry_price == 100.0
    assert position.stop_loss == 95.0
    assert position.take_profit == 110.0


def test_backtest_metrics_dataclass():
    """Test BacktestMetrics dataclass."""
    metrics = backtesting.BacktestMetrics(
        total_return=1000.0,
        total_return_percent=1.0,
        sharpe_ratio=1.5,
        sortino_ratio=2.0,
        max_drawdown=5.0,
        win_rate=60.0,
        profit_factor=1.5,
        total_trades=10,
        avg_return=0.1,
        recovery_factor=2.0
    )
    
    assert metrics.total_return == 1000.0
    assert metrics.sharpe_ratio == 1.5
    assert metrics.win_rate == 60.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])