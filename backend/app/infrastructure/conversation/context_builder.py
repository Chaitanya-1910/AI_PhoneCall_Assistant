"""Context Builder Implementation."""

from app.domain.conversation.interfaces import ContextBuilder
from app.domain.conversation.models import ConversationContext, MemoryRecord

class SimpleContextBuilder(ContextBuilder):
    """Builds ConversationContext from a MemoryRecord, respecting token limits."""

    def __init__(self, max_history_turns: int = 10) -> None:
        self.max_history_turns = max_history_turns

    def build_context(self, memory: MemoryRecord) -> ConversationContext:
        """Construct the context by extracting recent turns and caller profile."""
        
        caller_info = (
            f"Name: {memory.caller_profile.name}\n"
            f"Phone: {memory.caller_profile.phone}\n"
            f"Company: {memory.caller_profile.company}\n"
            f"Relationship: {memory.caller_profile.relationship}"
        )
        
        recent_turns = memory.conversation_history[-self.max_history_turns:]
        history_lines = []
        for turn in recent_turns:
            history_lines.append(f"User: {turn.transcript}")
            if turn.response:
                history_lines.append(f"AI: {turn.response}")
                
        history_text = "\n".join(history_lines)
        
        return ConversationContext(
            history_text=history_text,
            caller_info=caller_info,
            pending_actions=memory.important_notes or ""
        )
