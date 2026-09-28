"""Reset admin password."""
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth import user_manager
from app.security import get_password_hash

def reset_admin_password():
    """Reset admin password."""
    print("=== Reset Admin Password ===")
    
    # Get credentials from environment or use defaults
    username = "admin"
    new_password = os.getenv("ADMIN_PASSWORD", "admin12345")
    
    print("Resetting password for user: {}".format(username))
    print("New password: {}".format('*' * len(new_password)))
    
    # Find admin user
    admin_user = None
    for user_id, user in user_manager.users.items():
        if user["username"].lower() == username.lower():
            admin_user = user
            break
    
    if not admin_user:
        print("User '{}' not found".format(username))
        return
    
    # Update password
    admin_user["hashed_password"] = get_password_hash(new_password)
    admin_user["updated_at"] = datetime.now(timezone.utc).isoformat()
    user_manager._save_users()
    
    print("\nPassword reset successfully for '{}'".format(username))
    print("\nLogin credentials:")
    print("  Username: {}".format(username))
    print("  Password: {}".format(new_password))
    print("\nLogin at: https://market-predictor-eta.vercel.app/auth/login")
    print("Then access admin at: https://market-predictor-eta.vercel.app/admin")

if __name__ == "__main__":
    reset_admin_password()
