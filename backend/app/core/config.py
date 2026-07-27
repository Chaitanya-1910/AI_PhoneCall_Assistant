"""Application configuration via environment variables."""

from dataclasses import dataclass
from typing import Literal, Self

from pydantic import Field, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    """Grouped database settings."""

    url: str
    pool_size: int
    max_overflow: int
    echo: bool


@dataclass(frozen=True, slots=True)
class GroqConfig:
    """Grouped Groq LLM settings."""

    enabled: bool
    api_key: str
    model: str
    timeout: float
    retry_count: int

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass(frozen=True, slots=True)
class WhisperConfig:
    """Grouped Faster-Whisper settings."""

    enabled: bool
    model: str
    device: Literal["cpu", "cuda"]
    compute_type: str
    timeout: float
    retry_count: int


@dataclass(frozen=True, slots=True)
class ElevenLabsConfig:
    """Grouped ElevenLabs TTS settings."""

    enabled: bool
    api_key: str
    voice_id: str
    model: str
    timeout: float
    retry_count: int

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.voice_id)


@dataclass(frozen=True, slots=True)
class ExotelConfig:
    """Grouped Exotel settings."""
    api_key: str
    api_token: str
    sid: str
    public_media_url: str

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_token and self.sid)


@dataclass(frozen=True, slots=True)
class StorageConfig:
    """Grouped Storage settings."""

    max_audio_upload_size_mb: int
    audio_expiration_seconds: int


@dataclass(frozen=True, slots=True)
class ConversationConfig:
    """Grouped Conversation Intelligence settings."""

    max_history_turns: int
    max_prompt_size_tokens: int
    max_summary_size_tokens: int
    fallback_response: str
    intent_confidence_threshold: float
    max_response_length: int

@dataclass(frozen=True, slots=True)
class GlobalConfig:
    """Global Deployment & Scalability Settings"""
    multi_region_enabled: bool
    primary_region: str
    redis_cluster_nodes: str
    dr_active: bool


class Settings(BaseSettings):
    """Centralized configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env", "app/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "CHAYA"
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://chaya:changeme@192.168.0.8:5432/chaya"
    )
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_echo: bool = False

    # Groq
    groq_enabled: bool = True
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout: float = 30.0
    groq_retry_count: int = 3

    # Faster-Whisper
    whisper_enabled: bool = True
    whisper_model: str = "base"
    whisper_device: Literal["cpu", "cuda"] = "cpu"
    whisper_compute_type: str = "int8"
    whisper_timeout: float = 30.0
    whisper_retry_count: int = 3

    # ElevenLabs
    elevenlabs_enabled: bool = True
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    elevenlabs_model: str = "eleven_multilingual_v2"
    elevenlabs_timeout: float = 30.0
    elevenlabs_retry_count: int = 3

    # CORS
    cors_origins: str | list[str] = Field(default=["http://192.168.0.8:3000"])
    
    # Storage
    max_audio_upload_size_mb: int = 10
    audio_expiration_seconds: int = 3600
    
    # Conversation
    conv_max_history_turns: int = 10
    conv_max_prompt_size_tokens: int = 8000
    conv_max_summary_size_tokens: int = 1000
    conv_fallback_response: str = "I'm sorry, but I'm having trouble understanding right now. Could we try again?"
    conv_intent_confidence_threshold: float = 0.7
    conv_max_response_length: int = 1000
    
    # Global Deployment
    global_multi_region_enabled: bool = False
    global_primary_region: str = "us-east-1"
    global_redis_cluster_nodes: str = "redis://localhost:6379"
    global_dr_active: bool = False

    # Exotel
    exotel_api_key: str = ""
    exotel_api_token: str = ""
    exotel_sid: str = ""
    public_media_url: str = "https://example.com/media/tts"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_config(self) -> Self:
        if not self.is_production:
            return self

        missing: list[str] = []
        if not self.groq_api_key:
            missing.append("GROQ_API_KEY")
        if not self.elevenlabs_api_key:
            missing.append("ELEVENLABS_API_KEY")
        if not self.elevenlabs_voice_id:
            missing.append("ELEVENLABS_VOICE_ID")

        if missing:
            msg = f"Missing required environment variables in production: {', '.join(missing)}"
            raise ValueError(msg)

        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def database(self) -> DatabaseConfig:
        return DatabaseConfig(
            url=str(self.database_url),
            pool_size=self.database_pool_size,
            max_overflow=self.database_max_overflow,
            echo=self.database_echo,
        )

    @property
    def groq(self) -> GroqConfig:
        return GroqConfig(
            enabled=self.groq_enabled,
            api_key=self.groq_api_key,
            model=self.groq_model,
            timeout=self.groq_timeout,
            retry_count=self.groq_retry_count,
        )

    @property
    def whisper(self) -> WhisperConfig:
        return WhisperConfig(
            enabled=self.whisper_enabled,
            model=self.whisper_model,
            device=self.whisper_device,
            compute_type=self.whisper_compute_type,
            timeout=self.whisper_timeout,
            retry_count=self.whisper_retry_count,
        )

    @property
    def elevenlabs(self) -> ElevenLabsConfig:
        return ElevenLabsConfig(
            enabled=self.elevenlabs_enabled,
            api_key=self.elevenlabs_api_key,
            voice_id=self.elevenlabs_voice_id,
            model=self.elevenlabs_model,
            timeout=self.elevenlabs_timeout,
            retry_count=self.elevenlabs_retry_count,
        )

    @property
    def storage(self) -> StorageConfig:
        return StorageConfig(
            max_audio_upload_size_mb=self.max_audio_upload_size_mb,
            audio_expiration_seconds=self.audio_expiration_seconds,
        )

    @property
    def conversation(self) -> ConversationConfig:
        return ConversationConfig(
            max_history_turns=self.conv_max_history_turns,
            max_prompt_size_tokens=self.conv_max_prompt_size_tokens,
            max_summary_size_tokens=self.conv_max_summary_size_tokens,
            fallback_response=self.conv_fallback_response,
            intent_confidence_threshold=self.conv_intent_confidence_threshold,
            max_response_length=self.conv_max_response_length,
        )

    @property
    def global_deploy(self) -> GlobalConfig:
        return GlobalConfig(
            multi_region_enabled=self.global_multi_region_enabled,
            primary_region=self.global_primary_region,
            redis_cluster_nodes=self.global_redis_cluster_nodes,
            dr_active=self.global_dr_active
        )
        
    @property
    def exotel(self) -> ExotelConfig:
        return ExotelConfig(
            api_key=self.exotel_api_key,
            api_token=self.exotel_api_token,
            sid=self.exotel_sid,
            public_media_url=self.public_media_url
        )


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return application settings singleton."""
    global _settings
    if _settings is None:
        print("[DEBUG] Settings initialized!")
        _settings = Settings()
        
        # Debug logging
        api_key = _settings.groq_api_key
        print(f"[DEBUG] GROQ_API_KEY loaded: {bool(api_key)}")
        print(f"[DEBUG] GROQ_API_KEY length: {len(api_key)}")
        if api_key:
            print(f"[DEBUG] GROQ_API_KEY first 6 chars: {api_key[:6]}...")
        print(f"[DEBUG] is_configured: {_settings.groq.is_configured}")

    return _settings


def override_settings(settings: Settings) -> None:
    """Replace active settings — for tests and local overrides."""
    global _settings
    _settings = settings


def clear_settings_cache() -> None:
    """Reset settings singleton."""
    global _settings
    _settings = None


settings = get_settings()
