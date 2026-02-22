"""
Task Model

SQLAlchemy model for tasks and to-do items.

Implements: 0.0.8 - Life Types / Task.md
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class Task(OwnedObject):
    """
    Tasks and to-do items from task managers or personal lists.
    """

    __tablename__ = "tasks"

    # Required
    title = Column(String(500), nullable=False, index=True)
    status = Column(String(50), nullable=False, default='pending', index=True)

    # Optional
    description = Column(Text, nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    priority = Column(String(50), nullable=True, index=True)
    tags = Column(ARRAY(Text), nullable=True)
    project = Column(String(200), nullable=True, index=True)

    # Subtasks
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True)
    subtask_order = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[OwnedObject.user_id])
    parent_task = relationship("Task", remote_side="Task.id", foreign_keys=[parent_task_id])
    subtasks = relationship("Task", back_populates="parent_task", foreign_keys=[parent_task_id])

    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'cancelled')", name='chk_task_status'),
        CheckConstraint("priority IS NULL OR priority IN ('low', 'medium', 'high', 'urgent')", name='chk_task_priority'),
        Index('idx_tasks_active', 'status', postgresql_where=Column('status').in_(['pending', 'in_progress'])),
        Index('idx_tasks_overdue', 'due_at', postgresql_where=Column('status') != 'completed'),
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
