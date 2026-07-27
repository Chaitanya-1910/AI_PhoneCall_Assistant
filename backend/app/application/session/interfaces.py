from typing import Protocol, Optional
from pydantic import BaseModel

class SessionState(BaseModel):
    session_id: str
    worker_id: str
    caller_phone: str
    is_active: bool = True
    last_heartbeat: float

class SessionRegistry(Protocol):
    """
    Distributed registry for tracking active call sessions across workers (e.g. backed by Redis).
    """
    async def register_session(self, session: SessionState) -> None: ...
    async def get_session(self, session_id: str) -> Optional[SessionState]: ...
    async def remove_session(self, session_id: str) -> None: ...
    async def heartbeat(self, session_id: str, timestamp: float) -> None: ...

class SessionAllocator(Protocol):
    """
    Allocates an incoming call to an available worker.
    """
    async def allocate_worker(self) -> str: ...
