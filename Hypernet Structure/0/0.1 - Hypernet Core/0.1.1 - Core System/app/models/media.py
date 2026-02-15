"""
Media Model

SQLAlchemy model for media table (photos, videos, audio, documents).

Polymorphic base for different media types.
Implements specifications from: 0.0.2 - Media Types
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, CheckConstraint, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class Media(OwnedObject):
    """
    Media files - photos, videos, audio, documents.

    This is a polymorphic base class. Specific media types (Photo, Video, etc.)
    can be implemented as subclasses or distinguished by media_type field.
    """

    __tablename__ = "media"

    # ============================================================================
    # FILE IDENTITY (Required)
    # ============================================================================

    filename = Column(
        String(255),
        nullable=False,
        doc="Original filename"
    )

    media_type = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Media type: photo, video, audio, document, screenshot"
    )

    mime_type = Column(
        String(100),
        nullable=False,
        index=True,
        doc="MIME type (image/jpeg, video/mp4, etc.)"
    )

    # ============================================================================
    # FILE STORAGE (Required)
    # ============================================================================

    file_size = Column(
        Integer,
        nullable=False,
        doc="File size in bytes"
    )

    file_path = Column(
        String(512),
        nullable=False,
        unique=True,
        doc="Relative path to file on storage (/media/{user_id}/{year}/{month}/{filename})"
    )

    hash = Column(
        String(64),
        nullable=False,
        index=True,
        doc="SHA-256 hash for deduplication"
    )

    # ============================================================================
    # DIMENSIONS (Optional - primarily for photo/video)
    # ============================================================================

    width = Column(
        Integer,
        nullable=True,
        doc="Width in pixels (for images/videos)"
    )

    height = Column(
        Integer,
        nullable=True,
        doc="Height in pixels (for images/videos)"
    )

    duration = Column(
        Float,
        nullable=True,
        doc="Duration in seconds (for video/audio)"
    )

    # ============================================================================
    # TEMPORAL DATA (Optional)
    # ============================================================================

    taken_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="When photo was taken/video recorded (from EXIF or user-provided)"
    )

    # ============================================================================
    # GEOLOCATION (Optional)
    # ============================================================================

    gps_latitude = Column(
        Float,
        nullable=True,
        doc="GPS latitude (-90 to 90)"
    )

    gps_longitude = Column(
        Float,
        nullable=True,
        doc="GPS longitude (-180 to 180)"
    )

    # ============================================================================
    # PROCESSING (Optional)
    # ============================================================================

    processing_status = Column(
        String(50),
        nullable=True,
        default='pending',
        index=True,
        doc="Processing status: pending, processing, ready, error"
    )

    thumbnail_path = Column(
        String(512),
        nullable=True,
        doc="Path to generated thumbnail"
    )

    # ============================================================================
    # AUDIO/VIDEO SPECIFIC (Optional)
    # ============================================================================

    codec = Column(
        String(50),
        nullable=True,
        doc="Codec: h264, aac, mp3, etc."
    )

    bitrate = Column(
        Integer,
        nullable=True,
        doc="Bitrate in bits per second"
    )

    # ============================================================================
    # RELATIONSHIPS
    # ============================================================================

    user = relationship(
        "User",
        back_populates="media",
        foreign_keys=[OwnedObject.user_id]
    )

    # Links to albums, integrations via Link model

    # ============================================================================
    # CONSTRAINTS
    # ============================================================================

    __table_args__ = (
        # Media type validation
        CheckConstraint(
            "media_type IN ('photo', 'video', 'audio', 'document', 'screenshot')",
            name='chk_media_type'
        ),
        # File size validation
        CheckConstraint(
            "file_size > 0",
            name='chk_file_size'
        ),
        # Dimensions validation
        CheckConstraint(
            "width IS NULL OR (width > 0 AND width <= 50000)",
            name='chk_width'
        ),
        CheckConstraint(
            "height IS NULL OR (height > 0 AND height <= 50000)",
            name='chk_height'
        ),
        # GPS validation
        CheckConstraint(
            "gps_latitude IS NULL OR (gps_latitude >= -90 AND gps_latitude <= 90)",
            name='chk_gps_latitude'
        ),
        CheckConstraint(
            "gps_longitude IS NULL OR (gps_longitude >= -180 AND gps_longitude <= 180)",
            name='chk_gps_longitude'
        ),
        # Duration validation
        CheckConstraint(
            "duration IS NULL OR duration > 0",
            name='chk_duration'
        ),
        # Processing status validation
        CheckConstraint(
            "processing_status IS NULL OR processing_status IN ('pending', 'processing', 'ready', 'error')",
            name='chk_processing_status'
        ),
        # Unique hash per user (prevent duplicate uploads)
        Index('idx_media_user_hash', 'user_id', 'hash', unique=True),
        # GPS index (partial - only where GPS exists)
        Index(
            'idx_media_gps',
            'gps_latitude', 'gps_longitude',
            postgresql_where=Column('gps_latitude').isnot(None)
        ),
        # Taken_at index (partial)
        Index(
            'idx_media_taken_at',
            'taken_at',
            postgresql_where=Column('taken_at').isnot(None)
        ),
        # Processing status index (partial - exclude ready)
        Index(
            'idx_media_processing',
            'processing_status',
            postgresql_where=Column('processing_status') != 'ready'
        ),
    )

    def __repr__(self):
        return f"<Media(id={self.id}, filename={self.filename}, type={self.media_type})>"

