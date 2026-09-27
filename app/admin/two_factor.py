"""Two-Factor Authentication (2FA) system for superuser login."""
import os
import secrets
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

# Optional imports for 2FA functionality
try:
    import pyotp
    import qrcode
    from io import BytesIO
    import base64
    PYOTP_AVAILABLE = True
except ImportError:
    pyotp = None
    qrcode = None
    BytesIO = None
    base64 = None
    PYOTP_AVAILABLE = False

from ..core import config
from ..security import log_security_event


class TwoFactorMethod(str, Enum):
    """Types of 2FA methods."""
    TOTP = "totp"  # Time-based One-Time Password (Google Authenticator, etc.)
    SMS = "sms"  # SMS verification
    EMAIL = "email"  # Email verification


class TwoFactorConfig:
    """2FA configuration for a user."""
    
    def __init__(
        self,
        user_id: str,
        method: TwoFactorMethod,
        secret: Optional[str] = None,
        enabled: bool = False,
        backup_codes: Optional[list] = None
    ):
        self.user_id = user_id
        self.method = method
        self.secret = secret or pyotp.random_base32()
        self.enabled = enabled
        self.backup_codes = backup_codes or self._generate_backup_codes()
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.last_used = None
    
    def _generate_backup_codes(self) -> list:
        """Generate backup codes for 2FA recovery."""
        return [secrets.token_hex(4).upper() for _ in range(10)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "method": self.method.value,
            "secret": self.secret,
            "enabled": self.enabled,
            "backup_codes": self.backup_codes,
            "created_at": self.created_at,
            "last_used": self.last_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TwoFactorConfig':
        """Create from dictionary."""
        config = cls(
            user_id=data["user_id"],
            method=TwoFactorMethod(data["method"]),
            secret=data["secret"],
            enabled=data["enabled"],
            backup_codes=data["backup_codes"]
        )
        config.created_at = data["created_at"]
        config.last_used = data.get("last_used")
        return config


class TwoFactorAuthManager:
    """Manage Two-Factor Authentication."""
    
    def __init__(self):
        self.config_file = config.ROOT / "data" / "two_factor_config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        self.configs: Dict[str, TwoFactorConfig] = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load 2FA configurations."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    data = json.load(f)
                    for user_id, config_data in data.items():
                        self.configs[user_id] = TwoFactorConfig.from_dict(config_data)
            except (FileNotFoundError, json.JSONDecodeError, KeyError, IOError):
                self.configs = {}
        else:
            self.configs = {}
    
    def _save_configs(self):
        """Save 2FA configurations."""
        data = {
            user_id: config.to_dict()
            for user_id, config in self.configs.items()
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def setup_2fa(
        self,
        user_id: str,
        method: TwoFactorMethod = TwoFactorMethod.TOTP
    ) -> Dict[str, Any]:
        """Setup 2FA for a user."""
        if method == TwoFactorMethod.TOTP and not PYOTP_AVAILABLE:
            raise ImportError("pyotp and qrcode packages are required for TOTP 2FA. Install with: pip install pyotp qrcode pillow")
        
        config = TwoFactorConfig(
            user_id=user_id,
            method=method,
            enabled=False  # Not enabled until verified
        )
        
        self.configs[user_id] = config
        self._save_configs()
        
        # Generate QR code for TOTP
        qr_code_data = None
        if method == TwoFactorMethod.TOTP and PYOTP_AVAILABLE:
            qr_code_data = self._generate_qr_code(user_id, config.secret)
        
        log_security_event("2FA_SETUP_INITIATED", {
            "user_id": user_id,
            "method": method.value
        })
        
        return {
            "user_id": user_id,
            "method": method.value,
            "secret": config.secret,
            "backup_codes": config.backup_codes,
            "qr_code": qr_code_data,
            "enabled": False,
            "message": "2FA setup initiated. Please verify with your authenticator app."
        }
    
    def _generate_qr_code(self, user_id: str, secret: str) -> str:
        """Generate QR code for TOTP setup."""
        if not PYOTP_AVAILABLE:
            raise ImportError("pyotp and qrcode packages are required for 2FA. Install with: pip install pyotp qrcode pillow")
        
        # Create TOTP URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_id,
            issuer_name="Market Predictor Admin"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Convert to base64 image
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_2fa_setup(
        self,
        user_id: str,
        code: str
    ) -> Dict[str, Any]:
        """Verify 2FA setup and enable it."""
        if user_id not in self.configs:
            return {
                "success": False,
                "message": "2FA not setup for this user"
            }
        
        config = self.configs[user_id]
        
        # Verify the code
        if not self._verify_code(config, code):
            log_security_event("2FA_SETUP_FAILED", {
                "user_id": user_id,
                "reason": "Invalid verification code"
            })
            return {
                "success": False,
                "message": "Invalid verification code"
            }
        
        # Enable 2FA
        config.enabled = True
        self._save_configs()
        
        log_security_event("2FA_ENABLED", {
            "user_id": user_id,
            "method": config.method.value
        })
        
        return {
            "success": True,
            "message": "2FA enabled successfully",
            "enabled": True
        }
    
    def _verify_code(self, config: TwoFactorConfig, code: str) -> bool:
        """Verify a 2FA code."""
        if not PYOTP_AVAILABLE:
            # Fallback: only check backup codes if pyotp is not available
            return code in config.backup_codes
            
        if config.method == TwoFactorMethod.TOTP:
            totp = pyotp.TOTP(config.secret)
            return totp.verify(code, valid_window=1)  # Allow 1 step window for clock skew
        elif config.method == TwoFactorMethod.SMS or config.method == TwoFactorMethod.EMAIL:
            # In a real implementation, you would verify against sent code
            # For now, check against backup codes
            return code in config.backup_codes
        return False
    
    def verify_2fa_login(
        self,
        user_id: str,
        code: str
    ) -> Dict[str, Any]:
        """Verify 2FA during login."""
        if user_id not in self.configs:
            return {
                "success": False,
                "message": "2FA not enabled for this user"
            }
        
        config = self.configs[user_id]
        
        if not config.enabled:
            return {
                "success": False,
                "message": "2FA not enabled for this user"
            }
        
        # Check if it's a backup code
        if code in config.backup_codes:
            # Remove used backup code
            config.backup_codes.remove(code)
            config.last_used = datetime.now(timezone.utc).isoformat()
            self._save_configs()
            
            log_security_event("2FA_LOGIN_BACKUP_CODE", {
                "user_id": user_id
            })
            
            return {
                "success": True,
                "message": "Login verified with backup code",
                "backup_code_used": True
            }
        
        # Verify regular code
        if not self._verify_code(config, code):
            log_security_event("2FA_LOGIN_FAILED", {
                "user_id": user_id,
                "reason": "Invalid code"
            })
            return {
                "success": False,
                "message": "Invalid verification code"
            }
        
        config.last_used = datetime.now(timezone.utc).isoformat()
        self._save_configs()
        
        log_security_event("2FA_LOGIN_SUCCESS", {
            "user_id": user_id,
            "method": config.method.value
        })
        
        return {
            "success": True,
            "message": "2FA verification successful"
        }
    
    def disable_2fa(self, user_id: str, code: str) -> Dict[str, Any]:
        """Disable 2FA for a user (requires verification)."""
        if user_id not in self.configs:
            return {
                "success": False,
                "message": "2FA not enabled for this user"
            }
        
        config = self.configs[user_id]
        
        # Verify code before disabling
        if not self._verify_code(config, code):
            log_security_event("2FA_DISABLE_FAILED", {
                "user_id": user_id,
                "reason": "Invalid verification code"
            })
            return {
                "success": False,
                "message": "Invalid verification code"
            }
        
        # Disable 2FA
        del self.configs[user_id]
        self._save_configs()
        
        log_security_event("2FA_DISABLED", {
            "user_id": user_id
        })
        
        return {
            "success": True,
            "message": "2FA disabled successfully"
        }
    
    def regenerate_backup_codes(self, user_id: str, code: str) -> Dict[str, Any]:
        """Regenerate backup codes (requires verification)."""
        if user_id not in self.configs:
            return {
                "success": False,
                "message": "2FA not enabled for this user"
            }
        
        config = self.configs[user_id]
        
        # Verify code before regenerating
        if not self._verify_code(config, code):
            return {
                "success": False,
                "message": "Invalid verification code"
            }
        
        # Regenerate backup codes
        config.backup_codes = config._generate_backup_codes()
        self._save_configs()
        
        log_security_event("2FA_BACKUP_CODES_REGENERATED", {
            "user_id": user_id
        })
        
        return {
            "success": True,
            "message": "Backup codes regenerated",
            "backup_codes": config.backup_codes
        }
    
    def is_2fa_enabled(self, user_id: str) -> bool:
        """Check if 2FA is enabled for a user."""
        return user_id in self.configs and self.configs[user_id].enabled
    
    def get_2fa_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get 2FA status for a user."""
        if user_id not in self.configs:
            return None
        
        config = self.configs[user_id]
        return {
            "enabled": config.enabled,
            "method": config.method.value,
            "created_at": config.created_at,
            "last_used": config.last_used,
            "backup_codes_remaining": len(config.backup_codes)
        }
    
    def generate_temp_code(self, user_id: str) -> Optional[str]:
        """Generate a temporary verification code (for SMS/Email)."""
        if user_id not in self.configs:
            return None
        
        config = self.configs[user_id]
        
        if config.method in [TwoFactorMethod.SMS, TwoFactorMethod.EMAIL]:
            # Generate a 6-digit code
            temp_code = f"{secrets.randbelow(1000000):06d}"
            
            # In a real implementation, you would send this via SMS or email
            # For now, just return it
            return temp_code
        
        return None


# Global 2FA manager
two_factor_manager = TwoFactorAuthManager()


def require_2fa(user_id: str) -> bool:
    """Check if 2FA is required for a user."""
    return two_factor_manager.is_2fa_enabled(user_id)


def verify_2fa_code(user_id: str, code: str) -> bool:
    """Verify a 2FA code."""
    result = two_factor_manager.verify_2fa_login(user_id, code)
    return result["success"]
