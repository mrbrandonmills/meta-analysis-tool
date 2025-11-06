"""Test user registration to verify fix."""
import asyncio
import httpx
from app.main import app
from app.db.session import async_engine
from sqlalchemy import text


async def test_registration():
    """Test user registration endpoint."""
    
    # Clean up any existing test user
    async with async_engine.begin() as conn:
        await conn.execute(text("DELETE FROM users WHERE email = 'testfix@example.com'"))
    
    # Test registration
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "testfix@example.com",
                "password": "TestPass123",
                "full_name": "Test Fix User",
                "institution": "Test University"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✓ Registration successful!")
            return True
        else:
            print(f"✗ Registration failed: {response.json()}")
            return False


if __name__ == "__main__":
    result = asyncio.run(test_registration())
    exit(0 if result else 1)
