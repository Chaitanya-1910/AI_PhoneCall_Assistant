"""Interfaces for Conversation Intelligence Modules."""

from typing import Protocol

from app.domain.conversation.models import (
    ConversationContext,
    ConversationSummary,
    IntentResult,
    MemoryRecord,
    PromptResponse,
    ValidatedResponse,
)

class MemoryStore(Protocol):
    async def save(self, record: MemoryRecord) -> None:
        ...

    async def load(self, conversation_id: str) -> MemoryRecord | None:
        ...

class MemoryManager(Protocol):
    async def get_memory(self, conversation_id: str) -> MemoryRecord:
        ...

    async def save_memory(self, record: MemoryRecord) -> None:
        ...

class ContextBuilder(Protocol):
    def build_context(self, memory: MemoryRecord) -> ConversationContext:
        ...

class PromptManager(Protocol):
    def build_prompt(self, context: ConversationContext, user_input: str) -> PromptResponse:
        ...

class IntentAnalyzer(Protocol):
    def prepare_request(self, user_input: str) -> str:
        ...

    def parse_result(self, llm_response: str) -> IntentResult:
        ...

class ResponseValidator(Protocol):
    def validate(self, response_text: str) -> ValidatedResponse:
        ...

class SummaryGenerator(Protocol):
    def prepare_request(self, memory: MemoryRecord) -> str:
        ...

    def parse_result(self, llm_response: str) -> ConversationSummary:
        ...
