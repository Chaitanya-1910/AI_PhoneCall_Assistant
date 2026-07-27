"""Faster-Whisper infrastructure adapter."""

import asyncio
import io
import time
from typing import AsyncIterator

import structlog
from faster_whisper import WhisperModel

from app.core.config import WhisperConfig
from app.domain.services.ai_interfaces import SpeechToTextService
from app.infrastructure.ai.whisper.exceptions import WhisperError

logger = structlog.get_logger()


class FasterWhisperAdapter(SpeechToTextService):
    """Adapter for Faster-Whisper."""

    def __init__(self, config: WhisperConfig) -> None:
        self.config = config
        self._model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        """Lazy load the Whisper model."""
        if self._model is None:
            if not self.config.enabled:
                raise WhisperError("Whisper service is disabled")
            try:
                self._model = WhisperModel(
                    model_size_or_path=self.config.model,
                    device=self.config.device,
                    compute_type=self.config.compute_type,
                )
            except Exception as e:
                raise WhisperError(f"Failed to load model: {str(e)}") from e
        return self._model

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text synchronously."""
        if not self.config.enabled:
            raise WhisperError("Whisper service is disabled")

        start_time = time.time()
        try:
            # Run the blocking transcription in a separate thread
            result = await asyncio.to_thread(self._transcribe_sync, audio_bytes)
            
            execution_time = time.time() - start_time
            logger.info(
                "whisper_transcribe_success",
                provider="whisper",
                execution_time=execution_time,
                success=True,
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "whisper_transcribe_failure",
                provider="whisper",
                execution_time=execution_time,
                success=False,
                error=str(e),
            )
            if isinstance(e, WhisperError):
                raise
            raise WhisperError(f"Transcription failed: {str(e)}") from e

    def _transcribe_sync(self, audio_bytes: bytes) -> str:
        """Internal synchronous method to run faster-whisper."""
        model = self._get_model()

        # DIAGNOSTIC LOGGING
        logger.info(
            "whisper_input_debug",
            size_bytes=len(audio_bytes),
            is_bytes_empty=len(audio_bytes) == 0
        )

        audio_file = io.BytesIO(audio_bytes)
        
        # faster_whisper accepts a file-like object or path
        segments, info = model.transcribe(audio_file, beam_size=5)
        
        # segments is a generator, so we must iterate it
        text = " ".join([segment.text for segment in segments])

        # DIAGNOSTIC LOGGING
        print(f"\nTRANSCRIPT:\n{text.strip()}\n")
        logger.info("whisper_output_debug", transcript=text.strip())

        return text.strip()
