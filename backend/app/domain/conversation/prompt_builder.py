from pydantic import BaseModel, Field
from typing import List

class Prompt(BaseModel):
    system_instructions: str
    assistant_identity: str
    conversation_context: str
    caller_profile: str
    transcript_history: List[str]
    latest_transcript: str
    conversation_goals: str
    safety_constraints: str

class PromptBuilder:
    @staticmethod
    def build_prompt(
        system_instructions: str,
        assistant_identity: str,
        context: "ConversationContext",
        memory: "WorkingMemory",
        long_term_memory: "LongTermMemory",
        latest_transcript: str
    ) -> Prompt:
        return Prompt(
            system_instructions=system_instructions,
            assistant_identity=assistant_identity,
            conversation_context=f"Status: {context.conversation_status}, Urgency: {context.urgency_level}",
            caller_profile=str(context.caller_info),
            transcript_history=memory.recent_transcript,
            latest_transcript=latest_transcript,
            conversation_goals=f"Topic: {memory.current_topic}. Pending Qs: {memory.pending_questions}",
            safety_constraints="Do not provide legal or medical advice."
        )
