from typing import AsyncGenerator
import logging

from app.domain.audio.models import AudioSessionState, AudioChunk, AudioResponse
from app.domain.audio.repository import CallAudioRepository

logger = logging.getLogger(__name__)

class CallAudioCoordinator:
    """
    Orchestrates the lifecycle of an active audio session, bridging
    the repository (e.g., Twilio Stream) with the AI engine components.
    """

    def __init__(self, repository: CallAudioRepository):
        self.repository = repository
        self._states: dict[str, AudioSessionState] = {}

    def get_state(self, session_id: str) -> AudioSessionState:
        return self._states.get(session_id, AudioSessionState.IDLE)

    async def start_session(self, session_id: str) -> None:
        if self.get_state(session_id) not in [AudioSessionState.IDLE, AudioSessionState.STOPPED]:
            logger.warning(f"Session {session_id} is already active.")
            return

        self._states[session_id] = AudioSessionState.INITIALIZING
        await self.repository.start_audio_session(session_id)
        self._states[session_id] = AudioSessionState.LISTENING
        logger.info(f"Started audio session {session_id}")

    async def stop_session(self, session_id: str) -> None:
        self._states[session_id] = AudioSessionState.STOPPED
        await self.repository.stop_audio_session(session_id)
        logger.info(f"Stopped audio session {session_id}")

    async def stream_inbound_audio(self, session_id: str) -> AsyncGenerator[AudioChunk, None]:
        """
        Exposes the inbound audio stream for VAD and STT (Whisper) to consume.
        """
        if self.get_state(session_id) != AudioSessionState.LISTENING:
            logger.warning(f"Session {session_id} is not in LISTENING state.")
        
        async for chunk in self.repository.receive_audio(session_id):
            # In future phases, VAD could be injected here before yielding
            yield chunk

    async def play_outbound_audio(self, response: AudioResponse) -> None:
        """
        Takes outbound audio (e.g., from ElevenLabs) and sends it to the repository.
        """
        current_state = self.get_state(response.session_id)
        # We might briefly transition to PLAYING here, or just let it rip
        self._states[response.session_id] = AudioSessionState.PLAYING
        
        await self.repository.play_audio(response)
        
        # Revert back to LISTENING if it hasn't been stopped
        if self.get_state(response.session_id) != AudioSessionState.STOPPED:
            self._states[response.session_id] = AudioSessionState.LISTENING
