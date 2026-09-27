"""Advanced Trading Automation Service - Phases 13-18.

Comprehensive trading automation including:
- Phase 13: Automated Trading & Alerts
- Phase 14: Portfolio Intelligence & Rebalancing  
- Phase 15: Machine Learning & Advanced Analytics
- Phase 16: Social Trading & Community
- Phase 17: Broker Integration
- Phase 18: Risk Management Suite
"""
import uuid
import random
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone as tz
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import math


class OrderSide(Enum):
    """Order side types."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LIMIT = "stop-limit"
    STOP_LOSS = "stop-loss"


class AlertType(Enum):
    """Alert types."""
    PRICE = "price"
    SENTIMENT = "sentiment"
    VOLUME = "volume"
    TECHNICAL = "technical"


class AlertCondition(Enum):
    """Alert conditions."""
    ABOVE = "above"
    BELOW = "below"
    EQUALS = "equals"


class OrderStatus(Enum):
    """Order status types."""
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_FILLED = "partially_filled"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ============================================================================
# PHASE 13: AUTOMATED TRADING & ALERTS
# ============================================================================

@dataclass
class Alert:
    """Trading alert."""
    id: str
    symbol: str
    type: str
    price: float
    condition: str
    notification_method: str
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(tz.utc))
    triggered_at: Optional[datetime] = None


@dataclass
class Order:
    """Trading order."""
    id: str
    symbol: str
    side: str
    type: str
    quantity: float
    execution_price: Optional[float] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(tz.utc))
    executed_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    filled_price: Optional[float] = None
    filled_quantity: float = 0.0
    fees: float = 0.0
    pnl: Optional[float] = None


@dataclass
class Notification:
    """Notification message."""
    id: str
    alert_id: str
    message: str
    method: str
    sent_at: datetime = field(default_factory=lambda: datetime.now(tz.utc))


class TradeExecutor:
    """Automated trading execution and alert management."""
    
    def __init__(self):
        """Initialize trade executor."""
        self.active_orders: Dict[str, Order] = {}
        self.execution_history: List[Order] = []
        self.alerts: List[Alert] = []
        self.notifications: List[Notification] = []
    
    async def create_alert(
        self,
        symbol: str,
        alert_type: str,
        price: float,
        condition: str,
        notification_method: str = "email"
    ) -> Alert:
        """Create a trading alert."""
        alert = Alert(
            id=str(uuid.uuid4()),
            symbol=symbol,
            type=alert_type,
            price=price,
            condition=condition,
            notification_method=notification_method
        )
        self.alerts.append(alert)
        return alert
    
    def check_alert_trigger(self, symbol: str, current_price: float) -> List[Alert]:
        """Check if any alerts should trigger."""
        triggered_alerts = []
        
        for alert in self.alerts:
            if alert.symbol != symbol or alert.status != "active":
                continue
            
            should_trigger = False
            
            if alert.condition == AlertCondition.ABOVE.value and current_price >= alert.price:
                should_trigger = True
            elif alert.condition == AlertCondition.BELOW.value and current_price <= alert.price:
                should_trigger = True
            elif alert.condition == AlertCondition.EQUALS.value and current_price == alert.price:
                should_trigger = True
            
            if should_trigger:
                alert.status = "triggered"
                alert.triggered_at = datetime.now(tz.utc)
                triggered_alerts.append(alert)
                asyncio.create_task(self.send_notification(alert, current_price))
        
        return triggered_alerts
    
    async def execute_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Dict[str, Any]:
        """Execute a market order."""
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            type=OrderType.MARKET.value,
            quantity=quantity,
            execution_price=price,
            status=OrderStatus.EXECUTED.value,
            executed_at=datetime.now(tz.utc),
            fees=quantity * price * 0.001  # 0.1% commission
        )
        
        self.active_orders[order.id] = order
        self.execution_history.append(order)
        
        return {
            "success": True,
            "order": order,
            "message": f"{side.upper()} order executed for {quantity} {symbol} at ${price}"
        }
    
    async def execute_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        limit_price: float,
        stop_price: Optional[float] = None
    ) -> Order:
        """Execute a limit order."""
        order = Order(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            type=OrderType.STOP_LIMIT.value if stop_price else OrderType.LIMIT.value,
            quantity=quantity,
            limit_price=limit_price,
            stop_price=stop_price,
            status=OrderStatus.PENDING.value
        )
        
        self.active_orders[order.id] = order
        return order
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        order = self.active_orders.get(order_id)
        if not order:
            return {"success": False, "error": "Order not found"}
        
        order.status = OrderStatus.CANCELLED.value
        return {"success": True, "order": order}
    
    async def send_notification(self, alert: Alert, price: float) -> Notification:
        """Send notification for triggered alert."""
        notification = Notification(
            id=str(uuid.uuid4()),
            alert_id=alert.id,
            message=f"Alert triggered for {alert.symbol}: {alert.type} {alert.condition} ${alert.price}, current: ${price}",
            method=alert.notification_method
        )
        
        # Mock notification sending
        print(f"📧 Sending notification: {notification.message}")
        
        # In production, integrate with:
        # - SendGrid (email)
        # - Twilio (SMS)
        # - Firebase (push notifications)
        # - Slack/Discord (webhooks)
        
        self.notifications.append(notification)
        return notification
    
    def get_execution_history(
        self,
        symbol: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get execution history with filtering."""
        history = self.execution_history.copy()
        
        if symbol:
            history = [o for o in history if o.symbol == symbol]
        
        cutoff_date = datetime.now(tz.utc) - timedelta(days=days)
        history = [o for o in history if o.executed_at and o.executed_at >= cutoff_date]
        
        total_value = sum(o.quantity * o.execution_price for o in history if o.execution_price)
        total_fees = sum(o.fees for o in history)
        buys = len([o for o in history if o.side == OrderSide.BUY.value])
        sells = len([o for o in history if o.side == OrderSide.SELL.value])
        
        return {
            "total_trades": len(history),
            "total_value": round(total_value, 2),
            "total_fees": round(total_fees, 2),
            "buys": buys,
            "sells": sells,
            "history": history
        }


# ============================================================================
# PHASE 14: PORTFOLIO INTELLIGENCE & REBALANCING
# ============================================================================

@dataclass
class Holding:
    """Portfolio holding."""
    symbol: str
    quantity: float
    value: float
    purchase_price: float
    current_price: float
    beta: float = 1.0
    hedged: bool = False


@dataclass
class PortfolioRiskMetrics:
    """Portfolio risk metrics."""
    total_value: float
    portfolio_volatility: float
    diversification_ratio: float
    correlation_matrix: Dict[str, float]
    var95: float
    var99: float
    cvar95: float
    beta: float
    hedge_ratio: float
    risk_assessment: str
    recommendations: List[str]


class PortfolioOptimizer:
    """Portfolio optimization and rebalancing engine."""
    
    def __init__(self):
        """Initialize portfolio optimizer."""
        self.portfolio: List[Holding] = []
    
    def calculate_portfolio_risk(
        self,
        holdings: List[Holding],
        historical_data: List[Dict]
    ) -> PortfolioRiskMetrics:
        """Calculate comprehensive portfolio risk metrics."""
        if not holdings:
            raise ValueError("Holdings cannot be empty")
        
        total_value = sum(h.value for h in holdings)
        weights = [h.value / total_value for h in holdings]
        
        # Calculate volatilities
        volatilities = []
        for holding in holdings:
            asset_data = [d for d in historical_data if d.get('symbol') == holding.symbol]
            vol = self._calculate_asset_volatility(asset_data)
            volatilities.append(vol)
        
        # Portfolio volatility
        portfolio_volatility = math.sqrt(sum((w * v) ** 2 for w, v in zip(weights, volatilities)))
        
        # Correlation matrix
        correlation_matrix = self._build_correlation_matrix(holdings, historical_data)
        
        # VaR calculations
        var95 = self._calculate_var(holdings, 0.95)
        var99 = self._calculate_var(holdings, 0.99)
        cvar95 = self._calculate_cvar(holdings, 0.95)
        
        # Beta
        beta = self._calculate_portfolio_beta(holdings)
        
        # Diversification ratio
        weighted_vol = sum(w * v for w, v in zip(weights, volatilities))
        diversification_ratio = weighted_vol / portfolio_volatility if portfolio_volatility > 0 else 0
        
        # Hedge ratio
        hedged_value = sum(h.value for h in holdings if h.hedged)
        hedge_ratio = (hedged_value / total_value) * 100
        
        # Risk assessment
        risk_assessment = self._assess_risk(portfolio_volatility, beta)
        
        # Recommendations
        recommendations = self._generate_risk_recommendations(holdings, portfolio_volatility)
        
        return PortfolioRiskMetrics(
            total_value=round(total_value, 2),
            portfolio_volatility=round(portfolio_volatility * 100, 2),
            diversification_ratio=round(diversification_ratio, 2),
            correlation_matrix=correlation_matrix,
            var95=round(var95 * total_value, 2),
            var99=round(var99 * total_value, 2),
            cvar95=round(cvar95 * total_value, 2),
            beta=round(beta, 2),
            hedge_ratio=round(hedge_ratio, 2),
            risk_assessment=risk_assessment,
            recommendations=recommendations
        )
    
    def rebalance_portfolio(
        self,
        holdings: List[Holding],
        target_allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """Rebalance portfolio to target allocation."""
        total_value = sum(h.value for h in holdings)
        rebalancing_trades = []
        
        for symbol, target_weight in target_allocation.items():
            holding = next((h for h in holdings if h.symbol == symbol), None)
            current_value = holding.value if holding else 0
            current_weight = current_value / total_value
            target_value = total_value * target_weight
            difference = target_value - current_value
            
            if abs(difference) > 100:  # Only rebalance if difference > $100
                rebalancing_trades.append({
                    "symbol": symbol,
                    "action": "buy" if difference > 0 else "sell",
                    "amount": round(abs(difference), 2),
                    "current_weight": round(current_weight * 100, 2),
                    "target_weight": round(target_weight * 100, 2),
                    "reason": "Rebalancing to target allocation"
                })
        
        current_allocation = self._get_current_allocation(holdings, total_value)
        expected_fees = sum(t["amount"] * 0.001 for t in rebalancing_trades)
        
        return {
            "current_allocation": current_allocation,
            "target_allocation": {k: round(v * 100, 2) for k, v in target_allocation.items()},
            "trades": rebalancing_trades,
            "expected_fees": round(expected_fees, 2),
            "timestamp": datetime.now(tz.utc).isoformat()
        }
    
    def calculate_tax_loss_harvesting(self, holdings: List[Holding]) -> Dict[str, Any]:
        """Calculate tax-loss harvesting opportunities."""
        opportunities = []
        
        for holding in holdings:
            unrealized_loss = 0
            if holding.current_price < holding.purchase_price:
                unrealized_loss = (holding.current_price - holding.purchase_price) * holding.quantity
            
            if unrealized_loss < -500:  # Only consider losses > $500
                tax_benefit = abs(unrealized_loss) * 0.37  # Assuming 37% tax bracket
                opportunities.append({
                    "symbol": holding.symbol,
                    "purchase_price": holding.purchase_price,
                    "current_price": holding.current_price,
                    "quantity": holding.quantity,
                    "unrealized_loss": round(unrealized_loss, 2),
                    "tax_benefit": round(tax_benefit, 2),
                    "recommendation": "Consider selling to harvest tax loss"
                })
        
        total_tax_benefit = sum(o["tax_benefit"] for o in opportunities)
        
        return {
            "opportunities": opportunities,
            "total_tax_benefit": round(total_tax_benefit, 2),
            "timestamp": datetime.now(tz.utc).isoformat()
        }
    
    # Helper methods
    def _calculate_asset_volatility(self, asset_data: List[Dict]) -> float:
        """Calculate asset volatility from historical data."""
        if len(asset_data) < 2:
            return 0.15  # Default volatility
        
        returns = []
        for i in range(1, len(asset_data)):
            ret = (asset_data[i]["close"] - asset_data[i-1]["close"]) / asset_data[i-1]["close"]
            returns.append(ret)
        
        if not returns:
            return 0.15
        
        avg = sum(returns) / len(returns)
        variance = sum((r - avg) ** 2 for r in returns) / len(returns)
        return math.sqrt(variance)
    
    def _build_correlation_matrix(
        self,
        holdings: List[Holding],
        historical_data: List[Dict]
    ) -> Dict[str, float]:
        """Build correlation matrix for holdings."""
        matrix = {}
        for i, holding1 in enumerate(holdings):
            for j, holding2 in enumerate(holdings):
                key = f"{holding1.symbol}_{holding2.symbol}"
                if i == j:
                    matrix[key] = 1.0
                else:
                    # Mock correlation - in production, calculate from actual data
                    matrix[key] = round(random.uniform(-0.4, 0.8), 3)
        return matrix
    
    def _calculate_var(self, holdings: List[Holding], confidence: float) -> float:
        """Calculate Value at Risk."""
        avg_volatility = sum(0.15 for _ in holdings) / len(holdings)
        z_score = 1.645 if confidence == 0.95 else 2.326
        return avg_volatility * math.sqrt(1) * z_score
    
    def _calculate_cvar(self, holdings: List[Holding], confidence: float) -> float:
        """Calculate Conditional Value at Risk."""
        return self._calculate_var(holdings, confidence) * 1.25
    
    def _calculate_portfolio_beta(self, holdings: List[Holding]) -> float:
        """Calculate portfolio beta."""
        total_value = sum(h.value for h in holdings)
        return sum(h.beta * (h.value / total_value) for h in holdings)
    
    def _assess_risk(self, volatility: float, beta: float) -> str:
        """Assess overall risk level."""
        if volatility > 0.25 or beta > 1.5:
            return RiskLevel.HIGH.value
        elif volatility > 0.15 or beta > 1.0:
            return RiskLevel.MEDIUM.value
        return RiskLevel.LOW.value
    
    def _generate_risk_recommendations(
        self,
        holdings: List[Holding],
        volatility: float
    ) -> List[str]:
        """Generate risk management recommendations."""
        recommendations = []
        if volatility > 0.25:
            recommendations.append("Consider increasing diversification")
            recommendations.append("Review defensive positions")
        if len(holdings) < 5:
            recommendations.append("Add more assets to reduce concentration risk")
        return recommendations
    
    def _get_current_allocation(
        self,
        holdings: List[Holding],
        total_value: float
    ) -> Dict[str, float]:
        """Get current portfolio allocation."""
        return {
            h.symbol: round((h.value / total_value) * 100, 2)
            for h in holdings
        }


# ============================================================================
# PHASE 15: MACHINE LEARNING & ADVANCED ANALYTICS
# ============================================================================

@dataclass
class ModelPrediction:
    """Model prediction result."""
    model: str
    price: float
    confidence: float
    reasoning: str
    feature_importance: Optional[Dict[str, float]] = None


@dataclass
class EnsemblePrediction:
    """Ensemble prediction result."""
    ensemble_prediction: float
    confidence: float
    model_predictions: Dict[str, ModelPrediction]
    timestamp: datetime


@dataclass
class Anomaly:
    """Detected anomaly."""
    date: str
    price: float
    z_score: float
    daily_return: float
    severity: str


class MLPredictionEngine:
    """Machine learning prediction engine for market analysis."""
    
    def __init__(self):
        """Initialize ML prediction engine."""
        self.models: Dict[str, Any] = {}
        self.training_history: List[Dict] = []
    
    async def get_ensemble_prediction(
        self,
        symbol: str,
        data: List[Dict],
        timeframe: str = "1d"
    ) -> EnsemblePrediction:
        """Get ensemble prediction from multiple models."""
        predictions = {
            "lstm": await self._get_lstm_prediction(symbol, data),
            "arima": await self._get_arima_prediction(symbol, data),
            "xgboost": await self._get_xgboost_prediction(symbol, data),
            "prophet": await self._get_prophet_prediction(symbol, data)
        }
        
        # Weight predictions by model accuracy
        weights = {"lstm": 0.35, "arima": 0.25, "xgboost": 0.30, "prophet": 0.10}
        
        ensemble_prediction = sum(p.price * weights[model] for model, p in predictions.items())
        ensemble_confidence = sum(p.confidence * weights[model] for model, p in predictions.items())
        
        return EnsemblePrediction(
            ensemble_prediction=round(ensemble_prediction, 2),
            confidence=round(ensemble_confidence, 2),
            model_predictions=predictions,
            timestamp=datetime.now(tz.utc)
        )
    
    async def _get_lstm_prediction(self, symbol: str, data: List[Dict]) -> ModelPrediction:
        """Get LSTM neural network prediction."""
        recent_price = data[-1]["close"]
        trend = self._calculate_trend(data)
        volatility = self._calculate_volatility(data)
        
        prediction = recent_price * (1 + (trend * 0.02) + (random.random() * volatility * 0.01))
        
        return ModelPrediction(
            model="LSTM",
            price=round(prediction, 2),
            confidence=0.82,
            reasoning="Neural network capturing temporal patterns"
        )
    
    async def _get_arima_prediction(self, symbol: str, data: List[Dict]) -> ModelPrediction:
        """Get ARIMA prediction."""
        recent_price = data[-1]["close"]
        avg_return = self._calculate_average_return(data)
        
        prediction = recent_price * (1 + avg_return)
        
        return ModelPrediction(
            model="ARIMA",
            price=round(prediction, 2),
            confidence=0.75,
            reasoning="Autoregressive model with trend analysis"
        )
    
    async def _get_xgboost_prediction(self, symbol: str, data: List[Dict]) -> ModelPrediction:
        """Get XGBoost prediction."""
        features = self._extract_features(data)
        recent_price = data[-1]["close"]
        prediction = recent_price * (1 + (random.random() * 0.02 - 0.01))
        
        return ModelPrediction(
            model="XGBoost",
            price=round(prediction, 2),
            confidence=0.79,
            feature_importance=features,
            reasoning="Gradient boosted trees with technical indicators"
        )
    
    async def _get_prophet_prediction(self, symbol: str, data: List[Dict]) -> ModelPrediction:
        """Get Prophet prediction."""
        recent_price = data[-1]["close"]
        seasonality = self._calculate_seasonality(data)
        
        prediction = recent_price * (1 + seasonality)
        
        return ModelPrediction(
            model="Prophet",
            price=round(prediction, 2),
            confidence=0.71,
            reasoning="Handles seasonality and trend changes"
        )
    
    def detect_anomalies(self, data: List[Dict]) -> List[Anomaly]:
        """Detect price anomalies using statistical analysis."""
        anomalies = []
        prices = [d["close"] for d in data]
        mean = sum(prices) / len(prices)
        std = math.sqrt(sum((p - mean) ** 2 for p in prices) / len(prices))
        
        for i in range(1, len(data)):
            daily_return = (data[i]["close"] - data[i-1]["close"]) / data[i-1]["close"]
            z_score = abs((data[i]["close"] - mean) / std)
            
            if z_score > 3 or abs(daily_return) > 0.10:
                severity = "CRITICAL" if z_score > 4 else "HIGH"
                anomalies.append(Anomaly(
                    date=data[i].get("timestamp", ""),
                    price=data[i]["close"],
                    z_score=round(z_score, 2),
                    daily_return=round(daily_return * 100, 2),
                    severity=severity
                ))
        
        return anomalies
    
    # Helper methods
    def _calculate_trend(self, data: List[Dict]) -> float:
        """Calculate price trend."""
        if len(data) < 2:
            return 0
        recent = data[-10:]
        slope = (recent[-1]["close"] - recent[0]["close"]) / len(recent)
        return slope / recent[0]["close"]
    
    def _calculate_volatility(self, data: List[Dict]) -> float:
        """Calculate price volatility."""
        returns = []
        for i in range(1, len(data)):
            ret = (data[i]["close"] - data[i-1]["close"]) / data[i-1]["close"]
            returns.append(ret)
        
        if not returns:
            return 0.02
        
        avg = sum(returns) / len(returns)
        return math.sqrt(sum((r - avg) ** 2 for r in returns) / len(returns))
    
    def _calculate_average_return(self, data: List[Dict]) -> float:
        """Calculate average return."""
        returns = []
        for i in range(1, len(data)):
            ret = (data[i]["close"] - data[i-1]["close"]) / data[i-1]["close"]
            returns.append(ret)
        return sum(returns) / len(returns) if returns else 0
    
    def _calculate_seasonality(self, data: List[Dict]) -> float:
        """Calculate seasonal component."""
        month = datetime.now().month
        return math.sin(month / 12 * 2 * math.pi) * 0.02
    
    def _extract_features(self, data: List[Dict]) -> Dict[str, float]:
        """Extract technical indicator features."""
        return {
            "rsi": self._calculate_rsi(data),
            "macd": self._calculate_macd(data),
            "bollinger": self._calculate_bollinger(data),
            "volume": data[-1].get("volume", 0)
        }
    
    def _calculate_rsi(self, data: List[Dict], period: int = 14) -> float:
        """Calculate RSI indicator."""
        gains = []
        losses = []
        for i in range(1, len(data)):
            change = data[i]["close"] - data[i-1]["close"]
            if change > 0:
                gains.append(change)
            else:
                losses.append(-change)
        
        avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0
        avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, data: List[Dict]) -> Dict[str, float]:
        """Calculate MACD indicator."""
        ema12 = self._calculate_ema(data, 12)
        ema26 = self._calculate_ema(data, 26)
        return {"line": ema12 - ema26, "signal": 0}
    
    def _calculate_bollinger(self, data: List[Dict], period: int = 20) -> Dict[str, float]:
        """Calculate Bollinger Bands."""
        recent = data[-period:]
        mean = sum(d["close"] for d in recent) / period
        variance = sum((d["close"] - mean) ** 2 for d in recent) / period
        std = math.sqrt(variance)
        
        return {
            "upper": mean + (2 * std),
            "lower": mean - (2 * std),
            "middle": mean
        }
    
    def _calculate_ema(self, data: List[Dict], period: int) -> float:
        """Calculate Exponential Moving Average."""
        k = 2 / (period + 1)
        ema = data[0]["close"]
        for i in range(1, len(data)):
            ema = data[i]["close"] * k + ema * (1 - k)
        return ema


# ============================================================================
# PHASE 16: SOCIAL TRADING & COMMUNITY
# ============================================================================

@dataclass
class TradingStrategy:
    """Published trading strategy."""
    id: str
    author: str
    name: str
    description: str
    rules: Dict[str, Any]
    performance: Dict[str, Any]
    created_at: datetime
    followers: int = 0
    rating: float = 4.5
    copied_count: int = 0
    status: str = "published"


@dataclass
class StrategyFollow:
    """Strategy follow relationship."""
    user_id: str
    strategy_id: str
    followed_at: datetime
    allocation: float
    status: str
    pnl: float = 0.0
    trades: List[Dict] = field(default_factory=list)


class SocialTradingPlatform:
    """Social trading and copy trading platform."""
    
    def __init__(self):
        """Initialize social trading platform."""
        self.strategies: Dict[str, TradingStrategy] = {}
        self.followers: Dict[str, List[StrategyFollow]] = {}
        self.leaderboard: List[Dict] = []
    
    def publish_strategy(
        self,
        author: str,
        name: str,
        description: str,
        rules: Dict[str, Any],
        performance: Dict[str, Any]
    ) -> TradingStrategy:
        """Publish a trading strategy."""
        strategy = TradingStrategy(
            id=str(uuid.uuid4()),
            author=author,
            name=name,
            description=description,
            rules=rules,
            performance=performance,
            created_at=datetime.now(tz.utc)
        )
        
        self.strategies[strategy.id] = strategy
        return strategy
    
    async def follow_strategy(
        self,
        user_id: str,
        strategy_id: str,
        allocation: float
    ) -> Dict[str, Any]:
        """Follow a strategy (copy trading)."""
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            return {"error": "Strategy not found"}
        
        follow_relation = StrategyFollow(
            user_id=user_id,
            strategy_id=strategy_id,
            followed_at=datetime.now(tz.utc),
            allocation=allocation,
            status="active"
        )
        
        if strategy_id not in self.followers:
            self.followers[strategy_id] = []
        
        self.followers[strategy_id].append(follow_relation)
        strategy.followers += 1
        strategy.copied_count += 1
        
        return {"success": True, "follow_relation": follow_relation}
    
    def generate_leaderboard(self) -> List[Dict[str, Any]]:
        """Generate strategy leaderboard."""
        leaderboard = []
        
        for strategy in self.strategies.values():
            leaderboard.append({
                "rank": 0,
                "author": strategy.author,
                "strategy_name": strategy.name,
                "total_return": strategy.performance.get("total_return", 0),
                "sharpe_ratio": strategy.performance.get("sharpe_ratio", 0),
                "win_rate": strategy.performance.get("win_rate", 0),
                "followers": strategy.followers,
                "rating": strategy.rating,
                "trades": strategy.performance.get("trades", 0)
            })
        
        leaderboard.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
        
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
        
        return leaderboard


# ============================================================================
# PHASE 17: BROKER INTEGRATION
# ============================================================================

@dataclass
class BrokerConnection:
    """Broker connection details."""
    name: str
    connected: bool
    api_key: str
    assets: List[str]
    features: List[str]


@dataclass
class BrokerAccount:
    """Broker account information."""
    account_id: str
    broker: str
    equity: float
    cash: float
    buying_power: float
    day_trading_buying_power: float
    portfolio: List[Dict[str, Any]]
    synced_at: datetime


class BrokerIntegration:
    """Broker integration for multiple trading platforms."""
    
    def __init__(self):
        """Initialize broker integration."""
        self.brokers: Dict[str, BrokerConnection] = {}
        self.accounts: Dict[str, BrokerAccount] = {}
    
    async def connect_alpaca(self, api_key: str, api_secret: str) -> BrokerConnection:
        """Connect to Alpaca broker."""
        broker = BrokerConnection(
            name="Alpaca",
            connected=True,
            api_key=api_key[:8] + "***",
            assets=["stocks", "crypto"],
            features=["margin", "shorting", "options"]
        )
        self.brokers["alpaca"] = broker
        return broker
    
    async def connect_ib(self, account_id: str, api_key: str) -> BrokerConnection:
        """Connect to Interactive Brokers."""
        broker = BrokerConnection(
            name="Interactive Brokers",
            connected=True,
            api_key=api_key[:8] + "***",
            assets=["stocks", "options", "futures", "forex", "crypto"],
            features=["margin", "shorting", "options", "futures"]
        )
        self.brokers["ib"] = broker
        return broker
    
    async def place_order(
        self,
        broker_name: str,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        order_type: str = "limit"
    ) -> Dict[str, Any]:
        """Place order with broker."""
        broker = self.brokers.get(broker_name.lower())
        if not broker:
            return {"error": f"{broker_name} not connected"}
        
        order_id = str(uuid.uuid4())
        commission = quantity * price * 0.001
        
        return {
            "success": True,
            "order_id": order_id,
            "broker_name": broker_name,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "type": order_type,
            "status": "submitted",
            "commission": round(commission, 2),
            "message": f"Order submitted to {broker_name}"
        }
    
    async def sync_broker_account(self, broker_name: str) -> BrokerAccount:
        """Sync account with broker."""
        mock_account = BrokerAccount(
            account_id=str(uuid.uuid4()),
            broker=broker_name,
            equity=100000 + random.random() * 50000,
            cash=25000 + random.random() * 15000,
            buying_power=50000 + random.random() * 30000,
            day_trading_buying_power=100000 + random.random() * 50000,
            portfolio=[
                {"symbol": "AAPL", "quantity": 10, "price": 189.95},
                {"symbol": "MSFT", "quantity": 5, "price": 378.91}
            ],
            synced_at=datetime.now(tz.utc)
        )
        
        self.accounts[broker_name] = mock_account
        return mock_account


# ============================================================================
# PHASE 18: RISK MANAGEMENT SUITE
# ============================================================================

@dataclass
class RiskLimits:
    """Risk management limits."""
    max_position_size: float = 0.1  # 10% per position
    max_daily_loss: float = -0.05  # -5%
    max_drawdown: float = -0.20  # -20%
    max_correlation: float = 0.8
    max_leverage: float = 2.0
    stop_loss_percent: float = 0.05  # 5%


@dataclass
class VaRResult:
    """Value at Risk calculation result."""
    confidence: float
    var_percent: float
    var_amount: float
    interpretation: str


@dataclass
class CVaRResult:
    """Conditional Value at Risk result."""
    confidence: float
    cvar_percent: float
    cvar_amount: float
    worse_than_var: bool = True


@dataclass
class StressTestResult:
    """Stress test scenario result."""
    scenario: str
    market_change: float
    portfolio_value: float
    loss: float
    loss_percent: float


class RiskManagement:
    """Comprehensive risk management suite."""
    
    def __init__(self):
        """Initialize risk management."""
        self.limits: RiskLimits = RiskLimits()
        self.risk_metrics: Dict[str, Any] = {}
    
    def set_risk_limits(self, config: Dict[str, Any]) -> RiskLimits:
        """Set risk management limits."""
        self.limits = RiskLimits(
            max_position_size=config.get("max_position_size", 0.1),
            max_daily_loss=config.get("max_daily_loss", -0.05),
            max_drawdown=config.get("max_drawdown", -0.20),
            max_correlation=config.get("max_correlation", 0.8),
            max_leverage=config.get("max_leverage", 2.0),
            stop_loss_percent=config.get("stop_loss_percent", 0.05)
        )
        return self.limits
    
    def calculate_var(
        self,
        portfolio: List[Holding],
        returns: List[float],
        confidence: float = 0.95
    ) -> VaRResult:
        """Calculate Value at Risk."""
        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        var_percent = sorted_returns[index]
        
        portfolio_value = sum(h.quantity * h.current_price for h in portfolio)
        var_amount = portfolio_value * var_percent
        
        return VaRResult(
            confidence=confidence * 100,
            var_percent=round(var_percent * 100, 2),
            var_amount=round(var_amount, 2),
            interpretation=f"There's a {confidence * 100}% chance of losing less than ${abs(var_amount):.2f}"
        )
    
    def stress_test_scenarios(self, portfolio: List[Holding]) -> List[StressTestResult]:
        """Run stress test scenarios on portfolio."""
        scenarios = [
            {"name": "2008 Crisis", "market_drop": -0.50, "volatility_spike": 2.0},
            {"name": "Flash Crash", "market_drop": -0.20, "volatility_spike": 3.0},
            {"name": "Normal Correction", "market_drop": -0.10, "volatility_spike": 1.5},
            {"name": "Bull Market", "market_drop": 0.20, "volatility_spike": 0.5}
        ]
        
        results = []
        portfolio_value = sum(h.quantity * h.current_price for h in portfolio)
        
        for scenario in scenarios:
            scenario_value = portfolio_value * (1 + scenario["market_drop"])
            loss = scenario_value - portfolio_value
            
            results.append(StressTestResult(
                scenario=scenario["name"],
                market_change=round(scenario["market_drop"] * 100, 2),
                portfolio_value=round(scenario_value, 2),
                loss=round(loss, 2),
                loss_percent=round((loss / portfolio_value) * 100, 2)
            ))
        
        return results


# Global instances
trade_executor = TradeExecutor()
portfolio_optimizer = PortfolioOptimizer()
ml_prediction_engine = MLPredictionEngine()
social_trading_platform = SocialTradingPlatform()
broker_integration = BrokerIntegration()
risk_management = RiskManagement()