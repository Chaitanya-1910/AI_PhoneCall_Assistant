from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class CallerIntent(str, Enum):
    GENERAL_QUERY = "GENERAL_QUERY"
    CALLBACK_REQUEST = "CALLBACK_REQUEST"
    APPOINTMENT_REQUEST = "APPOINTMENT_REQUEST"
    INFORMATION_REQUEST = "INFORMATION_REQUEST"
    MESSAGE_FOR_USER = "MESSAGE_FOR_USER"
    URGENT_REQUEST = "URGENT_REQUEST"
    FOLLOW_UP = "FOLLOW_UP"
    UNKNOWN = "UNKNOWN"

class EntityType(str, Enum):
    PERSON = "PERSON"
    COMPANY = "COMPANY"
    ORGANIZATION = "ORGANIZATION"
    PHONE_NUMBER = "PHONE_NUMBER"
    EMAIL = "EMAIL"
    LOCATION = "LOCATION"
    DATE = "DATE"
    TIME = "TIME"
    APPOINTMENT = "APPOINTMENT"
    TASK = "TASK"
    URL = "URL"

class ExtractedEntity(BaseModel):
    entity_type: EntityType
    value: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ActionType(str, Enum):
    CREATE_TASK = "CREATE_TASK"
    CREATE_REMINDER = "CREATE_REMINDER"
    SCHEDULE_CALLBACK = "SCHEDULE_CALLBACK"
    STORE_MESSAGE = "STORE_MESSAGE"
    FLAG_URGENT = "FLAG_URGENT"
    NO_ACTION = "NO_ACTION"

class StructuredAction(BaseModel):
    action_type: ActionType
    payload: Dict[str, Any] = Field(default_factory=dict)

class ConversationOutcome(str, Enum):
    COMPLETED = "COMPLETED"
    MESSAGE_RECORDED = "MESSAGE_RECORDED"
    CALLBACK_REQUIRED = "CALLBACK_REQUIRED"
    APPOINTMENT_REQUESTED = "APPOINTMENT_REQUESTED"
    URGENT = "URGENT"
    NO_ACTION = "NO_ACTION"
    FAILED = "FAILED"

class CallUrgency(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ConversationSummary(BaseModel):
    session_id: str
    short_summary: str
    detailed_summary: str
    action_list: List[StructuredAction]
    callback_requirement: bool
    urgency_assessment: CallUrgency
    extracted_entities: List[ExtractedEntity]
