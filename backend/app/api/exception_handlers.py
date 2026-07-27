"""Global exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import ChayaError, PipelineError
from app.core.logging import get_logger
from app.core.middleware import REQUEST_ID_HEADER
from app.schemas.errors import ErrorDetail, ErrorResponse

logger = get_logger(__name__)


def _request_id(request: Request) -> str | None:
    return request.headers.get(REQUEST_ID_HEADER)


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    stage: str | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorDetail(code=code, message=message, stage=stage),
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers."""

    @app.exception_handler(ChayaError)
    async def chaya_error_handler(request: Request, exc: ChayaError) -> JSONResponse:
        status_map = {
            "NOT_FOUND": 404,
            "VALIDATION_ERROR": 422,
            "EXTERNAL_SERVICE_ERROR": 502,
            "CONFIGURATION_ERROR": 500,
            "PIPELINE_ERROR": 502,
        }
        status_code = status_map.get(exc.code, 400)
        
        stage = None
        if isinstance(exc, PipelineError):
            stage = exc.stage
        elif exc.code == "VALIDATION_ERROR":
            stage = "validation"
            
        logger.warning("application_error", code=exc.code, message=exc.message, stage=stage)
        return _error_response(
            request,
            status_code=status_code,
            code=exc.code,
            message=exc.message,
            stage=stage,
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", error=str(exc))
        message = str(exc) if settings.app_debug else "Internal server error"
        return _error_response(
            request,
            status_code=500,
            code="INTERNAL_ERROR",
            message=message,
        )
