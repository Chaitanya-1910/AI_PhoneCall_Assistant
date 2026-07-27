from typing import Protocol, AsyncGenerator
from app.domain.audio.models import AudioResponse
from app.domain.audio.speech_segment import SpeechSegment
from app.domain.conversation.prompt_builder import Prompt
from app.domain.conversation.cancellation import CancellationToken
from app.domain.conversation.events import (
    TranscriptPartial, TranscriptFinal, 
    LLMTokenGenerated, LLMResponseCompleted,
    SpeechChunkGenerated, SpeechCompleted
)

class SpeechToTextService(Protocol):
    async def process_segment(self, segment: SpeechSegment) -> AsyncGenerator[TranscriptPartial | TranscriptFinal, None]:
        """Processes a speech segment and yields partial and final transcripts."""
        ...

class LanguageModelService(Protocol):
    async def generate_response(
        self, 
        prompt: Prompt, 
        session_id: str,
        cancellation_token: CancellationToken
    ) -> AsyncGenerator[LLMTokenGenerated | LLMResponseCompleted, None]:
        """Generates streaming tokens from a prompt."""
        ...

class TextToSpeechService(Protocol):
    async def synthesize(
        self, 
        session_id: str, 
        text: str,
        cancellation_token: CancellationToken
    ) -> AsyncGenerator[SpeechChunkGenerated | SpeechCompleted, None]:
        """Synthesizes text into streaming audio chunks."""
        ...
