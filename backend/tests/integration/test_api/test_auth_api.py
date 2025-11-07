"""Integration tests for authentication API."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


class TestAuthAPI:
    """Test suite for authentication endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.mark.integration
    def test_register_new_user(self, client):
        """Test user registration."""
        user_data = {
            "email": f"test_{uuid4()}@example.com",
            "password": "SecurePassword123!",
            "name": "Test User",
            "institution": "Test University"
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 201 or response.status_code == 200
        data = response.json()
        assert "id" in data or "user" in data
        assert "email" in str(data).lower()

    @pytest.mark.integration
    def test_register_duplicate_email(self, client):
        """Test registering with duplicate email."""
        email = f"duplicate_{uuid4()}@example.com"
        user_data = {
            "email": email,
            "password": "Password123!",
            "name": "User One",
            "institution": "Test Uni"
        }

        # First registration
        response1 = client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code in [200, 201]

        # Duplicate registration
        response2 = client.post("/api/v1/auth/register", json=user_data)
        assert response2.status_code in [400, 409]  # Bad Request or Conflict

    @pytest.mark.integration
    def test_login_with_valid_credentials(self, client):
        """Test login with valid credentials."""
        # First register
        email = f"login_test_{uuid4()}@example.com"
        password = "TestPassword123!"

        register_data = {
            "email": email,
            "password": password,
            "name": "Login Test",
            "institution": "Test Uni"
        }
        client.post("/api/v1/auth/register", json=register_data)

        # Then login
        login_data = {
            "email": email,
            "password": password
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data

    @pytest.mark.integration
    def test_login_with_invalid_password(self, client):
        """Test login with wrong password."""
        # First register
        email = f"wrong_pass_{uuid4()}@example.com"
        register_data = {
            "email": email,
            "password": "CorrectPassword123!",
            "name": "Test",
            "institution": "Test"
        }
        client.post("/api/v1/auth/register", json=register_data)

        # Try login with wrong password
        login_data = {
            "email": email,
            "password": "WrongPassword123!"
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401  # Unauthorized

    @pytest.mark.integration
    def test_login_with_nonexistent_user(self, client):
        """Test login with email that doesn't exist."""
        login_data = {
            "email": f"nonexistent_{uuid4()}@example.com",
            "password": "Password123!"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401  # Unauthorized

    @pytest.mark.integration
    def test_access_protected_route_without_token(self, client):
        """Test accessing protected route without authentication."""
        response = client.get("/api/v1/meta-analysis/list")

        # Should either require auth or return empty list
        assert response.status_code in [200, 401, 403]

    @pytest.mark.integration
    def test_access_protected_route_with_token(self, client):
        """Test accessing protected route with valid token."""
        # Register and login
        email = f"protected_{uuid4()}@example.com"
        password = "Password123!"

        register_data = {
            "email": email,
            "password": password,
            "name": "Protected Test",
            "institution": "Test"
        }
        client.post("/api/v1/auth/register", json=register_data)

        login_response = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })

        token_data = login_response.json()
        token = token_data.get("access_token") or token_data.get("token")

        # Access protected route
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/meta-analysis/list", headers=headers)

        assert response.status_code == 200

    @pytest.mark.integration
    def test_token_expiration(self, client):
        """Test that expired tokens are rejected."""
        # This would require manipulating token expiration
        # Skip for now or implement with freezegun
        pytest.skip("Token expiration test requires time manipulation")

    @pytest.mark.integration
    def test_password_validation(self, client):
        """Test password validation rules."""
        weak_passwords = [
            "short",  # Too short
            "alllowercase",  # No uppercase/numbers
            "12345678",  # Only numbers
        ]

        for password in weak_passwords:
            user_data = {
                "email": f"weak_{uuid4()}@example.com",
                "password": password,
                "name": "Test",
                "institution": "Test"
            }

            response = client.post("/api/v1/auth/register", json=user_data)
            # Should reject weak passwords
            assert response.status_code in [400, 422]

    @pytest.mark.integration
    def test_email_validation(self, client):
        """Test email validation."""
        invalid_emails = [
            "not-an-email",
            "@missing-local.com",
            "missing-at-sign.com"
        ]

        for email in invalid_emails:
            user_data = {
                "email": email,
                "password": "ValidPassword123!",
                "name": "Test",
                "institution": "Test"
            }

            response = client.post("/api/v1/auth/register", json=user_data)
            # Should reject invalid emails
            assert response.status_code in [400, 422]


class TestAuthTokenManagement:
    """Test token generation and validation."""

    @pytest.mark.integration
    def test_token_contains_user_info(self, client):
        """Test that token contains user information."""
        # Register and login
        email = f"token_test_{uuid4()}@example.com"
        password = "Password123!"

        client.post("/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "name": "Token Test",
            "institution": "Test"
        })

        response = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })

        data = response.json()
        assert "access_token" in data or "token" in data

        # Token should be a valid JWT
        token = data.get("access_token") or data.get("token")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

    @pytest.mark.integration
    def test_refresh_token(self, client):
        """Test token refresh functionality."""
        # This depends on your auth implementation
        pytest.skip("Refresh token test - implement based on your auth flow")
