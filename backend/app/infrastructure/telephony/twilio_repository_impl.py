import time
from typing import AsyncGenerator
import logging

from app.domain.audio.models import AudioChunk, AudioResponse
from app.domain.audio.repository import CallAudioRepository
from app.infrastructure.telephony.twilio_audio_source import TwilioAudioSource

logger = logging.getLogger(__name__)

class TwilioCallAudioRepositoryImpl(CallAudioRepository):
    """
    Implements the pure CallAudioRepository interface using the TwilioAudioSource.
    Transforms raw bytes from the source into domain-friendly AudioChunk objects.
    """

    def __init__(self, audio_source: TwilioAudioSource):
        self.source = audio_source
        self._ready_sessions: set[str] = set()

    async def start_audio_session(self, session_id: str) -> None:
        await self.source.connect_stream(session_id)
        self._ready_sessions.add(session_id)
        logger.info(f"Started Twilio audio session for {session_id}")

    async def stop_audio_session(self, session_id: str) -> None:
        await self.source.disconnect_stream(session_id)
        self._ready_sessions.discard(session_id)
        logger.info(f"Stopped Twilio audio session for {session_id}")

    async def receive_audio(self, session_id: str) -> AsyncGenerator[AudioChunk, None]:
        if not self.is_audio_ready(session_id):
            logger.error(f"Cannot receive audio, session {session_id} not ready.")
            return

        # Read raw PCM from the source and wrap in AudioChunk
        async for raw_pcm in self.source.stream_audio_in(session_id):
            yield AudioChunk(
                session_id=session_id,
                pcm_data=raw_pcm,
                timestamp=time.time(),
                sample_rate=8000,  # Twilio standard
                channels=1         # Twilio standard mono
            )

    async def play_audio(self, response: AudioResponse) -> None:
        if not self.is_audio_ready(response.session_id):
            logger.error(f"Cannot play audio, session {response.session_id} not ready.")
            return
            
        await self.source.write_audio_out(response.session_id, response.audio_data)

    def is_audio_ready(self, session_id: str) -> bool:
        return session_id in self._ready_sessions
