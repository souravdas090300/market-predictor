"""Activity analytics for user engagement dashboard."""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from enum import Enum

from ..core import config
from ..security import log_security_event


class ActivityType(str, Enum):
    """Types of user activities to track."""
    LOGIN = "login"
    LOGOUT = "logout"
    PAGE_VIEW = "page_view"
    API_REQUEST = "api_request"
    PREDICTION_REQUEST = "prediction_request"
    WATCHLIST_UPDATE = "watchlist_update"
    SIGNAL_VIEW = "signal_view"
    CHART_VIEW = "chart_view"
    NEWS_VIEW = "news_view"
    DATA_EXPORT = "data_export"
    SETTINGS_CHANGE = "settings_change"
    FEATURE_USAGE = "feature_usage"


class ActivityEvent:
    """User activity event."""
    
    def __init__(
        self,
        user_id: str,
        activity_type: ActivityType,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        self.user_id = user_id
        self.activity_type = activity_type
        self.details = details or {}
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.timestamp = datetime.utcnow().isoformat()
        self.id = f"{int(datetime.utcnow().timestamp() * 1000)}_{user_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_type": self.activity_type.value,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp
        }


class ActivityAnalytics:
    """Manage user activity analytics."""
    
    def __init__(self):
        self.activity_file = config.ROOT / "data" / "activity_analytics.json"
        self.activity_file.parent.mkdir(exist_ok=True)
        self.max_entries = 50000  # Keep last 50,000 entries
        self.events: List[Dict[str, Any]] = []
        self._load_events()
    
    def _load_events(self):
        """Load activity events from storage."""
        if self.activity_file.exists():
            try:
                with open(self.activity_file) as f:
                    self.events = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, IOError):
                self.events = []
        else:
            self.events = []
    
    def _save_events(self):
        """Save activity events to storage."""
        # Keep only the most recent entries
        if len(self.events) > self.max_entries:
            self.events = self.events[-self.max_entries:]
        
        with open(self.activity_file, 'w') as f:
            json.dump(self.events, f, indent=2)
    
    def track_activity(
        self,
        user_id: str,
        activity_type: ActivityType,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityEvent:
        """Track a user activity event."""
        event = ActivityEvent(
            user_id=user_id,
            activity_type=activity_type,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.events.append(event.to_dict())
        self._save_events()
        
        return event
    
    def get_user_activity(
        self,
        user_id: str,
        limit: int = 100,
        activity_type: Optional[ActivityType] = None
    ) -> List[Dict[str, Any]]:
        """Get activity for a specific user."""
        user_events = [event for event in self.events if event["user_id"] == user_id]
        
        if activity_type:
            user_events = [event for event in user_events if event["activity_type"] == activity_type.value]
        
        # Sort by timestamp descending
        user_events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return user_events[:limit]
    
    def get_activity_summary(
        self,
        days: int = 30,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get activity summary for the last N days."""
        from datetime import timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        filtered_events = [event for event in self.events if event["timestamp"] >= cutoff_date]
        
        if user_id:
            filtered_events = [event for event in filtered_events if event["user_id"] == user_id]
        
        # Count by activity type
        activity_counts = defaultdict(int)
        for event in filtered_events:
            activity = event["activity_type"]
            activity_counts[activity] += 1
        
        # Count by user
        user_counts = defaultdict(int)
        for event in filtered_events:
            user = event["user_id"]
            user_counts[user] += 1
        
        # Calculate daily activity
        daily_activity = defaultdict(int)
        for event in filtered_events:
            date = event["timestamp"][:10]  # YYYY-MM-DD
            daily_activity[date] += 1
        
        return {
            "period_days": days,
            "total_events": len(filtered_events),
            "activity_counts": dict(activity_counts),
            "unique_users": len(user_counts),
            "daily_activity": dict(daily_activity),
            "avg_daily_events": round(len(filtered_events) / days, 2) if days > 0 else 0
        }
    
    def get_engagement_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Calculate user engagement metrics."""
        from datetime import timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        recent_events = [event for event in self.events if event["timestamp"] >= cutoff_date]
        
        # Active users (users with at least one activity)
        active_users = set(event["user_id"] for event in recent_events)
        
        # Daily active users (DAU)
        dau = defaultdict(set)
        for event in recent_events:
            date = event["timestamp"][:10]
            dau[date].add(event["user_id"])
        
        # Weekly active users (WAU)
        wau = defaultdict(set)
        for event in recent_events:
            week = datetime.fromisoformat(event["timestamp"]).strftime("%Y-W%W")
            wau[week].add(event["user_id"])
        
        # Monthly active users (MAU)
        mau = defaultdict(set)
        for event in recent_events:
            month = event["timestamp"][:7]  # YYYY-MM
            mau[month].add(event["user_id"])
        
        # Calculate averages
        avg_dau = round(sum(len(users) for users in dau.values()) / len(dau), 2) if dau else 0
        avg_wau = round(sum(len(users) for users in wau.values()) / len(wau), 2) if wau else 0
        avg_mau = round(sum(len(users) for users in mau.values()) / len(mau), 2) if mau else 0
        
        # Stickiness ratio (DAU/MAU)
        stickiness = round(avg_dau / avg_mau * 100, 2) if avg_mau > 0 else 0
        
        return {
            "period_days": days,
            "total_active_users": len(active_users),
            "daily_active_users": avg_dau,
            "weekly_active_users": avg_wau,
            "monthly_active_users": avg_mau,
            "stickiness_ratio": stickiness,
            "daily_breakdown": {date: len(users) for date, users in dau.items()}
        }
    
    def get_feature_usage(self, days: int = 30) -> Dict[str, Any]:
        """Get feature usage statistics."""
        from datetime import timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        recent_events = [event for event in self.events if event["timestamp"] >= cutoff_date]
        
        # Count feature usage
        feature_usage = defaultdict(int)
        feature_users = defaultdict(set)
        
        for event in recent_events:
            activity = event["activity_type"]
            feature_usage[activity] += 1
            feature_users[activity].add(event["user_id"])
        
        # Calculate popularity
        total_events = len(recent_events)
        feature_popularity = {
            feature: round(count / total_events * 100, 2) if total_events > 0 else 0
            for feature, count in feature_usage.items()
        }
        
        return {
            "period_days": days,
            "feature_usage": dict(feature_usage),
            "feature_users": {feature: len(users) for feature, users in feature_users.items()},
            "feature_popularity": feature_popularity,
            "most_used_feature": max(feature_usage.items(), key=lambda x: x[1])[0] if feature_usage else None
        }
    
    def get_user_sessions(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get user sessions (login to logout pairs)."""
        from datetime import timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        user_events = [
            event for event in self.events
            if event["user_id"] == user_id and event["timestamp"] >= cutoff_date
        ]
        
        # Sort by timestamp
        user_events.sort(key=lambda x: x["timestamp"])
        
        # Group into sessions
        sessions = []
        current_session = None
        
        for event in user_events:
            if event["activity_type"] == ActivityType.LOGIN.value:
                current_session = {
                    "login_time": event["timestamp"],
                    "logout_time": None,
                    "duration": None,
                    "events": []
                }
            elif event["activity_type"] == ActivityType.LOGOUT.value and current_session:
                current_session["logout_time"] = event["timestamp"]
                # Calculate duration
                login = datetime.fromisoformat(current_session["login_time"])
                logout = datetime.fromisoformat(event["timestamp"])
                duration = (logout - login).total_seconds()
                current_session["duration"] = round(duration, 2)
                sessions.append(current_session)
                current_session = None
            elif current_session:
                current_session["events"].append(event)
        
        # Handle sessions without logout (still active)
        if current_session:
            login = datetime.fromisoformat(current_session["login_time"])
            now = datetime.utcnow()
            duration = (now - login).total_seconds()
            current_session["duration"] = round(duration, 2)
            current_session["is_active"] = True
            sessions.append(current_session)
        
        return sessions
    
    def get_top_users(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by activity."""
        from datetime import timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        recent_events = [event for event in self.events if event["timestamp"] >= cutoff_date]
        
        # Count activity per user
        user_activity = defaultdict(int)
        for event in recent_events:
            user_activity[event["user_id"]] += 1
        
        # Sort by activity count
        sorted_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "user_id": user_id,
                "activity_count": count,
                "avg_daily_activity": round(count / days, 2)
            }
            for user_id, count in sorted_users[:limit]
        ]
    
    def get_time_distribution(self, days: int = 30) -> Dict[str, Any]:
        """Get activity distribution by time of day and day of week."""
        from datetime import timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        recent_events = [event for event in self.events if event["timestamp"] >= cutoff_date]
        
        # Distribution by hour
        hourly_distribution = defaultdict(int)
        # Distribution by day of week
        daily_distribution = defaultdict(int)
        
        for event in recent_events:
            dt = datetime.fromisoformat(event["timestamp"])
            hour = dt.hour
            day_of_week = dt.strftime("%A")
            
            hourly_distribution[hour] += 1
            daily_distribution[day_of_week] += 1
        
        return {
            "period_days": days,
            "hourly_distribution": dict(hourly_distribution),
            "daily_distribution": dict(daily_distribution),
            "peak_hour": max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else None,
            "peak_day": max(daily_distribution.items(), key=lambda x: x[1])[0] if daily_distribution else None
        }
    
    def clear_old_events(self, days: int = 90) -> int:
        """Clear activity events older than N days."""
        from datetime import timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        original_count = len(self.events)
        
        self.events = [event for event in self.events if event["timestamp"] >= cutoff_date]
        
        cleared_count = original_count - len(self.events)
        if cleared_count > 0:
            self._save_events()
        
        return cleared_count


# Global activity analytics instance
activity_analytics = ActivityAnalytics()


def track_user_activity(
    user_id: str,
    activity_type: ActivityType,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> ActivityEvent:
    """Convenience function to track user activity."""
    return activity_analytics.track_activity(
        user_id=user_id,
        activity_type=activity_type,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
