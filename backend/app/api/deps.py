"""Shared FastAPI dependencies."""

from collections.abc import AsyncGenerator

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.domain.services.ai_interfaces import LlmService, SpeechToTextService, TextToSpeechService
from app.domain.services.call_pipeline_service import CallPipelineService
from app.domain.services.health_service import HealthService
from app.domain.services.storage_interfaces import StorageService
from app.infrastructure.ai.elevenlabs.adapter import ElevenLabsAdapter
from app.infrastructure.ai.groq.adapter import GroqAdapter
from app.infrastructure.ai.whisper.adapter import FasterWhisperAdapter
from app.infrastructure.database.session import get_session
from app.infrastructure.storage.local.adapter import LocalStorageAdapter
from app.application.conversation.manager import ConversationManager
from app.infrastructure.conversation.memory_store import InMemoryMemoryStore, SimpleMemoryManager
from app.infrastructure.conversation.context_builder import SimpleContextBuilder
from app.infrastructure.conversation.prompt_loader import FilePromptManager
from app.infrastructure.conversation.analyzers import LlmIntentAnalyzer, ConfigurableResponseValidator, LlmSummaryGenerator
from app.application.telephony.exotel_service import ExotelService

# Global instances for in-memory stores and stateless analyzers
_memory_store = InMemoryMemoryStore()
_memory_manager = SimpleMemoryManager(_memory_store)
_context_builder = SimpleContextBuilder()
_prompt_manager = FilePromptManager()
_intent_analyzer = LlmIntentAnalyzer()
_response_validator = ConfigurableResponseValidator()
_summary_generator = LlmSummaryGenerator()


def get_app_settings() -> Settings:
    """Provide application settings."""
    return get_settings()


def get_health_service() -> HealthService:
    """Provide health service with current settings."""
    return HealthService(get_settings())


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session per request."""
    async for session in get_session():
        yield session


def get_speech_to_text_service() -> SpeechToTextService:
    """Provide the current Speech-to-Text service."""
    settings = get_settings()
    return FasterWhisperAdapter(config=settings.whisper)


def get_llm_service() -> LlmService:
    """Provide the current LLM service."""
    settings = get_settings()
    return GroqAdapter(config=settings.groq)


def get_text_to_speech_service() -> TextToSpeechService:
    """Provide the current Text-to-Speech service."""
    settings = get_settings()
    return ElevenLabsAdapter(config=settings.elevenlabs)


def get_storage_service() -> StorageService:
    """Provide the current StorageService."""
    settings = get_settings()
    return LocalStorageAdapter(config=settings.storage)


def get_call_pipeline_service(
    stt: SpeechToTextService = Depends(get_speech_to_text_service),
    llm: LlmService = Depends(get_llm_service),
    tts: TextToSpeechService = Depends(get_text_to_speech_service),
) -> CallPipelineService:
    """Provide the CallPipelineService orchestrator."""
    return CallPipelineService(
        stt_service=stt,
        llm_service=llm,
        tts_service=tts,
    )

def get_conversation_manager(
    pipeline: CallPipelineService = Depends(get_call_pipeline_service),
) -> ConversationManager:
    """Provide the ConversationManager orchestrator."""
    return ConversationManager(
        call_pipeline=pipeline,
        memory_manager=_memory_manager,
        context_builder=_context_builder,
        prompt_manager=_prompt_manager,
        intent_analyzer=_intent_analyzer,
        response_validator=_response_validator,
        summary_generator=_summary_generator,
    )

def get_exotel_service(
    settings: Settings = Depends(get_app_settings),
    pipeline: CallPipelineService = Depends(get_call_pipeline_service),
    storage: StorageService = Depends(get_storage_service),
    conversation: ConversationManager = Depends(get_conversation_manager)
) -> ExotelService:
    """Provide the ExotelService."""
    return ExotelService(
        settings=settings,
        pipeline=pipeline,
        storage=storage,
        conversation_manager=conversation
    )
