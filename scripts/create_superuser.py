"""Create a superuser account for admin access."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.auth import user_manager

def create_superuser():
    """Create a superuser account."""
    print("=== Superuser Creation ===")
    print("This will create a superuser account for admin access.\n")
    
    # Get credentials from environment or use defaults
    username = os.getenv("ADMIN_USERNAME", "admin")
    email = os.getenv("ADMIN_EMAIL", "admin@marketpredictor.com")
    password = os.getenv("ADMIN_PASSWORD", "admin12345")
    
    print("Creating superuser with:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {'*' * len(password)}")
    print()
    
    try:
        # Check if user already exists
        existing_user = user_manager.get_user_by_username(username)
        
        if existing_user:
            print(f"User '{username}' already exists.")
            
            # Check if already superuser
            if existing_user.get("is_superuser", False):
                print(f"User is already a superuser!")
                print(f"\nYou can login at: https://market-predictor-eta.vercel.app/admin")
                print(f"Login credentials:")
                print(f"  Username: {username}")
                print(f"  Password: (use your existing password)")
            else:
                # Set as superuser
                user_manager.set_superuser(existing_user["user_id"], True)
                print(f"User '{username}' granted superuser privileges!")
                print(f"\nYou can now login at: https://market-predictor-eta.vercel.app/admin")
                print(f"Login credentials:")
                print(f"  Username: {username}")
                print(f"  Password: (use your existing password)")
        else:
            # Create user
            user_data = user_manager.create_user(username, email, password)
            
            # Set as superuser
            user_manager.set_superuser(user_data["user_id"], True)
            
            print(f"Superuser '{username}' created successfully!")
            print(f"  User ID: {user_data['user_id']}")
            print(f"  Email: {email}")
            print(f"  Is Superuser: True")
            print(f"\nYou can now login at: https://market-predictor-eta.vercel.app/admin")
            print(f"Login credentials:")
            print(f"  Username: {username}")
            print(f"  Password: {password}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_superuser()
