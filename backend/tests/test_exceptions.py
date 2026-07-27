"""Exception handler tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.exceptions import NotFoundError
from app.main import create_app


@pytest.fixture
def app_with_error_route(test_settings):
    from app.core.config import clear_settings_cache, override_settings

    clear_settings_cache()
    override_settings(test_settings)
    application = create_app(init_database=False)

    @application.get("/api/v1/test-not-found")
    async def trigger_not_found() -> None:
        raise NotFoundError("Call session not found")

    yield application
    clear_settings_cache()


@pytest.mark.asyncio
async def test_chaya_error_returns_structured_response(app_with_error_route):
    transport = ASGITransport(app=app_with_error_route)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/test-not-found")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert "Call session not found" in body["error"]["message"]
    assert "X-Request-ID" in response.headers
