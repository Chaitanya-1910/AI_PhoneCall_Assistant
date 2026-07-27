"""Configuration validation tests."""

import pytest

from app.core.config import Settings


def test_production_requires_gemini_and_elevenlabs_keys() -> None:
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        Settings(
            app_env="production",
            gemini_api_key="",
            elevenlabs_api_key="secret",
            elevenlabs_voice_id="voice",
        )


def test_development_allows_empty_api_keys() -> None:
    settings = Settings(app_env="development", gemini_api_key="")
    assert settings.gemini.is_configured is False


def test_grouped_config_access() -> None:
    settings = Settings(
        whisper_model="small",
        whisper_device="cpu",
        whisper_compute_type="float16",
    )
    assert settings.whisper.model == "small"
    assert settings.whisper.compute_type == "float16"
