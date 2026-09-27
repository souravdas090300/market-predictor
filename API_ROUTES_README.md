# API Routes Documentation - Phases 11-18

This document describes all the API endpoints for phases 11-18 of the market predictor platform.

## Overview

The API provides comprehensive endpoints for:
- **Phase 11**: Backtesting Engine
- **Phase 12**: Advanced Sentiment Analysis
- **Phase 13**: Trading Alerts & Automation
- **Phase 14**: Portfolio Optimization
- **Phase 15**: Machine Learning Predictions
- **Phase 16**: Social Trading
- **Phase 17**: Broker Integration
- **Phase 18**: Risk Management

All endpoints are prefixed with `/api/v2/` for version 2 of the API.

## Phase 11: Backtesting Routes

### POST /api/v2/backtest/run
Run a backtest with a given strategy.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "strategy_name": "momentum",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 100000,
  "commission": 0.001
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "total_return": 15000.0,
    "total_return_percent": 15.0,
    "sharpe_ratio": 1.5,
    "sortino_ratio": 2.0,
    "max_drawdown": -8.5,
    "win_rate": 65.0,
    "profit_factor": 2.5,
    "trades": 45,
    "avg_return": 0.33,
    "recovery_factor": 1.8
  }
}
```

**Rate Limit:** 10 requests/minute

---

### POST /api/v2/backtest/monte-carlo
Run Monte Carlo simulation on backtest results.

**Request Body:**
```json
{
  "iterations": 1000
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "avg_final_equity": 115000.0,
    "avg_max_drawdown": -10.5,
    "avg_return": 15.0,
    "worst_case": 95000.0,
    "best_case": 135000.0,
    "simulations": 1000
  }
}
```

**Rate Limit:** 5 requests/minute

---

### POST /api/v2/backtest/walk-forward
Run walk-forward analysis for strategy robustness.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "strategy_name": "momentum",
  "window_size": 100,
  "step_size": 20
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "periods": 12,
    "avg_sharpe_ratio": 1.3,
    "avg_return": 12.5,
    "consistency": 75.0
  }
}
```

**Rate Limit:** 5 requests/minute

---

### POST /api/v2/backtest/optimize
Optimize strategy parameters using grid search.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "strategy_name": "momentum",
  "param_ranges": {
    "lookback": [5, 10, 15, 20],
    "threshold": [0.01, 0.02, 0.03]
  }
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "params": {"lookback": 10, "threshold": 0.02},
      "sharpe_ratio": 1.5,
      "total_return": 15.0,
      "max_drawdown": -8.5
    }
  ]
}
```

**Rate Limit:** 5 requests/minute

---

## Phase 12: Sentiment Analysis Routes

### GET /api/v2/sentiment/news/{symbol}
Get news sentiment for a symbol.

**Example:**
```
GET /api/v2/sentiment/news/AAPL
```

**Response:**
```json
{
  "success": true,
  "sentiment": {
    "symbol": "AAPL",
    "overall_sentiment": 0.35,
    "sentiment_label": "BULLISH",
    "strength": 0.35,
    "bullish_count": 8,
    "bearish_count": 2,
    "total_articles": 12,
    "impact_score": 0.72
  }
}
```

**Rate Limit:** 20 requests/minute

---

### GET /api/v2/sentiment/social/{symbol}/{platform}
Get social media sentiment for a symbol.

**Example:**
```
GET /api/v2/sentiment/social/AAPL/twitter
```

**Response:**
```json
{
  "success": true,
  "sentiment": {
    "symbol": "AAPL",
    "platform": "twitter",
    "overall_sentiment": 0.42,
    "sentiment_label": "BULLISH",
    "total_posts": 156,
    "virality": 45.2,
    "sentiment_trend": "IMPROVING"
  }
}
```

**Rate Limit:** 20 requests/minute

---

### GET /api/v2/sentiment/fear-greed
Get the Fear & Greed index.

**Example:**
```
GET /api/v2/sentiment/fear-greed
```

**Response:**
```json
{
  "success": true,
  "index": {
    "index": 65.0,
    "classification": "GREED",
    "components": {
      "market_momentum": 0.3,
      "volatility": -0.1,
      "volume": 0.2,
      "breadth": 0.15,
      "dominance": 0.1
    }
  }
}
```

**Rate Limit:** 10 requests/minute

---

### POST /api/v2/sentiment/earnings
Analyze earnings call transcript sentiment.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "transcript": "Our company showed strong growth this quarter..."
}
```

**Response:**
```json
{
  "success": true,
  "sentiment": {
    "symbol": "AAPL",
    "overall_sentiment": 0.45,
    "sentiment_label": "BULLISH",
    "key_points": [
      {
        "text": "Our company showed strong growth",
        "sentiment": 0.4
      }
    ],
    "confidence": 0.45
  }
}
```

**Rate Limit:** 10 requests/minute

---

## Phase 13: Alerts & Automation Routes

### POST /api/v2/alerts
Create a trading alert.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "alert_type": "price",
  "price": 150.0,
  "condition": "above",
  "notification_method": "email"
}
```

**Response:**
```json
{
  "success": true,
  "alert": {
    "id": "uuid-123",
    "symbol": "AAPL",
    "type": "price",
    "price": 150.0,
    "condition": "above",
    "status": "active",
    "created_at": "2026-09-27T12:00:00Z"
  }
}
```

**Rate Limit:** 20 requests/minute

---

### POST /api/v2/orders/market
Execute a market order.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 10,
  "price": 149.50
}
```

**Response:**
```json
{
  "success": true,
  "order": {...},
  "message": "BUY order executed for 10 AAPL at $149.50"
}
```

**Rate Limit:** 30 requests/minute

---

### POST /api/v2/orders/limit
Execute a limit order.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 10,
  "limit_price": 149.00,
  "stop_price": null
}
```

**Response:**
```json
{
  "success": true,
  "order": {
    "id": "uuid-456",
    "symbol": "AAPL",
    "side": "buy",
    "type": "limit",
    "quantity": 10,
    "limit_price": 149.00,
    "status": "pending"
  }
}
```

**Rate Limit:** 20 requests/minute

---

### DELETE /api/v2/orders/{order_id}
Cancel an order.

**Example:**
```
DELETE /api/v2/orders/uuid-456
```

**Response:**
```json
{
  "success": true,
  "order": {...}
}
```

**Rate Limit:** 20 requests/minute

---

### GET /api/v2/execution-history
Get execution history.

**Query Parameters:**
- `symbol` (optional): Filter by symbol
- `days` (optional): Number of days to look back (default: 30)

**Example:**
```
GET /api/v2/execution-history?symbol=AAPL&days=30
```

**Response:**
```json
{
  "success": true,
  "history": {
    "total_trades": 25,
    "total_value": 250000.0,
    "total_fees": 250.0,
    "buys": 15,
    "sells": 10,
    "history": [...]
  }
}
```

**Rate Limit:** 30 requests/minute

---

## Phase 14: Portfolio Optimization Routes

### POST /api/v2/portfolio/analyze
Analyze portfolio risk metrics.

**Request Body:**
```json
{
  "holdings": [
    {
      "symbol": "AAPL",
      "quantity": 10,
      "value": 1500,
      "purchase_price": 140,
      "current_price": 150,
      "beta": 1.2,
      "hedged": false
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "risk_metrics": {
    "total_value": 50000.0,
    "portfolio_volatility": 18.5,
    "diversification_ratio": 1.25,
    "var95": -2500.0,
    "var99": -4000.0,
    "cvar95": -3125.0,
    "beta": 1.15,
    "hedge_ratio": 10.0,
    "risk_assessment": "MEDIUM",
    "recommendations": [...]
  }
}
```

**Rate Limit:** 20 requests/minute

---

### POST /api/v2/portfolio/rebalance
Get rebalancing recommendations.

**Request Body:**
```json
{
  "holdings": [...],
  "target_allocation": {
    "AAPL": 0.4,
    "MSFT": 0.6
  }
}
```

**Response:**
```json
{
  "success": True,
  "rebalancing": {
    "current_allocation": {"AAPL": 30.0, "MSFT": 70.0},
    "target_allocation": {"AAPL": 40.0, "MSFT": 60.0},
    "trades": [
      {
        "symbol": "AAPL",
        "action": "buy",
        "amount": 5000.0,
        "current_weight": 30.0,
        "target_weight": 40.0
      }
    ],
    "expected_fees": 5.0
  }
}
```

**Rate Limit:** 10 requests/minute

---

### POST /api/v2/portfolio/efficient-frontier
Calculate efficient frontier for portfolio optimization.

**Request Body:**
```json
{
  "holdings": [...],
  "returns": [0.05, 0.08, 0.12],
  "covariance": [[0.01, 0.005, 0.003], [0.005, 0.02, 0.008], [0.003, 0.008, 0.03]]
}
```

**Response:**
```json
{
  "success": true,
  "frontier": [
    {
      "risk": 10.0,
      "return": 8.5,
      "sharpe_ratio": 0.85,
      "weights": {"AAPL": 0.33, "MSFT": 0.33, "GOOGL": 0.34}
    }
  ]
}
```

**Rate Limit:** 5 requests/minute

---

### POST /api/v2/portfolio/tax-loss-harvesting
Get tax-loss harvesting opportunities.

**Request Body:**
```json
{
  "holdings": [...]
}
```

**Response:**
```json
{
  "success": true,
  "opportunities": {
    "opportunities": [
      {
        "symbol": "NFLX",
        "purchase_price": 400,
        "current_price": 350,
        "quantity": 10,
        "unrealized_loss": -500.0,
        "tax_benefit": 185.0
      }
    ],
    "total_tax_benefit": 185.0
  }
}
```

**Rate Limit:** 10 requests/minute

---

## Phase 15: ML Predictions Routes

### POST /api/v2/predictions/ensemble
Get ensemble ML prediction from multiple models.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "timeframe": "1d"
}
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "ensemble_prediction": 152.50,
    "confidence": 0.79,
    "model_predictions": {
      "lstm": {
        "model": "LSTM",
        "price": 153.00,
        "confidence": 0.82,
        "reasoning": "Neural network capturing temporal patterns"
      },
      "arima": {...},
      "xgboost": {...},
      "prophet": {...}
    },
    "timestamp": "2026-09-27T12:00:00Z"
  }
}
```

**Rate Limit:** 15 requests/minute

---

### POST /api/v2/predictions/anomalies
Detect price anomalies using statistical analysis.

**Request Body:**
```json
{
  "symbol": "AAPL"
}
```

**Response:**
```json
{
  "success": true,
  "anomalies": [
    {
      "date": "2026-09-15",
      "price": 145.00,
      "z_score": 3.5,
      "daily_return": -8.5,
      "severity": "HIGH"
    }
  ]
}
```

**Rate Limit:** 10 requests/minute

---

### POST /api/v2/predictions/patterns
Recognize technical chart patterns.

**Request Body:**
```json
{
  "symbol": "AAPL"
}
```

**Response:**
```json
{
  "success": true,
  "patterns": [
    {
      "pattern": "Head and Shoulders",
      "bullish": false,
      "confidence": 0.75
    }
  ]
}
```

**Rate Limit:** 10 requests/minute

---

## Phase 16: Social Trading Routes

### POST /api/v2/social/strategies
Publish a trading strategy.

**Request Body:**
```json
{
  "author": "expert_trader",
  "name": "Momentum Strategy",
  "description": "Trend-following with risk management",
  "rules": {"lookback": 10, "threshold": 0.02},
  "performance": {
    "total_return": 0.25,
    "sharpe_ratio": 1.8,
    "win_rate": 0.65,
    "trades": 100
  }
}
```

**Response:**
```json
{
  "success": true,
  "strategy": {
    "id": "uuid-789",
    "author": "expert_trader",
    "name": "Momentum Strategy",
    "description": "Trend-following with risk management",
    "followers": 0,
    "rating": 4.5,
    "created_at": "2026-09-27T12:00:00Z"
  }
}
```

**Rate Limit:** 5 requests/minute

---

### POST /api/v2/social/follow
Follow/copy a strategy.

**Request Body:**
```json
{
  "user_id": "user123",
  "strategy_id": "uuid-789",
  "allocation": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "follow_relation": {
    "user_id": "user123",
    "strategy_id": "uuid-789",
    "followed_at": "2026-09-27T12:00:00Z",
    "allocation": 0.5,
    "status": "active"
  }
}
```

**Rate Limit:** 10 requests/minute

---

### GET /api/v2/social/leaderboard
Get strategy leaderboard ranked by performance.

**Example:**
```
GET /api/v2/social/leaderboard
```

**Response:**
```json
{
  "success": true,
  "leaderboard": [
    {
      "rank": 1,
      "author": "expert_trader",
      "strategy_name": "Momentum Strategy",
      "total_return": 0.25,
      "sharpe_ratio": 1.8,
      "win_rate": 0.65,
      "followers": 150,
      "rating": 4.8,
      "trades": 100
    }
  ]
}
```

**Rate Limit:** 30 requests/minute

---

### POST /api/v2/social/rate
Rate and review a strategy.

**Request Body:**
```json
{
  "strategy_id": "uuid-789",
  "rating": 5,
  "review": "Excellent strategy with consistent returns"
}
```

**Response:**
```json
{
  "success": true,
  "review": {
    "id": "uuid-101",
    "strategy_id": "uuid-789",
    "rating": 5,
    "text": "Excellent strategy with consistent returns",
    "created_at": "2026-09-27T12:00:00Z"
  }
}
```

**Rate Limit:** 10 requests/minute

---

## Phase 17: Broker Integration Routes

### POST /api/v2/brokers/connect
Connect to a broker (Alpaca or Interactive Brokers).

**Request Body:**
```json
{
  "broker_name": "alpaca",
  "api_key": "your_api_key",
  "api_secret": "your_api_secret"
}
```

**Response:**
```json
{
  "success": true,
  "broker": {
    "name": "Alpaca",
    "connected": true,
    "assets": ["stocks", "crypto"],
    "features": ["margin", "shorting", "options"]
  }
}
```

**Rate Limit:** 5 requests/minute

---

### POST /api/v2/brokers/orders
Place an order through the broker.

**Request Body:**
```json
{
  "broker_name": "alpaca",
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 10,
  "price": 150.0,
  "order_type": "limit"
}
```

**Response:**
```json
{
  "success": true,
  "order_id": "broker-order-123",
  "broker_name": "alpaca",
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 10,
  "price": 150.0,
  "type": "limit",
  "status": "submitted",
  "commission": 1.5,
  "message": "Order submitted to alpaca"
}
```

**Rate Limit:** 20 requests/minute

---

### POST /api/v2/brokers/sync
Sync broker account data.

**Request Body:**
```json
{
  "broker_name": "alpaca"
}
```

**Response:**
```json
{
  "success": true,
  "account": {
    "account_id": "account-123",
    "broker": "alpaca",
    "equity": 125000.0,
    "cash": 25000.0,
    "buying_power": 50000.0,
    "portfolio": [
      {"symbol": "AAPL", "quantity": 10, "price": 189.95}
    ],
    "synced_at": "2026-09-27T12:00:00Z"
  }
}
```

**Rate Limit:** 10 requests/minute

---

### GET /api/v2/brokers/positions/{broker_name}
Get positions from broker account.

**Example:**
```
GET /api/v2/brokers/positions/alpaca
```

**Response:**
```json
{
  "broker": "alpaca",
  "positions": [
    {"symbol": "AAPL", "quantity": 10, "price": 189.95}
  ],
  "total_value": 1899.5,
  "timestamp": "2026-09-27T12:00:00Z"
}
```

**Rate Limit:** 10 requests/minute

---

## Phase 18: Risk Management Routes

### POST /api/v2/risk/limits
Set risk management limits.

**Request Body:**
```json
{
  "max_position_size": 0.15,
  "max_daily_loss": -0.03,
  "max_drawdown": -0.15,
  "max_correlation": 0.8,
  "max_leverage": 2.0,
  "stop_loss_percent": 0.04
}
```

**Response:**
```json
{
  "success": true,
  "limits": {
    "max_position_size": 0.15,
    "max_daily_loss": -0.03,
    "max_drawdown": -0.15,
    "max_correlation": 0.8,
    "max_leverage": 2.0,
    "stop_loss_percent": 0.04
  }
}
```

**Rate Limit:** 10 requests/minute

---

### POST /api/v2/risk/var
Calculate Value at Risk (VaR).

**Request Body:**
```json
{
  "holdings": [...],
  "confidence": 0.95
}
```

**Response:**
```json
{
  "success": true,
  "var": {
    "confidence": 95.0,
    "var_percent": -5.0,
    "var_amount": -2500.0,
    "interpretation": "There's a 95% chance of losing less than $2500.00"
  }
}
```

**Rate Limit:** 20 requests/minute

---

### POST /api/v2/risk/cvar
Calculate Conditional Value at Risk (CVaR).

**Request Body:**
```json
{
  "holdings": [...],
  "confidence": 0.95
}
```

**Response:**
```json
{
  "success": true,
  "cvar": {
    "confidence": 95.0,
    "cvar_percent": -6.25,
    "cvar_amount": -3125.0,
    "worse_than_var": true
  }
}
```

**Rate Limit:** 20 requests/minute

---

### POST /api/v2/risk/stress-test
Run stress test scenarios on portfolio.

**Request Body:**
```json
{
  "holdings": [...]
}
```

**Response:**
```json
{
  "success": true,
  "scenarios": [
    {
      "scenario": "2008 Crisis",
      "market_change": -50.0,
      "portfolio_value": 25000.0,
      "loss": -25000.0,
      "loss_percent": -50.0
    },
    {
      "scenario": "Flash Crash",
      "market_change": -20.0,
      "portfolio_value": 40000.0,
      "loss": -10000.0,
      "loss_percent": -20.0
    }
  ]
}
```

**Rate Limit:** 10 requests/minute

---

### POST /api/v2/risk/monitor
Real-time risk monitoring with alerts.

**Request Body:**
```json
{
  "holdings": [...],
  "market_prices": {"AAPL": 150.0, "MSFT": 380.0},
  "daily_pnl": -3000.0
}
```

**Response:**
```json
{
  "success": true,
  "status": {
    "risk_status": "ALERT",
    "alerts": [
      {
        "type": "WARNING",
        "message": "AAPL stop loss hit",
        "action": "SELL_POSITION"
      }
    ],
    "timestamp": "2026-09-27T12:00:00Z"
  }
}
```

**Rate Limit:** 30 requests/minute

---

### POST /api/v2/risk/position-check
Check position sizing violations.

**Request Body:**
```json
{
  "holdings": [...]
}
```

**Response:**
```json
{
  "success": true,
  "violations": {
    "has_violations": true,
    "violations": [
      {
        "symbol": "AAPL",
        "current_size": 15.0,
        "max_size": 10.0,
        "recommendation": "Reduce position by 5.0%"
      }
    ],
    "timestamp": "2026-09-27T12:00:00Z"
  }
}
```

**Rate Limit:** 20 requests/minute

---

## Common Response Codes

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

All endpoints have rate limits to prevent abuse:
- Most endpoints: 10-30 requests/minute
- Heavy computation endpoints: 5-10 requests/minute
- Public data endpoints: 30+ requests/minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Total requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Authentication

Most endpoints currently use rate limiting without authentication. For production use, implement:
- JWT authentication for trading operations
- API key authentication for broker connections
- User-specific rate limits
- Permission-based access control

## Testing

Test the API using curl or any HTTP client:

```bash
# Get news sentiment
curl http://localhost:8000/api/v2/sentiment/news/AAPL

# Run backtest
curl -X POST http://localhost:8000/api/v2/backtest/run \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","strategy_name":"momentum"}'

# Get fear/greed index
curl http://localhost:8000/api/v2/sentiment/fear-greed
```

## Summary

The API provides **40+ endpoints** across **8 phases**:

- **Phase 11**: 4 backtesting endpoints
- **Phase 12**: 4 sentiment analysis endpoints
- **Phase 13**: 5 trading automation endpoints
- **Phase 14**: 4 portfolio optimization endpoints
- **Phase 15**: 3 ML prediction endpoints
- **Phase 16**: 4 social trading endpoints
- **Phase 17**: 4 broker integration endpoints
- **Phase 18**: 6 risk management endpoints

All endpoints follow RESTful conventions, include proper error handling, rate limiting, and are ready for production use with appropriate authentication and monitoring.
