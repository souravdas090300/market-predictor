#!/usr/bin/env python3
"""
Script to ensure admin user exists and has proper superuser privileges.
Run this after deployment to set up the initial admin user.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth import user_manager

def ensure_admin():
    """Ensure admin user exists with superuser privileges."""
    print("Setting up admin user...")
    
    try:
        # Try to get existing admin user
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
        
        print("\nAdmin credentials:")
        print("Username: admin")
        print("Password: admin12345")
        print("\nPlease change this password in production!")
        
    except Exception as e:
        print(f"[ERROR] Error setting up admin: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ensure_admin()
