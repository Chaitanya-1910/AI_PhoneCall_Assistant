from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class KnowledgeNodeType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    PHONE_NUMBER = "PHONE_NUMBER"
    EMAIL = "EMAIL"
    ADDRESS = "ADDRESS"
    APPOINTMENT = "APPOINTMENT"
    CALLBACK = "CALLBACK"
    TASK = "TASK"
    MEETING = "MEETING"
    DATE = "DATE"
    TIME = "TIME"
    LOCATION = "LOCATION"
    MESSAGE = "MESSAGE"

class KnowledgeRelationshipType(str, Enum):
    CALLED_BY = "CALLED_BY"
    REQUESTED = "REQUESTED"
    WORKS_FOR = "WORKS_FOR"
    HAS_PHONE = "HAS_PHONE"
    HAS_EMAIL = "HAS_EMAIL"
    LOCATED_AT = "LOCATED_AT"
    RELATED_TO = "RELATED_TO"
    SCHEDULED_FOR = "SCHEDULED_FOR"
    ASSIGNED_TO = "ASSIGNED_TO"
    FOLLOW_UP_FOR = "FOLLOW_UP_FOR"
    MENTIONED_DURING_CALL = "MENTIONED_DURING_CALL"

class KnowledgeNode(BaseModel):
    node_id: str
    node_type: KnowledgeNodeType
    value: str
    attributes: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeRelationship(BaseModel):
    source_id: str
    target_id: str
    relationship_type: KnowledgeRelationshipType
    attributes: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeGraph(BaseModel):
    nodes: Dict[str, KnowledgeNode] = Field(default_factory=dict)
    relationships: List[KnowledgeRelationship] = Field(default_factory=list)
    
class ValidatedKnowledgeGraph(BaseModel):
    graph: KnowledgeGraph

class ExecutionPriority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ExecutionDecision(str, Enum):
    COLLECT_PHONE_NUMBER = "COLLECT_PHONE_NUMBER"
    COLLECT_CALLBACK_TIME = "COLLECT_CALLBACK_TIME"
    COLLECT_MEETING_LOCATION = "COLLECT_MEETING_LOCATION"
    COLLECT_DATE = "COLLECT_DATE"
    COLLECT_RECIPIENT = "COLLECT_RECIPIENT"
    RESOLVE_CONFLICT = "RESOLVE_CONFLICT"
    PROCEED = "PROCEED"

class ExecutionStep(BaseModel):
    decision: ExecutionDecision
    priority: ExecutionPriority
    context: Dict[str, Any] = Field(default_factory=dict)

class ExecutionPlan(BaseModel):
    steps: List[ExecutionStep] = Field(default_factory=list)

class Goal(BaseModel):
    goal_id: str
    description: str
    is_completed: bool = False
    priority: ExecutionPriority = ExecutionPriority.MEDIUM
