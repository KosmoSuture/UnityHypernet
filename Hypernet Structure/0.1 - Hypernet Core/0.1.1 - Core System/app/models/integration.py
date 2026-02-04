"""
Integration Models

SQLAlchemy models for integrations and integration_secrets tables.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Integration(Base):
    """Connected external services (Instagram, Google Photos, etc.)"""

    __tablename__ = "integrations"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Integration Details
    integration_type = Column(String(50), nullable=False, index=True)  # 'instagram', 'google_photos', etc.
    integration_name = Column(String(200), nullable=False)

    # Status
    status = Column(String(50), nullable=False, default='pending', index=True)
    is_enabled = Column(Boolean, nullable=False, default=True)

    # OAuth2
    token_expires_at = Column(DateTime(timezone=True))

    # Sync State
    last_sync_at = Column(DateTime(timezone=True))
    last_sync_status = Column(String(50))
    sync_cursor = Column(Text)  # Pagination cursor for incremental sync

    # Statistics
    items_synced = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Source Tracking
    source_type = Column(String(50))
    source_id = Column(String(255))

    # Extensibility
    metadata = Column(JSONB, nullable=False, default={})

    # Relationships
    user = relationship("User", back_populates="integrations")
    secrets = relationship("IntegrationSecret", back_populates="integration", uselist=False, cascade="all, delete-orphan")
    # Media sourced from this integration will be via Link model

    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('connected', 'disconnected', 'error', 'pending')", name='chk_integration_status'),
        CheckConstraint("last_sync_status IS NULL OR last_sync_status IN ('success', 'partial', 'failed')", name='chk_sync_status'),
        CheckConstraint("items_synced >= 0", name='chk_items_synced'),
    )

    def __repr__(self):
        return f"<Integration(id={self.id}, type={self.integration_type}, name={self.integration_name})>"


class IntegrationSecret(Base):
    """OAuth tokens and secrets for integrations (encrypted at rest)"""

    __tablename__ = "integration_secrets"

    # Identity (one-to-one with Integration)
    integration_id = Column(
        UUID(as_uuid=True),
        ForeignKey("integrations.id", ondelete="CASCADE"),
        primary_key=True
    )

    # OAuth2 Tokens (should be encrypted at application level or database level)
    access_token = Column(Text)
    refresh_token = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    integration = relationship("Integration", back_populates="secrets")

    def __repr__(self):
        return f"<IntegrationSecret(integration_id={self.integration_id})>"
