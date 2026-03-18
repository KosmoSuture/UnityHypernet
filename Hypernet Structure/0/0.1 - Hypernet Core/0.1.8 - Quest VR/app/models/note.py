"""
Note Model

SQLAlchemy model for personal notes.

Implements: 0.0.8 - Life Types / Note.md
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class Note(OwnedObject):
    """
    Personal notes from note apps (Apple Notes, Notion, Evernote, Obsidian, etc.).
    """

    __tablename__ = "notes"

    # Required
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    note_format = Column(String(50), nullable=False, default='plain')

    # Optional
    folder = Column(String(255), nullable=True, index=True)
    tags = Column(ARRAY(Text), nullable=True)

    is_pinned = Column(Boolean, nullable=False, default=False)
    is_locked = Column(Boolean, nullable=False, default=False)

    word_count = Column(Integer, nullable=True)

    has_attachments = Column(Boolean, nullable=False, default=False)
    attachment_count = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User", foreign_keys=[OwnedObject.user_id])

    # Constraints
    __table_args__ = (
        CheckConstraint("note_format IN ('plain', 'markdown', 'html', 'rich_text')", name='chk_note_format'),
        CheckConstraint("attachment_count >= 0", name='chk_note_attachments'),
        Index('idx_notes_pinned', 'is_pinned', postgresql_where=Column('is_pinned') == True),
        Index('idx_notes_folder', 'folder', postgresql_where=Column('folder').isnot(None)),
    )

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title[:50]})>"
