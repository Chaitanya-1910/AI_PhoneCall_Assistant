from typing import List
from app.domain.intelligence.models import CallerIntent
from app.domain.knowledge.models import ValidatedKnowledgeGraph, KnowledgeNodeType

class ConversationCompleteness:
    """
    Calculates a completion percentage based on the intent and knowledge graph.
    """
    
    @classmethod
    def calculate(cls, graph: ValidatedKnowledgeGraph, intent: CallerIntent) -> float:
        nodes = graph.graph.nodes.values()
        
        has_phone = any(n.node_type == KnowledgeNodeType.PHONE_NUMBER for n in nodes)
        has_date = any(n.node_type == KnowledgeNodeType.DATE for n in nodes)
        has_location = any(n.node_type == KnowledgeNodeType.LOCATION for n in nodes)
        
        if intent == CallerIntent.CALLBACK_REQUEST:
            # Requires just phone number for now (1 requirement)
            return 100.0 if has_phone else 0.0
            
        elif intent == CallerIntent.APPOINTMENT_REQUEST:
            # Requires Date and Location (2 requirements)
            score = 0.0
            if has_date: score += 50.0
            if has_location: score += 50.0
            return score
            
        # Defaults to 100% for intents with no strict requirements
        return 100.0
