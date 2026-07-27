"""AI Call Pipeline Orchestrator."""

import time
from dataclasses import dataclass
from typing import Any, Callable, Coroutine

import structlog

from app.core.exceptions import AiServiceError, PipelineError
from app.domain.services.ai_interfaces import LlmService, SpeechToTextService, TextToSpeechService

logger = structlog.get_logger()


@dataclass
class PipelineResult:
    """Result of a single pipeline execution."""

    transcript: str
    response: str
    audio_bytes: bytes
    stt_latency_ms: int
    llm_latency_ms: int
    tts_latency_ms: int
    total_latency_ms: int


class CallPipelineService:
    """Orchestrates the AI pipeline: Audio -> STT -> LLM -> TTS."""

    def __init__(
        self,
        stt_service: SpeechToTextService,
        llm_service: LlmService,
        tts_service: TextToSpeechService,
    ) -> None:
        self.stt_service = stt_service
        self.llm_service = llm_service
        self.tts_service = tts_service

    async def transcribe(self, audio_bytes: bytes, request_id: str) -> tuple[str, float]:
        """Convert speech to text using the STT provider."""
        transcript, stt_latency = await self._run_stage(
            "stt",
            request_id,
            self.stt_service.transcribe,
            audio_bytes,
        )
        return transcript, stt_latency

    async def generateResponse(self, prompt: str, request_id: str) -> tuple[str, float]:
        """Generate response text using the LLM provider."""
        response_text, llm_latency = await self._run_stage(
            "llm",
            request_id,
            self.llm_service.generate_response,
            prompt,
        )
        return response_text, llm_latency

    async def synthesizeSpeech(self, text: str, request_id: str) -> tuple[bytes, float]:
        """Convert text to speech using the TTS provider."""
        response_audio, tts_latency = await self._run_stage(
            "tts",
            request_id,
            self.tts_service.synthesize,
            text,
        )
        return response_audio, tts_latency

    async def _run_stage(
        self, stage: str, request_id: str, func: Callable[..., Coroutine[Any, Any, Any]], *args: Any, **kwargs: Any
    ) -> tuple[Any, float]:
        start_time = time.time()
        logger.info(
            "pipeline_stage_started",
            request_id=request_id,
            stage=stage,
        )
        try:
            result = await func(*args, **kwargs)

            execution_time = time.time() - start_time
            logger.info(
                "pipeline_stage_completed",
                request_id=request_id,
                stage=stage,
                execution_time=execution_time,
                success=True,
            )
            return result, execution_time
        except AiServiceError as e:
            execution_time = time.time() - start_time
            logger.error(
                "pipeline_stage_failed",
                request_id=request_id,
                stage=stage,
                provider=e.service,
                execution_time=execution_time,
                success=False,
                failure_reason=str(e),
            )
            raise PipelineError(stage=stage, message=str(e)) from e
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "pipeline_stage_failed",
                request_id=request_id,
                stage=stage,
                execution_time=execution_time,
                success=False,
                failure_reason=str(e),
            )
            raise PipelineError(stage=stage, message=f"Unexpected error: {str(e)}") from e
