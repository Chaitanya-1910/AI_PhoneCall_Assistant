"""Health check domain service."""

from app.core.config import Settings
from app.domain.models.health import HealthStatus


class HealthService:
    """Provides service health information."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def get_status(self) -> HealthStatus:
        return HealthStatus(
            status="ok",
            service=self._settings.app_name,
            environment=self._settings.app_env,
        )
