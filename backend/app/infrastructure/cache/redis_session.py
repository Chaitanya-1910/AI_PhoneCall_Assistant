import json
from typing import Optional, Dict
from app.application.session.interfaces import SessionRegistry, SessionAllocator, SessionState

class RedisSessionRegistry(SessionRegistry):
    """
    Redis-backed implementation of the session registry.
    """
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "chaya:session:"
        
    async def register_session(self, session: SessionState) -> None:
        # Assuming redis_client is an async redis connection (e.g. from redis.asyncio)
        await self.redis.set(
            f"{self.prefix}{session.session_id}",
            session.model_dump_json(),
            ex=3600 # 1 hour TTL to prevent leaked sessions
        )
        
    async def get_session(self, session_id: str) -> Optional[SessionState]:
        data = await self.redis.get(f"{self.prefix}{session_id}")
        if data:
            return SessionState.model_validate_json(data)
        return None
        
    async def remove_session(self, session_id: str) -> None:
        await self.redis.delete(f"{self.prefix}{session_id}")
        
    async def heartbeat(self, session_id: str, timestamp: float) -> None:
        session = await self.get_session(session_id)
        if session:
            session.last_heartbeat = timestamp
            await self.register_session(session) # Refresh TTL

class RoundRobinAllocator(SessionAllocator):
    """Simple allocator that just assigns to the current worker for now."""
    def __init__(self, local_worker_id: str):
        self.local_worker_id = local_worker_id
        
    async def allocate_worker(self) -> str:
        # In a real distributed setup, this would check Redis for active workers and load balance.
        return self.local_worker_id
