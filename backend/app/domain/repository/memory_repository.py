from typing import Protocol, Optional
from app.domain.memory.models import PersistentMemory, CallerProfile

class MemoryRepository(Protocol):
    async def get_memory_by_phone(self, phone_number: str) -> Optional[PersistentMemory]:
        ...
        
    async def save_memory(self, memory: PersistentMemory) -> None:
        ...
        
    async def get_profile(self, caller_id: str) -> Optional[CallerProfile]:
        ...
