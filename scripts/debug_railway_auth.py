"""Debug Railway backend authentication issues."""
import requests
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

RAILWAY_API_URL = "https://market-predictor-production.up.railway.app"

def debug_railway_auth():
    """Debug Railway backend authentication."""
    print("=== Debug Railway Backend Authentication ===")
    print("Backend URL: {}".format(RAILWAY_API_URL))
    
    # Test 1: Check if backend is accessible
    print("\nTest 1: Check backend health...")
    try:
        response = requests.get("{}/api/watchlist".format(RAILWAY_API_URL), timeout=10)
        print("Backend is accessible: {}".format(response.status_code == 200))
    except Exception as e:
        print("ERROR: Backend not accessible")
        print("  Error: {}".format(str(e)))
        return
    
    # Test 2: Try to register a new user
    print("\nTest 2: Register a test user...")
    test_username = "test_admin_{}".format(int(__import__('time').time()))
    test_password = "test12345"
    test_email = "{}@example.com".format(test_username)
    
    try:
        register_response = requests.post(
            "{}/api/auth/register".format(RAILWAY_API_URL),
            json={
                "username": test_username,
                "email": test_email,
                "password": test_password
            },
            timeout=10
        )
        
        print("Registration status: {}".format(register_response.status_code))
        print("Response: {}".format(register_response.text))
        
        if register_response.status_code == 200:
            print("SUCCESS: Test user registered")
            
            # Test 3: Try to login with the new user
            print("\nTest 3: Login with test user...")
            login_response = requests.post(
                "{}/api/auth/login".format(RAILWAY_API_URL),
                json={
                    "username": test_username,
                    "password": test_password
                },
                timeout=10
            )
            
            print("Login status: {}".format(login_response.status_code))
            print("Response: {}".format(login_response.text))
            
            if login_response.status_code == 200:
                print("SUCCESS: Login worked with new user")
                data = login_response.json()
                print("User data: {}".format(data.get("user", {})))
            else:
                print("ISSUE: Login failed even with fresh registration")
        else:
            print("ISSUE: Registration failed")
    except Exception as e:
        print("ERROR: Registration test failed")
        print("  Error: {}".format(str(e)))

if __name__ == "__main__":
    debug_railway_auth()
