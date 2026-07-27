from pydantic import BaseModel

class ConversationConfidence(BaseModel):
    stt_confidence: float = 1.0
    intent_confidence: float = 1.0
    response_confidence: float = 1.0
    interruption_confidence: float = 0.0
