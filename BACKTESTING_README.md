# Advanced Backtesting Engine

This document describes the advanced backtesting engine implementation for the market predictor platform.

## Overview

The backtesting engine provides comprehensive strategy analysis with the following features:

- **Complete Backtesting**: Run historical simulations with custom strategies
- **Performance Metrics**: Calculate Sharpe ratio, Sortino ratio, max drawdown, win rate, profit factor, etc.
- **Monte Carlo Simulation**: Assess strategy robustness through randomization
- **Walk-Forward Analysis**: Test strategy stability across different time periods
- **Stress Testing**: Evaluate performance under various market conditions
- **Parameter Optimization**: Grid search for optimal strategy parameters

## API Endpoints

### 1. Run Backtest
**Endpoint**: `POST /api/backtest/run`

Run a comprehensive backtest with optional Monte Carlo simulation and stress testing.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "strategy_type": "momentum",
  "initial_capital": 100000,
  "commission": 0.001,
  "monte_carlo_iterations": 1000,
  "run_stress_tests": true,
  "run_monte_carlo": true
}
```

**Response**:
```json
{
  "symbol": "AAPL",
  "strategy_type": "momentum",
  "main_metrics": {
    "total_return": 15000.50,
    "total_return_percent": 15.01,
    "sharpe_ratio": 1.25,
    "sortino_ratio": 1.80,
    "max_drawdown": 8.5,
    "win_rate": 55.0,
    "profit_factor": 1.45,
    "total_trades": 42,
    "avg_return": 0.35,
    "recovery_factor": 2.5,
    "equity_history": [...],
    "trades": [...]
  },
  "monte_carlo": {
    "avg_final_equity": 115000.00,
    "avg_max_drawdown": 7.5,
    "avg_return": 15.0,
    "worst_case": 95000.00,
    "best_case": 135000.00,
    "simulations": 1000
  },
  "stress_tests": {
    "high_volatility": {...},
    "trending_market": {...},
    "mean_reversion": {...}
  },
  "timestamp": "2026-09-27T12:00:00Z"
}
```

### 2. Optimize Parameters
**Endpoint**: `POST /api/backtest/optimize`

Optimize strategy parameters using grid search.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "strategy_type": "momentum",
  "param_ranges": {
    "lookback_period": [5, 10, 15, 20],
    "threshold": [0.01, 0.02, 0.03, 0.05]
  },
  "initial_capital": 100000
}
```

**Response**:
```json
{
  "symbol": "AAPL",
  "strategy_type": "momentum",
  "optimization_results": [
    {
      "params": {"lookback_period": 10, "threshold": 0.02},
      "sharpe_ratio": 1.45,
      "total_return_percent": 18.5,
      "max_drawdown": 7.2,
      "win_rate": 58.0,
      "total_trades": 38
    },
    ...
  ],
  "timestamp": "2026-09-27T12:00:00Z"
}
```

### 3. Walk-Forward Analysis
**Endpoint**: `POST /api/backtest/walk-forward`

Run walk-forward analysis for robust strategy testing.

**Request Body**:
```json
{
  "symbol": "AAPL",
  "strategy_type": "momentum",
  "window_size": 100,
  "step_size": 20,
  "initial_capital": 100000
}
```

**Response**:
```json
{
  "symbol": "AAPL",
  "strategy_type": "momentum",
  "walk_forward": {
    "periods": 8,
    "avg_sharpe_ratio": 1.15,
    "avg_return": 12.5,
    "consistency": 75.0,
    "std_return": 4.2,
    "results": [...]
  },
  "timestamp": "2026-09-27T12:00:00Z"
}
```

## Performance Metrics

The backtesting engine calculates the following metrics:

### Core Metrics
- **Total Return**: Absolute profit/loss in currency
- **Total Return %**: Percentage return on initial capital
- **Sharpe Ratio**: Risk-adjusted return (annualized)
- **Sortino Ratio**: Risk-adjusted return considering only downside risk
- **Max Drawdown**: Maximum peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Recovery Factor**: Total return divided by largest loss

### Advanced Metrics
- **Consistency Score**: Measure of return stability (0-100)
- **Monte Carlo Percentiles**: 5th and 95th percentile outcomes
- **Stress Test Results**: Performance under different market conditions

## Built-in Strategies

### 1. Simple Momentum Strategy
- **Parameters**: `lookback_period`, `threshold`
- **Logic**: Buy when price change over lookback period exceeds threshold
- **Best for**: Trending markets

### 2. Mean Reversion Strategy
- **Parameters**: `lookback_period`, `std_threshold`
- **Logic**: Buy when price is below mean by standard deviation threshold
- **Best for**: Range-bound markets

## Custom Strategies

You can implement custom strategies by extending the `StrategyBase` class:

```python
from app.services.backtesting import StrategyBase, Signal, ActionType
import pandas as pd

class MyCustomStrategy(StrategyBase):
    def __init__(self, param1=10, param2=0.5):
        self.param1 = param1
        self.param2 = param2
        self.parameters = {'param1': param1, 'param2': param2}
    
    def get_signal(self, historical_data: pd.DataFrame) -> Signal:
        # Your custom signal generation logic
        if len(historical_data) < self.param1:
            return Signal(action=ActionType.HOLD)
        
        # Example: RSI-based signal
        current_price = historical_data['close'].iloc[-1]
        if current_price > historical_data['close'].iloc[-self.param1] * (1 + self.param2):
            return Signal(action=ActionType.BUY, allocation=0.5)
        else:
            return Signal(action=ActionType.HOLD)
    
    def set_parameters(self, parameters: dict) -> None:
        self.param1 = parameters.get('param1', 10)
        self.param2 = parameters.get('param2', 0.5)
        self.parameters = parameters
    
    def optimize(self, historical_data: pd.DataFrame) -> dict:
        # Your custom optimization logic
        return self.parameters
```

## Usage Examples

### Python API Usage

```python
import pandas as pd
from app.services.backtesting import BacktestingEngine, SimpleMomentumStrategy

# Load historical data
data = pd.read_csv('historical_data.csv')

# Initialize strategy and engine
strategy = SimpleMomentumStrategy(lookback_period=10, threshold=0.02)
engine = BacktestingEngine()

# Run backtest
import asyncio
metrics = asyncio.run(engine.run_backtest(data, strategy, initial_capital=100000))

print(f"Total Return: {metrics.total_return_percent}%")
print(f"Sharpe Ratio: {metrics.sharpe_ratio}")
print(f"Max Drawdown: {metrics.max_drawdown}%")

# Run Monte Carlo simulation
monte_carlo = engine.monte_carlo_simulation(iterations=1000)
print(f"Average Final Equity: ${monte_carlo['avg_final_equity']}")

# Run stress tests
stress_results = engine.stress_test(data, strategy)
print("Stress Test Results:", stress_results)
```

### Parameter Optimization

```python
# Define parameter ranges
param_ranges = {
    'lookback_period': [5, 10, 15, 20],
    'threshold': [0.01, 0.02, 0.03, 0.05]
}

# Run optimization
results = asyncio.run(engine.optimize_parameters(
    data, strategy, param_ranges, initial_capital=100000
))

# Display top results
for result in results[:3]:
    print(f"Params: {result['params']}")
    print(f"Sharpe: {result['sharpe_ratio']}")
    print(f"Return: {result['total_return_percent']}%")
```

## Best Practices

1. **Data Quality**: Ensure historical data is clean and complete
2. **Commission Costs**: Include realistic commission rates in backtests
3. **Look-ahead Bias**: Avoid using future data in signal generation
4. **Overfitting**: Use walk-forward analysis to detect overfitting
5. **Sample Size**: Ensure sufficient data for statistically significant results
6. **Market Regimes**: Test across different market conditions

## Performance Considerations

- **Monte Carlo**: Requires more iterations for statistical significance (1000+ recommended)
- **Parameter Optimization**: Grid search can be computationally expensive
- **Walk-Forward**: Larger window sizes provide more robust results
- **Memory Usage**: Large datasets may require significant memory

## Testing

The backtesting engine includes comprehensive test coverage:

```bash
# Run all backtesting tests
python -m pytest tests/test_backtesting.py -v

# Run specific test
python -m pytest tests/test_backtesting.py::test_run_backtest_basic -v
```

## Integration

The backtesting engine is integrated with the existing market predictor infrastructure:

- Uses existing data fetching via `_auto_signal()`
- Follows existing security patterns with rate limiting
- Compatible with existing authentication system
- Integrates with existing API structure

## Future Enhancements

Potential future improvements:

- Additional built-in strategies (Bollinger Bands, MACD, etc.)
- Multi-asset portfolio backtesting
- Real-time paper trading mode
- Advanced performance attribution
- Machine learning-based strategy optimization
- Custom risk management rules
- Short selling support
- Options and derivatives backtesting

## Support

For issues or questions about the backtesting engine, please refer to the main project documentation or create an issue in the project repository.