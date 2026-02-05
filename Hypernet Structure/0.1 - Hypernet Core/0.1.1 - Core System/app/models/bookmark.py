"""
Bookmark Model

SQLAlchemy model for web bookmarks.

Implements: 0.0.7 - Web Types / Bookmark.md
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class Bookmark(OwnedObject):
    """
    Browser bookmarks - saved links without full page content.
    """

    __tablename__ = "bookmarks"

    # Required
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    bookmarked_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Optional
    description = Column(Text, nullable=True)
    favicon_url = Column(String(500), nullable=True)

    folder = Column(String(255), nullable=True, index=True)
    tags = Column(ARRAY(Text), nullable=True)

    is_favorite = Column(Boolean, nullable=False, default=False)
    visit_count = Column(Integer, nullable=False, default=0)
    last_visited_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[OwnedObject.user_id])

    # Constraints
    __table_args__ = (
        Index('idx_bookmarks_favorites', 'is_favorite', postgresql_where=Column('is_favorite') == True),
        Index('idx_bookmarks_folder', 'folder', postgresql_where=Column('folder').isnot(None)),
    )

    def __repr__(self):
        return f"<Bookmark(id={self.id}, title={self.title[:50]})>"
