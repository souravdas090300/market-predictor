#!/usr/bin/env python3
"""
Deployment helper script for Vercel + Railway deployment.
This script helps prepare your application for production deployment.
Usage: python scripts/deploy.py [--non-interactive]
"""

import os
import sys
import secrets
import subprocess
import argparse
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key for production."""
    return secrets.token_urlsafe(32)

def check_git_status():
    """Check if git repository is clean."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.stdout.strip():
            print("[WARNING] Git repository has uncommitted changes")
            print("Please commit your changes before deploying:")
            print("  git add .")
            print("  git commit -m 'Prepare for production deployment'")
            return False
        return True
    except Exception as e:
        print(f"[WARNING] Could not check git status: {e}")
        return True

def is_interactive():
    """Check if running in interactive mode."""
    import sys
    return sys.stdin.isatty() and not getattr(sys, 'non_interactive', False)

def create_production_env():
    """Create production environment template."""
    root = Path(__file__).parent.parent
    env_template = root / ".env.production.template"
    
    if env_template.exists():
        print(f"[OK] Production environment template exists: {env_template}")
    else:
        print("[ERROR] Production environment template not found")
        return False
    
    # Check if backend env template exists
    backend_env = root / ".env.production.template"
    if backend_env.exists():
        print(f"[OK] Backend environment template exists: {backend_env}")
    
    # Check if frontend env template exists
    frontend_env = root / "frontend.env.production.template"
    if frontend_env.exists():
        print(f"[OK] Frontend environment template exists: {frontend_env}")
    
    return True

def check_deployment_files():
    """Check if all necessary deployment files exist."""
    root = Path(__file__).parent.parent
    
    required_files = [
        "Dockerfile",
        ".dockerignore",
        "railway.json",
        "nixpacks.toml",
        "DEPLOYMENT.md"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = root / file
        if file_path.exists():
            print(f"[OK] {file} exists")
        else:
            print(f"[ERROR] {file} missing")
            missing_files.append(file)
    
    # Check frontend files
    frontend_files = [
        "frontend/vercel.json"
    ]
    
    for file in frontend_files:
        file_path = root / file
        if file_path.exists():
            print(f"[OK] {file} exists")
        else:
            print(f"[ERROR] {file} missing")
            missing_files.append(file)
    
    return len(missing_files) == 0, missing_files

def print_deployment_checklist():
    """Print deployment checklist."""
    print("\n" + "="*60)
    print("DEPLOYMENT CHECKLIST")
    print("="*60)
    
    print("\n1. Pre-deployment:")
    print("   [ ] Commit all changes to git")
    print("   [ ] Push to GitHub repository")
    print("   [ ] Generate SECRET_KEY for production")
    print("   [ ] Review environment variables")
    
    print("\n2. Backend Deployment (Railway):")
    print("   [ ] Create Railway project")
    print("   [ ] Connect GitHub repository")
    print("   [ ] Add Redis service")
    print("   [ ] Configure environment variables")
    print("   [ ] Deploy backend")
    print("   [ ] Copy backend URL")
    
    print("\n3. Frontend Deployment (Vercel):")
    print("   [ ] Create Vercel project")
    print("   [ ] Connect GitHub repository")
    print("   [ ] Set NEXT_PUBLIC_API_URL environment variable")
    print("   [ ] Deploy frontend")
    print("   [ ] Copy frontend URL")
    
    print("\n4. Post-deployment:")
    print("   [ ] Update CORS settings in Railway")
    print("   [ ] Test all API endpoints")
    print("   [ ] Test authentication flow")
    print("   [ ] Configure custom domain (optional)")
    print("   [ ] Set up monitoring")
    
    print("\n5. Documentation:")
    print("   [ ] Read DEPLOYMENT.md for detailed instructions")
    print("   [ ] Update environment variables with real values")
    print("   [ ] Test health check endpoint")

def main():
    """Main deployment helper function."""
    parser = argparse.ArgumentParser(description='Market Predictor Deployment Helper')
    parser.add_argument('--non-interactive', action='store_true', help='Run in non-interactive mode')
    args = parser.parse_args()
    
    if args.non_interactive:
        sys.non_interactive = True
    
    print("Market Predictor Deployment Helper")
    print("="*60)
    
    # Check git status
    if not check_git_status():
        if is_interactive():
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Deployment cancelled.")
                sys.exit(1)
        else:
            print("[INFO] Non-interactive mode - continuing despite uncommitted changes")
    
    # Check deployment files
    print("\n[INFO] Checking deployment files...")
    files_ok, missing_files = check_deployment_files()
    
    if not files_ok:
        print(f"\n[WARNING] Missing deployment files: {', '.join(missing_files)}")
        print("Please ensure all deployment files are present.")
        if is_interactive():
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Deployment cancelled.")
                sys.exit(1)
        else:
            print("[INFO] Non-interactive mode - continuing despite missing files")
    
    # Check environment templates
    print("\n[INFO] Checking environment templates...")
    if not create_production_env():
        print("[WARNING] Environment templates not found")
        if is_interactive():
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Deployment cancelled.")
                sys.exit(1)
        else:
            print("[INFO] Non-interactive mode - continuing despite missing templates")
    
    # Generate secret key
    print("\n[INFO] Generating production secret key...")
    secret_key = generate_secret_key()
    print(f"Your production SECRET_KEY: {secret_key}")
    print("[WARNING] Save this key securely and add it to Railway environment variables!")
    
    # Print checklist
    print_deployment_checklist()
    
    print("\n[SUCCESS] Deployment preparation complete!")
    print("[INFO] For detailed instructions, see DEPLOYMENT.md")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Deploy backend to Railway (see DEPLOYMENT.md)")
    print("3. Deploy frontend to Vercel (see DEPLOYMENT.md)")
    print("4. Update CORS settings with actual URLs")

if __name__ == "__main__":
    main()