"""Risk calculation and management module."""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RiskMetrics:
    """Risk metrics for a position or portfolio."""
    position_size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_per_share: float
    risk_percent: float
    reward_per_share: float
    reward_percent: float
    risk_reward_ratio: float
    position_value: float
    max_loss: float
    max_gain: float
    volatility: float
    var_95: float  # Value at Risk at 95% confidence


class RiskCalculator:
    """Calculate risk metrics for trading positions."""
    
    def __init__(self, account_balance: float = 100000, max_risk_percent: float = 2.0):
        """
        Initialize risk calculator.
        
        Args:
            account_balance: Total account balance
            max_risk_percent: Maximum risk per trade as percentage of balance
        """
        self.account_balance = account_balance
        self.max_risk_percent = max_risk_percent
        self.max_risk_amount = account_balance * (max_risk_percent / 100)
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        max_risk_percent: Optional[float] = None
    ) -> Dict:
        """
        Calculate optimal position size based on risk parameters.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            max_risk_percent: Override default max risk percent
        
        Returns:
            Dictionary with position sizing recommendations
        """
        if max_risk_percent:
            max_risk_amount = self.account_balance * (max_risk_percent / 100)
        else:
            max_risk_amount = self.max_risk_amount
        
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return {
                'error': 'Stop loss cannot be equal to entry price',
                'shares': 0,
                'position_value': 0
            }
        
        # Calculate number of shares
        shares = int(max_risk_amount / risk_per_share)
        
        # Calculate position value
        position_value = shares * entry_price
        
        # Check if position fits in account
        position_percent = (position_value / self.account_balance) * 100
        
        return {
            'account_balance': self.account_balance,
            'max_risk_percent': max_risk_percent or self.max_risk_percent,
            'max_risk_amount': max_risk_amount,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'risk_per_share': risk_per_share,
            'shares': shares,
            'position_value': position_value,
            'position_percent': position_percent,
            'leverage': self.account_balance / position_value if position_value > 0 else 0
        }
    
    def calculate_risk_metrics(
        self,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        shares: int,
        historical_data: Optional[pd.DataFrame] = None
    ) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics.
        
        Args:
            symbol: Asset symbol
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            shares: Number of shares
            historical_data: Historical price data for volatility calculation
        
        Returns:
            RiskMetrics object with all calculated metrics
        """
        position_size = shares * entry_price
        risk_per_share = abs(entry_price - stop_loss)
        reward_per_share = abs(take_profit - entry_price)
        
        risk_percent = (risk_per_share / entry_price) * 100
        reward_percent = (reward_per_share / entry_price) * 100
        risk_reward_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
        
        max_loss = risk_per_share * shares
        max_gain = reward_per_share * shares
        
        # Calculate volatility from historical data
        volatility = 0.0
        var_95 = 0.0
        
        if historical_data is not None and len(historical_data) > 20:
            returns = historical_data['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
            
            # Calculate VaR at 95% confidence
            var_95 = np.percentile(returns, 5) * position_size
        
        return RiskMetrics(
            position_size=position_size,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_per_share=risk_per_share,
            risk_percent=risk_percent,
            reward_per_share=reward_per_share,
            reward_percent=reward_percent,
            risk_reward_ratio=risk_reward_ratio,
            position_value=position_size,
            max_loss=max_loss,
            max_gain=max_gain,
            volatility=volatility,
            var_95=var_95
        )
    
    def portfolio_risk_analysis(
        self,
        positions: List[Dict],
        correlation_matrix: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Analyze portfolio-level risk.
        
        Args:
            positions: List of position dictionaries
            correlation_matrix: Correlation matrix between assets
        
        Returns:
            Dictionary with portfolio risk metrics
        """
        total_value = sum(pos['value'] for pos in positions)
        total_risk = sum(pos['max_loss'] for pos in positions)
        total_potential_gain = sum(pos['max_gain'] for pos in positions)
        
        # Calculate concentration risk
        position_weights = [pos['value'] / total_value for pos in positions]
        max_concentration = max(position_weights)
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        hhi = sum(w ** 2 for w in position_weights)
        
        # Calculate portfolio volatility if correlation matrix provided
        portfolio_volatility = 0.0
        if correlation_matrix is not None and len(positions) > 1:
            weights = np.array(position_weights)
            volatilities = np.array([pos.get('volatility', 0.20) for pos in positions])
            portfolio_variance = np.dot(weights, np.dot(correlation_matrix, weights * volatilities))
            portfolio_volatility = np.sqrt(portfolio_variance)
        
        return {
            'total_value': total_value,
            'total_risk': total_risk,
            'total_risk_percent': (total_risk / total_value) * 100,
            'total_potential_gain': total_potential_gain,
            'total_potential_gain_percent': (total_potential_gain / total_value) * 100,
            'max_concentration': max_concentration,
            'hhi': hhi,
            'diversification_score': 1 - hhi,  # Higher is better
            'portfolio_volatility': portfolio_volatility,
            'position_count': len(positions),
            'account_balance': self.account_balance,
            'utilization_percent': (total_value / self.account_balance) * 100
        }
    
    def kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Calculate Kelly Criterion for optimal position sizing.
        
        Args:
            win_rate: Win rate as decimal (0.5 = 50%)
            avg_win: Average win amount
            avg_loss: Average loss amount
        
        Returns:
            Kelly percentage as decimal
        """
        if avg_loss == 0:
            return 0.0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Cap Kelly at 25% to prevent overbetting
        return min(max(kelly, 0.25), 0.0)


def calculate_position_risk(
    symbol: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    account_balance: float = 100000,
    max_risk_percent: float = 2.0
) -> Dict:
    """
    Quick risk calculation for a single position.
    
    Args:
        symbol: Asset symbol
        entry_price: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
        account_balance: Account balance
        max_risk_percent: Maximum risk percentage
    
    Returns:
        Dictionary with risk analysis
    """
    calculator = RiskCalculator(account_balance, max_risk_percent)
    
    # Calculate position size
    sizing = calculator.calculate_position_size(entry_price, stop_loss)
    
    if 'error' in sizing:
        return sizing
    
    # Calculate comprehensive metrics
    metrics = calculator.calculate_risk_metrics(
        symbol=symbol,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        shares=sizing['shares']
    )
    
    return {
        'symbol': symbol,
        'position_sizing': sizing,
        'risk_metrics': {
            'entry_price': metrics.entry_price,
            'stop_loss': metrics.stop_loss,
            'take_profit': metrics.take_profit,
            'risk_per_share': metrics.risk_per_share,
            'risk_percent': metrics.risk_percent,
            'reward_per_share': metrics.reward_per_share,
            'reward_percent': metrics.reward_percent,
            'risk_reward_ratio': metrics.risk_reward_ratio,
            'position_value': metrics.position_value,
            'max_loss': metrics.max_loss,
            'max_gain': metrics.max_gain,
            'volatility': metrics.volatility,
            'var_95': metrics.var_95
        },
        'recommendation': _generate_risk_recommendation(metrics)
    }


def _generate_risk_recommendation(metrics: RiskMetrics) -> str:
    """Generate risk recommendation based on metrics."""
    if metrics.risk_reward_ratio < 1.0:
        return "HIGH RISK: Risk/Reward ratio is less than 1. Consider adjusting stop loss or take profit."
    elif metrics.risk_reward_ratio < 1.5:
        return "MODERATE RISK: Risk/Reward ratio is acceptable but could be improved."
    elif metrics.risk_reward_ratio < 2.5:
        return "GOOD RISK: Risk/Reward ratio is favorable."
    else:
        return "EXCELLENT RISK: Risk/Reward ratio is very favorable."