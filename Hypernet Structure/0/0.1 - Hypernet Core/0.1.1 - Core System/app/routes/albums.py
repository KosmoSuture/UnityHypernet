"""
Album Routes

Endpoints for album management.
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_album():
    """Create album (placeholder)"""
    return {"message": "Album routes - coming soon"}
