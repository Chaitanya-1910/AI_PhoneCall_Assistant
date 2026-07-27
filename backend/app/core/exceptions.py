"""Application-level exception hierarchy."""


class ChayaError(Exception):
    """Base exception for all CHAYA application errors."""

    def __init__(self, message: str, *, code: str = "CHAYA_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(ChayaError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="NOT_FOUND")


class ValidationError(ChayaError):
    """Domain validation failure."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="VALIDATION_ERROR")


class AiServiceError(ChayaError):
    """Third-party AI service failure (Whisper, Gemini, ElevenLabs)."""

    def __init__(self, service: str, message: str) -> None:
        super().__init__(f"{service}: {message}", code="AI_SERVICE_ERROR")
        self.service = service


class ConfigurationError(ChayaError):
    """Invalid or missing configuration."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFIGURATION_ERROR")


class PipelineError(ChayaError):
    """Failure within the AI Call Pipeline."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(f"Pipeline failed at {stage}: {message}", code="PIPELINE_ERROR")
        self.stage = stage
