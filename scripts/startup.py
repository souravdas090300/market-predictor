#!/usr/bin/env python3
"""
Startup script to initialize admin user for production.
This should be called during deployment, not on every import.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth import user_manager
from app.core import config

def initialize_admin():
    """Initialize admin user for production."""
    print("Initializing admin user...")
    
    try:
        # Check if admin already exists
        admin_user = user_manager.get_user_by_username("admin")
        
        if admin_user:
            print(f"Admin user exists: {admin_user['username']}")
            # Ensure it has superuser privileges
            if not user_manager.is_superuser(admin_user["user_id"]):
                print("Granting superuser privileges to admin...")
                user_manager.set_superuser(admin_user["user_id"], True)
                print("[OK] Admin user now has superuser privileges")
            else:
                print("[OK] Admin user already has superuser privileges")
        else:
            print("Creating new admin user...")
            # Create admin user
            admin_user = user_manager.create_user(
                username="admin",
                email="admin@marketpredictor.com",
                password="admin12345"
            )
            # Set as superuser
            user_manager.set_superuser(admin_user["user_id"], True)
            print("[OK] Admin user created with superuser privileges")
        
        if config.ENV == "development":
            print("\nAdmin credentials:")
            print("Username: admin")
            print("Password: admin12345")
            print("\nPlease change this password in production!")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error initializing admin: {e}")
        return False

if __name__ == "__main__":
    success = initialize_admin()
    sys.exit(0 if success else 1)