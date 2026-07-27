import pytest
import asyncio
from typing import AsyncGenerator

from app.domain.audio.models import AudioChunk, AudioResponse
from app.infrastructure.telephony.twilio_audio_source import TwilioAudioSource
from app.infrastructure.telephony.twilio_repository_impl import TwilioCallAudioRepositoryImpl

class FakeTwilioAudioSource(TwilioAudioSource):
    def __init__(self):
        super().__init__()
        self.written_audio = []

    async def stream_audio_in(self, session_id: str) -> AsyncGenerator[bytes, None]:
        if session_id in self._active_streams:
            yield b"pcm_data"
            yield b"more_pcm_data"

    async def write_audio_out(self, session_id: str, pcm_data: bytes) -> None:
        if session_id in self._active_streams:
            self.written_audio.append(pcm_data)

@pytest.mark.asyncio
async def test_twilio_repository_lifecycle():
    source = FakeTwilioAudioSource()
    repo = TwilioCallAudioRepositoryImpl(audio_source=source)
    session_id = "test_session_1"

    assert not repo.is_audio_ready(session_id)

    await repo.start_audio_session(session_id)
    assert repo.is_audio_ready(session_id)
    assert session_id in source._active_streams

    await repo.stop_audio_session(session_id)
    assert not repo.is_audio_ready(session_id)
    assert session_id not in source._active_streams

@pytest.mark.asyncio
async def test_twilio_repository_receive_audio():
    source = FakeTwilioAudioSource()
    repo = TwilioCallAudioRepositoryImpl(audio_source=source)
    session_id = "test_session_1"

    await repo.start_audio_session(session_id)

    chunks = []
    async for chunk in repo.receive_audio(session_id):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert chunks[0].pcm_data == b"pcm_data"
    assert chunks[1].pcm_data == b"more_pcm_data"
    assert chunks[0].sample_rate == 8000
    assert chunks[0].channels == 1

@pytest.mark.asyncio
async def test_twilio_repository_play_audio():
    source = FakeTwilioAudioSource()
    repo = TwilioCallAudioRepositoryImpl(audio_source=source)
    session_id = "test_session_1"

    await repo.start_audio_session(session_id)

    response = AudioResponse(session_id=session_id, audio_data=b"outbound_bytes", timestamp=1.0)
    await repo.play_audio(response)

    assert len(source.written_audio) == 1
    assert source.written_audio[0] == b"outbound_bytes"
