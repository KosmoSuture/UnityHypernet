"""
User Routes

Endpoints for user profile management.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
async def get_current_user():
    """Get current user profile (placeholder)"""
    return {"message": "User routes - coming soon"}
