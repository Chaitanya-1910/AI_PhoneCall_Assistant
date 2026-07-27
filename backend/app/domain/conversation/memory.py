from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.domain.intelligence.models import (
    StructuredAction, ConversationSummary, CallUrgency, ConversationOutcome
)

class WorkingMemory(BaseModel):
    """Temporary memory holding context during an active call."""
    recent_transcript: List[str] = Field(default_factory=list)
    short_term_context: Dict[str, Any] = Field(default_factory=dict)
    
class ConversationFacts(BaseModel):
    """Extracted facts from the conversation."""
    facts: Dict[str, str] = Field(default_factory=dict)

class ConversationActions(BaseModel):
    """Actions generated during the conversation."""
    actions: List[StructuredAction] = Field(default_factory=list)

class LongTermMemory(BaseModel):
    """Persistent, append-only memory constructed via events."""
    session_id: str = ""
    facts: ConversationFacts = Field(default_factory=ConversationFacts)
    actions: ConversationActions = Field(default_factory=ConversationActions)
    urgency: CallUrgency = CallUrgency.LOW
    summary: Optional[ConversationSummary] = None
    outcome: ConversationOutcome = ConversationOutcome.COMPLETED
    historical_interactions: List[Dict[str, Any]] = Field(default_factory=list)
    
    def apply_fact_added(self, key: str, value: str):
        self.facts.facts[key] = value
        
    def apply_action_added(self, action: StructuredAction):
        self.actions.actions.append(action)
        
    def apply_priority_changed(self, urgency: CallUrgency):
        self.urgency = urgency
        
    def apply_summary_created(self, summary: ConversationSummary):
        self.summary = summary
