"""
API Key Management Service

Handles encryption, storage, and retrieval of user API keys.
"""
import os
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from cryptography.fernet import Fernet
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.api_keys import (
    APIKeyVerificationResult,
    DatabaseProvider,
    DatabaseUsageStats,
    UserAPIKey,
)

settings = get_settings()


class APIKeyService:
    """Service for managing user API keys."""

    def __init__(self):
        """Initialize with encryption key."""
        # Get encryption key from environment or generate one
        encryption_key = settings.api_key_encryption_key

        if not encryption_key:
            # Generate a key if not provided (for development)
            encryption_key = Fernet.generate_key().decode()
            logger.warning(
                "No API_KEY_ENCRYPTION_KEY found, generated temporary key. "
                "Set API_KEY_ENCRYPTION_KEY in production!"
            )

        self.cipher = Fernet(encryption_key.encode())

    def encrypt_key(self, api_key: str) -> str:
        """Encrypt an API key for storage.

        Args:
            api_key: Plain text API key

        Returns:
            Encrypted API key as string
        """
        return self.cipher.encrypt(api_key.encode()).decode()

    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key for use.

        Args:
            encrypted_key: Encrypted API key

        Returns:
            Plain text API key
        """
        return self.cipher.decrypt(encrypted_key.encode()).decode()

    async def add_api_key(
        self,
        db: AsyncSession,
        user_id: UUID,
        provider: DatabaseProvider,
        api_key: str,
        key_name: Optional[str] = None,
        verify: bool = True,
    ) -> UserAPIKey:
        """Add a new API key for a user.

        Args:
            db: Database session
            user_id: User ID
            provider: Database provider
            api_key: Plain text API key
            key_name: Optional name/label for the key
            verify: Whether to verify the key immediately

        Returns:
            UserAPIKey object
        """
        # Encrypt the key
        encrypted = self.encrypt_key(api_key)

        # Create database record
        key_record = UserAPIKey(
            user_id=user_id,
            provider=provider,
            encrypted_key=encrypted,
            key_name=key_name or f"{provider.value} API Key",
            enabled=True,
            verified=False,
        )

        db.add(key_record)
        await db.commit()
        await db.refresh(key_record)

        # Verify the key if requested
        if verify:
            await self.verify_api_key(db, key_record.id, api_key)

        logger.info(f"Added API key for user {user_id}, provider {provider.value}")
        return key_record

    async def get_api_key(
        self,
        db: AsyncSession,
        user_id: UUID,
        provider: DatabaseProvider,
    ) -> Optional[str]:
        """Get a decrypted API key for use.

        Args:
            db: Database session
            user_id: User ID
            provider: Database provider

        Returns:
            Decrypted API key or None if not found
        """
        # Find the key
        result = await db.execute(
            select(UserAPIKey)
            .where(UserAPIKey.user_id == user_id)
            .where(UserAPIKey.provider == provider)
            .where(UserAPIKey.enabled == True)
        )
        key_record = result.scalar_one_or_none()

        if not key_record:
            return None

        # Update last used timestamp
        key_record.last_used_at = datetime.utcnow()
        key_record.total_requests = str(int(key_record.total_requests) + 1)
        await db.commit()

        # Decrypt and return
        return self.decrypt_key(key_record.encrypted_key)

    async def list_user_keys(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> List[Dict]:
        """List all API keys for a user (without showing actual keys).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of API key metadata
        """
        result = await db.execute(
            select(UserAPIKey)
            .where(UserAPIKey.user_id == user_id)
            .order_by(UserAPIKey.created_at.desc())
        )
        keys = result.scalars().all()

        return [
            {
                "id": str(key.id),
                "provider": key.provider.value,
                "key_name": key.key_name,
                "enabled": key.enabled,
                "verified": key.verified,
                "last_verified_at": key.last_verified_at.isoformat() if key.last_verified_at else None,
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                "created_at": key.created_at.isoformat(),
                "total_requests": key.total_requests,
                "failed_requests": key.failed_requests,
            }
            for key in keys
        ]

    async def delete_api_key(
        self,
        db: AsyncSession,
        user_id: UUID,
        key_id: UUID,
    ) -> bool:
        """Delete an API key.

        Args:
            db: Database session
            user_id: User ID (for security check)
            key_id: Key ID to delete

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            select(UserAPIKey)
            .where(UserAPIKey.id == key_id)
            .where(UserAPIKey.user_id == user_id)
        )
        key_record = result.scalar_one_or_none()

        if not key_record:
            return False

        await db.delete(key_record)
        await db.commit()

        logger.info(f"Deleted API key {key_id} for user {user_id}")
        return True

    async def verify_api_key(
        self,
        db: AsyncSession,
        key_id: UUID,
        api_key: Optional[str] = None,
    ) -> bool:
        """Verify that an API key works.

        Args:
            db: Database session
            key_id: Key ID to verify
            api_key: Optional plain text key (if not provided, will decrypt from DB)

        Returns:
            True if key works, False otherwise
        """
        # Get key record
        result = await db.execute(
            select(UserAPIKey).where(UserAPIKey.id == key_id)
        )
        key_record = result.scalar_one_or_none()

        if not key_record:
            return False

        # Decrypt if not provided
        if api_key is None:
            api_key = self.decrypt_key(key_record.encrypted_key)

        # Test the key based on provider
        success = False
        error_message = None
        test_query = "test query"
        response_time_ms = None

        try:
            import time
            start_time = time.time()

            if key_record.provider == DatabaseProvider.SCOPUS:
                success = await self._verify_scopus_key(api_key)
            elif key_record.provider == DatabaseProvider.WEB_OF_SCIENCE:
                success = await self._verify_wos_key(api_key)
            elif key_record.provider == DatabaseProvider.GOOGLE_SCHOLAR:
                success = await self._verify_serpapi_key(api_key)
            elif key_record.provider == DatabaseProvider.IEEE_XPLORE:
                success = await self._verify_ieee_key(api_key)
            else:
                # For now, assume key is valid if it exists
                success = True

            response_time_ms = int((time.time() - start_time) * 1000)

        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Error verifying API key: {e}")

        # Update key record
        if success:
            key_record.verified = True
            key_record.last_verified_at = datetime.utcnow()
        else:
            key_record.failed_requests = str(int(key_record.failed_requests) + 1)

        # Save verification result
        verification = APIKeyVerificationResult(
            api_key_id=key_id,
            success=success,
            error_message=error_message,
            test_query=test_query,
            response_time_ms=str(response_time_ms) if response_time_ms else None,
        )
        db.add(verification)
        await db.commit()

        return success

    async def _verify_scopus_key(self, api_key: str) -> bool:
        """Verify Scopus API key."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.elsevier.com/content/search/scopus",
                    params={"query": "test", "count": 1},
                    headers={"X-ELS-APIKey": api_key},
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    async def _verify_wos_key(self, api_key: str) -> bool:
        """Verify Web of Science API key."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.clarivate.com/api/wos",
                    headers={"X-ApiKey": api_key},
                    timeout=10.0,
                )
                return response.status_code in [200, 401]  # 401 means key format is valid
        except Exception:
            return False

    async def _verify_serpapi_key(self, api_key: str) -> bool:
        """Verify SerpApi key (for Google Scholar)."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://serpapi.com/account.json",
                    params={"api_key": api_key},
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    async def _verify_ieee_key(self, api_key: str) -> bool:
        """Verify IEEE Xplore API key."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://ieeexploreapi.ieee.org/api/v1/search/articles",
                    params={"apikey": api_key, "querytext": "test", "max_records": 1},
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False

    async def track_database_usage(
        self,
        db: AsyncSession,
        user_id: UUID,
        provider: DatabaseProvider,
        meta_analysis_id: Optional[UUID],
        queries_made: int,
        results_found: int,
        execution_time_ms: Optional[int],
        success: bool,
        error_message: Optional[str] = None,
    ):
        """Track database usage for analytics.

        Args:
            db: Database session
            user_id: User ID
            provider: Database provider
            meta_analysis_id: Optional meta-analysis ID
            queries_made: Number of queries made
            results_found: Number of results found
            execution_time_ms: Execution time in milliseconds
            success: Whether the query succeeded
            error_message: Optional error message
        """
        usage = DatabaseUsageStats(
            provider=provider,
            meta_analysis_id=meta_analysis_id,
            user_id=user_id,
            queries_made=str(queries_made),
            results_found=str(results_found),
            execution_time_ms=str(execution_time_ms) if execution_time_ms else None,
            success=success,
            error_message=error_message,
        )
        db.add(usage)
        await db.commit()


# Singleton instance
api_key_service = APIKeyService()
