from typing import Optional, Dict
from app.domain.repository.memory_repository import MemoryRepository
from app.domain.memory.models import PersistentMemory, CallerProfile

class InMemoryMemoryRepository(MemoryRepository):
    """
    In-memory implementation for testing before Postgres/Redis.
    """
    def __init__(self):
        self._memories: Dict[str, PersistentMemory] = {}
        
    async def get_memory_by_phone(self, phone_number: str) -> Optional[PersistentMemory]:
        for mem in self._memories.values():
            if phone_number in mem.caller_profile.phone_numbers:
                return mem
        return None
        
    async def save_memory(self, memory: PersistentMemory) -> None:
        self._memories[memory.caller_profile.caller_id] = memory
        
    async def get_profile(self, caller_id: str) -> Optional[CallerProfile]:
        mem = self._memories.get(caller_id)
        if mem:
            return mem.caller_profile
        return None
