"""
Link Model

SQLAlchemy model for the links table (first-class relationships between objects).

Implements: 0.0.1 - Core Types / Link.md
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class Link(OwnedObject):
    """
    First-class relationships between any two objects in Hypernet.

    Links are not just foreign keys - they are objects themselves with metadata.
    This enables graph queries, relationship tracking, and rich connections.
    """

    __tablename__ = "links"

    # ============================================================================
    # LINK ENDPOINTS (Required)
    # ============================================================================

    from_object_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        doc="Source object UUID (can be any type)"
    )

    from_object_type = Column(
        String(50),
        nullable=False,
        doc="Source object type (Photo, Album, User, etc.)"
    )

    to_object_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        doc="Target object UUID (can be any type)"
    )

    to_object_type = Column(
        String(50),
        nullable=False,
        doc="Target object type"
    )

    # ============================================================================
    # LINK TYPE (Required)
    # ============================================================================

    link_type = Column(
        String(50),
        nullable=False,
        index=True,
        doc="Link type: contains, source, duplicate_of, variant_of, related_to"
    )

    # ============================================================================
    # LINK PROPERTIES (Optional)
    # ============================================================================

    strength = Column(
        Float,
        nullable=False,
        default=1.0,
        doc="Confidence/weight of relationship (0.0 to 1.0)"
    )

    is_bidirectional = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="If true, relationship works both ways"
    )

    sort_order = Column(
        Integer,
        nullable=True,
        doc="For ordered relationships (e.g., photos in album)"
    )

    # ============================================================================
    # RELATIONSHIPS
    # ============================================================================

    user = relationship("User", back_populates="links", foreign_keys=[OwnedObject.user_id])

    # ============================================================================
    # CONSTRAINTS
    # ============================================================================

    __table_args__ = (
        # Link type validation
        CheckConstraint(
            "link_type IN ('contains', 'source', 'duplicate_of', 'variant_of', 'related_to')",
            name='chk_link_type'
        ),
        # Strength validation
        CheckConstraint(
            "strength >= 0.0 AND strength <= 1.0",
            name='chk_strength'
        ),
        # Prevent self-links
        CheckConstraint(
            "from_object_id != to_object_id OR from_object_type != to_object_type",
            name='chk_not_self_link'
        ),
        # Composite indexes for graph traversal
        Index(
            'idx_links_from',
            'from_object_id', 'link_type',
            postgresql_where=Column('deleted_at').is_(None)
        ),
        Index(
            'idx_links_to',
            'to_object_id', 'link_type',
            postgresql_where=Column('deleted_at').is_(None)
        ),
        Index(
            'idx_links_ordered',
            'from_object_id', 'sort_order',
            postgresql_where=Column('deleted_at').is_(None)
        ),
        # Unique constraint: No duplicate links
        Index(
            'idx_links_unique',
            'from_object_id', 'to_object_id', 'link_type',
            unique=True,
            postgresql_where=Column('deleted_at').is_(None)
        ),
    )

    def __repr__(self):
        return f"<Link(id={self.id}, type={self.link_type}, {self.from_object_type}→{self.to_object_type})>"
