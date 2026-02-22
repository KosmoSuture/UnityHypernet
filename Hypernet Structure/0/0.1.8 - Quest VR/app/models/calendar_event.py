"""
CalendarEvent Model

SQLAlchemy model for calendar events and appointments.

Implements: 0.0.8 - Life Types / CalendarEvent.md
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import ARRAY, INTEGER
from sqlalchemy.orm import relationship

from app.models.base import OwnedObject


class CalendarEvent(OwnedObject):
    """
    Calendar events from Google Calendar, Outlook, Apple Calendar, etc.
    """

    __tablename__ = "calendar_events"

    # Required
    title = Column(String(500), nullable=False, index=True)
    starts_at = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, default='event')

    # Optional
    ends_at = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    # Recurrence
    is_recurring = Column(Boolean, nullable=False, default=False)
    recurrence_rule = Column(String(255), nullable=True, doc="iCal RRULE format")

    # Participants
    organizer_email = Column(String(255), nullable=True)
    attendees = Column(ARRAY(Text), nullable=True)

    # Virtual meeting
    meeting_url = Column(String(500), nullable=True)

    # Status
    status = Column(String(50), nullable=False, default='confirmed')
    reminder_minutes = Column(ARRAY(INTEGER), nullable=True, doc="Minutes before event for reminders")

    # Relationships
    user = relationship("User", foreign_keys=[OwnedObject.user_id])

    # Constraints
    __table_args__ = (
        CheckConstraint("event_type IN ('event', 'reminder', 'task', 'birthday')", name='chk_event_type'),
        CheckConstraint("status IN ('confirmed', 'tentative', 'cancelled')", name='chk_event_status'),
        CheckConstraint("ends_at IS NULL OR ends_at >= starts_at", name='chk_event_times'),
        Index('idx_calendar_upcoming', 'starts_at', postgresql_where=Column('deleted_at').is_(None)),
    )

    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title={self.title}, starts={self.starts_at})>"
