"""API v1 route aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import calls, dev, health
from app.api.v1 import exotel

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, tags=["health"])
api_v1_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_v1_router.include_router(dev.router, prefix="/dev", tags=["dev"])
api_v1_router.include_router(exotel.router)
api_v1_router.include_router(exotel.media_router)
