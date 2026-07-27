"""Standard error response schemas."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Single error detail entry."""

    code: str = Field(..., examples=["NOT_FOUND"])
    message: str = Field(..., examples=["Resource not found"])
    stage: str | None = Field(None, examples=["stt", "llm", "tts", "validation"])


class ErrorResponse(BaseModel):
    """Consistent API error envelope."""

    error: ErrorDetail
    request_id: str | None = None
