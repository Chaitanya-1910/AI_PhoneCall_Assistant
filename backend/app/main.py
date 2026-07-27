"""Application entry point."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.router import api_v1_router
from app.core.config import Settings, clear_settings_cache, get_settings, override_settings
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestContextMiddleware
from app.infrastructure.database.session import close_db, init_db
from app.infrastructure.storage.local.adapter import LocalStorageAdapter

logger = get_logger(__name__)

async def storage_cleanup_loop() -> None:
    """Periodically cleans up expired audio files from temporary storage."""
    while True:
        try:
            settings = get_settings()
            storage = LocalStorageAdapter(settings.storage)
            await storage.cleanup_expired()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("storage_cleanup_failed", error=str(e))
        await asyncio.sleep(600)  # Run every 10 minutes


def _lifespan(*, init_database: bool):
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        active_settings = get_settings()
        logger.info("application_starting", env=active_settings.app_env)
        if init_database:
            await init_db()
        
        cleanup_task = asyncio.create_task(storage_cleanup_loop())
        yield
        
        cleanup_task.cancel()
        if init_database:
            await close_db()
        logger.info("application_stopped")

    return lifespan


def create_app(
    *,
    settings_override: Settings | None = None,
    init_database: bool = True,
) -> FastAPI:
    """Application factory.

    Args:
        settings_override: Optional settings for tests.
        init_database: When False, skips DB pool initialization (unit tests).
    """
    if settings_override is not None:
        clear_settings_cache()
        override_settings(settings_override)

    active_settings = get_settings()

    app = FastAPI(
        title=active_settings.app_name,
        version="0.1.0",
        debug=active_settings.app_debug,
        lifespan=_lifespan(init_database=init_database),
        docs_url=None if active_settings.is_production else "/docs",
        redoc_url=None if active_settings.is_production else "/redoc",
        openapi_url=None if active_settings.is_production else "/openapi.json",
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
