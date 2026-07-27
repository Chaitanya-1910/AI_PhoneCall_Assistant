"""Pytest fixtures."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, clear_settings_cache
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        app_env="development",
        app_debug=True,
        database_url="postgresql+asyncpg://chaya:changeme@192.168.0.8:5432/chaya_test",
    )


@pytest.fixture
def app(test_settings: Settings):
    clear_settings_cache()
    application = create_app(settings_override=test_settings, init_database=False)
    yield application
    clear_settings_cache()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
