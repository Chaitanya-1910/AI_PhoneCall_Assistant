import asyncio
import logging
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field

from app.domain.conversation.events import (
    ConversationEvent, ErrorOccurred, ConversationEnded, 
    SpeechStarted, PotentialInterruptionDetected, SpeechEnded, 
    TranscriptPartial, TranscriptFinal,
    LLMTokenGenerated, LLMResponseCompleted, SpeechChunkGenerated, SpeechCompleted,
    PlaybackCompleted, TimeoutOccurred, MetricsUpdate, MemoryExtractionEvent
)
from app.domain.conversation.states import ConversationState
from app.domain.conversation.context import ConversationContext
from app.domain.conversation.memory import WorkingMemory, LongTermMemory
from app.domain.conversation.policy import ResponsePolicy, PolicyAction
from app.domain.conversation.prompt_builder import PromptBuilder
from app.domain.conversation.ai_services import SpeechToTextService, LanguageModelService, TextToSpeechService
from app.domain.conversation.cancellation import CancellationToken
from app.application.conversation.interruption_detector import InterruptionDetector
from app.application.conversation.turn_manager import TurnManager

logger = logging.getLogger(__name__)

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    event: ConversationEvent = field(compare=False)

class ConversationOrchestrator:
    def __init__(
        self,
        stt_service: SpeechToTextService,
        llm_service: LanguageModelService,
        tts_service: TextToSpeechService,
        intelligence_bus = None
    ):
        self.stt_service = stt_service
        self.llm_service = llm_service
        self.tts_service = tts_service
        self.intelligence_bus = intelligence_bus
        
        self._queues: Dict[str, asyncio.PriorityQueue] = {}
        self._contexts: Dict[str, ConversationContext] = {}
        self._working_memories: Dict[str, WorkingMemory] = {}
        self._long_term_memories: Dict[str, LongTermMemory] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._cancellation_tokens: Dict[str, CancellationToken] = {}
        
        # Track interruption timing
        self._last_speech_started_time: Dict[str, float] = {}

    def start_session(self, session_id: str, caller_info: dict = None) -> None:
        if session_id in self._tasks:
            return

        self._queues[session_id] = asyncio.PriorityQueue()
        self._contexts[session_id] = ConversationContext(session_id=session_id, caller_info=caller_info or {})
        self._working_memories[session_id] = WorkingMemory()
        self._long_term_memories[session_id] = LongTermMemory(session_id=session_id)
        self._last_speech_started_time[session_id] = 0.0
        
        self._tasks[session_id] = asyncio.create_task(self._event_loop(session_id))

    async def emit_event(self, event: ConversationEvent) -> None:
        queue = self._queues.get(event.session_id)
        if queue:
            await queue.put(PrioritizedItem(priority=event.priority, event=event))
            
        if self.intelligence_bus:
            await self.intelligence_bus.publish(event)

    async def stop_session(self, session_id: str) -> None:
        await self.emit_event(ConversationEnded(session_id=session_id))

    async def _event_loop(self, session_id: str) -> None:
        try:
            while True:
                queue = self._queues.get(session_id)
                if not queue:
                    break
                    
                item: PrioritizedItem = await queue.get()
                event = item.event
                await self._process_event(session_id, event)
                queue.task_done()
                
                if isinstance(event, ConversationEnded):
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(f"Fatal error in session {session_id} loop: {e}")
        finally:
            self._cleanup_session(session_id)

    async def _process_event(self, session_id: str, event: ConversationEvent) -> None:
        context = self._contexts[session_id]
        working_memory = self._working_memories[session_id]
        long_term_memory = self._long_term_memories[session_id]
        
        try:
            if isinstance(event, SpeechStarted):
                self._last_speech_started_time[session_id] = time.time()
                await self.emit_event(PotentialInterruptionDetected(session_id=session_id))

            elif isinstance(event, PotentialInterruptionDetected):
                if context.state in (ConversationState.SPEAKING, ConversationState.SYNTHESIZING, ConversationState.THINKING):
                    token = self._cancellation_tokens.get(session_id)
                    if token:
                        overlap = (time.time() - self._last_speech_started_time.get(session_id, time.time())) * 1000
                        decision = InterruptionDetector.evaluate("", overlap)
                        TurnManager.execute_decision(decision, token)

            elif isinstance(event, TranscriptPartial):
                token = self._cancellation_tokens.get(session_id)
                if token and context.state in (ConversationState.SPEAKING, ConversationState.SYNTHESIZING, ConversationState.THINKING):
                    overlap = (time.time() - self._last_speech_started_time.get(session_id, time.time())) * 1000
                    decision = InterruptionDetector.evaluate(event.transcript, overlap)
                    TurnManager.execute_decision(decision, token)
                    if token.is_cancelled:
                        self._contexts[session_id] = context.copy_with_state(ConversationState.LISTENING)

            elif isinstance(event, TranscriptFinal):
                new_context = context.copy_with_state(ConversationState.THINKING)
                self._contexts[session_id] = new_context
                
                working_memory.recent_transcript.append(event.transcript)
                action = ResponsePolicy.evaluate(new_context, working_memory, event.transcript)
                
                if action == PolicyAction.RESPOND:
                    prompt = PromptBuilder.build_prompt(
                        system_instructions="You are CHAYA.",
                        assistant_identity="CHAYA",
                        context=new_context,
                        memory=working_memory,
                        long_term_memory=long_term_memory,
                        latest_transcript=event.transcript
                    )
                    
                    cancellation_token = CancellationToken()
                    self._cancellation_tokens[session_id] = cancellation_token
                    asyncio.create_task(self._run_generation_pipeline(session_id, prompt, cancellation_token))
                
                elif action == PolicyAction.ASK_CLARIFICATION:
                    # Ask a standard clarification question
                    prompt = PromptBuilder.build_prompt(
                        system_instructions="You are CHAYA. Ask the user to clarify what they meant, as you did not understand.",
                        assistant_identity="CHAYA",
                        context=new_context,
                        memory=working_memory,
                        long_term_memory=long_term_memory,
                        latest_transcript="Please ask a clarification question."
                    )
                    cancellation_token = CancellationToken()
                    self._cancellation_tokens[session_id] = cancellation_token
                    asyncio.create_task(self._run_generation_pipeline(session_id, prompt, cancellation_token))

                elif action == PolicyAction.END_CALL:
                    await self.emit_event(ConversationEnded(session_id=session_id))

            elif isinstance(event, LLMResponseCompleted):
                working_memory.recent_transcript.append(f"CHAYA: {event.full_text}")

            elif isinstance(event, SpeechChunkGenerated):
                if context.state != ConversationState.SPEAKING:
                    self._contexts[session_id] = context.copy_with_state(ConversationState.SPEAKING)

            elif isinstance(event, PlaybackCompleted):
                self._contexts[session_id] = context.copy_with_state(ConversationState.WAITING_FOR_REPLY)

            elif isinstance(event, ErrorOccurred):
                self._contexts[session_id] = context.copy_with_state(ConversationState.ERROR)
                
            elif isinstance(event, ConversationEnded):
                new_context = context.copy_with_state(ConversationState.ENDING)
                self._contexts[session_id] = new_context
                token = self._cancellation_tokens.get(session_id)
                if token:
                    token.cancel()
                self._contexts[session_id] = new_context.copy_with_state(ConversationState.COMPLETED)
                
        except Exception as e:
            await self.emit_event(ErrorOccurred(session_id=session_id, error=str(e)))

    async def _run_generation_pipeline(self, session_id: str, prompt: Prompt, cancellation_token: CancellationToken):
        try:
            full_text = ""
            async for chunk in self.llm_service.generate_response(prompt, session_id, cancellation_token):
                if cancellation_token.is_cancelled:
                    return
                await cancellation_token.wait_if_paused()
                await self.emit_event(chunk)
                if isinstance(chunk, LLMResponseCompleted):
                    full_text = chunk.full_text

            if cancellation_token.is_cancelled or not full_text:
                return

            self._contexts[session_id] = self._contexts[session_id].copy_with_state(ConversationState.SYNTHESIZING)
            
            async for chunk in self.tts_service.synthesize(session_id, full_text, cancellation_token):
                if cancellation_token.is_cancelled:
                    return
                await cancellation_token.wait_if_paused()
                await self.emit_event(chunk)

        except Exception as e:
            await self.emit_event(ErrorOccurred(session_id=session_id, error=str(e)))

    def _cleanup_session(self, session_id: str) -> None:
        self._queues.pop(session_id, None)
        self._contexts.pop(session_id, None)
        self._working_memories.pop(session_id, None)
        self._long_term_memories.pop(session_id, None)
        self._tasks.pop(session_id, None)
        self._cancellation_tokens.pop(session_id, None)
        self._last_speech_started_time.pop(session_id, None)
