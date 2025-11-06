#!/usr/bin/env python3
"""Test Pydantic UserCreate model."""
import sys
sys.path.insert(0, '/Users/brandon/meta-analysis-tool/backend')

from app.models.user import UserCreate

try:
    print("Testing UserCreate model...")
    user = UserCreate(
        email="test@example.com",
        password="SecurePass123",
        full_name="Test User",
        institution="Test U"
    )
    print(f"✓ UserCreate validated successfully: {user.email}")
    print(f"  Password: {'*' * len(user.password)}")
except Exception as e:
    print(f"✗ UserCreate validation failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
