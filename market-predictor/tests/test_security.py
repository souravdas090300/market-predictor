"""Security tests for authentication, rate limiting, and input validation."""
import pytest
from app.security import security as sec
from app.security import get_current_active_user
from app.auth import UserManager, user_manager


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hashing(self):
        """Test that passwords can be hashed and verified."""
        password = "SecurePassword123"
        hashed = sec.get_password_hash(password)
        
        # Hash should be different from original
        assert hashed != password
        
        # Verification should work
        assert sec.verify_password(password, hashed)
        
        # Wrong password should fail
        assert not sec.verify_password("WrongPassword", hashed)
    
    def test_hash_consistency(self):
        """Test that same password produces different hashes (salt)."""
        password = "SamePassword123"
        hash1 = sec.get_password_hash(password)
        hash2 = sec.get_password_hash(password)
        
        # Different hashes due to salt
        assert hash1 != hash2
        
        # Both should verify
        assert sec.verify_password(password, hash1)
        assert sec.verify_password(password, hash2)


class TestJWTTokens:
    """Test JWT token creation and validation."""
    
    def test_access_token_creation(self):
        """Test access token creation."""
        data = {"sub": "testuser", "role": "user"}
        token = sec.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_decoding(self):
        """Test token decoding."""
        data = {"sub": "testuser", "role": "user"}
        token = sec.create_access_token(data)
        
        payload = sec.decode_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "user"
        assert "exp" in payload
    
    def test_invalid_token(self):
        """Test invalid token handling."""
        with pytest.raises(sec.AuthenticationError):
            sec.decode_token("invalid_token_string")
    
    def test_expired_token(self):
        """Test expired token handling."""
        from datetime import timedelta
        data = {"sub": "testuser"}
        # Create token with negative expiration (already expired)
        token = sec.create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(sec.AuthenticationError):
            sec.decode_token(token)


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_symbol_sanitization(self):
        """Test symbol sanitization."""
        # Valid symbols
        assert sec.sanitize_symbol("aapl") == "AAPL"
        assert sec.sanitize_symbol("BTC-USD") == "BTC-USD"
        assert sec.sanitize_symbol("  msft  ") == "MSFT"
        
        # Invalid symbols
        with pytest.raises(ValueError):
            sec.sanitize_symbol("AAPL<script>")
        
        with pytest.raises(ValueError):
            sec.sanitize_symbol("A" * 25)  # Too long
    
    def test_url_validation(self):
        """Test URL validation."""
        # Valid URLs
        assert sec.validate_url("https://example.com")
        assert sec.validate_url("http://example.com")
        
        # Invalid URLs
        assert not sec.validate_url("ftp://example.com")
        assert not sec.validate_url("http://localhost")
        assert not sec.validate_url("http://192.168.1.1")
        assert not sec.validate_url("invalid-url")
    
    def test_text_sanitization(self):
        """Test text sanitization."""
        # Normal text
        text = "This is normal text."
        assert sec.sanitize_text(text) == text
        
        # Long text should be truncated
        long_text = "A" * 30000
        sanitized = sec.sanitize_text(long_text, max_length=100)
        assert len(sanitized) == 100
        
        # Control characters should be removed
        text_with_control = "Text\x00with\x08control\x1fchars"
        sanitized = sec.sanitize_text(text_with_control)
        assert "\x00" not in sanitized
        assert "\x08" not in sanitized


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = sec.RateLimiter()
        assert limiter.max_requests == 100
        assert limiter.window == 60
    
    def test_rate_limit_allowed(self):
        """Test that requests are allowed under limit."""
        limiter = sec.RateLimiter()
        limiter.max_requests = 5
        
        for i in range(5):
            assert limiter.is_allowed("test_key")
    
    def test_rate_limit_exceeded(self):
        """Test that requests are blocked over limit."""
        limiter = sec.RateLimiter()
        limiter.max_requests = 3
        
        # First 3 should be allowed
        for i in range(3):
            assert limiter.is_allowed("test_key")
        
        # 4th should be blocked
        assert not limiter.is_allowed("test_key")
    
    def test_rate_limit_remaining(self):
        """Test remaining requests calculation."""
        limiter = sec.RateLimiter()
        limiter.max_requests = 10
        
        # Make 3 requests
        for i in range(3):
            limiter.is_allowed("test_key")
        
        # Should have 7 remaining
        assert limiter.get_remaining("test_key") == 7


class TestAPIKeyManagement:
    """Test API key management."""
    
    def test_api_key_generation(self):
        """Test API key generation."""
        manager = sec.APIKeyManager()
        api_key = manager.generate_api_key("user123", "Test Key", ["read"])
        
        assert api_key.startswith("mp_")
        assert len(api_key) > 10
    
    def test_api_key_validation(self):
        """Test API key validation."""
        manager = sec.APIKeyManager()
        api_key = manager.generate_api_key("user123", "Test Key", ["read"])
        
        data = manager.validate_api_key(api_key)
        assert data is not None
        assert data["user_id"] == "user123"
        assert data["name"] == "Test Key"
    
    def test_invalid_api_key(self):
        """Test invalid API key handling."""
        manager = sec.APIKeyManager()
        data = manager.validate_api_key("invalid_key")
        assert data is None
    
    def test_api_key_revocation(self):
        """Test API key revocation."""
        manager = sec.APIKeyManager()
        api_key = manager.generate_api_key("user123", "Test Key", ["read"])
        
        # Should validate initially
        assert manager.validate_api_key(api_key) is not None
        
        # Revoke the key
        assert manager.revoke_api_key(api_key)
        
        # Should not validate after revocation
        assert manager.validate_api_key(api_key) is None


class TestSessionManagement:
    """Test session management."""
    
    def test_session_creation(self):
        """Test session creation."""
        manager = sec.SessionManager()
        user_data = {"username": "testuser", "email": "test@example.com"}
        
        session_id = manager.create_session("user123", user_data)
        assert session_id is not None
        assert len(session_id) > 0
    
    def test_session_retrieval(self):
        """Test session retrieval."""
        manager = sec.SessionManager()
        user_data = {"username": "testuser", "email": "test@example.com"}
        
        session_id = manager.create_session("user123", user_data)
        session = manager.get_session(session_id)
        
        assert session is not None
        assert session["user_id"] == "user123"
        assert session["user_data"]["username"] == "testuser"
    
    def test_session_deletion(self):
        """Test session deletion."""
        manager = sec.SessionManager()
        user_data = {"username": "testuser", "email": "test@example.com"}
        
        session_id = manager.create_session("user123", user_data)
        assert manager.get_session(session_id) is not None
        
        manager.delete_session(session_id)
        assert manager.get_session(session_id) is None


class TestSecurityHeaders:
    """Test security headers generation."""
    
    def test_security_headers(self):
        """Test security headers are generated correctly."""
        headers = sec.get_security_headers()
        
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers
        
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["X-Content-Type-Options"] == "nosniff"


class TestUserManagement:
    """Test user management."""
    
    def test_user_creation(self):
        """Test user creation."""
        user = user_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="SecurePassword123"
        )
        
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        assert user["is_active"] is True
        assert "hashed_password" in user
        assert user["hashed_password"] != "SecurePassword123"
    
    def test_duplicate_user_prevention(self):
        """Test that duplicate users are prevented."""
        user_manager.create_user(
            username="duplicate",
            email="dup@example.com",
            password="SecurePassword123"
        )
        
        with pytest.raises(ValueError):
            user_manager.create_user(
                username="duplicate",
                email="different@example.com",
                password="SecurePassword123"
            )
    
    def test_user_authentication(self):
        """Test user authentication."""
        user_manager.create_user(
            username="authuser",
            email="auth@example.com",
            password="AuthPassword123"
        )
        
        # Correct password
        user = user_manager.authenticate_user("authuser", "AuthPassword123")
        assert user is not None
        assert user["username"] == "authuser"
        
        # Wrong password
        user = user_manager.authenticate_user("authuser", "WrongPassword")
        assert user is None
    
    def test_user_preferences(self):
        """Test user preferences update."""
        user = user_manager.create_user(
            username="prefuser",
            email="pref@example.com",
            password="PrefPassword123"
        )
        
        preferences = {
            "default_horizon": 10,
            "confidence_threshold": 0.7
        }
        
        success = user_manager.update_user_preferences(user["user_id"], preferences)
        assert success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])