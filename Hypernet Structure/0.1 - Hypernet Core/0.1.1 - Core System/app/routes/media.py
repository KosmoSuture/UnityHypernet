"""
Media Routes

Endpoints for media upload, retrieval, and management.
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
async def upload_media():
    """Upload media file (placeholder)"""
    return {"message": "Media routes - coming soon"}
