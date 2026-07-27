import asyncio
import logging
from typing import Dict, Any
from app.domain.events.models import DomainEvent
from app.infrastructure.events.repository import EventRepository

logger = logging.getLogger(__name__)

class EventStore:
    """
    Core component that receives asynchronous write requests for Domain Events.
    Enforces append-only storage and dispatches to background tasks.
    """
    def __init__(self, repository: EventRepository):
        self.repository = repository
        # Simple queue for background persistence
        self._queue: asyncio.Queue[DomainEvent] = asyncio.Queue()
        self._worker_task = None
        
    def start(self):
        if not self._worker_task:
            self._worker_task = asyncio.create_task(self._persist_worker())
            
    async def stop(self):
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
                
    async def append(self, event: DomainEvent) -> None:
        """Asynchronously appends an event to the store without blocking the caller."""
        await self._queue.put(event)
        
    async def _persist_worker(self):
        """Background worker that continuously pulls events and saves them."""
        while True:
            try:
                event = await self._queue.get()
                await self.repository.append(event)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Failed to persist event to EventStore: {e}")
