"""
Album Model

SQLAlchemy model for the albums table (collections of media).
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Album(Base):
    """Collections of media objects"""

    __tablename__ = "albums"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic Info
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)

    # Display
    cover_media_id = Column(UUID(as_uuid=True), ForeignKey("media.id", ondelete="SET NULL"))
    sort_order = Column(String(50), nullable=False, default='date_desc')

    # Counts (denormalized for performance)
    media_count = Column(Integer, nullable=False, default=0)

    # Privacy (future use)
    visibility = Column(String(50), nullable=False, default='private')

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
    user = relationship("User", back_populates="albums")
    cover_media = relationship("Media", foreign_keys=[cover_media_id])
    # Media in album will be via Link model (many-to-many through links)

    # Constraints
    __table_args__ = (
        CheckConstraint("sort_order IN ('date_asc', 'date_desc', 'manual')", name='chk_sort_order'),
        CheckConstraint("visibility IN ('private', 'unlisted', 'public')", name='chk_visibility'),
        CheckConstraint("media_count >= 0", name='chk_media_count'),
    )

    def __repr__(self):
        return f"<Album(id={self.id}, name={self.name}, media_count={self.media_count})>"
