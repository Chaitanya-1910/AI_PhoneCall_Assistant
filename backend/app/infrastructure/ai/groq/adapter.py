"""Groq infrastructure adapter."""

import time
from typing import AsyncIterator

import structlog
from groq import AsyncGroq, APIError

from app.core.config import GroqConfig
from app.domain.services.ai_interfaces import LlmService
from app.infrastructure.ai.groq.exceptions import GroqError

logger = structlog.get_logger()


class GroqAdapter(LlmService):
    """Adapter for Groq using the official groq SDK."""

    def __init__(self, config: GroqConfig) -> None:
        self.config = config
        self._client: AsyncGroq | None = None

    def _get_client(self) -> AsyncGroq:
        if self._client is None:
            if not self.config.enabled:
                raise GroqError("Groq service is disabled")
            if not self.config.api_key:
                raise GroqError("Groq API key is missing")
            try:
                self._client = AsyncGroq(
                    api_key=self.config.api_key,
                    timeout=self.config.timeout,
                    max_retries=self.config.retry_count,
                )
            except Exception as e:
                raise GroqError(f"Failed to initialize client: {str(e)}") from e
        return self._client

    async def generate_response(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a complete response string asynchronously."""
        if not self.config.enabled:
            raise GroqError("Groq service is disabled")

        start_time = time.time()
        try:
            client = self._get_client()
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                messages=messages,
                model=self.config.model,
                stream=False,
            )
            
            execution_time = time.time() - start_time
            logger.info(
                "groq_generate_success",
                provider="groq",
                execution_time=execution_time,
                success=True,
            )
            return response.choices[0].message.content or ""
            
        except APIError as e:
            execution_time = time.time() - start_time
            logger.error(
                "groq_generate_failure",
                provider="groq",
                execution_time=execution_time,
                success=False,
                error=str(e),
            )
            raise GroqError(f"API Error: {str(e)}") from e
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "groq_generate_failure",
                provider="groq",
                execution_time=execution_time,
                success=False,
                error=str(e),
            )
            raise GroqError(f"Generation failed: {str(e)}") from e

    async def generate_response_stream(self, prompt: str, system_prompt: str | None = None) -> AsyncIterator[str]:
        """Generate response chunks asynchronously for streaming."""
        if not self.config.enabled:
            raise GroqError("Groq service is disabled")

        start_time = time.time()
        try:
            client = self._get_client()
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            stream = await client.chat.completions.create(
                messages=messages,
                model=self.config.model,
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
            execution_time = time.time() - start_time
            logger.info(
                "groq_generate_stream_success",
                provider="groq",
                execution_time=execution_time,
                success=True,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                "groq_generate_stream_failure",
                provider="groq",
                execution_time=execution_time,
                success=False,
                error=str(e),
            )
            raise GroqError(f"Streaming failed: {str(e)}") from e
