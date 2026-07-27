from app.domain.conversation.confidence import ConversationConfidence
from app.domain.conversation.policy import PolicyAction

class ClarificationManager:
    """Determines if CHAYA needs to ask for clarification based on confidence metrics."""
    
    STT_THRESHOLD = 0.6
    INTENT_THRESHOLD = 0.5
    
    @classmethod
    def needs_clarification(cls, confidence: ConversationConfidence) -> bool:
        if confidence.stt_confidence < cls.STT_THRESHOLD:
            return True
        if confidence.intent_confidence < cls.INTENT_THRESHOLD:
            return True
        return False
