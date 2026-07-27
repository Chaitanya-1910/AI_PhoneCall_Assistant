"""Domain interfaces for AI services."""

from typing import AsyncIterator, Protocol


class SpeechToTextService(Protocol):
    """Protocol for Speech-to-Text translation (e.g., Whisper)."""

    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text synchronously."""
        ...


class LlmService(Protocol):
    """Protocol for Large Language Models (e.g., Gemini)."""

    async def generate_response(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a complete response string synchronously."""
        ...

    async def generate_response_stream(self, prompt: str, system_prompt: str | None = None) -> AsyncIterator[str]:
        """Generate response chunks asynchronously for streaming."""
        ...


class TextToSpeechService(Protocol):
    """Protocol for Text-to-Speech synthesis (e.g., ElevenLabs)."""

    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio bytes synchronously."""
        ...

    async def synthesize_stream(self, text: str) -> AsyncIterator[bytes]:
        """Synthesize text and stream audio bytes asynchronously."""
        ...
