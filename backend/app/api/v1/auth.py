"""Authentication endpoints for user registration, login, and token management."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.db.session import get_async_db
from app.models.user import User, UserCreate, UserResponse, APIKey, APIKeyCreate, APIKeyResponse, APIKeyWithSecret
from app.core.security import (
    hash_password,
    verify_password,
    create_token_pair,
    get_current_user_token,
    decode_token,
    TokenData,
    Token,
    UserRole,
    generate_api_key,
    TokenType,
)

router = APIRouter()


@router.get("/test-pydantic")
async def test_pydantic():
    """Test Pydantic UserCreate model validation."""
    try:
        from app.models.user import UserCreate
        user_data = UserCreate(
            email="test@example.com",
            password="TestPass123",
            full_name="Test",
            institution="Test U"
        )
        return {"status": "success", "message": "Pydantic validation works", "email": user_data.email}
    except Exception as e:
        logger.exception("Pydantic test failed")
        return {"status": "error", "error": str(e), "type": type(e).__name__}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Register a new user.

    - **email**: Valid email address
    - **password**: Strong password (8+ chars, uppercase, lowercase, digit)
    - **full_name**: Optional user's full name
    - **institution**: Optional user's institution

    Returns the created user (without password).
    """
    try:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = hash_password(user_data.password)

        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            institution=user_data.institution,
            role=UserRole.RESEARCHER,  # Default role
            is_active=True,
            is_verified=False,  # Will be verified via email
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"New user registered: {user_data.email}")

        return UserResponse(
            id=str(new_user.id),
            email=new_user.email,
            full_name=new_user.full_name,
            institution=new_user.institution,
            role=new_user.role,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            created_at=new_user.created_at,
            last_login=new_user.last_login,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error for {user_data.email}: {type(e).__name__}: {e}")
        logger.exception("Full traceback:")
        raise


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    """
    OAuth2 password flow login.

    - **username**: User's email address
    - **password**: User's password

    Returns access and refresh tokens.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )

    # Update last login time
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create token pair
    tokens = create_token_pair(
        user_id=str(user.id),
        email=user.email,
        role=user.role
    )

    logger.info(f"User logged in: {user.email}")

    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Refresh access token using refresh token.

    - **refresh_token**: Valid refresh token

    Returns new access and refresh tokens.
    """
    try:
        token_data = decode_token(refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify it's a refresh token
    if token_data.token_type != TokenType.REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Refresh token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new token pair
    tokens = create_token_pair(
        user_id=str(user.id),
        email=user.email,
        role=user.role
    )

    logger.info(f"Token refreshed for user: {user.email}")

    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current authenticated user's information.

    Requires valid access token in Authorization header.
    """
    result = await db.execute(select(User).where(User.id == token.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        institution=user.institution,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.post("/api-keys", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new API key for programmatic access.

    - **name**: Human-readable name for the API key
    - **description**: Optional description
    - **expires_in_days**: Number of days until expiration (default 365)

    Returns the API key (only shown once - store it securely!).
    """
    # Generate API key
    api_key = generate_api_key()
    key_prefix = api_key[:8]
    key_hash = hash_password(api_key)

    # Calculate expiration
    expires_at = None
    if api_key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=api_key_data.expires_in_days)

    # Create API key record
    new_api_key = APIKey(
        user_id=token.user_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=api_key_data.name,
        description=api_key_data.description,
        is_active=True,
        expires_at=expires_at,
    )

    db.add(new_api_key)
    await db.commit()
    await db.refresh(new_api_key)

    logger.info(f"API key created for user {token.user_id}: {api_key_data.name}")

    return APIKeyWithSecret(
        id=str(new_api_key.id),
        name=new_api_key.name,
        description=new_api_key.description,
        key_prefix=new_api_key.key_prefix,
        is_active=new_api_key.is_active,
        created_at=new_api_key.created_at,
        expires_at=new_api_key.expires_at,
        last_used_at=new_api_key.last_used_at,
        key=api_key,  # Only returned on creation
    )


@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db)
):
    """
    List all API keys for the current user.

    Returns list of API keys (without the actual key values).
    """
    result = await db.execute(
        select(APIKey).where(APIKey.user_id == token.user_id).order_by(APIKey.created_at.desc())
    )
    api_keys = result.scalars().all()

    return [
        APIKeyResponse(
            id=str(key.id),
            name=key.name,
            description=key.description,
            key_prefix=key.key_prefix,
            is_active=key.is_active,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used_at=key.last_used_at,
        )
        for key in api_keys
    ]


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Delete an API key.

    Only the owner of the API key can delete it.
    """
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == token.user_id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    await db.delete(api_key)
    await db.commit()

    logger.info(f"API key deleted: {api_key.name} (user {token.user_id})")

    return None


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token: TokenData = Depends(get_current_user_token)
):
    """
    Logout endpoint.

    Note: Since we use stateless JWT tokens, this is mainly for client-side cleanup.
    Clients should delete their stored tokens.

    In a production system, you might:
    - Add token to blacklist (requires Redis)
    - Track active sessions in database
    - Implement token revocation
    """
    logger.info(f"User logged out: {token.user_id}")
    return None
