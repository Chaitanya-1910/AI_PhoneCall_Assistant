import logging
from typing import Dict, Callable, Awaitable, Any
from app.domain.agent.models import AgentProfile, CollaborationSession

logger = logging.getLogger(__name__)

class AgentCollaborationBus:
    """
    Message bus for inter-agent communication.
    Primary Orchestrator agents use this to delegate complex tasks to specialized Sub-Agents.
    """
    def __init__(self):
        # Maps agent_id -> async callback function
        self.subscribers: Dict[str, Callable[[CollaborationSession, Dict[str, Any]], Awaitable[None]]] = {}
        
    def register_agent(self, agent: AgentProfile, callback: Callable[[CollaborationSession, Dict[str, Any]], Awaitable[None]]):
        self.subscribers[agent.agent_id] = callback
        logger.info(f"Registered Agent {agent.name} ({agent.role}) to Collaboration Bus.")
        
    async def delegate_task(self, session: CollaborationSession, target_agent_id: str, payload: Dict[str, Any]) -> bool:
        if target_agent_id not in self.subscribers:
            logger.error(f"Cannot delegate to {target_agent_id} - Agent not registered.")
            return False
            
        logger.info(f"Delegating task to Agent {target_agent_id} for session {session.collaboration_id}")
        # In a distributed system, this would publish to Redis Pub/Sub
        await self.subscribers[target_agent_id](session, payload)
        return True
