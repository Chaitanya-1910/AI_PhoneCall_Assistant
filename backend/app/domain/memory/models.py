from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.domain.knowledge.models import KnowledgeGraph

class CallerProfile(BaseModel):
    caller_id: str
    name: Optional[str] = None
    phone_numbers: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    relationship: str = "NEW"
    preferred_language: str = "en"
    preferred_callback_time: Optional[str] = None
    communication_style: str = "NEUTRAL"
    previous_topics: List[str] = Field(default_factory=list)

class ConversationHistory(BaseModel):
    session_id: str
    timestamp: float
    summary: str
    outcome: str
    knowledge_graph: KnowledgeGraph

class MemorySnapshot(BaseModel):
    """Immutable snapshot of a point in time."""
    timestamp: float
    state_dump: str

class PersistentMemory(BaseModel):
    """The root long-term memory graph for a caller."""
    caller_profile: CallerProfile
    history: List[ConversationHistory] = Field(default_factory=list)
    pending_tasks: List[Dict[str, Any]] = Field(default_factory=list)
