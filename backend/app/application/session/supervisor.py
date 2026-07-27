import time
import logging
from typing import Optional
from app.application.session.interfaces import SessionRegistry, SessionAllocator, SessionState

logger = logging.getLogger(__name__)

class SessionSupervisor:
    """
    Manages distributed call states, session recovery, and worker routing.
    Entrypoint for new telephony webhooks before they hit the Orchestrator.
    """
    def __init__(self, registry: SessionRegistry, allocator: SessionAllocator, local_worker_id: str):
        self.registry = registry
        self.allocator = allocator
        self.local_worker_id = local_worker_id
        
    async def handle_incoming_call(self, session_id: str, caller_phone: str) -> bool:
        """
        Called when a new call arrives. Decides if this worker should take it.
        Returns True if this local worker should handle it.
        """
        existing = await self.registry.get_session(session_id)
        if existing and existing.is_active:
            # Reconnection or migration
            logger.info(f"Session {session_id} already exists on worker {existing.worker_id}.")
            if existing.worker_id == self.local_worker_id:
                return True
            else:
                # In a real system, proxy the request to the correct worker, or steal it if dead.
                logger.warning(f"Routing logic needed to proxy to {existing.worker_id}")
                return False
                
        # Allocate
        assigned_worker = await self.allocator.allocate_worker()
        if assigned_worker == self.local_worker_id:
            state = SessionState(
                session_id=session_id,
                worker_id=self.local_worker_id,
                caller_phone=caller_phone,
                last_heartbeat=time.time()
            )
            await self.registry.register_session(state)
            logger.info(f"Session {session_id} allocated to this worker.")
            return True
            
        logger.info(f"Session {session_id} allocated to worker {assigned_worker}.")
        return False
        
    async def terminate_call(self, session_id: str) -> None:
        await self.registry.remove_session(session_id)
