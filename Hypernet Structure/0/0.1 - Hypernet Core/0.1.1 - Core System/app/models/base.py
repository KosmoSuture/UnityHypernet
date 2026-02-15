"""
Base Object Model

Abstract base class that all Hypernet objects inherit from.
Implements the BaseObject specification from 0.0.1.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declared_attr
from app.core.database import Base
import uuid
from datetime import datetime


class BaseObject(Base):
    """
    Universal parent class for all Hypernet objects.

    Implements the canonical BaseObject specification from:
    0.0 - Object Type Registry / 0.0.1 - Core Types / BaseObject.md

    All objects in Hypernet inherit these fields and behaviors.
    """

    __abstract__ = True  # This class is not instantiated directly

    # ============================================================================
    # IDENTITY
    # ============================================================================

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Globally unique identifier (UUID v4)"
    )

    # ============================================================================
    # OWNERSHIP
    # ============================================================================

    # Note: user_id is NOT on BaseObject itself for User model
    # (users don't own themselves). Child classes add this as needed.

    # ============================================================================
    # TIMESTAMPS
    # ============================================================================

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="When this object was created (UTC)"
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="When this object was last modified (UTC)"
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="When this object was soft-deleted (NULL = not deleted)"
    )

    # ============================================================================
    # SOURCE TRACKING
    # ============================================================================

    source_type = Column(
        String(50),
        nullable=True,
        index=True,
        doc="Where this object came from (upload, integration, api, import, ai_generated)"
    )

    source_id = Column(
        String(255),
        nullable=True,
        index=True,
        doc="External identifier at the source (e.g., 'instagram:12345')"
    )

    # ============================================================================
    # EXTENSIBILITY
    # ============================================================================

    metadata = Column(
        JSONB,
        nullable=False,
        default={},
        server_default='{}',
        doc="Extensible JSON field for type-specific data"
    )

    # ============================================================================
    # BEHAVIORS
    # ============================================================================

    def soft_delete(self):
        """Soft delete this object (sets deleted_at to current time)"""
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore a soft-deleted object (sets deleted_at to NULL)"""
        self.deleted_at = None

    @property
    def is_deleted(self):
        """Check if object is soft-deleted"""
        return self.deleted_at is not None

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class OwnedObject(BaseObject):
    """
    Base class for objects that have an owner (user_id).

    Most objects inherit from this, except User itself.
    """

    __abstract__ = True

    @declared_attr
    def user_id(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
            doc="Owner of this object (human or AI account)"
        )
