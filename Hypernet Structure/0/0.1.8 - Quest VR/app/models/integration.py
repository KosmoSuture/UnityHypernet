"""
Integration Models

SQLAlchemy models for integrations and integration_secrets tables.

Implements: 0.0.1 - Core Types / Integration.md
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject, BaseObject


class Integration(OwnedObject):
    """
    Connected external services (Instagram, Google Photos, Gmail, etc.).

    Manages OAuth2 connections and sync state for external integrations.
    """

    __tablename__ = "integrations"

    # Integration Details (Required)
    integration_type = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Integration type: instagram, google_photos, gmail, dropbox, etc."
    )

    integration_name = Column(
        String(200),
        nullable=False,
        doc="User-friendly name (e.g., 'My Instagram', 'Work Gmail')"
    )

    status = Column(
        String(50),
        nullable=False,
        default='pending',
        index=True,
        doc="Status: pending, connected, disconnected, error"
    )

    # OAuth2 (Optional)
    token_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When access token expires (NULL if doesn't expire)"
    )

    # Sync State (Optional)
    last_sync_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last successful sync timestamp"
    )

    last_sync_status = Column(
        String(50),
        nullable=True,
        doc="Last sync status: success, partial, failed"
    )

    sync_cursor = Column(
        Text,
        nullable=True,
        doc="Pagination cursor for incremental sync (platform-specific)"
    )

    items_synced = Column(
        Integer,
        nullable=False,
        default=0,
        doc="Total items imported from this integration"
    )

    # Status (Optional)
    is_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        doc="User can disable without deleting"
    )

    # Relationships
    user = relationship("User", back_populates="integrations", foreign_keys=[OwnedObject.user_id])
    secrets = relationship("IntegrationSecret", back_populates="integration", uselist=False, cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'connected', 'disconnected', 'error')",
            name='chk_integration_status'
        ),
        CheckConstraint(
            "last_sync_status IS NULL OR last_sync_status IN ('success', 'partial', 'failed')",
            name='chk_sync_status'
        ),
        CheckConstraint(
            "items_synced >= 0",
            name='chk_items_synced'
        ),
    )

    def __repr__(self):
        return f"<Integration(id={self.id}, type={self.integration_type}, name={self.integration_name})>"


class IntegrationSecret(BaseObject):
    """
    OAuth tokens and secrets for integrations.

    Stored separately for security. Should be encrypted at rest.
    One-to-one relationship with Integration.
    """

    __tablename__ = "integration_secrets"

    # Foreign key to integration (one-to-one)
    integration_id = Column(
        UUID(as_uuid=True),
        ForeignKey("integrations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        doc="Integration this secret belongs to"
    )

    # OAuth2 Tokens (should be encrypted at rest)
    access_token = Column(
        Text,
        nullable=True,
        doc="OAuth2 access token (encrypted)"
    )

    refresh_token = Column(
        Text,
        nullable=True,
        doc="OAuth2 refresh token (encrypted)"
    )

    # Relationships
    integration = relationship("Integration", back_populates="secrets")

    def __repr__(self):
        return f"<IntegrationSecret(integration_id={self.integration_id})>"
