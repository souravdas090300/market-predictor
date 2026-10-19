"""Test Redis connection locally"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env.dev")

# Test Redis connection
try:
    from app.providers.redis_cache import init_redis

    redis_cache = init_redis(
        host="localhost",
        port=6379,
        db=0,
        password=None,
        raise_on_error=True
    )

    # Test set and get
    redis_cache.set("test_key", "test_value", ex=60)
    value = redis_cache.get("test_key")

    print(f"✅ Redis connection successful!")
    print(f"✅ Set test_key: test_value")
    print(f"✅ Get test_key: {value}")

    # Clean up
    redis_cache.delete("test_key")
    print(f"✅ Deleted test_key")

except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    sys.exit(1)
