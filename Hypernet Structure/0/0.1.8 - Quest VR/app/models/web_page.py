"""
WebPage Model

SQLAlchemy model for saved web pages.

Implements: 0.0.7 - Web Types / WebPage.md
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class WebPage(OwnedObject):
    """
    Saved web pages - full page archives, article content, research.
    """

    __tablename__ = "web_pages"

    # Required
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    saved_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Optional
    html_content = Column(Text, nullable=True)
    text_content = Column(Text, nullable=True)
    screenshot_id = Column(UUID(as_uuid=True), ForeignKey("media.id", ondelete="SET NULL"), nullable=True)

    # Metadata extracted from page
    author = Column(String(200), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    site_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)

    # Archive
    archive_path = Column(String(512), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[OwnedObject.user_id])
    screenshot = relationship("Media", foreign_keys=[screenshot_id], post_update=True)

    def __repr__(self):
        return f"<WebPage(id={self.id}, title={self.title[:50]})>"
