import asyncio
from typing import Callable, Dict, List, Awaitable
from app.domain.conversation.events import ConversationEvent
import logging

logger = logging.getLogger(__name__)

EventHandler = Callable[[ConversationEvent], Awaitable[None]]

class IntelligenceEventBus:
    """
    Event bus for the ConversationIntelligencePipeline.
    Decouples the real-time orchestrator from asynchronous intelligence processing.
    """
    def __init__(self):
        self._subscribers: Dict[type, List[EventHandler]] = {}
        # In a production system, this could be Kafka, RabbitMQ, or Redis PubSub.

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler {handler.__name__} to {event_type.__name__}")

    async def publish(self, event: ConversationEvent) -> None:
        event_type = type(event)
        handlers = self._subscribers.get(event_type, [])
        
        if handlers:
            # We fan out to all subscribers.
            # In a real system we might use asyncio.gather to run them concurrently.
            tasks = []
            for handler in handlers:
                tasks.append(asyncio.create_task(handler(event)))
            
            # Fire and forget (or await if we need strict ordering, but the prompt implies async decoupled)
            # We'll await here for simplicity in testing, but we can configure it to not block.
            await asyncio.gather(*tasks, return_exceptions=True)
