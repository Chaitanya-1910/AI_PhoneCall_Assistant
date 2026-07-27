from pydantic import BaseModel, Field
import time
import uuid
from typing import Dict, Any, Optional

class DomainEvent(BaseModel):
    """
    Immutable base class for all domain events stored in the Event Store.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    session_id: str
    correlation_id: Optional[str] = None
    
    timestamp: float = Field(default_factory=time.time)
    event_type: str = Field(default="")  # Usually set dynamically
    
    aggregate_id: str
    aggregate_version: int = 1
    
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source_component: str = "UNKNOWN"
    trace_id: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.event_type:
            self.event_type = self.__class__.__name__
