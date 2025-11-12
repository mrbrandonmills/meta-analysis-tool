"""Admin action audit trail model."""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pydantic import BaseModel, Field

from app.db.base import Base
from app.models.base import BaseModel as BaseModelMixin
import enum


class AdminActionType(str, enum.Enum):
    """Types of admin actions."""

    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_SUSPENDED = "user_suspended"
    USER_ACTIVATED = "user_activated"
    USER_DELETED = "user_deleted"

    RESEARCHER_UPDATED = "researcher_updated"
    RESEARCHER_SUSPENDED = "researcher_suspended"
    RESEARCHER_ACTIVATED = "researcher_activated"

    PAYOUT_POOL_CREATED = "payout_pool_created"
    PAYOUT_DISTRIBUTED = "payout_distributed"
    PAYOUT_POOL_CLOSED = "payout_pool_closed"

    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    SUBSCRIPTION_REFUNDED = "subscription_refunded"

    CONTENT_MODERATED = "content_moderated"
    REVIEW_APPROVED = "review_approved"
    REVIEW_REJECTED = "review_rejected"

    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    PERMISSIONS_CHANGED = "permissions_changed"


class AdminAction(Base, BaseModelMixin):
    """Admin action audit trail model."""

    __tablename__ = "admin_actions"

    # Who performed the action
    admin_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    admin_email = Column(String(255), nullable=False)

    # What action was performed
    action_type = Column(
        SQLEnum(AdminActionType, name="admin_action_type", native_enum=False),
        nullable=False,
        index=True
    )

    # What entity was affected
    target_type = Column(String(50), nullable=True, index=True)  # user, researcher, payout_pool, etc.
    target_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    target_identifier = Column(String(255), nullable=True)  # email, name, etc. for easy reference

    # Action details
    description = Column(Text, nullable=False)

    # Previous and new values (for updates)
    previous_values = Column(JSONB, nullable=True, default=dict)
    new_values = Column(JSONB, nullable=True, default=dict)

    # Additional metadata
    action_metadata = Column(JSONB, nullable=True, default=dict)

    # Request context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)

    # Timestamp
    performed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<AdminAction({self.action_type.value} by {self.admin_email} at {self.performed_at})>"


# Pydantic schemas for API
class AdminActionCreate(BaseModel):
    """Schema for creating an admin action log."""

    admin_id: str
    admin_email: str
    action_type: AdminActionType
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    target_identifier: Optional[str] = None
    description: str
    previous_values: Optional[dict] = None
    new_values: Optional[dict] = None
    action_metadata: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AdminActionResponse(BaseModel):
    """Schema for admin action response."""

    id: str
    admin_id: str
    admin_email: str
    action_type: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    target_identifier: Optional[str] = None
    description: str
    previous_values: Optional[dict] = None
    new_values: Optional[dict] = None
    action_metadata: Optional[dict] = None
    performed_at: datetime

    class Config:
        from_attributes = True
