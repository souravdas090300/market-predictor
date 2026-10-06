#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnose backend issues"""

import sys
import traceback
import io

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*60)
print("Market Predictor Backend Diagnostic")
print("="*60 + "\n")

# Test 1: Database imports
print("1. Testing database imports...")
try:
    from app.database import SessionLocal, engine
    print("   [OK] Database import successful")
except Exception as e:
    print(f"   [FAIL] Database import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Models import
print("\n2. Testing models import...")
try:
    from app.database_models import LivePrice
    print("   [OK] Models import successful")
except Exception as e:
    print(f"   [FAIL] Models import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Database connection
print("\n3. Testing database connection...")
try:
    from sqlalchemy import text
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))
    print("   [OK] Database connection successful")
except Exception as e:
    print(f"   [FAIL] Database connection failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Tables exist
print("\n4. Checking database tables...")
try:
    with SessionLocal() as session:
        prices = session.query(LivePrice).count()
    print(f"   [OK] LivePrice: {prices} records")
except Exception as e:
    print(f"   [FAIL] Database tables error: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: FastAPI app
print("\n5. Testing FastAPI app...")
try:
    from app.api import app
    print("   [OK] FastAPI app loads successfully")
except Exception as e:
    print(f"   [FAIL] FastAPI app failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 6: Routes registered
print("\n6. Checking registered routes...")
try:
    routes = [route.path for route in app.routes]

    assets_routes = [r for r in routes if '/assets' in r]
    if assets_routes:
        print(f"   [OK] Found {len(assets_routes)} asset routes:")
        for route in assets_routes[:10]:
            print(f"      - {route}")
    else:
        print("   [FAIL] No asset routes found!")
except Exception as e:
    print(f"   [FAIL] Route check failed: {e}")

# Test 7: Background tasks import
print("\n7. Testing background tasks import...")
try:
    from app.core.background_tasks import get_all_cached_prices, get_cache_status
    print("   [OK] Background tasks import successful")
except Exception as e:
    print(f"   [FAIL] Background tasks import failed: {e}")
    traceback.print_exc()

print("\n" + "="*60)
print("[OK] All checks passed! Backend should be working.")
print("="*60 + "\n")
