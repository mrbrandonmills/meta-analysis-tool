"""
User API Key Management Models

Allows users to bring their own API keys for subscription databases.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class DatabaseProvider(str, Enum):
    """Supported database providers for BYOK."""

    # Free databases (no key needed)
    PUBMED = "pubmed"
    ARXIV = "arxiv"
    EUROPEPMC = "europepmc"
    CORE = "core"
    DOAJ = "doaj"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    CROSSREF = "crossref"
    BASE = "base"

    # Paid databases (BYOK)
    GOOGLE_SCHOLAR = "google_scholar"  # SerpApi key
    SCOPUS = "scopus"  # Elsevier API key
    WEB_OF_SCIENCE = "web_of_science"  # Clarivate API key
    IEEE_XPLORE = "ieee_xplore"  # IEEE API key
    JSTOR = "jstor"  # JSTOR API key
    SCIENCEDIRECT = "sciencedirect"  # Elsevier API key (can share with Scopus)
    PSYCINFO = "psycinfo"  # APA PsycNET key
    ERIC = "eric"  # Free but separate
    COCHRANE = "cochrane"  # Cochrane Library key


class UserAPIKey(Base):
    """User-provided API keys for subscription databases.

    This allows users with institutional access to use their own API keys
    for premium databases like Scopus, Web of Science, etc.

    Security:
    - Keys are encrypted at rest using Fernet encryption
    - Keys are never logged or exposed in API responses
    - Users can only access their own keys
    - Keys can be rotated/deleted at any time
    """

    __tablename__ = "user_api_keys"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Database provider
    provider = Column(SQLEnum(DatabaseProvider), nullable=False)

    # Encrypted API key (using Fernet symmetric encryption)
    encrypted_key = Column(String, nullable=False)

    # Optional: Key name/label for user reference
    key_name = Column(String, nullable=True)

    # Status
    enabled = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)  # Has the key been tested?
    last_verified_at = Column(DateTime, nullable=True)

    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    total_requests = Column(String, default="0")  # BigInt as string
    failed_requests = Column(String, default="0")  # BigInt as string

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration

    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<UserAPIKey {self.provider.value} for user {self.user_id}>"


class APIKeyVerificationResult(Base):
    """Track API key verification attempts.

    When a user adds an API key, we test it to make sure it works.
    This table tracks those verification attempts.
    """

    __tablename__ = "api_key_verifications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    api_key_id = Column(PGUUID(as_uuid=True), ForeignKey("user_api_keys.id"), nullable=False)

    # Verification result
    success = Column(Boolean, nullable=False)
    error_message = Column(String, nullable=True)

    # Test details
    test_query = Column(String, nullable=True)  # What query was used to test
    response_time_ms = Column(String, nullable=True)  # How fast did it respond

    # Metadata
    verified_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<APIKeyVerification {'SUCCESS' if self.success else 'FAILED'} at {self.verified_at}>"


class DatabaseUsageStats(Base):
    """Track which databases are being used and how often.

    This helps understand:
    - Which databases are most valuable
    - Whether paid API keys are worth the cost
    - Usage patterns for optimization
    """

    __tablename__ = "database_usage_stats"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Which database
    provider = Column(SQLEnum(DatabaseProvider), nullable=False)

    # Which meta-analysis
    meta_analysis_id = Column(PGUUID(as_uuid=True), ForeignKey("meta_analyses.id"), nullable=True)

    # Which user
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Usage data
    queries_made = Column(String, default="1")
    results_found = Column(String, default="0")
    execution_time_ms = Column(String, nullable=True)

    # Success/failure
    success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DatabaseUsage {self.provider.value} by user {self.user_id}>"
