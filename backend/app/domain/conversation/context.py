from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from app.domain.conversation.states import ConversationState

class ConversationContext(BaseModel):
    session_id: str
    caller_info: Dict[str, Any] = Field(default_factory=dict)
    conversation_status: str = "ACTIVE"
    urgency_level: str = "NORMAL"
    callback_requested: bool = False
    state: ConversationState = ConversationState.WAITING_FOR_SPEECH

    def copy_with_state(self, new_state: ConversationState) -> "ConversationContext":
        """Returns a new context instance with the updated state."""
        return self.model_copy(update={"state": new_state})
