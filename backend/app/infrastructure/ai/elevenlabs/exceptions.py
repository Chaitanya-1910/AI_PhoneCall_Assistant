"""Exceptions for the ElevenLabs provider."""

from app.core.exceptions import AiServiceError


class ElevenLabsError(AiServiceError):
    """Specific error for ElevenLabs failures."""

    def __init__(self, message: str) -> None:
        super().__init__("ElevenLabs", message)
