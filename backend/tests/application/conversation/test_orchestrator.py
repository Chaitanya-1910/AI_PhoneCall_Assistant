import pytest
import asyncio
from typing import AsyncGenerator

from app.domain.audio.models import AudioChunk, AudioResponse
from app.domain.conversation.prompt_builder import Prompt
from app.domain.conversation.ai_services import SpeechToTextService, LanguageModelService, TextToSpeechService
from app.domain.conversation.events import TranscriptReady, ConversationEnded
from app.domain.conversation.states import ConversationState
from app.application.conversation.orchestrator import ConversationOrchestrator

class MockSTT(SpeechToTextService):
    async def start_session(self, session_id: str) -> None: pass
    async def process_audio(self, audio_chunk: AudioChunk) -> None: pass
    async def finish_session(self, session_id: str) -> None: pass

class MockLLM(LanguageModelService):
    async def generate_response(self, prompt: Prompt) -> AsyncGenerator[str, None]:
        yield "Hello "
        yield "World"

class MockTTS(TextToSpeechService):
    async def synthesize(self, session_id: str, text: str) -> AsyncGenerator[AudioResponse, None]:
        yield AudioResponse(session_id=session_id, audio_data=b"mock", timestamp=0.0)

@pytest.fixture
def orchestrator():
    return ConversationOrchestrator(
        stt_service=MockSTT(),
        llm_service=MockLLM(),
        tts_service=MockTTS()
    )

@pytest.mark.asyncio
async def test_orchestrator_start_stop(orchestrator):
    session_id = "test_session_1"
    
    orchestrator.start_session(session_id)
    assert session_id in orchestrator._contexts
    
    context = orchestrator._contexts[session_id]
    assert context.state == ConversationState.WAITING_FOR_SPEECH
    
    await orchestrator.stop_session(session_id)
    
    # Wait for the event loop to process the ConversationEnded event and cleanup
    await asyncio.sleep(0.1)
    
    assert session_id not in orchestrator._contexts

@pytest.mark.asyncio
async def test_orchestrator_transcript_event_flow(orchestrator):
    session_id = "test_session_2"
    orchestrator.start_session(session_id)
    
    # Emit transcript
    await orchestrator.emit_event(TranscriptReady(session_id=session_id, transcript="Hi"))
    
    # Wait for processing
    await asyncio.sleep(0.1)
    
    # It should have transitioned to THINKING, generated response (SYNTHESIZING), simulated playback (SPEAKING), and then WAITING_FOR_REPLY
    # Let's see where it lands. The mock LLM yields text quickly.
    
    # Cleanup hasn't happened yet since we didn't end the conversation
    assert session_id in orchestrator._contexts
    
    context = orchestrator._contexts[session_id]
    assert context.state == ConversationState.WAITING_FOR_REPLY
    
    memory = orchestrator._working_memories[session_id]
    assert "Hi" in memory.recent_transcript
    assert "CHAYA: Hello World" in memory.recent_transcript

    # End
    await orchestrator.stop_session(session_id)
    await asyncio.sleep(0.1)
    assert session_id not in orchestrator._contexts
