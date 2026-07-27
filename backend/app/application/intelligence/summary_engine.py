from typing import Protocol
from app.domain.conversation.memory import LongTermMemory
from app.domain.intelligence.models import ConversationSummary

class SummaryEngine(Protocol):
    async def generate_summary(self, memory: LongTermMemory) -> ConversationSummary:
        """Generates a structured summary at the end of a call."""
        ...

class MockSummaryEngine(SummaryEngine):
    async def generate_summary(self, memory: LongTermMemory) -> ConversationSummary:
        """Simple mock to fulfill the pipeline without an LLM for now."""
        action_types = [a.action_type.value for a in memory.actions.actions]
        
        return ConversationSummary(
            session_id=memory.session_id,
            short_summary=f"Call completed with urgency {memory.urgency.value}.",
            detailed_summary=f"Extracted facts: {len(memory.facts.facts)}. Actions: {len(action_types)}.",
            action_list=memory.actions.actions,
            callback_requirement=any(a == "SCHEDULE_CALLBACK" for a in action_types),
            urgency_assessment=memory.urgency,
            extracted_entities=[]
        )
