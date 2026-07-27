from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import uuid
import time

class AgentRole(Enum):
    ORCHESTRATOR = "ORCHESTRATOR"
    RESEARCHER = "RESEARCHER"
    SCHEDULER = "SCHEDULER"
    ESCALATION = "ESCALATION"
    ANALYZER = "ANALYZER"

class AgentState(Enum):
    IDLE = "IDLE"
    WORKING = "WORKING"
    WAITING_ON_TOOL = "WAITING_ON_TOOL"
    WAITING_ON_HUMAN = "WAITING_ON_HUMAN"
    TERMINATED = "TERMINATED"

class AgentProfile(BaseModel):
    """
    Profile definition for a specialized sub-agent within the multi-agent framework.
    """
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    role: AgentRole
    system_prompt: str
    allowed_tools: List[str] = Field(default_factory=list)
    preferred_model: str = "gpt-4o" # or claude-3.5-sonnet, etc.
    
class CollaborationSession(BaseModel):
    """
    State tracking for a collaboration between multiple agents on a specific task.
    """
    collaboration_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    task_description: str
    primary_agent_id: str
    assigned_agent_ids: List[str] = Field(default_factory=list)
    shared_context: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    status: str = "IN_PROGRESS"
