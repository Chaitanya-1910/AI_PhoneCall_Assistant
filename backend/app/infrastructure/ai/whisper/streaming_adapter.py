from typing import AsyncGenerator
import logging
from app.domain.conversation.ai_services import SpeechToTextService
from app.domain.audio.speech_segment import SpeechSegment
from app.domain.conversation.events import TranscriptPartial, TranscriptFinal
from app.infrastructure.ai.whisper.adapter import FasterWhisperAdapter

logger = logging.getLogger(__name__)

class StreamingWhisperAdapter(SpeechToTextService):
    """
    Thin wrapper over FasterWhisperAdapter to adapt it to the streaming protocol.
    Converts SpeechSegment into TranscriptPartial and TranscriptFinal events.
    """
    def __init__(self, whisper_adapter: FasterWhisperAdapter):
        self._adapter = whisper_adapter

    async def process_segment(self, segment: SpeechSegment) -> AsyncGenerator[TranscriptPartial | TranscriptFinal, None]:
        try:
            # FasterWhisper is currently synchronous/batch.
            # In the future, a streaming variant would yield TranscriptPartial here.
            
            transcript = await self._adapter.transcribe(segment.audio_data)
            
            if transcript and transcript.strip():
                yield TranscriptFinal(
                    session_id=segment.session_id,
                    segment_id=segment.segment_id,
                    transcript=transcript.strip()
                )
        except Exception as e:
            logger.error(f"Whisper transcription failed for segment {segment.segment_id}: {e}")
            raise
