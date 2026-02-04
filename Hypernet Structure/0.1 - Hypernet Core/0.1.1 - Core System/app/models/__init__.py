"""
Database Models

SQLAlchemy ORM models for all Hypernet objects.

All models inherit from Base and map to PostgreSQL tables.
"""

from app.models.user import User
from app.models.media import Media
from app.models.album import Album
from app.models.integration import Integration, IntegrationSecret
from app.models.link import Link

# Export all models
__all__ = [
    "User",
    "Media",
    "Album",
    "Integration",
    "IntegrationSecret",
    "Link",
]

# Note: Import this module in main.py to ensure all models are registered
# before creating tables or running Alembic migrations.
