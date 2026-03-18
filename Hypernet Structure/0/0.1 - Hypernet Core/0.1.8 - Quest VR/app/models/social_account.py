"""
SocialAccount Model

SQLAlchemy model for social media accounts/profiles.

Implements: 0.0.3 - Social Types / SocialAccount.md
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class SocialAccount(OwnedObject):
    """
    External social media accounts belonging to the user or others.
    """

    __tablename__ = "social_accounts"

    # Required
    platform = Column(String(50), nullable=False, index=True)
    username = Column(String(100), nullable=False, index=True)
    account_type = Column(String(50), nullable=False)

    # Optional
    display_name = Column(String(200), nullable=True)
    profile_url = Column(String(500), nullable=True)
    profile_picture_id = Column(UUID(as_uuid=True), ForeignKey("media.id", ondelete="SET NULL"), nullable=True)

    # Stats
    followers_count = Column(Integer, nullable=True)
    following_count = Column(Integer, nullable=True)
    posts_count = Column(Integer, nullable=True)

    bio = Column(Text, nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_private = Column(Boolean, nullable=False, default=False)

    # Relationships
    user = relationship("User", foreign_keys=[OwnedObject.user_id])
    profile_picture = relationship("Media", foreign_keys=[profile_picture_id], post_update=True)

    # Constraints
    __table_args__ = (
        CheckConstraint("platform IN ('instagram', 'twitter', 'facebook', 'tiktok', 'linkedin')", name='chk_platform'),
        CheckConstraint("account_type IN ('own', 'following', 'other')", name='chk_account_type'),
        Index('idx_social_account_platform_username', 'platform', 'username'),
    )

    def __repr__(self):
        return f"<SocialAccount(id={self.id}, platform={self.platform}, username={self.username})>"
