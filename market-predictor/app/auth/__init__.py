"""Authentication module for user management and authentication."""
import os
import secrets
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib
from enum import Enum

from ..security import (
    get_password_hash, verify_password, log_security_event
)
from ..core import config


class SubscriptionPlan(str, Enum):
    """Subscription plan types."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status types."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

# User storage (in production, use a proper database)
USERS_FILE = config.ROOT / "data" / "users.json"
USERS_FILE.parent.mkdir(exist_ok=True)


class UserManager:
    """Manage user accounts."""
    
    def __init__(self):
        self.users = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from storage."""
        if USERS_FILE.exists():
            try:
                with open(USERS_FILE) as f:
                    self.users = json.load(f)
            except:
                self.users = {}
    
    def _save_users(self):
        """Save users to storage."""
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Create a new user account."""
        # Check if user already exists
        if username.lower() in [u["username"].lower() for u in self.users.values()]:
            raise ValueError("Username already exists")
        
        # Check if email already exists
        if email.lower() in [u["email"].lower() for u in self.users.values()]:
            raise ValueError("Email already registered")
        
        # Validate password strength
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(password) > 128:
            raise ValueError("Password must be less than 128 characters")
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create user
        user_id = str(secrets.token_urlsafe(16))
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "disabled": False,
            "roles": ["user"],
            "is_superuser": False,
            "preferences": {
                "default_horizon": 5,
                "confidence_threshold": 0.6,
                "auto_refresh": 0,
                "notifications_enabled": False,
                "sound_enabled": False
            },
            "subscription": {
                "plan": "free",
                "status": "active",
                "start_date": datetime.utcnow().isoformat(),
                "expiry_date": None,
                "auto_renew": False
            },
            "profile": {
                "first_name": None,
                "last_name": None,
                "avatar_url": None,
                "bio": None,
                "location": None,
                "website": None
            },
            "oauth_providers": {},
            "email_verified": False,
            "last_login": None
        }
        
        self.users[user_id] = user_data
        self._save_users()
        
        # Log security event
        log_security_event("USER_CREATED", {
            "user_id": user_id,
            "username": username,
            "email": email
        })
        
        return user_data
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password."""
        # Find user by username
        user = None
        for u in self.users.values():
            if u["username"].lower() == username.lower():
                user = u
                break
        
        if not user:
            return None
        
        # Check if user is active
        if not user.get("is_active") or user.get("disabled"):
            return None
        
        # Verify password
        if not verify_password(password, user["hashed_password"]):
            return None
        
        # Update last login
        user["last_login"] = datetime.utcnow().isoformat()
        self._save_users()
        
        # Log security event
        log_security_event("USER_AUTHENTICATED", {
            "user_id": user["user_id"],
            "username": username
        })
        
        # Add admin flag from admin manager (lazy import to avoid circular dependency)
        try:
            from ..admin import admin_manager
            if admin_manager.is_admin_user(username):
                user["is_admin"] = True
            else:
                user["is_admin"] = False
        except:
            user["is_admin"] = False
        
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        for user in self.users.values():
            if user["username"].lower() == username.lower():
                return user
        return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user["preferences"].update(preferences)
        user["updated_at"] = datetime.utcnow().isoformat()
        self._save_users()
        
        return True
    
    def disable_user(self, user_id: str) -> bool:
        """Disable a user account."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user["disabled"] = True
        user["updated_at"] = datetime.utcnow().isoformat()
        self._save_users()
        
        # Log security event
        log_security_event("USER_DISABLED", {
            "user_id": user_id,
            "username": user["username"]
        })
        
        return True
    
    def enable_user(self, user_id: str) -> bool:
        """Enable a user account."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user["disabled"] = False
        user["updated_at"] = datetime.utcnow().isoformat()
        self._save_users()
        
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user account."""
        if user_id in self.users:
            username = self.users[user_id]["username"]
            del self.users[user_id]
            self._save_users()
            
            # Log security event
            log_security_event("USER_DELETED", {
                "user_id": user_id,
                "username": username
            })
            
            return True
        return False
    
    def update_subscription(self, user_id: str, plan: str, duration_days: int = 30) -> Dict[str, Any]:
        """Update user subscription."""
        user = self.users.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Calculate expiry date
        start_date = datetime.utcnow()
        expiry_date = start_date + timedelta(days=duration_days)
        
        user["subscription"] = {
            "plan": plan,
            "status": "active",
            "start_date": start_date.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "auto_renew": False
        }
        user["updated_at"] = datetime.utcnow().isoformat()
        self._save_users()
        
        return user["subscription"]
    
    def get_subscription_status(self, user_id: str) -> Dict[str, Any]:
        """Get user subscription status."""
        user = self.users.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        subscription = user.get("subscription", {})
        expiry_date = subscription.get("expiry_date")
        
        # Check if subscription is expired
        if expiry_date:
            expiry = datetime.fromisoformat(expiry_date)
            if datetime.utcnow() > expiry:
                subscription["status"] = "expired"
        
        return subscription
    
    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if "profile" not in user:
            user["profile"] = {}
        
        user["profile"].update(profile_data)
        user["updated_at"] = datetime.utcnow().isoformat()
        self._save_users()
        
        return True
    
    def verify_email(self, user_id: str) -> bool:
        """Verify user email."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user["email_verified"] = True
        user["updated_at"] = datetime.utcnow().isoformat()
        self._save_users()
        
        return True
    
    def link_oauth_account(self, user_id: str, provider: str, provider_user_id: str, provider_data: Dict[str, Any]) -> bool:
        """Link OAuth account to user."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if "oauth_providers" not in user:
            user["oauth_providers"] = {}
        
        user["oauth_providers"][provider] = {
            "provider_user_id": provider_user_id,
            "provider_data": provider_data,
            "linked_at": datetime.utcnow().isoformat()
        }
        user["updated_at"] = datetime.utcnow().isoformat()
        self._save_users()
        
        return True
    
    def find_user_by_oauth(self, provider: str, provider_user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by OAuth provider and user ID."""
        for user in self.users.values():
            oauth_providers = user.get("oauth_providers", {})
            if provider in oauth_providers:
                if oauth_providers[provider]["provider_user_id"] == provider_user_id:
                    return user
        return None
    
    def create_user_from_oauth(self, provider: str, provider_user_id: str, email: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user from OAuth provider."""
        # Check if user already exists with this email
        existing_user = None
        for user in self.users.values():
            if user["email"].lower() == email.lower():
                existing_user = user
                break
        
        if existing_user:
            # Link OAuth to existing user
            self.link_oauth_account(existing_user["user_id"], provider, provider_user_id, profile_data)
            return existing_user
        
        # Generate username from email or profile
        username = profile_data.get("username") or email.split("@")[0]
        # Ensure username is unique
        base_username = username
        counter = 1
        while username.lower() in [u["username"].lower() for u in self.users.values()]:
            username = f"{base_username}{counter}"
            counter += 1
        
        # Create user
        user_id = str(secrets.token_urlsafe(16))
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "hashed_password": None,  # No password for OAuth users
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "disabled": False,
            "roles": ["user"],
            "is_superuser": False,
            "preferences": {
                "default_horizon": 5,
                "confidence_threshold": 0.6,
                "auto_refresh": 0,
                "notifications_enabled": False,
                "sound_enabled": False
            },
            "subscription": {
                "plan": "free",
                "status": "active",
                "start_date": datetime.utcnow().isoformat(),
                "expiry_date": None,
                "auto_renew": False
            },
            "profile": {
                "first_name": profile_data.get("first_name"),
                "last_name": profile_data.get("last_name"),
                "avatar_url": profile_data.get("avatar_url"),
                "bio": None,
                "location": profile_data.get("location"),
                "website": None
            },
            "oauth_providers": {
                provider: {
                    "provider_user_id": provider_user_id,
                    "provider_data": profile_data,
                    "linked_at": datetime.utcnow().isoformat()
                }
            },
            "email_verified": True,  # OAuth emails are verified
            "last_login": None
        }
        
        self.users[user_id] = user_data
        self._save_users()
        
        # Log security event
        log_security_event("USER_CREATED_OAUTH", {
            "user_id": user_id,
            "username": username,
            "email": email,
            "provider": provider
        })
        
        return user_data
    
    def set_superuser(self, user_id: str, is_superuser: bool = True) -> bool:
        """Set or unset superuser status."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user["is_superuser"] = is_superuser
        user["updated_at"] = datetime.utcnow().isoformat()
        
        # Update roles based on superuser status
        if is_superuser:
            if "admin" not in user["roles"]:
                user["roles"].append("admin")
        else:
            user["roles"] = [role for role in user["roles"] if role != "admin"]
        
        self._save_users()
        
        # Log security event
        log_security_event("SUPERUSER_CHANGED", {
            "user_id": user_id,
            "username": user["username"],
            "is_superuser": is_superuser
        })
        
        return True
    
    def is_superuser(self, user_id: str) -> bool:
        """Check if user is superuser."""
        user = self.users.get(user_id)
        if not user:
            return False
        return user.get("is_superuser", False)
    
    def is_superuser_by_username(self, username: str) -> bool:
        """Check if user is superuser by username."""
        for user in self.users.values():
            if user["username"].lower() == username.lower():
                return user.get("is_superuser", False)
        return False
    
    def add_role(self, user_id: str, role: str) -> bool:
        """Add a role to user."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if role not in user["roles"]:
            user["roles"].append(role)
            user["updated_at"] = datetime.utcnow().isoformat()
            self._save_users()
        
        return True
    
    def remove_role(self, user_id: str, role: str) -> bool:
        """Remove a role from user."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if role in user["roles"]:
            user["roles"].remove(role)
            user["updated_at"] = datetime.utcnow().isoformat()
            self._save_users()
        
        return True
    
    def has_role(self, user_id: str, role: str) -> bool:
        """Check if user has a specific role."""
        user = self.users.get(user_id)
        if not user:
            return False
        return role in user.get("roles", [])
    
    def list_users(self) -> list:
        """List all users (admin function)."""
        return [
            {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "created_at": user["created_at"],
                "is_active": user["is_active"],
                "disabled": user["disabled"],
                "roles": user["roles"],
                "subscription": user.get("subscription", {})
            }
            for user in self.users.values()
        ]


# Global user manager
user_manager = UserManager()


# Create demo user for testing
def ensure_demo_user():
    """Ensure demo user exists for testing."""
    try:
        user_manager.create_user(
            username="demo",
            email="demo@marketpredictor.com",
            password="demo12345"  # Meets minimum 8 character requirement
        )
    except ValueError:
        # User already exists
        pass


# Initialize demo user on import
ensure_demo_user()