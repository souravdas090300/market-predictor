"""Setup default superuser account."""
import sys
import io
from pathlib import Path

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth import UserManager, user_manager


def setup_superuser():
    """Create default superuser account."""
    username = "admin"
    email = "admin@marketpredictor.local"
    password = "admin123"
    
    try:
        # Try to create user
        user_data = user_manager.create_user(username, email, password)
        
        # Set as superuser
        user_manager.set_superuser(user_data["user_id"], True)
        
        print(f"[OK] Superuser '{username}' created successfully!")
        print(f"   User ID: {user_data['user_id']}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Roles: {user_data['roles']}")
        print(f"   Is Superuser: {user_data['is_superuser']}")
        print("\n[!] IMPORTANT: Change the default password before production!")
        print("\nYou can now access the admin dashboard at http://localhost:8001")
        
    except ValueError as e:
        if "Username already exists" in str(e) or "Email already registered" in str(e):
            # User already exists, just set as superuser
            print(f"User '{username}' already exists, setting as superuser...")
            
            # Find user
            user_id = None
            for uid, user in user_manager.users.items():
                if user["username"] == username:
                    user_id = uid
                    break
            
            if user_id:
                user_manager.set_superuser(user_id, True)
                print(f"[OK] User '{username}' set as superuser!")
            else:
                print(f"[ERROR] User '{username}' not found")
        else:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    setup_superuser()