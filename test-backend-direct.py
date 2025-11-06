#!/usr/bin/env python3
"""Direct test of backend registration without going through HTTP."""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, '/Users/brandon/meta-analysis-tool/backend')

async def test_registration():
    """Test registration directly."""
    from app.db.session import async_session
    from app.models.user import User
    from app.core.security import hash_password, UserRole
    from sqlalchemy import select

    print("1. Creating async session...")
    async with async_session() as session:
        try:
            print("2. Checking if test user exists...")
            result = await session.execute(select(User).where(User.email == "test@example.com"))
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  - User already exists: {existing.id}")
            else:
                print("3. Creating new user...")
                hashed_pw = hash_password("TestPass123")

                new_user = User(
                    email="test@example.com",
                    hashed_password=hashed_pw,
                    full_name="Test User",
                    institution="Test U",
                    role=UserRole.RESEARCHER,
                    is_active=True,
                    is_verified=False,
                )

                session.add(new_user)
                print("4. Committing...")
                await session.commit()
                print("5. Refreshing...")
                await session.refresh(new_user)
                print(f"✓ User created: {new_user.id} - {new_user.email}")

        except Exception as e:
            print(f"✗ Error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(test_registration())
