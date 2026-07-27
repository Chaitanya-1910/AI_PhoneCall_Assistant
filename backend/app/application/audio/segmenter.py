import uuid
import time
from typing import AsyncGenerator
from app.domain.audio.models import AudioChunk
from app.domain.audio.speech_segment import SpeechSegment
import logging

logger = logging.getLogger(__name__)

class SpeechSegmenter:
    """
    Responsible for receiving raw AudioChunks and grouping them into logical SpeechSegments.
    This implementation uses a simple chunk counter to simulate silence/VAD detection.
    Future implementations can drop in WebRTC or Silero VAD without changing the signature.
    """
    def __init__(self, silence_threshold_chunks: int = 50):
        self.silence_threshold_chunks = silence_threshold_chunks
        self._current_buffer = b""
        self._current_segment_id = None
        self._start_timestamp = 0.0

    async def process_audio_stream(self, session_id: str, audio_stream: AsyncGenerator[AudioChunk, None]) -> AsyncGenerator[SpeechSegment, None]:
        """
        Consumes an AudioChunk stream and yields completed SpeechSegments.
        """
        chunk_count = 0
        
        async for chunk in audio_stream:
            if not self._current_buffer:
                self._current_segment_id = str(uuid.uuid4())
                self._start_timestamp = chunk.timestamp
                
            self._current_buffer += chunk.pcm_data
            chunk_count += 1
            
            # Simulate silence detection: if we've accumulated enough chunks, we consider the speech ended
            if chunk_count >= self.silence_threshold_chunks:
                segment = SpeechSegment(
                    session_id=session_id,
                    segment_id=self._current_segment_id,
                    audio_data=self._current_buffer,
                    start_timestamp=self._start_timestamp,
                    end_timestamp=chunk.timestamp,
                    sample_rate=chunk.sample_rate,
                    channels=chunk.channels
                )
                yield segment
                
                # Reset buffer for the next speech segment
                self._current_buffer = b""
                chunk_count = 0
                self._current_segment_id = None
