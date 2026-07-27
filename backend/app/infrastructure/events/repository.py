from typing import Protocol, List, Optional
from app.domain.events.models import DomainEvent

class EventRepository(Protocol):
    """
    Append-only repository for storing domain events.
    """
    async def append(self, event: DomainEvent) -> None:
        ...
        
    async def get_events_by_session(self, session_id: str) -> List[DomainEvent]:
        ...
        
    async def get_events_by_aggregate(self, aggregate_id: str) -> List[DomainEvent]:
        ...

class InMemoryEventRepository(EventRepository):
    """
    In-memory implementation for testing before Postgres implementation.
    """
    def __init__(self):
        self._events: List[DomainEvent] = []
        
    async def append(self, event: DomainEvent) -> None:
        self._events.append(event)
        
    async def get_events_by_session(self, session_id: str) -> List[DomainEvent]:
        return [e for e in self._events if e.session_id == session_id]
        
    async def get_events_by_aggregate(self, aggregate_id: str) -> List[DomainEvent]:
        return [e for e in self._events if e.aggregate_id == aggregate_id]
