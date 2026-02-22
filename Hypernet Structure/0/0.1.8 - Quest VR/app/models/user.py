"""
User Model

SQLAlchemy model for the users table (human and AI accounts).

Implements the canonical User specification from:
0.0 - Object Type Registry / 0.0.1 - Core Types / User.md
"""

from sqlalchemy import Column, String, Boolean, BigInteger, DateTime, Text, ForeignKey, CheckConstraint, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.models.base import BaseObject


class User(BaseObject):
    """
    User accounts - both human and AI entities.

    Humans and AI can both have accounts in Hypernet.
    AI accounts enable persistent identity, personality storage, and collaboration.
    """

    __tablename__ = "users"

    # ============================================================================
    # AUTHENTICATION (Required)
    # ============================================================================

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Email address (can be pseudo-email for AI like claude@ai.hypernet.local)"
    )

    password_hash = Column(
        String(255),
        nullable=True,  # Nullable for AI accounts (use API key auth instead)
        doc="Bcrypt hashed password (NULL for AI accounts)"
    )

    account_type = Column(
        String(50),
        nullable=False,
        default='human',
        index=True,
        doc="Account type: human, ai, or service"
    )

    display_name = Column(
        String(200),
        nullable=False,
        doc="Public display name (e.g., 'Matt Schaeffer', 'Claude (Sonnet 4.5)')"
    )

    # ============================================================================
    # PROFILE (Optional)
    # ============================================================================

    avatar_photo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("media.id", ondelete="SET NULL"),
        nullable=True,
        doc="Profile picture (FK to Photo)"
    )

    bio = Column(
        Text,
        nullable=True,
        doc="User biography/description"
    )

    location = Column(
        String(200),
        nullable=True,
        doc="User location"
    )

    website = Column(
        String(500),
        nullable=True,
        doc="User website URL"
    )

    # ============================================================================
    # AI-SPECIFIC (Only for account_type='ai')
    # ============================================================================

    ai_provider = Column(
        String(100),
        nullable=True,
        doc="AI provider: anthropic, openai, google, meta (required if account_type='ai')"
    )

    ai_model = Column(
        String(100),
        nullable=True,
        doc="AI model: claude-sonnet-4.5, gpt-4, gemini-pro (required if account_type='ai')"
    )

    ai_version = Column(
        String(50),
        nullable=True,
        doc="Personality version for AI"
    )

    # ============================================================================
    # QUOTAS (Optional but with defaults)
    # ============================================================================

    storage_used = Column(
        BigInteger,
        nullable=False,
        default=0,
        server_default='0',
        doc="Storage used in bytes"
    )

    storage_quota = Column(
        BigInteger,
        nullable=False,
        default=107374182400,  # 100 GB default
        server_default='107374182400',
        doc="Storage quota in bytes"
    )

    media_count = Column(
        Integer,
        nullable=False,
        default=0,
        server_default='0',
        doc="Denormalized count of media objects (for performance)"
    )

    # ============================================================================
    # PREFERENCES (Optional)
    # ============================================================================

    preferences = Column(
        JSONB,
        nullable=False,
        default={},
        server_default='{}',
        doc="User preferences (UI settings, notifications, etc.)"
    )

    # ============================================================================
    # STATUS (Optional)
    # ============================================================================

    is_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default='false',
        doc="Email verified"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default='true',
        doc="Account active"
    )

    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last login timestamp"
    )

    # ============================================================================
    # RELATIONSHIPS
    # ============================================================================

    # Avatar photo
    avatar_photo = relationship(
        "Media",
        foreign_keys=[avatar_photo_id],
        post_update=True  # Avoid circular dependency
    )

    # Owned objects
    media = relationship("Media", back_populates="user", foreign_keys="Media.user_id", cascade="all, delete-orphan")
    albums = relationship("Album", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
    links = relationship("Link", back_populates="user", cascade="all, delete-orphan")

    # ============================================================================
    # CONSTRAINTS
    # ============================================================================

    __table_args__ = (
        # Account type validation
        CheckConstraint(
            "account_type IN ('human', 'ai', 'service')",
            name='chk_account_type'
        ),
        # Email format validation (basic)
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name='chk_email_format'
        ),
        # Storage validation
        CheckConstraint(
            "storage_used >= 0 AND storage_used <= storage_quota",
            name='chk_storage'
        ),
        # AI accounts must have provider and model
        CheckConstraint(
            "account_type != 'ai' OR (ai_provider IS NOT NULL AND ai_model IS NOT NULL)",
            name='chk_ai_fields'
        ),
        # Indexes
        Index('idx_users_account_type', 'account_type', 'is_active'),
        Index('idx_users_ai', 'ai_provider', 'ai_model', postgresql_where=Column('account_type') == 'ai'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, type={self.account_type})>"

