from enum import Enum
from pydantic import BaseModel

class AudioSessionState(str, Enum):
    IDLE = "IDLE"
    INITIALIZING = "INITIALIZING"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    PLAYING = "PLAYING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"

class AudioChunk(BaseModel):
    session_id: str
    pcm_data: bytes
    timestamp: float
    sample_rate: int
    channels: int

class AudioResponse(BaseModel):
    session_id: str
    audio_data: bytes
    timestamp: float
