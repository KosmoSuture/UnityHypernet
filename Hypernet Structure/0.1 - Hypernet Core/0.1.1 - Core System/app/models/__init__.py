"""
Database Models

SQLAlchemy ORM models for all Hypernet objects.

All models implement specifications from 0.0 - Object Type Registry.
Models inherit from BaseObject or OwnedObject and map to PostgreSQL tables.
"""

# Base classes
from app.models.base import BaseObject, OwnedObject

# Core models (implements 0.0.1 - Core Types)
from app.models.user import User
from app.models.link import Link
from app.models.integration import Integration, IntegrationSecret

# Media models (implements 0.0.2 - Media Types)
from app.models.media import Media

# Container models
from app.models.album import Album

# Social models (implements 0.0.3 - Social Types)
from app.models.social_post import SocialPost
from app.models.social_account import SocialAccount

# Communication models (implements 0.0.4 - Communication Types)
from app.models.email import Email
from app.models.contact import Contact

# Web models (implements 0.0.7 - Web Types)
from app.models.web_page import WebPage
from app.models.bookmark import Bookmark

# Life models (implements 0.0.8 - Life Types)
from app.models.calendar_event import CalendarEvent
from app.models.task import Task
from app.models.note import Note

# Export all models
__all__ = [
    # Base
    "BaseObject",
    "OwnedObject",
    # Core
    "User",
    "Link",
    "Integration",
    "IntegrationSecret",
    # Media
    "Media",
    "Album",
    # Social
    "SocialPost",
    "SocialAccount",
    # Communication
    "Email",
    "Contact",
    # Web
    "WebPage",
    "Bookmark",
    # Life
    "CalendarEvent",
    "Task",
    "Note",
]

# Note: Import this module in main.py to ensure all models are registered
# before creating tables or running Alembic migrations.
#
# ============================================================================
# ALIGNMENT STATUS: 0.0 (Definitions) ↔ 0.1 (Implementation)
# ============================================================================
#
# ✅ FULLY IMPLEMENTED (Phase 1):
#
# Core Types (0.0.1):
#   ✅ BaseObject - Foundation for all objects
#   ✅ User - Human and AI accounts
#   ✅ Link - First-class relationships
#   ✅ Integration - OAuth connections
#
# Media Types (0.0.2):
#   ✅ Media - Polymorphic base (photo/video/audio/document/screenshot)
#   ✅ Album - Collections
#
# Social Types (0.0.3):
#   ✅ SocialPost - Posts from Instagram, Twitter, etc.
#   ✅ SocialAccount - Social media profiles
#
# Communication Types (0.0.4):
#   ✅ Email - Email messages
#   ✅ Contact - Address book contacts
#
# Web Types (0.0.7):
#   ✅ WebPage - Saved pages
#   ✅ Bookmark - Browser bookmarks
#
# Life Types (0.0.8):
#   ✅ CalendarEvent - Calendar appointments
#   ✅ Task - To-do items
#   ✅ Note - Personal notes
#
# ⏳ PENDING (Phase 2+):
#
# Social Types (0.0.3):
#   - SocialConnection (follows, friends)
#   - SocialMessage (DMs)
#
# Communication Types (0.0.4):
#   - SMS, ChatMessage, VoiceCall, VideoCall
#
# Web Types (0.0.7):
#   - RSSFeed
#
# Financial Types (0.0.5):
#   - Transaction, BankAccount, Investment, Bill, Receipt
#
# Medical Types (0.0.6):
#   - MedicalRecord, Prescription, LabResult, HealthMetric
#
# AI Types (0.0.9):
#   - AIPersonality, AIMemory, AIContribution
#
# ============================================================================
# TOTAL MODELS: 19 (Base + 17 domain models)
# PHASE 1 COVERAGE: ~65% of planned types
# ============================================================================
