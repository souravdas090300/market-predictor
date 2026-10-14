"""
Test script to verify Redis caching is working
Run this after starting the application
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_cache_stats():
    """Test cache stats endpoint"""
    print("\n📊 Testing cache stats endpoint...")
    response = requests.get(f"{BASE_URL}/api/cache/stats")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_live_prices_caching():
    """Test live prices endpoint with caching"""
    print("\n💰 Testing live prices endpoint with caching...")

    # First request (cache miss)
    print("\n1️⃣ First request (cache miss - should be slower)...")
    start = time.time()
    response1 = requests.get(f"{BASE_URL}/api/assets/live-prices?limit=10")
    elapsed1 = time.time() - start
    print(f"Status: {response1.status_code}")
    print(f"Time: {elapsed1:.3f}s")
    data1 = response1.json()
    print(f"Source: {data1.get('source', 'unknown')}")
    print(f"Total assets: {data1.get('total', 0)}")

    # Second request (cache hit - should be much faster)
    print("\n2️⃣ Second request (cache hit - should be faster)...")
    start = time.time()
    response2 = requests.get(f"{BASE_URL}/api/assets/live-prices?limit=10")
    elapsed2 = time.time() - start
    print(f"Status: {response2.status_code}")
    print(f"Time: {elapsed2:.3f}s")
    data2 = response2.json()
    print(f"Source: {data2.get('source', 'unknown')}")

    # Compare
    print("\n📈 Performance comparison:")
    print(f"First request:  {elapsed1:.3f}s")
    print(f"Second request: {elapsed2:.3f}s")
    if elapsed2 < elapsed1:
        speedup = elapsed1 / elapsed2
        print(f"✅ Cache hit is {speedup:.1f}x faster!")
    else:
        print("⚠️ Cache may not be working (second request not faster)")

def test_pagination():
    """Test pagination"""
    print("\n📄 Testing pagination...")

    # Page 1
    print("\n📖 Page 1...")
    response1 = requests.get(f"{BASE_URL}/api/assets/live-prices?page=1&limit=5")
    print(f"Status: {response1.status_code}")
    data1 = response1.json()
    print(f"Page: {data1.get('page')}")
    print(f"Limit: {data1.get('limit')}")
    print(f"Total: {data1.get('total')}")
    print(f"Pages: {data1.get('pages')}")
    print(f"Assets returned: {len(data1.get('assets', []))}")

    # Page 2
    print("\n📖 Page 2...")
    response2 = requests.get(f"{BASE_URL}/api/assets/live-prices?page=2&limit=5")
    print(f"Status: {response2.status_code}")
    data2 = response2.json()
    print(f"Page: {data2.get('page')}")
    print(f"Assets returned: {len(data2.get('assets', []))}")

if __name__ == "__main__":
    print("🚀 Starting Redis cache tests...")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)

    try:
        test_health()
        test_cache_stats()
        test_live_prices_caching()
        test_pagination()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("\n💡 If cache is working, you should see:")
        print("   - Health: Redis active")
        print("   - Cache stats: status: active")
        print("   - Second request faster than first")
        print("   - Source: cache (for second request)")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("   Make sure the app is running: python -m uvicorn app.api:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
