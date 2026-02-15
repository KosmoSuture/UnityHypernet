"""
Link Routes

Endpoints for managing relationships between objects.
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_link():
    """Create link (placeholder)"""
    return {"message": "Link routes - coming soon"}
