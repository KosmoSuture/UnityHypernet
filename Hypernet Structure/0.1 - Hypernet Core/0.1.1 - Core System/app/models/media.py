"""
Media Model

SQLAlchemy model for the media table (photos, videos, documents).
"""

from sqlalchemy import Column, String, BigInteger, Integer, Float, Boolean, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Media(Base):
    """Photos, videos, and other media files"""

    __tablename__ = "media"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Basic Info
    filename = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False)  # 'photo', 'video', 'document', 'other'
    mime_type = Column(String(100), nullable=False)

    # File Information
    size = Column(BigInteger, nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    duration = Column(Float)  # seconds (for videos)

    # Storage
    file_path = Column(String(1024), nullable=False)
    thumbnail_path = Column(String(1024))
    hash = Column(String(64), nullable=False, index=True)  # SHA-256

    # Dates and Location
    taken_at = Column(DateTime(timezone=True), index=True)
    latitude = Column(Float)
    longitude = Column(Float)

    # Source Tracking
    source_type = Column(String(50))  # 'upload', 'integration', 'import'
    source_id = Column(String(255))

    # Processing Status
    processing_status = Column(String(50), nullable=False, default='pending')
    thumbnail_generated = Column(Boolean, nullable=False, default=False)
    metadata_extracted = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Extensibility
    metadata = Column(JSONB, nullable=False, default={})

    # Relationships
    user = relationship("User", back_populates="media")
    # Links will be via Link model (many-to-many through links)

    # Constraints
    __table_args__ = (
        CheckConstraint("media_type IN ('photo', 'video', 'document', 'other')", name='chk_media_type'),
        CheckConstraint("processing_status IN ('pending', 'processing', 'complete', 'failed')", name='chk_processing_status'),
        CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name='chk_latitude'),
        CheckConstraint("longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name='chk_longitude'),
        CheckConstraint("size > 0", name='chk_size'),
    )

    def __repr__(self):
        return f"<Media(id={self.id}, filename={self.filename}, type={self.media_type})>"
