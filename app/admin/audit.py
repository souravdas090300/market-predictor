"""Audit logging system for tracking all admin actions."""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum

from ..core import config
from ..security import log_security_event


class AuditActionType(str, Enum):
    """Types of audit actions."""
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    USER_DISABLED = "user_disabled"
    USER_ENABLED = "user_enabled"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    
    SUPERUSER_GRANTED = "superuser_granted"
    SUPERUSER_REVOKED = "superuser_revoked"
    
    SUBSCRIPTION_UPDATED = "subscription_updated"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    
    RATE_LIMIT_UPDATED = "rate_limit_updated"
    RATE_LIMITING_TOGGLED = "rate_limiting_toggled"
    
    MAINTENANCE_TOGGLED = "maintenance_toggled"
    
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    
    CONFIG_CHANGED = "config_changed"
    BATCH_PREDICTION_RUN = "batch_prediction_run"
    
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"
    
    SECURITY_BREACH = "security_breach"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog:
    """Audit log entry."""
    
    def __init__(
        self,
        action_type: AuditActionType,
        admin_user: str,
        target_user: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        self.action_type = action_type
        self.admin_user = admin_user
        self.target_user = target_user
        self.details = details or {}
        self.severity = severity
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.id = f"{int(datetime.now(timezone.utc).timestamp() * 1000)}_{admin_user}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "action_type": self.action_type.value,
            "admin_user": self.admin_user,
            "target_user": self.target_user,
            "details": self.details,
            "severity": self.severity.value,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp
        }


class AuditLogger:
    """Manage audit logs."""
    
    def __init__(self):
        self.audit_file = config.ROOT / "data" / "audit_logs.json"
        self.audit_file.parent.mkdir(exist_ok=True)
        self.max_entries = 10000  # Keep last 10,000 entries
        self._load_logs()
    
    def _load_logs(self):
        """Load audit logs from storage."""
        if self.audit_file.exists():
            try:
                with open(self.audit_file) as f:
                    self.logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, IOError):
                self.logs = []
        else:
            self.logs = []
    
    def _save_logs(self):
        """Save audit logs to storage."""
        # Keep only the most recent entries
        if len(self.logs) > self.max_entries:
            self.logs = self.logs[-self.max_entries:]
        
        with open(self.audit_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def log(
        self,
        action_type: AuditActionType,
        admin_user: str,
        target_user: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log an audit event."""
        audit_log = AuditLog(
            action_type=action_type,
            admin_user=admin_user,
            target_user=target_user,
            details=details,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.logs.append(audit_log.to_dict())
        self._save_logs()
        
        # Also log to security logger for critical events
        if severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
            log_security_event(
                f"AUDIT_{action_type.value.upper()}",
                {
                    "admin_user": admin_user,
                    "target_user": target_user,
                    "details": details,
                    "ip_address": ip_address
                }
            )
        
        return audit_log
    
    def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        action_type: Optional[AuditActionType] = None,
        admin_user: Optional[str] = None,
        target_user: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get filtered audit logs."""
        filtered_logs = self.logs.copy()
        
        # Apply filters
        if action_type:
            filtered_logs = [log for log in filtered_logs if log["action_type"] == action_type.value]
        
        if admin_user:
            filtered_logs = [log for log in filtered_logs if log["admin_user"] == admin_user]
        
        if target_user:
            filtered_logs = [log for log in filtered_logs if log["target_user"] == target_user]
        
        if severity:
            filtered_logs = [log for log in filtered_logs if log["severity"] == severity.value]
        
        if start_date:
            filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_date]
        
        if end_date:
            filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end_date]
        
        # Sort by timestamp descending
        filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        return filtered_logs[offset:offset + limit]
    
    def get_log_count(
        self,
        action_type: Optional[AuditActionType] = None,
        admin_user: Optional[str] = None,
        target_user: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> int:
        """Get count of filtered audit logs."""
        filtered_logs = self.logs.copy()
        
        if action_type:
            filtered_logs = [log for log in filtered_logs if log["action_type"] == action_type.value]
        
        if admin_user:
            filtered_logs = [log for log in filtered_logs if log["admin_user"] == admin_user]
        
        if target_user:
            filtered_logs = [log for log in filtered_logs if log["target_user"] == target_user]
        
        if severity:
            filtered_logs = [log for log in filtered_logs if log["severity"] == severity.value]
        
        if start_date:
            filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_date]
        
        if end_date:
            filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end_date]
        
        return len(filtered_logs)
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get audit log statistics for the last N days."""
        from datetime import timedelta
        
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        recent_logs = [log for log in self.logs if log["timestamp"] >= cutoff_date]
        
        # Count by action type
        action_counts = {}
        for log in recent_logs:
            action = log["action_type"]
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for log in recent_logs:
            severity = log["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by admin user
        admin_counts = {}
        for log in recent_logs:
            admin = log["admin_user"]
            admin_counts[admin] = admin_counts.get(admin, 0) + 1
        
        return {
            "total_logs": len(recent_logs),
            "period_days": days,
            "action_counts": action_counts,
            "severity_counts": severity_counts,
            "admin_counts": admin_counts,
            "most_active_admin": max(admin_counts.items(), key=lambda x: x[1])[0] if admin_counts else None
        }
    
    def export_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: str = "json"
    ) -> str:
        """Export audit logs to a file."""
        filtered_logs = self.get_logs(
            limit=100000,  # Large limit for export
            start_date=start_date,
            end_date=end_date
        )
        
        export_dir = config.ROOT / "data" / "exports"
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            export_file = export_dir / f"audit_logs_{timestamp}.json"
            with open(export_file, 'w') as f:
                json.dump(filtered_logs, f, indent=2)
        elif format == "csv":
            import csv
            export_file = export_dir / f"audit_logs_{timestamp}.csv"
            with open(export_file, 'w', newline='') as f:
                if filtered_logs:
                    writer = csv.DictWriter(f, fieldnames=filtered_logs[0].keys())
                    writer.writeheader()
                    writer.writerows(filtered_logs)
        
        return str(export_file)
    
    def clear_old_logs(self, days: int = 90) -> int:
        """Clear audit logs older than N days."""
        from datetime import timedelta
        
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        original_count = len(self.logs)
        
        self.logs = [log for log in self.logs if log["timestamp"] >= cutoff_date]
        
        cleared_count = original_count - len(self.logs)
        if cleared_count > 0:
            self._save_logs()
        
        return cleared_count


# Global audit logger
audit_logger = AuditLogger()


def log_audit_event(
    action_type: AuditActionType,
    admin_user: str,
    target_user: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    severity: AuditSeverity = AuditSeverity.INFO,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> AuditLog:
    """Convenience function to log an audit event."""
    return audit_logger.log(
        action_type=action_type,
        admin_user=admin_user,
        target_user=target_user,
        details=details,
        severity=severity,
        ip_address=ip_address,
        user_agent=user_agent
    )
