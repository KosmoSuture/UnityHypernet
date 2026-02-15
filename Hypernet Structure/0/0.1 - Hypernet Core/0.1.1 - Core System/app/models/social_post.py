"""
SocialPost Model

SQLAlchemy model for social media posts.

Implements: 0.0.3 - Social Types / SocialPost.md
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, CheckConstraint, Index
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class SocialPost(OwnedObject):
    """
    Social media posts from Instagram, Twitter/X, Facebook, TikTok, LinkedIn, etc.
    """

    __tablename__ = "social_posts"

    # Required
    platform = Column(String(50), nullable=False, index=True)
    post_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False, default='')
    posted_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Optional
    platform_post_id = Column(String(255), nullable=True, index=True)
    platform_url = Column(String(500), nullable=True)

    # Engagement
    likes_count = Column(Integer, nullable=True)
    comments_count = Column(Integer, nullable=True)
    shares_count = Column(Integer, nullable=True)
    views_count = Column(Integer, nullable=True)

    # Status
    visibility = Column(String(50), nullable=True)
    is_pinned = Column(Boolean, nullable=False, default=False)
    location = Column(String(200), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[OwnedObject.user_id])

    # Constraints
    __table_args__ = (
        CheckConstraint("platform IN ('instagram', 'twitter', 'facebook', 'tiktok', 'linkedin')", name='chk_social_platform'),
        CheckConstraint("post_type IN ('text', 'photo', 'video', 'story', 'reel', 'carousel')", name='chk_post_type'),
        CheckConstraint("visibility IS NULL OR visibility IN ('public', 'private', 'friends', 'followers')", name='chk_visibility'),
        Index('idx_social_platform_posted', 'platform', 'posted_at'),
    )

    def __repr__(self):
        return f"<SocialPost(id={self.id}, platform={self.platform}, type={self.post_type})>"
