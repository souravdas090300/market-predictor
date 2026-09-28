"""Setup admin user on Railway backend via API."""
import requests
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

RAILWAY_API_URL = "https://market-predictor-production.up.railway.app"

def setup_railway_admin():
    """Setup admin user on Railway backend."""
    print("=== Setup Admin User on Railway Backend ===")
    print("Backend URL: {}".format(RAILWAY_API_URL))
    
    # Admin credentials
    username = "admin"
    email = "admin@marketpredictor.com"
    password = "admin12345"
    
    print("\nStep 1: Registering admin user...")
    try:
        register_response = requests.post(
            "{}/api/auth/register".format(RAILWAY_API_URL),
            json={
                "username": username,
                "email": email,
                "password": password
            },
            timeout=10
        )
        
        if register_response.status_code == 200:
            print("SUCCESS: Admin user registered")
            print("  User ID: {}".format(register_response.json().get("user_id", "N/A")))
        elif register_response.status_code == 400:
            print("User might already exist, trying login directly...")
            # Try to login directly
            login_response = requests.post(
                "{}/api/auth/login".format(RAILWAY_API_URL),
                json={
                    "username": username,
                    "password": password
                },
                timeout=10
            )
            if login_response.status_code == 200:
                print("SUCCESS: Login worked with existing user")
                data = login_response.json()
                access_token = data.get("access_token")
                user_data = data.get("user", {})
                print("  User data: {}".format(user_data))
            else:
                print("ERROR: Could not login with existing user")
                print("  Status: {}".format(login_response.status_code))
                print("  Response: {}".format(login_response.text))
                return
        else:
            print("ERROR: Registration failed")
            print("  Status: {}".format(register_response.status_code))
            print("  Response: {}".format(register_response.text))
            return
    except Exception as e:
        print("ERROR: Could not connect to Railway backend")
        print("  Error: {}".format(str(e)))
        return
    
    print("\nStep 2: Logging in as admin...")
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
            print("SUCCESS: Login successful")
            print("  Access token obtained")
        else:
            print("ERROR: Login failed")
            print("  Status: {}".format(login_response.status_code))
            print("  Response: {}".format(login_response.text))
            return
    except Exception as e:
        print("ERROR: Could not login")
        print("  Error: {}".format(str(e)))
        return
    
    print("\nStep 3: Setting superuser status...")
    try:
        # You'll need to manually set the superuser status or add an endpoint for this
        # For now, let's check if there's an admin endpoint to set superuser
        set_admin_response = requests.post(
            "{}/api/admin/add-admin/{}".format(RAILWAY_API_URL, username),
            headers={"Authorization": "Bearer {}".format(access_token)},
            timeout=10
        )
        
        if set_admin_response.status_code == 200:
            print("SUCCESS: Admin privileges granted")
        else:
            print("Could not set admin via API (might need manual setup)")
            print("  Status: {}".format(set_admin_response.status_code))
    except Exception as e:
        print("Could not set admin status via API")
        print("  Error: {}".format(str(e)))
    
    print("\n=== Setup Complete ===")
    print("Admin credentials for Railway backend:")
    print("  Username: {}".format(username))
    print("  Password: {}".format(password))
    print("  Backend URL: {}".format(RAILWAY_API_URL))
    print("\nLogin at: https://market-predictor-eta.vercel.app/auth/login")
    print("Then access admin at: https://market-predictor-eta.vercel.app/admin")

if __name__ == "__main__":
    setup_railway_admin()
