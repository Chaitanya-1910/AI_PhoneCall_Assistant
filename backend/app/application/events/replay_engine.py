from typing import List, Optional
from app.infrastructure.events.repository import EventRepository
from app.domain.events.models import DomainEvent

class EventReplayEngine:
    """
    Engine capable of reconstructing state by replaying events from the Event Store.
    """
    def __init__(self, repository: EventRepository):
        self.repository = repository
        
    async def get_conversation_history(self, session_id: str) -> List[DomainEvent]:
        """Returns the chronological sequence of events for a given session."""
        events = await self.repository.get_events_by_session(session_id)
        # Ensure ordered by timestamp
        return sorted(events, key=lambda e: e.timestamp)
        
    async def reconstruct_aggregate(self, aggregate_id: str, up_to_timestamp: Optional[float] = None) -> List[DomainEvent]:
        """
        Replays events for a specific aggregate (e.g. Goal, Memory) to reconstruct its state,
        optionally stopping at a specific point in time.
        """
        events = await self.repository.get_events_by_aggregate(aggregate_id)
        events = sorted(events, key=lambda e: e.aggregate_version)
        
        if up_to_timestamp is not None:
            events = [e for e in events if e.timestamp <= up_to_timestamp]
            
        return events
