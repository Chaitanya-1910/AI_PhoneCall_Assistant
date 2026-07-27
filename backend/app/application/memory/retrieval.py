from typing import Optional
from app.domain.repository.memory_repository import MemoryRepository
from app.domain.memory.models import PersistentMemory, CallerProfile
import uuid

class MemoryRetrievalEngine:
    """
    Retrieves and provisions memory at the start of a call.
    """
    def __init__(self, repository: MemoryRepository):
        self.repository = repository
        
    async def retrieve_for_call(self, phone_number: str) -> PersistentMemory:
        memory = await self.repository.get_memory_by_phone(phone_number)
        
        if not memory:
            # Create a new blank profile for unknown callers
            caller_id = str(uuid.uuid4())
            profile = CallerProfile(
                caller_id=caller_id,
                phone_numbers=[phone_number]
            )
            memory = PersistentMemory(caller_profile=profile)
            
        return memory
