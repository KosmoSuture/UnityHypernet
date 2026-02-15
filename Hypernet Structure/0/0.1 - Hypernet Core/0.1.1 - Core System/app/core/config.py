"""
Application Configuration

Loads configuration from environment variables using Pydantic Settings.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://hypernet:dev-password@localhost:5432/hypernet",
        description="PostgreSQL connection string"
    )

    # Security
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15,
        description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=30,
        description="Refresh token expiration in days"
    )

    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8443, description="Server port")
    RELOAD: bool = Field(default=True, description="Auto-reload on code changes (dev only)")

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )

    # Storage
    MEDIA_ROOT: str = Field(
        default="/media",
        description="Root directory for media files"
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=104857600,  # 100MB
        description="Maximum upload size in bytes"
    )

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )

    # Environment
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    DEBUG: bool = Field(
        default=True,
        description="Debug mode"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()
