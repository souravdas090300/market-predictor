"""Create a superuser account for admin access."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth import UserManager, user_manager


def create_superuser():
    """Create a superuser account."""
    print("=== Create Superuser Account ===\n")
    
    username = input("Username: ").strip()
    if not username:
        print("Username is required")
        return
    
    email = input("Email: ").strip()
    if not email:
        print("Email is required")
        return
    
    password = input("Password: ").strip()
    if len(password) < 8:
        print("Password must be at least 8 characters")
        return
    
    confirm_password = input("Confirm Password: ").strip()
    if password != confirm_password:
        print("Passwords do not match")
        return
    
    try:
        # Create user
        user_data = user_manager.create_user(username, email, password)
        
        # Set as superuser
        user_manager.set_superuser(user_data["user_id"], True)
        
        print(f"\n✅ Superuser '{username}' created successfully!")
        print(f"   User ID: {user_data['user_id']}")
        print(f"   Email: {email}")
        print(f"   Roles: {user_data['roles']}")
        print(f"   Is Superuser: {user_data['is_superuser']}")
        print("\nYou can now access the admin dashboard at http://localhost:8001")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    create_superuser()