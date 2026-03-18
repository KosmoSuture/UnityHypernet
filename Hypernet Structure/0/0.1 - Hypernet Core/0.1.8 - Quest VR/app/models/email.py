"""
Email Model

SQLAlchemy model for email messages.

Implements: 0.0.4 - Communication Types / Email.md
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class Email(OwnedObject):
    """
    Email messages from Gmail, Outlook, iCloud Mail, etc.
    """

    __tablename__ = "emails"

    # Required fields
    subject = Column(String(500), nullable=False, index=True)
    from_address = Column(String(255), nullable=False, index=True)
    to_addresses = Column(ARRAY(Text), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=False, index=True)
    direction = Column(String(50), nullable=False, index=True, doc="sent, received, draft")

    # Optional fields
    cc_addresses = Column(ARRAY(Text), nullable=True)
    bcc_addresses = Column(ARRAY(Text), nullable=True)

    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)

    thread_id = Column(String(255), nullable=True, index=True)
    message_id = Column(String(255), nullable=True, index=True, doc="RFC 822 Message-ID")

    has_attachments = Column(Boolean, nullable=False, default=False)
    attachment_count = Column(Integer, nullable=False, default=0)

    is_read = Column(Boolean, nullable=False, default=False)
    is_starred = Column(Boolean, nullable=False, default=False)
    is_important = Column(Boolean, nullable=False, default=False)

    labels = Column(ARRAY(Text), nullable=True, doc="Gmail labels or folder names")

    # Relationships
    user = relationship("User", foreign_keys=[OwnedObject.user_id])

    # Constraints
    __table_args__ = (
        CheckConstraint("direction IN ('sent', 'received', 'draft')", name='chk_email_direction'),
        CheckConstraint("attachment_count >= 0", name='chk_attachment_count'),
        Index('idx_emails_thread', 'thread_id', postgresql_where=Column('thread_id').isnot(None)),
        Index('idx_emails_unread', 'is_read', postgresql_where=Column('is_read') == False),
    )

    def __repr__(self):
        return f"<Email(id={self.id}, subject={self.subject[:50]}, from={self.from_address})>"
