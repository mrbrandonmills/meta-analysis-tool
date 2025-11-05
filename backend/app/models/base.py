"""Base model mixins."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """Mixin for timestamp fields."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""

    deleted_at = Column(DateTime, nullable=True, index=True)

    @property
    def is_deleted(self) -> bool:
        """Check if record is deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Soft delete the record."""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore soft deleted record."""
        self.deleted_at = None


class AuditMixin:
    """Mixin for audit trail fields."""

    @declared_attr
    def created_by(cls):
        """User who created the record."""
        return Column(UUID(as_uuid=True), nullable=True, index=True)

    @declared_attr
    def updated_by(cls):
        """User who last updated the record."""
        return Column(UUID(as_uuid=True), nullable=True)


class UUIDMixin:
    """Mixin for UUID primary key."""

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )


class BaseModel(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Base model with all common fields."""

    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
