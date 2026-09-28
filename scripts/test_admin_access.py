"""Test admin access and authentication flow."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth import user_manager

def test_admin_access():
    """Test admin access and authentication."""
    print("=== Admin Access Test ===")
    
    # Check admin user
    admin_user = None
    for user_id, user in user_manager.users.items():
        if user["username"].lower() == "admin":
            admin_user = user
            break
    
    if not admin_user:
        print("ERROR: Admin user not found!")
        return
    
    print("Admin User Found:")
    print("  Username: {}".format(admin_user["username"]))
    print("  Email: {}".format(admin_user["email"]))
    print("  Is Superuser: {}".format(admin_user.get("is_superuser", False)))
    print("  Roles: {}".format(admin_user.get("roles", [])))
    print("  Is Active: {}".format(admin_user.get("is_active", False)))
    print("  Disabled: {}".format(admin_user.get("disabled", False)))
    
    # Test authentication
    print("\n=== Testing Authentication ===")
    test_password = "admin12345"
    auth_result = user_manager.authenticate_user("admin", test_password)
    
    if auth_result:
        print("SUCCESS: Authentication worked!")
        print("  Authenticated User: {}".format(auth_result["username"]))
        print("  Roles in auth result: {}".format(auth_result.get("roles", [])))
        print("  Is Superuser in auth result: {}".format(auth_result.get("is_superuser", False)))
    else:
        print("ERROR: Authentication failed!")
        print("  Try resetting the password with: python scripts/reset_admin_password.py")
    
    # Check if user has admin role
    if admin_user.get("is_superuser", False) and "admin" in admin_user.get("roles", []):
        print("\nOK: User has proper admin access")
    else:
        print("\nERROR: User does not have proper admin access")
        print("  Run: python scripts/update_admin_roles.py")

if __name__ == "__main__":
    test_admin_access()
