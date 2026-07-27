"""ElevenLabs infrastructure adapter."""

import asyncio
import time
from typing import AsyncIterator

import structlog
from elevenlabs import AsyncElevenLabs
from elevenlabs.core.api_error import ApiError

from app.core.config import ElevenLabsConfig
from app.domain.services.ai_interfaces import TextToSpeechService
from app.infrastructure.ai.elevenlabs.exceptions import ElevenLabsError

logger = structlog.get_logger()


class ElevenLabsAdapter(TextToSpeechService):
    """Adapter for ElevenLabs."""

    def __init__(self, config: ElevenLabsConfig) -> None:
        self.config = config
        self._client: AsyncElevenLabs | None = None

    def _get_client(self) -> AsyncElevenLabs:
        """Lazy load the ElevenLabs client."""
        if self._client is None:
            if not self.config.enabled:
                raise ElevenLabsError("ElevenLabs service is disabled")
            if not self.config.api_key:
                raise ElevenLabsError("ElevenLabs API key is missing")
            try:
                self._client = AsyncElevenLabs(
                    api_key=self.config.api_key,
                    timeout=self.config.timeout,
                )
            except Exception as e:
                raise ElevenLabsError(f"Failed to initialize client: {str(e)}") from e
        return self._client

    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio bytes synchronously."""
        if not self.config.enabled:
            raise ElevenLabsError("ElevenLabs service is disabled")

        start_time = time.time()
        for attempt in range(max(1, self.config.retry_count)):
            try:
                client = self._get_client()
                response_generator = client.text_to_speech.convert(
                    voice_id=self.config.voice_id,
                    output_format="mp3_44100_128",
                    text=text,
                    model_id=self.config.model,
                )
                
                # response_generator is an async generator yielding bytes
                audio_bytes = b""
                async for chunk in response_generator:
                    audio_bytes += chunk
                    
                execution_time = time.time() - start_time
                logger.info(
                    "elevenlabs_synthesize_success",
                    provider="elevenlabs",
                    execution_time=execution_time,
                    success=True,
                )
                return audio_bytes
            except Exception as e:
                if attempt == max(1, self.config.retry_count) - 1:
                    execution_time = time.time() - start_time
                    logger.error(
                        "elevenlabs_synthesize_failure",
                        provider="elevenlabs",
                        execution_time=execution_time,
                        success=False,
                        error=str(e),
                    )
                    if isinstance(e, ApiError):
                        raise ElevenLabsError(f"API Error: {str(e)}") from e
                    raise ElevenLabsError(f"Synthesis failed: {str(e)}") from e
                
                await asyncio.sleep(1)
        
        raise ElevenLabsError("Synthesis failed after all retries")

    async def synthesize_stream(self, text: str) -> AsyncIterator[bytes]:
        """Synthesize text and stream audio bytes asynchronously."""
        if not self.config.enabled:
            raise ElevenLabsError("ElevenLabs service is disabled")

        start_time = time.time()
        for attempt in range(max(1, self.config.retry_count)):
            try:
                client = self._get_client()
                response_generator = client.text_to_speech.convert(
                    voice_id=self.config.voice_id,
                    output_format="mp3_44100_128",
                    text=text,
                    model_id=self.config.model,
                )
                
                async for chunk in response_generator:
                    yield chunk
                    
                execution_time = time.time() - start_time
                logger.info(
                    "elevenlabs_synthesize_stream_success",
                    provider="elevenlabs",
                    execution_time=execution_time,
                    success=True,
                )
                return  # Stream completed successfully
            except Exception as e:
                if attempt == max(1, self.config.retry_count) - 1:
                    execution_time = time.time() - start_time
                    logger.error(
                        "elevenlabs_synthesize_stream_failure",
                        provider="elevenlabs",
                        execution_time=execution_time,
                        success=False,
                        error=str(e),
                    )
                    if isinstance(e, ApiError):
                        raise ElevenLabsError(f"API Error: {str(e)}") from e
                    raise ElevenLabsError(f"Streaming failed: {str(e)}") from e
                
                await asyncio.sleep(1)
