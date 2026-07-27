from enum import Enum
from pydantic import BaseModel, Field

class EmotionType(Enum):
    NEUTRAL = "NEUTRAL"
    FRUSTRATED = "FRUSTRATED"
    URGENT = "URGENT"
    HAPPY = "HAPPY"
    CONFUSED = "CONFUSED"

class SentimentScore(BaseModel):
    positive: float = 0.0
    neutral: float = 1.0
    negative: float = 0.0
    
class EmotionDetectionResult(BaseModel):
    primary_emotion: EmotionType = EmotionType.NEUTRAL
    sentiment: SentimentScore = Field(default_factory=SentimentScore)
    confidence: float = 1.0

class EmotionEngine:
    """
    Analyzes caller input for emotional state and sentiment.
    Can be powered by a lightweight local NLP model or the LLM itself.
    """
    async def analyze(self, transcript: str) -> EmotionDetectionResult:
        # Stub implementation. In production, this would call an NLP model or LLM.
        text = transcript.lower()
        if any(word in text for word in ["mad", "angry", "terrible", "hate", "waiting"]):
            return EmotionDetectionResult(
                primary_emotion=EmotionType.FRUSTRATED,
                sentiment=SentimentScore(negative=0.9, neutral=0.1),
                confidence=0.85
            )
        if any(word in text for word in ["urgent", "emergency", "now", "quick"]):
            return EmotionDetectionResult(
                primary_emotion=EmotionType.URGENT,
                sentiment=SentimentScore(negative=0.4, neutral=0.6),
                confidence=0.9
            )
        
        return EmotionDetectionResult()
