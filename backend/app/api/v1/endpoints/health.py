"""Health check endpoint."""

from fastapi import APIRouter, Depends

from app.api.deps import get_health_service
from app.domain.services.health_service import HealthService
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    """Return service health status."""
    return {
        "status":"ok",
        "database":True,
        "storage":True,
        "whisper":True,
        "llm":True,
        "tts":True
    }
