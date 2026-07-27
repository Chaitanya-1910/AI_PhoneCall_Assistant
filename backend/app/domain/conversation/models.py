"""Domain models for Conversation Intelligence Engine."""

import time
from dataclasses import dataclass, field
from typing import Any

@dataclass
class CallerProfile:
    name: str = "Unknown"
    phone: str = "Unknown"
    company: str = "Unknown"
    relationship: str = "Unknown"

@dataclass
class ConversationTurn:
    turn_id: str
    speaker: str
    transcript: str
    response: str | None = None
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None
    latency_ms: int | None = None

@dataclass
class ConversationSummary:
    caller: str
    phone: str
    intent: str
    priority: str
    summary: str
    action_required: str
    callback_required: bool
    confidence: float

@dataclass
class IntentResult:
    intent: str
    confidence: float
    priority: str

@dataclass
class ValidatedResponse:
    is_valid: bool
    text: str
    reason: str | None = None

@dataclass
class PromptRequest:
    system_prompt: str
    context: str
    user_input: str

@dataclass
class PromptResponse:
    final_prompt: str

@dataclass
class MemoryRecord:
    conversation_id: str
    caller_profile: CallerProfile
    conversation_history: list[ConversationTurn] = field(default_factory=list)
    conversation_summary: ConversationSummary | None = None
    important_notes: str | None = None
    memory_version: int = 1
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class ConversationContext:
    history_text: str
    caller_info: str
    pending_actions: str

@dataclass
class Conversation:
    conversation_id: str
    request_id: str
    turn_id: str
