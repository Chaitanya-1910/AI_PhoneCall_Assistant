"""Exceptions for the Whisper provider."""

from app.core.exceptions import AiServiceError


class WhisperError(AiServiceError):
    """Specific error for Whisper failures."""

    def __init__(self, message: str) -> None:
        super().__init__("Whisper", message)
