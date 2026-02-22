"""
Integration Routes

Endpoints for connecting and syncing external services.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_integrations():
    """List integrations (placeholder)"""
    return {"message": "Integration routes - coming soon"}
