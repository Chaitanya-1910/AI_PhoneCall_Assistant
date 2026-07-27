from typing import Protocol, List
from app.domain.intelligence.models import CallerIntent, ExtractedEntity, CallUrgency
from app.domain.conversation.confidence import ConversationConfidence
from app.domain.conversation.metrics import ConversationMetrics

class PriorityEngine(Protocol):
    async def calculate_urgency(
        self, 
        intent: CallerIntent, 
        entities: List[ExtractedEntity],
        metrics: ConversationMetrics,
        confidence: ConversationConfidence
    ) -> CallUrgency:
        """Calculates urgency based on available intelligence."""
        ...

class HeuristicPriorityEngine(PriorityEngine):
    async def calculate_urgency(
        self, 
        intent: CallerIntent, 
        entities: List[ExtractedEntity],
        metrics: ConversationMetrics,
        confidence: ConversationConfidence
    ) -> CallUrgency:
        
        if intent == CallerIntent.URGENT_REQUEST:
            return CallUrgency.CRITICAL
            
        if intent in (CallerIntent.CALLBACK_REQUEST, CallerIntent.APPOINTMENT_REQUEST):
            if metrics.interruption_count > 3:
                # High caller agitation
                return CallUrgency.HIGH
            return CallUrgency.MEDIUM
            
        return CallUrgency.LOW
