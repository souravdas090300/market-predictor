"""Admin module for administrative functions."""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

from ..core import config
from ..security import (
    verify_password, create_access_token, create_refresh_token,
    decode_token, AuthenticationError
)
from ..auth import UserManager, user_manager


# Admin configuration file
ADMIN_CONFIG_FILE = config.ROOT / "data" / "admin_config.json"
ADMIN_CONFIG_FILE.parent.mkdir(exist_ok=True)


class AdminManager:
    """Manage administrative functions."""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load admin configuration."""
        if ADMIN_CONFIG_FILE.exists():
            try:
                with open(ADMIN_CONFIG_FILE) as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, IOError):
                pass
        
        # Default configuration
        return {
            "rate_limiting_enabled": True,
            "rate_limits": {
                "watchlist": "100/minute",
                "signal": "60/minute",
                "material": "30/minute",
                "bulk": "10/minute",
                "chart": "60/minute",
                "risk": "30/minute",
                "strategy": "20/minute",
                "news": "30/minute",
                "correlation": "20/minute"
            },
            "maintenance_mode": False,
            "allowed_ips": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _save_config(self):
        """Save admin configuration."""
        self.config["updated_at"] = datetime.now(timezone.utc).isoformat()
        with open(ADMIN_CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def is_admin_user(self, username: str) -> bool:
        """Check if user is admin (superuser check)."""
        from ..auth import user_manager
        return user_manager.is_superuser_by_username(username)
    
    def enable_rate_limiting(self, enabled: bool) -> Dict[str, Any]:
        """Enable or disable rate limiting globally.
        
        When rate limiting is enabled, subscription mode is also enabled to restrict
        non-subscribed users to basic features. When disabled, all users get full access.
        """
        self.config["rate_limiting_enabled"] = enabled
        self._save_config()
        
        # Sync subscription mode with rate limiting
        # When rate limiting is ON, enable subscription mode (restrict features)
        # When rate limiting is OFF, disable subscription mode (full access for all)
        config.SUBSCRIPTION_MODE_ENABLED = enabled
        
        return {
            "message": f"Rate limiting {'enabled' if enabled else 'disabled'}. Subscription mode {'enabled' if enabled else 'disabled'}.",
            "rate_limiting_enabled": enabled,
            "subscription_mode_enabled": enabled,
            "updated_at": self.config["updated_at"]
        }
    
    def update_rate_limit(self, endpoint: str, limit: str) -> Dict[str, Any]:
        """Update rate limit for a specific endpoint."""
        if "rate_limits" not in self.config:
            self.config["rate_limits"] = {}
        
        self.config["rate_limits"][endpoint] = limit
        self._save_config()
        
        return {
            "message": f"Rate limit updated for {endpoint}",
            "endpoint": endpoint,
            "new_limit": limit,
            "updated_at": self.config["updated_at"]
        }
    
    def get_rate_limits(self) -> Dict[str, Any]:
        """Get current rate limit configuration."""
        return {
            "rate_limiting_enabled": self.config.get("rate_limiting_enabled", True),
            "rate_limits": self.config.get("rate_limits", {}),
            "updated_at": self.config.get("updated_at")
        }
    
    def set_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """Enable or disable maintenance mode."""
        self.config["maintenance_mode"] = enabled
        self._save_config()
        
        return {
            "message": f"Maintenance mode {'enabled' if enabled else 'disabled'}",
            "maintenance_mode": enabled,
            "updated_at": self.config["updated_at"]
        }
    
    def add_allowed_ip(self, ip: str) -> Dict[str, Any]:
        """Add an IP to the allowed list."""
        if "allowed_ips" not in self.config:
            self.config["allowed_ips"] = []
        
        if ip not in self.config["allowed_ips"]:
            self.config["allowed_ips"].append(ip)
            self._save_config()
        
        return {
            "message": f"IP {ip} added to allowed list",
            "allowed_ips": self.config["allowed_ips"]
        }
    
    def remove_allowed_ip(self, ip: str) -> Dict[str, Any]:
        """Remove an IP from the allowed list."""
        if "allowed_ips" in self.config and ip in self.config["allowed_ips"]:
            self.config["allowed_ips"].remove(ip)
            self._save_config()
        
        return {
            "message": f"IP {ip} removed from allowed list",
            "allowed_ips": self.config.get("allowed_ips", [])
        }
    
    def add_admin_user(self, username: str) -> Dict[str, Any]:
        """Add a user to admin list."""
        if "admin_users" not in self.config:
            self.config["admin_users"] = []
        
        if username not in self.config["admin_users"]:
            self.config["admin_users"].append(username)
            self._save_config()
        
        return {
            "message": f"User {username} added to admin list",
            "admin_users": self.config["admin_users"]
        }
    
    def remove_admin_user(self, username: str) -> Dict[str, Any]:
        """Remove a user from admin list."""
        if "admin_users" in self.config and username in self.config["admin_users"]:
            self.config["admin_users"].remove(username)
            self._save_config()
        
        return {
            "message": f"User {username} removed from admin list",
            "admin_users": self.config.get("admin_users", [])
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        from ..services import batch_prediction
        
        batch_stats = batch_prediction.get_batch_status()
        
        return {
            "config": {
                "rate_limiting_enabled": self.config.get("rate_limiting_enabled", True),
                "maintenance_mode": self.config.get("maintenance_mode", False),
                "total_admin_users": len(self.config.get("admin_users", [])),
                "total_allowed_ips": len(self.config.get("allowed_ips", []))
            },
            "batch_predictions": batch_stats,
            "system_info": {
                "python_version": "3.12.8",
                "watchlist_size": len(config.WATCHLIST),
                "root_path": str(config.ROOT)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Global admin manager
admin_manager = AdminManager()


def check_admin_access(username: str) -> bool:
    """Check if user has admin access."""
    return admin_manager.is_admin_user(username)


def get_admin_config() -> Dict[str, Any]:
    """Get admin configuration."""
    return admin_manager.get_rate_limits()