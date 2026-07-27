from app.application.intelligence.event_bus import IntelligenceEventBus
from app.domain.conversation.events import ConversationEvent
from app.domain.events.models import DomainEvent
from app.application.events.store import EventStore

class EventStoreSubscriber:
    """
    Subscribes to all events flowing through the IntelligenceEventBus and 
    dispatches them to the EventStore for background persistence.
    """
    def __init__(self, event_bus: IntelligenceEventBus, event_store: EventStore):
        self.bus = event_bus
        self.store = event_store
        
        # In a real system, we'd hook into a catch-all subscriber. 
        # For our simple bus, we subscribe to ConversationEvent base class or monkeypatch it.
        # We will simulate a global catch-all by overriding publish or registering for base types.
        
    async def handle_event(self, event: ConversationEvent) -> None:
        """Adapts a ConversationEvent into a DomainEvent and stores it."""
        domain_event = DomainEvent(
            conversation_id=event.session_id, # Assuming session_id maps to 1 conversation here
            session_id=event.session_id,
            correlation_id=event.correlation_id,
            timestamp=event.timestamp,
            event_type=event.__class__.__name__,
            aggregate_id=event.session_id, # Default aggregate is the conversation
            payload=event.model_dump()
        )
        await self.store.append(domain_event)
