import pytest
import asyncio
from typing import AsyncGenerator

from app.domain.audio.models import AudioSessionState, AudioChunk, AudioResponse
from app.domain.audio.repository import CallAudioRepository
from app.domain.services.call_audio_coordinator import CallAudioCoordinator

class FakeCallAudioRepository(CallAudioRepository):
    def __init__(self):
        self.started_sessions = set()
        self.played_responses = []

    async def start_audio_session(self, session_id: str) -> None:
        self.started_sessions.add(session_id)

    async def stop_audio_session(self, session_id: str) -> None:
        self.started_sessions.discard(session_id)

    async def receive_audio(self, session_id: str) -> AsyncGenerator[AudioChunk, None]:
        if session_id in self.started_sessions:
            yield AudioChunk(
                session_id=session_id,
                pcm_data=b"test",
                timestamp=1.0,
                sample_rate=8000,
                channels=1
            )

    async def play_audio(self, response: AudioResponse) -> None:
        self.played_responses.append(response)

    def is_audio_ready(self, session_id: str) -> bool:
        return session_id in self.started_sessions


@pytest.mark.asyncio
async def test_coordinator_lifecycle():
    repo = FakeCallAudioRepository()
    coordinator = CallAudioCoordinator(repository=repo)
    session_id = "test_session_1"

    assert coordinator.get_state(session_id) == AudioSessionState.IDLE

    await coordinator.start_session(session_id)
    assert coordinator.get_state(session_id) == AudioSessionState.LISTENING
    assert session_id in repo.started_sessions

    await coordinator.stop_session(session_id)
    assert coordinator.get_state(session_id) == AudioSessionState.STOPPED
    assert session_id not in repo.started_sessions


@pytest.mark.asyncio
async def test_coordinator_stream_inbound_audio():
    repo = FakeCallAudioRepository()
    coordinator = CallAudioCoordinator(repository=repo)
    session_id = "test_session_1"

    await coordinator.start_session(session_id)
    
    chunks = []
    async for chunk in coordinator.stream_inbound_audio(session_id):
        chunks.append(chunk)

    assert len(chunks) == 1
    assert chunks[0].pcm_data == b"test"


@pytest.mark.asyncio
async def test_coordinator_play_outbound_audio():
    repo = FakeCallAudioRepository()
    coordinator = CallAudioCoordinator(repository=repo)
    session_id = "test_session_1"

    await coordinator.start_session(session_id)
    response = AudioResponse(session_id=session_id, audio_data=b"outbound", timestamp=2.0)
    
    await coordinator.play_outbound_audio(response)

    assert len(repo.played_responses) == 1
    assert repo.played_responses[0].audio_data == b"outbound"
    assert coordinator.get_state(session_id) == AudioSessionState.LISTENING
