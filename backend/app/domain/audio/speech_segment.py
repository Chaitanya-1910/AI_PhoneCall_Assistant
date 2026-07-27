from pydantic import BaseModel
from typing import Optional

class SpeechSegment(BaseModel):
    session_id: str
    segment_id: str
    audio_data: bytes
    start_timestamp: float
    end_timestamp: float
    sample_rate: int
    channels: int
