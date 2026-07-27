from typing import AsyncGenerator
from typing import Protocol

from .models import AudioChunk, AudioResponse

class CallAudioRepository(Protocol):
    """
    Interface for live call audio streaming.
    Implementations must bridge telephony-specific WebSockets/WebRTC (e.g., Twilio)
    into this pure domain representation.
    """

    async def start_audio_session(self, session_id: str) -> None:
        ...

    async def stop_audio_session(self, session_id: str) -> None:
        ...

    async def receive_audio(self, session_id: str) -> AsyncGenerator[AudioChunk, None]:
        ...

    async def play_audio(self, response: AudioResponse) -> None:
        ...

    def is_audio_ready(self, session_id: str) -> bool:
        ...
