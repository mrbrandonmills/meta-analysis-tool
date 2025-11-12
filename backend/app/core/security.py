"""
Security utilities for authentication and authorization.

Includes:
- JWT token creation and validation (access + refresh tokens)
- Password hashing with bcrypt
- Role-based access control (RBAC)
- API key management
- OAuth2 password flow
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

# Password hashing context using argon2 (more secure than bcrypt, no length limits)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# HTTP Bearer scheme for JWT
http_bearer = HTTPBearer(auto_error=False)


# User roles for RBAC
class UserRole(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"  # Full system access
    RESEARCHER = "researcher"  # Can create and manage own projects
    REVIEWER = "reviewer"  # Can review and comment on projects
    VIEWER = "viewer"  # Read-only access


# Token types
class TokenType(str, Enum):
    """JWT token types."""

    ACCESS = "access"
    REFRESH = "refresh"


# Pydantic models for security
class Token(BaseModel):
    """OAuth2 token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Data extracted from JWT token."""

    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    token_type: Optional[TokenType] = None


class PasswordResetRequest(BaseModel):
    """Password reset request."""

    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset with token."""

    token: str
    new_password: str

    @field_validator("new_password")
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


class APIKeyCreate(BaseModel):
    """API key creation request."""

    name: str
    expires_in_days: Optional[int] = 365  # Default 1 year


# Password utilities
def hash_password(password: str) -> str:
    """
    Hash a password using argon2.

    Argon2 is the modern standard for password hashing (recommended by OWASP).
    It has no practical length limits and is more secure than bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# JWT token utilities
def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": TokenType.ACCESS.value,
    })

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Payload data to encode
        expires_delta: Optional expiration time delta (default 7 days)

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens last 7 days

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": TokenType.REFRESH.value,
    })

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        TokenData object with extracted information

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        token_type: str = payload.get("type")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(
            user_id=user_id,
            email=email,
            role=UserRole(role) if role else None,
            token_type=TokenType(token_type) if token_type else None,
        )

    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_token_pair(user_id: str, email: str, role: UserRole) -> Token:
    """
    Create both access and refresh tokens for a user.

    Args:
        user_id: User's unique identifier
        email: User's email address
        role: User's role

    Returns:
        Token object with access and refresh tokens
    """
    token_data = {
        "sub": user_id,
        "email": email,
        "role": role.value,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


# Dependency injection for authentication
async def get_current_user_token(
    token: str = Depends(oauth2_scheme)
) -> TokenData:
    """
    Extract and validate the current user from JWT token.

    FastAPI dependency for protected routes.

    Usage:
        @router.get("/protected")
        async def protected_route(token: TokenData = Depends(get_current_user_token)):
            return {"user_id": token.user_id}
    """
    token_data = decode_token(token)

    # Verify it's an access token
    if token_data.token_type != TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Access token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def get_current_user_from_bearer(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(http_bearer)
) -> Optional[TokenData]:
    """
    Extract user from Bearer token (alternative to OAuth2).

    Returns None if no credentials provided (for optional auth).
    """
    if credentials is None:
        return None

    return decode_token(credentials.credentials)


# Role-based access control
class RoleChecker:
    """
    Dependency class for role-based access control.

    Usage:
        @router.post("/admin-only")
        async def admin_endpoint(user: TokenData = Depends(RoleChecker([UserRole.ADMIN]))):
            return {"message": "Admin access granted"}
    """

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, token: TokenData = Depends(get_current_user_token)) -> TokenData:
        """Check if user has required role."""
        if token.role not in self.allowed_roles:
            logger.warning(
                f"Access denied: User {token.user_id} with role {token.role} "
                f"attempted to access endpoint requiring {self.allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in self.allowed_roles]}",
            )
        return token


# Specific role dependencies for convenience
require_admin = RoleChecker([UserRole.ADMIN])
require_editor = RoleChecker([UserRole.ADMIN, UserRole.EDITOR])
require_researcher = RoleChecker([UserRole.ADMIN, UserRole.RESEARCHER])
require_reviewer = RoleChecker([UserRole.ADMIN, UserRole.RESEARCHER, UserRole.REVIEWER])
require_any_role = RoleChecker([UserRole.ADMIN, UserRole.RESEARCHER, UserRole.REVIEWER, UserRole.VIEWER])


# API key authentication
async def verify_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> Optional[str]:
    """
    Verify API key from header.

    Returns user_id if valid, None if no key provided, raises exception if invalid.

    Usage:
        @router.get("/api-endpoint")
        async def api_endpoint(user_id: str = Depends(verify_api_key)):
            if user_id is None:
                raise HTTPException(401, "API key required")
            return {"user_id": user_id}
    """
    if api_key is None:
        return None

    # TODO: Implement API key lookup in database
    # For now, this is a placeholder
    # In production, query database for API key and return associated user_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )


# Utility functions for password reset
def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token.

    Args:
        email: User's email address

    Returns:
        JWT token for password reset
    """
    expire = datetime.utcnow() + timedelta(hours=1)  # Reset tokens expire in 1 hour

    to_encode = {
        "sub": email,
        "type": "password_reset",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and extract email.

    Args:
        token: Password reset JWT token

    Returns:
        Email address if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if token_type != "password_reset":
            return None

        return email

    except JWTError:
        return None


# Security utilities for production
def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        Random API key string
    """
    import secrets

    return f"sk_{''.join(secrets.token_urlsafe(32))}"


def mask_email(email: str) -> str:
    """
    Mask email for privacy (e.g., for logging).

    Args:
        email: Email to mask

    Returns:
        Masked email (e.g., "j***@example.com")
    """
    if "@" not in email:
        return "***"

    local, domain = email.split("@")
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 1)

    return f"{masked_local}@{domain}"


def mask_token(token: str, visible_chars: int = 8) -> str:
    """
    Mask token for secure logging.

    Args:
        token: Token to mask
        visible_chars: Number of characters to show at start/end

    Returns:
        Masked token (e.g., "eyJhbGc...***...xyz123")
    """
    if len(token) <= visible_chars * 2:
        return "***"

    return f"{token[:visible_chars]}...***...{token[-visible_chars:]}"
