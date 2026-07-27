import uuid
from typing import List, Dict
from app.domain.knowledge.models import KnowledgeGraph, KnowledgeNode, KnowledgeNodeType
from app.domain.intelligence.models import ExtractedEntity, StructuredAction

class KnowledgeGraphBuilder:
    """
    Incrementally builds and updates the Knowledge Graph from intelligence events.
    Never rebuilds from scratch.
    """
    
    @classmethod
    def update_graph(
        cls, 
        current_graph: KnowledgeGraph, 
        entities: List[ExtractedEntity], 
        actions: List[StructuredAction]
    ) -> KnowledgeGraph:
        
        # Simple entity mapping to knowledge nodes
        for entity in entities:
            # We map entity types to node types.
            # In a real system, we'd use robust deduplication here or in validator.
            node_id = str(uuid.uuid4())
            try:
                node_type = KnowledgeNodeType[entity.entity_type.name]
            except KeyError:
                node_type = KnowledgeNodeType.MESSAGE
                
            node = KnowledgeNode(
                node_id=node_id,
                node_type=node_type,
                value=entity.value,
                attributes=entity.metadata
            )
            
            # Very naive insertion, avoiding exact string duplicates for demo
            existing_values = {n.value: n.node_id for n in current_graph.nodes.values()}
            if node.value not in existing_values:
                current_graph.nodes[node_id] = node
                
        # Handle actions similarly if they introduce new knowledge
        # e.g., a SCHEDULE_CALLBACK action implies a CALLBACK node.
        
        return current_graph
