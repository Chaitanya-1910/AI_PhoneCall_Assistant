"""Groq exception classes."""

from app.core.exceptions import AiServiceError


class GroqError(AiServiceError):
    """Base exception for Groq provider errors."""

    def __init__(self, message: str) -> None:
        super().__init__(service="Groq", message=message)
