import pytest
import asyncio
from typing import AsyncGenerator

from app.domain.conversation.cancellation import CancellationToken
from app.domain.conversation.events import (
    SpeechStarted, TranscriptFinal, ConversationEnded, 
    LLMResponseCompleted, SpeechCompleted
)
from app.domain.conversation.states import ConversationState
from app.application.conversation.orchestrator import ConversationOrchestrator

# Mocks
class MockStreamingSTT:
    pass # In this test we inject events directly into the orchestrator queue

class MockStreamingLLM:
    async def generate_response(self, prompt, session_id, cancellation_token: CancellationToken):
        for i in range(5):
            if cancellation_token.is_cancelled:
                return
            await asyncio.sleep(0.01)
        if not cancellation_token.is_cancelled:
            yield LLMResponseCompleted(session_id=session_id, full_text="Hi")

class MockStreamingTTS:
    async def synthesize(self, session_id, text, cancellation_token: CancellationToken):
        for i in range(5):
            if cancellation_token.is_cancelled:
                return
            await asyncio.sleep(0.01)
        if not cancellation_token.is_cancelled:
            yield SpeechCompleted(session_id=session_id)


@pytest.fixture
def orchestrator():
    return ConversationOrchestrator(
        stt_service=MockStreamingSTT(),
        llm_service=MockStreamingLLM(),
        tts_service=MockStreamingTTS()
    )


@pytest.mark.asyncio
async def test_full_conversation_turn(orchestrator):
    session_id = "test_session"
    orchestrator.start_session(session_id)
    
    await orchestrator.emit_event(TranscriptFinal(session_id=session_id, transcript="Hello"))
    
    # Wait for processing and pipeline generation
    await asyncio.sleep(0.2)
    
    # After LLM and TTS tasks complete, state should end up as WAITING_FOR_REPLY
    context = orchestrator._contexts[session_id]
    assert context.state == ConversationState.WAITING_FOR_REPLY
    
    await orchestrator.stop_session(session_id)
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_barge_in_cancellation(orchestrator):
    session_id = "test_session_bargein"
    orchestrator.start_session(session_id)
    
    # Trigger a full turn which starts the LLM/TTS background task
    await orchestrator.emit_event(TranscriptFinal(session_id=session_id, transcript="Tell me a long story"))
    
    # Wait just a tiny bit so generation starts (context hits THINKING/SYNTHESIZING)
    await asyncio.sleep(0.02)
    
    # Verify we are in the middle of generation
    context = orchestrator._contexts[session_id]
    assert context.state in (ConversationState.THINKING, ConversationState.SYNTHESIZING, ConversationState.SPEAKING)
    
    # Now simulate the caller interrupting
    await orchestrator.emit_event(SpeechStarted(session_id=session_id))
    
    # Let the orchestrator process the barge-in
    await asyncio.sleep(0.05)
    
    # The generation task should be cancelled, and state should immediately revert to LISTENING
    context = orchestrator._contexts[session_id]
    assert context.state == ConversationState.LISTENING
    
    # Ensure the cancellation token was tripped
    token = orchestrator._cancellation_tokens.get(session_id)
    assert token.is_cancelled is True
    
    await orchestrator.stop_session(session_id)
    await asyncio.sleep(0.1)
