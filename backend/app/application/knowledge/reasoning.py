from typing import List
from app.domain.knowledge.models import ValidatedKnowledgeGraph, KnowledgeNodeType
from app.domain.intelligence.models import CallerIntent

class ReasoningEngine:
    """
    Infers missing information and detects contradictions from the validated graph.
    Returns structured models indicating what is missing.
    """
    
    @classmethod
    def infer_missing_information(
        cls, 
        validated_graph: ValidatedKnowledgeGraph, 
        intent: CallerIntent
    ) -> List[str]:
        """Returns a list of missing required fields based on the intent."""
        
        nodes = validated_graph.graph.nodes.values()
        missing = []
        
        has_phone = any(n.node_type == KnowledgeNodeType.PHONE_NUMBER for n in nodes)
        has_date = any(n.node_type == KnowledgeNodeType.DATE for n in nodes)
        has_location = any(n.node_type == KnowledgeNodeType.LOCATION for n in nodes)
        
        if intent == CallerIntent.CALLBACK_REQUEST:
            if not has_phone:
                missing.append("PHONE_NUMBER")
                
        elif intent == CallerIntent.APPOINTMENT_REQUEST:
            if not has_date:
                missing.append("DATE")
            if not has_location:
                missing.append("LOCATION")
                
        return missing
