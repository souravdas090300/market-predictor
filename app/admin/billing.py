"""Billing analytics for revenue, churn, and LTV metrics."""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from enum import Enum

from ..core import config
from ..auth import UserManager, user_manager, SubscriptionPlan, SubscriptionStatus


class BillingPeriod(str, Enum):
    """Billing period types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class SubscriptionTier(str, Enum):
    """Subscription tiers with pricing."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# Pricing configuration (in USD)
TIER_PRICING = {
    SubscriptionTier.FREE: {
        "monthly": 0,
        "yearly": 0,
        "features": ["basic_predictions", "limited_watchlist", "community_support"]
    },
    SubscriptionTier.BASIC: {
        "monthly": 9.99,
        "yearly": 99.99,
        "features": ["basic_predictions", "unlimited_watchlist", "email_support", "advanced_signals"]
    },
    SubscriptionTier.PRO: {
        "monthly": 29.99,
        "yearly": 299.99,
        "features": ["all_basic", "real_time_predictions", "api_access", "priority_support", "advanced_analytics"]
    },
    SubscriptionTier.ENTERPRISE: {
        "monthly": 99.99,
        "yearly": 999.99,
        "features": ["all_pro", "custom_models", "dedicated_support", "sla_guarantee", "white_label"]
    }
}


class BillingAnalytics:
    """Manage billing analytics and metrics."""
    
    def __init__(self):
        self.analytics_file = config.ROOT / "data" / "billing_analytics.json"
        self.analytics_file.parent.mkdir(exist_ok=True)
        self._load_analytics()
    
    def _load_analytics(self):
        """Load analytics data from storage."""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file) as f:
                    self.analytics = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, IOError):
                self.analytics = {"daily_metrics": [], "monthly_metrics": []}
        else:
            self.analytics = {"daily_metrics": [], "monthly_metrics": []}
    
    def _save_analytics(self):
        """Save analytics data to storage."""
        with open(self.analytics_file, 'w') as f:
            json.dump(self.analytics, f, indent=2)
    
    def calculate_daily_metrics(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate daily billing metrics."""
        if date is None:
            date = datetime.now(timezone.utc)
        
        date_str = date.strftime("%Y-%m-%d")
        
        # Get all users
        users = user_manager.list_users()
        
        # Count subscriptions by tier
        tier_counts = defaultdict(int)
        active_subscriptions = 0
        total_mrr = 0.0  # Monthly Recurring Revenue
        
        for user in users:
            subscription = user.get("subscription", {})
            plan = subscription.get("plan", "free")
            status = subscription.get("status", "active")
            
            if status == "active":
                tier_counts[plan] += 1
                active_subscriptions += 1
                
                # Calculate MRR contribution
                if plan in TIER_PRICING:
                    monthly_price = TIER_PRICING[plan]["monthly"]
                    total_mrr += monthly_price
        
        # Calculate daily revenue (MRR / 30)
        daily_revenue = total_mrr / 30
        
        metrics = {
            "date": date_str,
            "total_users": len(users),
            "active_subscriptions": active_subscriptions,
            "tier_distribution": dict(tier_counts),
            "mrr": round(total_mrr, 2),
            "daily_revenue": round(daily_revenue, 2),
            "new_signups": self._count_new_signups(date_str),
            "cancellations": self._count_cancellations(date_str),
            "upgrades": self._count_plan_changes(date_str, "upgrade"),
            "downgrades": self._count_plan_changes(date_str, "downgrade")
        }
        
        return metrics
    
    def _count_new_signups(self, date_str: str) -> int:
        """Count new user signups for a date."""
        count = 0
        users = user_manager.list_users()
        
        for user in users:
            created_at = user.get("created_at", "")
            if created_at.startswith(date_str):
                count += 1
        
        return count
    
    def _count_cancellations(self, date_str: str) -> int:
        """Count subscription cancellations for a date."""
        # This would be tracked in audit logs in a real implementation
        # For now, return 0
        return 0
    
    def _count_plan_changes(self, date_str: str, change_type: str) -> int:
        """Count plan upgrades/downgrades for a date."""
        # This would be tracked in audit logs in a real implementation
        # For now, return 0
        return 0
    
    def calculate_churn_rate(self, days: int = 30) -> Dict[str, Any]:
        """Calculate churn rate for the last N days."""
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        users = user_manager.list_users()
        
        # Count active users at start of period
        active_at_start = 0
        cancelled_during_period = 0
        
        for user in users:
            subscription = user.get("subscription", {})
            created_at = datetime.fromisoformat(user.get("created_at", datetime.now(timezone.utc).isoformat()))
            
            if created_at < cutoff_date:
                # User existed at start of period
                status = subscription.get("status", "active")
                if status == "active":
                    active_at_start += 1
                elif status in ["cancelled", "expired"]:
                    cancelled_during_period += 1
        
        # Calculate churn rate
        churn_rate = (cancelled_during_period / active_at_start * 100) if active_at_start > 0 else 0
        
        return {
            "period_days": days,
            "active_at_start": active_at_start,
            "cancelled_during_period": cancelled_during_period,
            "churn_rate": round(churn_rate, 2)
        }
    
    def calculate_ltv(self) -> Dict[str, Any]:
        """Calculate Lifetime Value (LTV) by tier."""
        users = user_manager.list_users()
        
        tier_ltv = {}
        tier_revenue = defaultdict(float)
        tier_user_count = defaultdict(int)
        
        for user in users:
            subscription = user.get("subscription", {})
            plan = subscription.get("plan", "free")
            status = subscription.get("status", "active")
            
            if status == "active":
                tier_user_count[plan] += 1
                
                # Estimate LTV based on monthly price and average lifetime (assume 12 months)
                if plan in TIER_PRICING:
                    monthly_price = TIER_PRICING[plan]["monthly"]
                    tier_revenue[plan] += monthly_price * 12  # Assume 12-month lifetime
        
        # Calculate average LTV per tier
        for tier in tier_user_count:
            if tier_user_count[tier] > 0:
                tier_ltv[tier] = round(tier_revenue[tier] / tier_user_count[tier], 2)
        
        return {
            "tier_ltv": tier_ltv,
            "tier_user_count": dict(tier_user_count),
            "average_ltv": round(sum(tier_ltv.values()) / len(tier_ltv), 2) if tier_ltv else 0
        }
    
    def get_revenue_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get revenue trend for the last N days."""
        from datetime import timedelta
        
        trend = []
        for i in range(days):
            date = datetime.now(timezone.utc) - timedelta(days=days - i - 1)
            metrics = self.calculate_daily_metrics(date)
            trend.append(metrics)
        
        return trend
    
    def get_subscription_funnel(self) -> Dict[str, Any]:
        """Get subscription conversion funnel."""
        users = user_manager.list_users()
        
        funnel = {
            "total_users": len(users),
            "free_tier": 0,
            "basic_tier": 0,
            "pro_tier": 0,
            "enterprise_tier": 0,
            "conversion_rates": {}
        }
        
        for user in users:
            subscription = user.get("subscription", {})
            plan = subscription.get("plan", "free")
            
            if plan == "free":
                funnel["free_tier"] += 1
            elif plan == "basic":
                funnel["basic_tier"] += 1
            elif plan == "pro":
                funnel["pro_tier"] += 1
            elif plan == "enterprise":
                funnel["enterprise_tier"] += 1
        
        # Calculate conversion rates
        total = funnel["total_users"]
        if total > 0:
            funnel["conversion_rates"] = {
                "free_to_basic": round(funnel["basic_tier"] / funnel["free_tier"] * 100, 2) if funnel["free_tier"] > 0 else 0,
                "basic_to_pro": round(funnel["pro_tier"] / funnel["basic_tier"] * 100, 2) if funnel["basic_tier"] > 0 else 0,
                "pro_to_enterprise": round(funnel["enterprise_tier"] / funnel["pro_tier"] * 100, 2) if funnel["pro_tier"] > 0 else 0,
                "overall_paid_conversion": round((funnel["basic_tier"] + funnel["pro_tier"] + funnel["enterprise_tier"]) / total * 100, 2)
            }
        
        return funnel
    
    def get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top customers by revenue contribution."""
        users = user_manager.list_users()
        
        customer_revenue = []
        
        for user in users:
            subscription = user.get("subscription", {})
            plan = subscription.get("plan", "free")
            status = subscription.get("status", "active")
            
            if status == "active" and plan in TIER_PRICING:
                monthly_revenue = TIER_PRICING[plan]["monthly"]
                customer_revenue.append({
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "email": user["email"],
                    "plan": plan,
                    "monthly_revenue": monthly_revenue,
                    "created_at": user["created_at"]
                })
        
        # Sort by revenue descending
        customer_revenue.sort(key=lambda x: x["monthly_revenue"], reverse=True)
        
        return customer_revenue[:limit]
    
    def generate_billing_report(self, period: BillingPeriod = BillingPeriod.MONTHLY) -> Dict[str, Any]:
        """Generate comprehensive billing report."""
        metrics = self.calculate_daily_metrics()
        churn = self.calculate_churn_rate()
        ltv = self.calculate_ltv()
        funnel = self.get_subscription_funnel()
        top_customers = self.get_top_customers()
        
        return {
            "period": period.value,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
            "churn_analysis": churn,
            "ltv_analysis": ltv,
            "subscription_funnel": funnel,
            "top_customers": top_customers
        }


# Global billing analytics instance
billing_analytics = BillingAnalytics()
