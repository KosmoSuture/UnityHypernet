"""
Contact Model

SQLAlchemy model for contact information.

Implements: 0.0.8 - Life Types / Contact.md
"""

from sqlalchemy import Column, String, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class Contact(OwnedObject):
    """
    Contact information for people (address book, phone contacts).
    """

    __tablename__ = "contacts"

    # Required
    display_name = Column(String(200), nullable=False, index=True)

    # Optional - Name parts
    first_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True, index=True)

    # Contact methods
    email_addresses = Column(ARRAY(Text), nullable=True)
    phone_numbers = Column(ARRAY(Text), nullable=True)

    # Address
    street_address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)

    # Social/Work
    company = Column(String(200), nullable=True)
    job_title = Column(String(200), nullable=True)
    website = Column(String(500), nullable=True)

    # Profile
    profile_photo_id = Column(UUID(as_uuid=True), ForeignKey("media.id", ondelete="SET NULL"), nullable=True)
    birthday = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    nickname = Column(String(100), nullable=True)
    tags = Column(ARRAY(Text), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[OwnedObject.user_id])
    profile_photo = relationship("Media", foreign_keys=[profile_photo_id], post_update=True)

    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.display_name})>"
