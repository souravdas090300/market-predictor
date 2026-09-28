"""Check current admin status on Railway backend."""
import requests
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

RAILWAY_API_URL = "https://market-predictor-production.up.railway.app"

def check_railway_admin_status():
    """Check admin status on Railway backend."""
    print("=== Check Admin Status on Railway Backend ===")
    print("Backend URL: {}".format(RAILWAY_API_URL))
    
    # Admin credentials
    username = "admin"
    password = "admin12345"
    
    print("\nStep 1: Logging in as admin...")
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
            user_data = data.get("user", {})
            print("Login successful")
            print("  User data: {}".format(user_data))
        else:
            print("ERROR: Login failed")
            print("  Status: {}".format(login_response.status_code))
            print("  Response: {}".format(login_response.text))
            return
    except Exception as e:
        print("ERROR: Could not login")
        print("  Error: {}".format(str(e)))
        return
    
    print("\nStep 2: Checking user info...")
    try:
        me_response = requests.get(
            "{}/api/auth/me".format(RAILWAY_API_URL),
            headers={"Authorization": "Bearer {}".format(access_token)},
            timeout=10
        )
        
        if me_response.status_code == 200:
            user_info = me_response.json()
            print("User info retrieved:")
            print("  Username: {}".format(user_info.get("username")))
            print("  Is Superuser: {}".format(user_info.get("is_superuser", False)))
            print("  Roles: {}".format(user_info.get("roles", [])))
            
            if user_info.get("is_superuser", False) and "admin" in user_info.get("roles", []):
                print("\nSUCCESS: User has admin access!")
                print("You can now access the admin panel at:")
                print("https://market-predictor-eta.vercel.app/admin")
            else:
                print("\nISSUE: User does not have admin access yet")
                print("You need to redeploy the backend with the setup endpoint")
        else:
            print("ERROR: Could not get user info")
            print("  Status: {}".format(me_response.status_code))
            print("  Response: {}".format(me_response.text))
    except Exception as e:
        print("ERROR: Could not get user info")
        print("  Error: {}".format(str(e)))

if __name__ == "__main__":
    check_railway_admin_status()
