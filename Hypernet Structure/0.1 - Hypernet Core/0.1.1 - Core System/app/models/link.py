"""
Link Model

SQLAlchemy model for the links table (relationships between objects).
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, CheckConstraint, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Link(Base):
    """Relationships between objects (first-class links)"""

    __tablename__ = "links"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Link Endpoints
    from_object_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    from_object_type = Column(String(50), nullable=False)
    to_object_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    to_object_type = Column(String(50), nullable=False)

    # Link Type
    link_type = Column(String(50), nullable=False, index=True)

    # Link Properties
    strength = Column(Float, nullable=False, default=1.0)
    is_bidirectional = Column(Boolean, nullable=False, default=False)

    # Ordering (for ordered relationships like album -> photos)
    sort_order = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    # Source Tracking
    source_type = Column(String(50))
    source_id = Column(String(255))

    # Extensibility
    metadata = Column(JSONB, nullable=False, default={})

    # Relationships
    user = relationship("User", back_populates="links")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "link_type IN ('contains', 'source', 'duplicate_of', 'variant_of', 'related_to')",
            name='chk_link_type'
        ),
        CheckConstraint(
            "strength >= 0.0 AND strength <= 1.0",
            name='chk_strength'
        ),
        CheckConstraint(
            "from_object_id != to_object_id OR from_object_type != to_object_type",
            name='chk_not_self_link'
        ),
        # Composite indexes
        Index('idx_links_from', 'from_object_id', 'link_type', postgresql_where=Column('deleted_at').is_(None)),
        Index('idx_links_to', 'to_object_id', 'link_type', postgresql_where=Column('deleted_at').is_(None)),
        Index('idx_links_ordered', 'from_object_id', 'sort_order', postgresql_where=Column('deleted_at').is_(None)),
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
