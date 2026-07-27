"""In-memory implementation of MemoryStore."""

from app.domain.conversation.interfaces import MemoryStore
from app.domain.conversation.models import MemoryRecord


class InMemoryMemoryStore(MemoryStore):
    """Stores conversation history in a Python dictionary. For development only."""

    def __init__(self) -> None:
        self._store: dict[str, MemoryRecord] = {}

    async def save(self, record: MemoryRecord) -> None:
        """Save a MemoryRecord to the store."""
        self._store[record.conversation_id] = record

    async def load(self, conversation_id: str) -> MemoryRecord | None:
        """Load a MemoryRecord from the store."""
        return self._store.get(conversation_id)

class SimpleMemoryManager:
    """Manages memory using a MemoryStore."""

    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    async def get_memory(self, conversation_id: str) -> MemoryRecord:
        record = await self.store.load(conversation_id)
        if not record:
            from app.domain.conversation.models import CallerProfile
            record = MemoryRecord(
                conversation_id=conversation_id,
                caller_profile=CallerProfile()
            )
            await self.store.save(record)
        return record

    async def save_memory(self, record: MemoryRecord) -> None:
        await self.store.save(record)
