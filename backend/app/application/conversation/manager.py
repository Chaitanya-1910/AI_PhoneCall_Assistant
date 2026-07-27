"""Conversation Intelligence Orchestrator."""

import time
import structlog
from dataclasses import dataclass

from app.domain.conversation.models import (
    CallerProfile,
    ConversationTurn,
    MemoryRecord,
)
from app.domain.conversation.state import ConversationState
from app.domain.conversation.interfaces import (
    ContextBuilder,
    IntentAnalyzer,
    MemoryManager,
    PromptManager,
    ResponseValidator,
    SummaryGenerator,
)
from app.domain.services.call_pipeline_service import CallPipelineService

logger = structlog.get_logger()

@dataclass
class ConversationResponse:
    conversation_id: str
    transcript: str
    response: str
    audio_bytes: bytes
    intent: str
    intent_confidence: float
    summary: str | None
    metrics: dict[str, int]


class ConversationManager:
    """High-level orchestrator for the Conversation Intelligence Engine."""

    def __init__(
        self,
        call_pipeline: CallPipelineService,
        memory_manager: MemoryManager,
        context_builder: ContextBuilder,
        prompt_manager: PromptManager,
        intent_analyzer: IntentAnalyzer,
        response_validator: ResponseValidator,
        summary_generator: SummaryGenerator,
    ) -> None:
        self.call_pipeline = call_pipeline
        self.memory_manager = memory_manager
        self.context_builder = context_builder
        self.prompt_manager = prompt_manager
        self.intent_analyzer = intent_analyzer
        self.response_validator = response_validator
        self.summary_generator = summary_generator

    async def start_session(self, conversation_id: str) -> None:
        """Create a new conversation session idempotently."""
        logger.info("session_started", conversation_id=conversation_id)
        await self.memory_manager.get_memory(conversation_id)
        
    async def end_session(self, conversation_id: str) -> None:
        """End and cleanup the conversation session."""
        logger.info("session_ended", conversation_id=conversation_id)
        # Memory cleanup could be implemented here if needed

    async def process_turn(
        self, audio_bytes: bytes, conversation_id: str, request_id: str, turn_id: str
    ) -> ConversationResponse:
        """Process a single conversation turn through the full state machine."""
        
        start_time_total = time.time()
        logger = structlog.get_logger().bind(
            conversation_id=conversation_id,
            request_id=request_id,
            turn_id=turn_id
        )
        
        metrics = {}
        state = ConversationState.LISTENING

        # 1. Transcribe (LISTENING)
        logger.info("conversation_state", state=state.value)
        transcript, stt_latency = await self.call_pipeline.transcribe(audio_bytes, request_id)
        metrics["stt_latency_ms"] = int(stt_latency * 1000)

        # 2. Intelligence & Context Building (THINKING)
        state = ConversationState.THINKING
        logger.info("conversation_state", state=state.value)
        
        memory = await self.memory_manager.get_memory(conversation_id)
        
        # Analyze Intent on the first turn
        intent_str = "UNKNOWN"
        intent_conf = 0.0
        if not memory.conversation_history:
            intent_req = self.intent_analyzer.prepare_request(transcript)
            intent_resp_text, _ = await self.call_pipeline.generateResponse(intent_req, request_id)
            intent_result = self.intent_analyzer.parse_result(intent_resp_text)
            intent_str = intent_result.intent
            intent_conf = intent_result.confidence
            logger.info("intent_detected", intent=intent_str, confidence=intent_conf)
        else:
            if memory.conversation_summary:
                intent_str = memory.conversation_summary.intent
                intent_conf = memory.conversation_summary.confidence

        context = self.context_builder.build_context(memory)
        prompt_resp = self.prompt_manager.build_prompt(context, transcript)

        # DIAGNOSTIC LOGGING
        print(f"\nPROMPT SENT TO GROQ:\n{prompt_resp.final_prompt}\n")
        logger.info("groq_prompt_debug", prompt=prompt_resp.final_prompt)

        # 3. Generate & Validate (RESPONDING)
        state = ConversationState.RESPONDING
        logger.info("conversation_state", state=state.value)
        
        raw_response, llm_latency = await self.call_pipeline.generateResponse(prompt_resp.final_prompt, request_id)
        validated = self.response_validator.validate(raw_response)
        final_text = validated.text
        metrics["llm_latency_ms"] = int(llm_latency * 1000)

        # 4. Synthesize Audio
        audio_out, tts_latency = await self.call_pipeline.synthesizeSpeech(final_text, request_id)
        metrics["tts_latency_ms"] = int(tts_latency * 1000)

        # 5. Summary & Storage (COMPLETED)
        state = ConversationState.COMPLETED
        logger.info("conversation_state", state=state.value)
        
        # Update memory
        turn = ConversationTurn(
            turn_id=turn_id,
            speaker="USER",
            transcript=transcript,
            response=final_text,
            latency_ms=int((time.time() - start_time_total) * 1000)
        )
        turn.ended_at = time.time()
        memory.conversation_history.append(turn)
        memory.memory_version += 1
        memory.updated_at = time.time()
        
        # Optionally generate summary asynchronously or synchronously
        summary_str = None
        if len(memory.conversation_history) > 0:
            sum_req = self.summary_generator.prepare_request(memory)
            sum_resp_text, _ = await self.call_pipeline.generateResponse(sum_req, request_id)
            sum_obj = self.summary_generator.parse_result(sum_resp_text)
            memory.conversation_summary = sum_obj
            summary_str = sum_obj.summary
            
        await self.memory_manager.save_memory(memory)
        metrics["total_latency_ms"] = int((time.time() - start_time_total) * 1000)

        return ConversationResponse(
            conversation_id=conversation_id,
            transcript=transcript,
            response=final_text,
            audio_bytes=audio_out,
            intent=intent_str,
            intent_confidence=intent_conf,
            summary=summary_str,
            metrics=metrics
        )
