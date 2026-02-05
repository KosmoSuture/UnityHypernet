"""
Hypernet Core - Main Application Entry Point

This is the FastAPI application that serves the Hypernet API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
from app.routes import (
    auth, users, media, albums, integrations, links,
    social_posts, social_accounts, notes, bookmarks,
    contacts, calendar_events, tasks, emails, web_pages
)

# Create database tables (in production, use Alembic migrations)
# Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Hypernet Core API",
    description="Universal Personal Data Platform - API v1",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Core
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])
app.include_router(links.router, prefix="/api/v1/links", tags=["Links"])

# Media
app.include_router(media.router, prefix="/api/v1/media", tags=["Media"])
app.include_router(albums.router, prefix="/api/v1/albums", tags=["Albums"])

# Social
app.include_router(social_posts.router, prefix="/api/v1/social-posts", tags=["Social Media"])
app.include_router(social_accounts.router, prefix="/api/v1/social-accounts", tags=["Social Media"])

# Communication
app.include_router(emails.router, prefix="/api/v1/emails", tags=["Communication"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["Communication"])

# Web
app.include_router(web_pages.router, prefix="/api/v1/web-pages", tags=["Web Content"])
app.include_router(bookmarks.router, prefix="/api/v1/bookmarks", tags=["Web Content"])

# Life
app.include_router(calendar_events.router, prefix="/api/v1/calendar-events", tags=["Productivity"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Productivity"])
app.include_router(notes.router, prefix="/api/v1/notes", tags=["Productivity"])


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirects to API docs"""
    return JSONResponse({
        "message": "Hypernet Core API v0.1.0",
        "docs": "/api/docs",
        "health": "/health",
    })


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint

    Returns:
        dict: Health status and version information
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "api_version": "v1",
        "environment": settings.ENVIRONMENT,
    }


# Version info endpoint
@app.get("/api/v1/version", tags=["System"])
async def version_info():
    """
    Get API version and capabilities

    Returns:
        dict: Version and capabilities information
    """
    return {
        "version": "0.1.0",
        "api_version": "v1",
        "capabilities": [
            # Core
            "users",
            "integrations",
            "links",
            # Media
            "media",
            "albums",
            # Social
            "social-posts",
            "social-accounts",
            # Communication
            "emails",
            "contacts",
            # Web
            "web-pages",
            "bookmarks",
            # Productivity
            "calendar-events",
            "tasks",
            "notes"
        ],
        "integrations_available": ["google-photos"],  # Start with one
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("🚀 Hypernet Core API starting...")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"📚 Docs available at: /api/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("👋 Hypernet Core API shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
