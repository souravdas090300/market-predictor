"""Feature limits system for subscription tier access control."""
import os
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from pathlib import Path
from enum import Enum

from ..core import config
from ..auth import SubscriptionPlan


class FeatureType(str, Enum):
    """Types of features that can be limited."""
    API_REQUESTS = "api_requests"
    PREDICTIONS = "predictions"
    WATCHLIST_SIZE = "watchlist_size"
    REAL_TIME_DATA = "real_time_data"
    ADVANCED_SIGNALS = "advanced_signals"
    BACKTESTING = "backtesting"
    CUSTOM_MODELS = "custom_models"
    API_ACCESS = "api_access"
    WEBHOOKS = "webhooks"
    EXPORT_DATA = "export_data"
    TEAM_SHARING = "team_sharing"
    PRIORITY_SUPPORT = "priority_support"
    CUSTOM_BRANDING = "custom_branding"
    WHITE_LABEL = "white_label"


class FeatureLimit:
    """Feature limit configuration."""
    
    def __init__(
        self,
        feature: FeatureType,
        limits: Dict[str, int],
        description: str
    ):
        self.feature = feature
        self.limits = limits  # Dict of plan -> limit value
        self.description = description
    
    def get_limit(self, plan: SubscriptionPlan) -> Optional[int]:
        """Get limit for a specific plan."""
        return self.limits.get(plan.value)
    
    def has_access(self, plan: SubscriptionPlan) -> bool:
        """Check if a plan has access to this feature."""
        return plan.value in self.limits and self.limits[plan.value] > 0


class FeatureLimitsManager:
    """Manage feature limits by subscription tier."""
    
    def __init__(self):
        self.config_file = config.ROOT / "data" / "feature_limits.json"
        self.config_file.parent.mkdir(exist_ok=True)
        self.features: Dict[FeatureType, FeatureLimit] = {}
        self._load_config()
    
    def _load_config(self):
        """Load feature limits configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config_data = json.load(f)
                    for feature_name, feature_data in config_data.items():
                        feature = FeatureType(feature_name)
                        self.features[feature] = FeatureLimit(
                            feature=feature,
                            limits=feature_data["limits"],
                            description=feature_data["description"]
                        )
            except (FileNotFoundError, json.JSONDecodeError, KeyError, IOError):
                self._initialize_default_config()
        else:
            self._initialize_default_config()
    
    def _save_config(self):
        """Save feature limits configuration."""
        config_data = {}
        for feature, limit in self.features.items():
            config_data[feature.value] = {
                "limits": limit.limits,
                "description": limit.description
            }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def _initialize_default_config(self):
        """Initialize default feature limits."""
        self.features = {
            FeatureType.API_REQUESTS: FeatureLimit(
                feature=FeatureType.API_REQUESTS,
                limits={
                    "free": 100,
                    "basic": 1000,
                    "pro": 10000,
                    "enterprise": -1  # Unlimited
                },
                description="API requests per hour"
            ),
            FeatureType.PREDICTIONS: FeatureLimit(
                feature=FeatureType.PREDICTIONS,
                limits={
                    "free": 50,
                    "basic": 500,
                    "pro": 5000,
                    "enterprise": -1
                },
                description="Predictions per day"
            ),
            FeatureType.WATCHLIST_SIZE: FeatureLimit(
                feature=FeatureType.WATCHLIST_SIZE,
                limits={
                    "free": 10,
                    "basic": 50,
                    "pro": 200,
                    "enterprise": -1
                },
                description="Maximum watchlist size"
            ),
            FeatureType.REAL_TIME_DATA: FeatureLimit(
                feature=FeatureType.REAL_TIME_DATA,
                limits={
                    "free": 0,
                    "basic": 1,
                    "pro": 1,
                    "enterprise": 1
                },
                description="Real-time data access (1 = enabled, 0 = disabled)"
            ),
            FeatureType.ADVANCED_SIGNALS: FeatureLimit(
                feature=FeatureType.ADVANCED_SIGNALS,
                limits={
                    "free": 0,
                    "basic": 1,
                    "pro": 1,
                    "enterprise": 1
                },
                description="Advanced trading signals (1 = enabled, 0 = disabled)"
            ),
            FeatureType.BACKTESTING: FeatureLimit(
                feature=FeatureType.BACKTESTING,
                limits={
                    "free": 0,
                    "basic": 10,
                    "pro": 100,
                    "enterprise": -1
                },
                description="Backtesting runs per month"
            ),
            FeatureType.CUSTOM_MODELS: FeatureLimit(
                feature=FeatureType.CUSTOM_MODELS,
                limits={
                    "free": 0,
                    "basic": 0,
                    "pro": 1,
                    "enterprise": -1
                },
                description="Custom prediction models"
            ),
            FeatureType.API_ACCESS: FeatureLimit(
                feature=FeatureType.API_ACCESS,
                limits={
                    "free": 0,
                    "basic": 1,
                    "pro": 1,
                    "enterprise": 1
                },
                description="API access (1 = enabled, 0 = disabled)"
            ),
            FeatureType.WEBHOOKS: FeatureLimit(
                feature=FeatureType.WEBHOOKS,
                limits={
                    "free": 0,
                    "basic": 0,
                    "pro": 5,
                    "enterprise": -1
                },
                description="Webhook integrations"
            ),
            FeatureType.EXPORT_DATA: FeatureLimit(
                feature=FeatureType.EXPORT_DATA,
                limits={
                    "free": 0,
                    "basic": 1,
                    "pro": 1,
                    "enterprise": 1
                },
                description="Data export (1 = enabled, 0 = disabled)"
            ),
            FeatureType.TEAM_SHARING: FeatureLimit(
                feature=FeatureType.TEAM_SHARING,
                limits={
                    "free": 0,
                    "basic": 0,
                    "pro": 5,
                    "enterprise": -1
                },
                description="Team members for sharing"
            ),
            FeatureType.PRIORITY_SUPPORT: FeatureLimit(
                feature=FeatureType.PRIORITY_SUPPORT,
                limits={
                    "free": 0,
                    "basic": 0,
                    "pro": 1,
                    "enterprise": 1
                },
                description="Priority support (1 = enabled, 0 = disabled)"
            ),
            FeatureType.CUSTOM_BRANDING: FeatureLimit(
                feature=FeatureType.CUSTOM_BRANDING,
                limits={
                    "free": 0,
                    "basic": 0,
                    "pro": 0,
                    "enterprise": 1
                },
                description="Custom branding (1 = enabled, 0 = disabled)"
            ),
            FeatureType.WHITE_LABEL: FeatureLimit(
                feature=FeatureType.WHITE_LABEL,
                limits={
                    "free": 0,
                    "basic": 0,
                    "pro": 0,
                    "enterprise": 1
                },
                description="White label solution (1 = enabled, 0 = disabled)"
            )
        }
        self._save_config()
    
    def get_limit(self, feature: FeatureType, plan: SubscriptionPlan) -> Optional[int]:
        """Get limit for a specific feature and plan."""
        if feature not in self.features:
            return None
        return self.features[feature].get_limit(plan)
    
    def has_access(self, feature: FeatureType, plan: SubscriptionPlan) -> bool:
        """Check if a plan has access to a feature."""
        if feature not in self.features:
            return False
        return self.features[feature].has_access(plan)
    
    def check_limit(
        self,
        feature: FeatureType,
        plan: SubscriptionPlan,
        current_usage: int
    ) -> Dict[str, Any]:
        """Check if current usage is within limits."""
        limit = self.get_limit(feature, plan)
        
        if limit is None:
            return {
                "allowed": False,
                "reason": "Feature not configured",
                "limit": None,
                "current_usage": current_usage
            }
        
        if limit == -1:  # Unlimited
            return {
                "allowed": True,
                "reason": "Unlimited",
                "limit": "unlimited",
                "current_usage": current_usage
            }
        
        if current_usage >= limit:
            return {
                "allowed": False,
                "reason": "Limit exceeded",
                "limit": limit,
                "current_usage": current_usage
            }
        
        return {
            "allowed": True,
            "reason": "Within limits",
            "limit": limit,
            "current_usage": current_usage,
            "remaining": limit - current_usage
        }
    
    def update_limit(self, feature: FeatureType, plan: SubscriptionPlan, new_limit: int) -> bool:
        """Update limit for a specific feature and plan."""
        if feature not in self.features:
            return False
        
        self.features[feature].limits[plan.value] = new_limit
        self._save_config()
        return True
    
    def get_user_limits(self, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Get all limits for a specific plan."""
        limits = {}
        for feature, limit in self.features.items():
            limits[feature.value] = {
                "limit": limit.get_limit(plan),
                "description": limit.description,
                "has_access": limit.has_access(plan)
            }
        return limits
    
    def get_feature_comparison(self) -> Dict[str, Any]:
        """Get feature comparison across all plans."""
        comparison = {}
        for feature, limit in self.features.items():
            comparison[feature.value] = {
                "description": limit.description,
                "limits": limit.limits
            }
        return comparison
    
    def get_available_features(self, plan: SubscriptionPlan) -> List[str]:
        """Get list of available features for a plan."""
        available = []
        for feature, limit in self.features.items():
            if limit.has_access(plan):
                available.append(feature.value)
        return available
    
    def upgrade_features(self, old_plan: SubscriptionPlan, new_plan: SubscriptionPlan) -> List[str]:
        """Get list of features that will be unlocked with upgrade."""
        old_features = set(self.get_available_features(old_plan))
        new_features = set(self.get_available_features(new_plan))
        return list(new_features - old_features)
    
    def downgrade_features(self, old_plan: SubscriptionPlan, new_plan: SubscriptionPlan) -> List[str]:
        """Get list of features that will be lost with downgrade."""
        old_features = set(self.get_available_features(old_plan))
        new_features = set(self.get_available_features(new_plan))
        return list(old_features - new_features)


# Global feature limits manager
feature_limits_manager = FeatureLimitsManager()


def check_feature_access(feature: FeatureType, plan: SubscriptionPlan) -> bool:
    """Convenience function to check feature access."""
    # If subscription mode is disabled, all users have access to all features
    if not config.SUBSCRIPTION_MODE_ENABLED:
        return True
    return feature_limits_manager.has_access(feature, plan)


def check_feature_limit(feature: FeatureType, plan: SubscriptionPlan, current_usage: int) -> Dict[str, Any]:
    """Convenience function to check feature limits."""
    # If subscription mode is disabled, all users have unlimited access
    if not config.SUBSCRIPTION_MODE_ENABLED:
        return {
            "allowed": True,
            "reason": "Subscription mode disabled - unlimited access",
            "limit": "unlimited",
            "current_usage": current_usage
        }
    return feature_limits_manager.check_limit(feature, plan, current_usage)


def get_user_effective_plan(user_plan: SubscriptionPlan) -> SubscriptionPlan:
    """Get the effective plan for a user considering subscription mode."""
    # If subscription mode is disabled, treat all users as enterprise (full access)
    if not config.SUBSCRIPTION_MODE_ENABLED:
        return SubscriptionPlan.ENTERPRISE
    return user_plan
