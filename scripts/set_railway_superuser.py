"""Set superuser status on Railway backend by directly calling the endpoint."""
import requests
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

RAILWAY_API_URL = "https://market-predictor-production.up.railway.app"

def set_railway_superuser():
    """Set superuser status for admin on Railway backend."""
    print("=== Set Superuser Status on Railway Backend ===")
    
    # Admin credentials
    username = "admin"
    password = "admin12345"
    
    print("Logging in as admin...")
    try:
        login_response = requests.post(
            "{}/api/auth/login".format(RAILWAY_API_URL),
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )
        
        if login_response.status_code == 200:
            data = login_response.json()
            access_token = data.get("access_token")
            print("Login successful")
        else:
            print("ERROR: Login failed")
            print("  Status: {}".format(login_response.status_code))
            print("  Response: {}".format(login_response.text))
            return
    except Exception as e:
        print("ERROR: Could not login")
        print("  Error: {}".format(str(e)))
        return
    
    print("\nTrying to set superuser status...")
    
    # Try different endpoints that might work
    endpoints_to_try = [
        "/api/admin/add-admin/{}".format(username),
        "/api/admin/add-admin/{}".format(username),
        "/api/admin/add-admin/{}".format(username)
    ]
    
    for endpoint in endpoints_to_try:
        try:
            response = requests.post(
                "{}{}".format(RAILWAY_API_URL, endpoint),
                headers={"Authorization": "Bearer {}".format(access_token)},
                timeout=10
            )
            
            if response.status_code == 200:
                print("SUCCESS: Superuser status set via {}".format(endpoint))
                print("  Response: {}".format(response.json()))
                return
            else:
                print("Failed with {}: Status {}".format(endpoint, response.status_code))
        except Exception as e:
            print("Error with {}: {}".format(endpoint, str(e)))
    
    print("\n=== Manual Setup Required ===")
    print("The Railway backend might need manual superuser setup.")
    print("You can try:")
    print("1. Access the Railway console directly")
    print("2. Or modify the Railway backend code to auto-promote first user")
    print("3. Or use Railway's CLI to set environment variables")

if __name__ == "__main__":
    set_railway_superuser()
