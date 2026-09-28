"""Update existing superusers to have admin role."""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth import user_manager

def update_admin_roles():
    """Update all superusers to have admin role."""
    print("=== Updating Admin Roles ===")
    
    # Print current user data for debugging
    print("\nCurrent users:")
    for user_id, user in user_manager.users.items():
        print(f"  Username: {user['username']}")
        print(f"  Email: {user['email']}")
        print(f"  Is Superuser: {user.get('is_superuser', False)}")
        print(f"  Roles: {user.get('roles', [])}")
        print()
    
    updated_count = 0
    for user_id, user in user_manager.users.items():
        if user.get("is_superuser", False):
            # Ensure roles array exists
            if "roles" not in user:
                user["roles"] = ["user"]
            
            # Add admin role if not present
            if "admin" not in user["roles"]:
                user["roles"].append("admin")
                updated_count += 1
                print(f"Updated user '{user['username']}' with admin role")
    
    if updated_count > 0:
        user_manager._save_users()
        print(f"\nSuccessfully updated {updated_count} user(s) with admin role")
    else:
        print("\nNo updates needed - all superusers already have admin role")

if __name__ == "__main__":
    update_admin_roles()
