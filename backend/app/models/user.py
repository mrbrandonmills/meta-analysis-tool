"""User model for authentication and authorization."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, field_validator

from app.db.base import Base
from app.core.security import UserRole


class User(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)  # Legacy field
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    institution = Column(String(255), nullable=True)

    # Tier system (separate from role)
    tier = Column(
        SQLEnum(
            "tier_1_researcher",
            "tier_2_reviewer",
            "tier_3_editor",
            name="user_tier_enum"
        ),
        nullable=False,
        default="tier_1_researcher",
        index=True
    )

    # Role-based access control
    role = Column(
        SQLEnum(UserRole, name="user_role", native_enum=False),
        nullable=False,
        default=UserRole.RESEARCHER,
    )

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Email verification
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)

    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Payment fields
    stripe_customer_id = Column(String(255), unique=True, nullable=True, index=True)
    is_paying_member = Column(Boolean, default=False, nullable=False)
    member_since = Column(DateTime, nullable=True)
    subscription_status = Column(String(50), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    report_templates = relationship("ReportTemplate", back_populates="creator", cascade="all, delete-orphan", lazy="dynamic")
    meta_analyses = relationship("MetaAnalysis", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    contributions = relationship("PayoutContribution", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    # api_keys = relationship("APIKey", back_populates="user")

    def __repr__(self):
        """String representation."""
        return f"<User {self.email} ({self.role.value})>"


class APIKey(Base):
    """API Key model for programmatic access."""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key to users

    # API key details
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    key_prefix = Column(String(20), nullable=False)  # First 8 chars for identification
    name = Column(String(255), nullable=False)  # User-friendly name
    description = Column(Text, nullable=True)

    # Permissions (can be more granular than user role)
    scopes = Column(Text, nullable=True)  # JSON array of permission scopes

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    # user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        """String representation."""
        return f"<APIKey {self.key_prefix}... for user {self.user_id}>"


# Pydantic schemas for API requests/responses
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: Optional[str] = None
    institution: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: Optional[str] = None
    institution: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        """Validate password strength."""
        if v is not None:
            if len(v) < 8:
                raise ValueError("Password must be at least 8 characters")
            if not any(c.isupper() for c in v):
                raise ValueError("Password must contain at least one uppercase letter")
            if not any(c.islower() for c in v):
                raise ValueError("Password must contain at least one lowercase letter")
            if not any(c.isdigit() for c in v):
                raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(UserBase):
    """User response schema (excludes password)."""

    id: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserInDB(UserResponse):
    """User schema with hashed password (internal use)."""

    hashed_password: str


class APIKeyCreate(BaseModel):
    """API key creation schema."""

    name: str
    description: Optional[str] = None
    expires_in_days: Optional[int] = 365


class APIKeyResponse(BaseModel):
    """API key response schema."""

    id: str
    name: str
    description: Optional[str] = None
    key_prefix: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class APIKeyWithSecret(APIKeyResponse):
    """API key response with the actual key (only shown once on creation)."""

    key: str
