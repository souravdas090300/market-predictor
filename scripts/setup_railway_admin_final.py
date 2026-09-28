"""Setup admin user on Railway backend using the setup endpoint."""
import requests
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

RAILWAY_API_URL = "https://market-predictor-production.up.railway.app"

def setup_railway_admin_final():
    """Setup admin user on Railway backend using setup endpoint."""
    print("=== Setup Admin User on Railway Backend ===")
    print("Backend URL: {}".format(RAILWAY_API_URL))
    
    # Admin credentials
    username = "admin"
    password = "admin12345"
    
    print("\nUsing setup endpoint to grant admin privileges...")
    try:
        setup_response = requests.post(
            "{}/api/setup-initial-admin".format(RAILWAY_API_URL),
            json={
                "username": username,
                "password": password
            },
            timeout=10
        )
        
        if setup_response.status_code == 200:
            print("SUCCESS: Admin setup completed")
            print("  Response: {}".format(setup_response.json()))
        elif setup_response.status_code == 403:
            print("Admin already exists on Railway backend")
            print("  This is actually good - means admin is already set up")
        else:
            print("ERROR: Setup failed")
            print("  Status: {}".format(setup_response.status_code))
            print("  Response: {}".format(setup_response.text))
            return
    except Exception as e:
        print("ERROR: Could not connect to Railway backend")
        print("  Error: {}".format(str(e)))
        return
    
    print("\n=== Setup Complete ===")
    print("Admin credentials for Railway backend:")
    print("  Username: {}".format(username))
    print("  Password: {}".format(password))
    print("  Backend URL: {}".format(RAILWAY_API_URL))
    print("\nLogin at: https://market-predictor-eta.vercel.app/auth/login")
    print("Then access admin at: https://market-predictor-eta.vercel.app/admin")

if __name__ == "__main__":
    setup_railway_admin_final()
