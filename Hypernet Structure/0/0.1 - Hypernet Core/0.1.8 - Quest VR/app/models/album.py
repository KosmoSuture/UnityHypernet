"""
Album Model

SQLAlchemy model for the albums table (collections of media).

Implements: 0.0 - Object Type Registry / [Future: Album type definition]
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class Album(OwnedObject):
    """Collections of media objects"""

    __tablename__ = "albums"

    # Basic Info (Identity and Ownership inherited from OwnedObject)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)

    # Display
    cover_media_id = Column(UUID(as_uuid=True), ForeignKey("media.id", ondelete="SET NULL"))
    sort_order = Column(String(50), nullable=False, default='date_desc')

    # Counts (denormalized for performance)
    media_count = Column(Integer, nullable=False, default=0)

    # Privacy (future use)
    visibility = Column(String(50), nullable=False, default='private')

    # Timestamps, Source Tracking, and Metadata inherited from OwnedObject

    # Relationships
    user = relationship("User", back_populates="albums", foreign_keys=[OwnedObject.user_id])
    cover_media = relationship("Media", foreign_keys=[cover_media_id], post_update=True)
    # Media in album will be via Link model (many-to-many through links)

    # Constraints
    __table_args__ = (
        CheckConstraint("sort_order IN ('date_asc', 'date_desc', 'manual')", name='chk_sort_order'),
        CheckConstraint("visibility IN ('private', 'unlisted', 'public')", name='chk_visibility'),
        CheckConstraint("media_count >= 0", name='chk_media_count'),
    )

    def __repr__(self):
        return f"<Album(id={self.id}, name={self.name}, media_count={self.media_count})>"
