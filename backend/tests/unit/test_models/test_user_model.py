"""Tests for User database model."""
import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from app.models.user import User
from app.core.security import get_password_hash, verify_password


class TestUserModel:
    """Tests for User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, async_session):
        """Test creating a new user."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpass123"),
            name="Test User",
            institution="Test University",
        )

        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.institution == "Test University"
        assert user.role == "researcher"  # Default role
        assert user.is_active is True
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_user_email_unique(self, async_session):
        """Test that user email must be unique."""
        user1 = User(
            email="duplicate@example.com",
            hashed_password=get_password_hash("pass1"),
            name="User 1",
        )
        user2 = User(
            email="duplicate@example.com",
            hashed_password=get_password_hash("pass2"),
            name="User 2",
        )

        async_session.add(user1)
        await async_session.commit()

        async_session.add(user2)
        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_user_password_hashing(self, async_session):
        """Test that passwords are properly hashed."""
        plain_password = "mysecurepassword123"
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash(plain_password),
            name="Test User",
        )

        async_session.add(user)
        await async_session.commit()

        # Password should be hashed, not plain text
        assert user.hashed_password != plain_password
        # Should be able to verify with correct password
        assert verify_password(plain_password, user.hashed_password)
        # Should fail with incorrect password
        assert not verify_password("wrongpassword", user.hashed_password)

    @pytest.mark.asyncio
    async def test_user_roles(self, async_session):
        """Test different user roles."""
        researcher = User(
            email="researcher@example.com",
            hashed_password=get_password_hash("pass"),
            name="Researcher",
            role="researcher",
        )
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("pass"),
            name="Admin",
            role="admin",
        )
        reviewer = User(
            email="reviewer@example.com",
            hashed_password=get_password_hash("pass"),
            name="Reviewer",
            role="reviewer",
        )

        async_session.add_all([researcher, admin, reviewer])
        await async_session.commit()

        assert researcher.role == "researcher"
        assert admin.role == "admin"
        assert reviewer.role == "reviewer"

    @pytest.mark.asyncio
    async def test_user_deactivation(self, async_session):
        """Test user can be deactivated."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("pass"),
            name="Test User",
            is_active=True,
        )

        async_session.add(user)
        await async_session.commit()

        assert user.is_active is True

        # Deactivate user
        user.is_active = False
        await async_session.commit()
        await async_session.refresh(user)

        assert user.is_active is False

    @pytest.mark.asyncio
    async def test_user_updated_at(self, async_session):
        """Test that updated_at is tracked."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("pass"),
            name="Original Name",
        )

        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        original_updated_at = user.updated_at

        # Update user
        user.name = "Updated Name"
        await async_session.commit()
        await async_session.refresh(user)

        assert user.name == "Updated Name"
        assert user.updated_at > original_updated_at

    @pytest.mark.asyncio
    async def test_user_representation(self, async_session):
        """Test user __repr__ method."""
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("pass"),
            name="Test User",
        )

        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        repr_string = repr(user)
        assert "User" in repr_string
        assert user.email in repr_string or str(user.id) in repr_string
