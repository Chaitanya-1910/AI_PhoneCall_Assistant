from typing import Any, Optional, List
import time
import uuid
from pydantic import BaseModel, Field
from app.domain.conversation.states import ConversationState
from app.domain.intelligence.models import (
    CallerIntent, ExtractedEntity, StructuredAction, CallUrgency, ConversationSummary
)

class ConversationEvent(BaseModel):
    session_id: str
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    segment_id: Optional[str] = None
    conversation_state: Optional[ConversationState] = None
    timestamp: float = Field(default_factory=time.time)
    
    @property
    def priority(self) -> int:
        return 50  # Default normal priority

class ErrorOccurred(ConversationEvent):
    error: str
    details: dict[str, Any] = Field(default_factory=dict)
    
    @property
    def priority(self) -> int:
        return 10

class ConversationEnded(ConversationEvent):
    @property
    def priority(self) -> int:
        return 10

class SpeechStarted(ConversationEvent):
    pass

class PotentialInterruptionDetected(ConversationEvent):
    pass

class SpeechSegmentCreated(ConversationEvent):
    pass

class SpeechEnded(ConversationEvent):
    pass

class TranscriptPartial(ConversationEvent):
    transcript: str

class TranscriptFinal(ConversationEvent):
    transcript: str

class LLMTokenGenerated(ConversationEvent):
    token: str

class LLMResponseCompleted(ConversationEvent):
    full_text: str

class SpeechChunkGenerated(ConversationEvent):
    audio_data: bytes

class SpeechCompleted(ConversationEvent):
    pass

class PlaybackCompleted(ConversationEvent):
    pass

class TimeoutOccurred(ConversationEvent):
    context: str

class BackchannelDetected(ConversationEvent):
    pass

class InterruptionDetected(ConversationEvent):
    pass

class ClarificationRequested(ConversationEvent):
    pass

class ResponsePaused(ConversationEvent):
    pass

class ResponseResumed(ConversationEvent):
    pass

class ConversationConfidenceUpdated(ConversationEvent):
    confidence_score: float

class TurnCompleted(ConversationEvent):
    pass

class MetricsUpdate(ConversationEvent):
    metric_name: str
    value: float
    
    @property
    def priority(self) -> int:
        return 90

class MemoryExtractionEvent(ConversationEvent):
    transcript_segment: str
    
    @property
    def priority(self) -> int:
        return 90

# Phase 7.4 Intelligence Events

class IntentDetected(ConversationEvent):
    intent: CallerIntent

class EntitiesExtracted(ConversationEvent):
    entities: List[ExtractedEntity]

class ActionCreated(ConversationEvent):
    action: StructuredAction

class SummaryGenerated(ConversationEvent):
    summary: ConversationSummary

class PriorityUpdated(ConversationEvent):
    urgency: CallUrgency

class ConversationCompleted(ConversationEvent):
    pass

# Phase 7.4 Memory Append Events

class FactAdded(ConversationEvent):
    key: str
    value: str

class ActionAdded(ConversationEvent):
    action: StructuredAction

class PriorityChanged(ConversationEvent):
    urgency: CallUrgency

class SummaryCreated(ConversationEvent):
    summary: ConversationSummary

# Phase 7.5 Knowledge & Reasoning Events
class KnowledgeGraphUpdated(ConversationEvent):
    pass

class ReasoningCompleted(ConversationEvent):
    pass

class PlanCreated(ConversationEvent):
    pass

class GoalCompleted(ConversationEvent):
    pass

class GoalCreated(ConversationEvent):
    pass

class ConversationComplete(ConversationEvent):
    pass

class ConversationIncomplete(ConversationEvent):
    pass

class FollowUpRequired(ConversationEvent):
    pass

# Phase 7.6 Memory & Personalization Events
class MemoryStored(ConversationEvent):
    pass

class MemoryUpdated(ConversationEvent):
    pass

class MemoryExpired(ConversationEvent):
    pass

class ProfileUpdated(ConversationEvent):
    pass

class PreferenceLearned(ConversationEvent):
    pass

class MemoryRetrieved(ConversationEvent):
    pass
