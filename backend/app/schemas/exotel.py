from pydantic import BaseModel, Field
from typing import Optional

class ExotelIncomingCall(BaseModel):
    CallSid: str
    From: str
    To: str
    Direction: Optional[str] = None
    CallType: Optional[str] = None
    DialWhomNumber: Optional[str] = None
    TimeCreated: Optional[str] = None

class ExotelRecording(BaseModel):
    CallSid: str
    From: str
    To: str
    RecordingUrl: str
    digits: Optional[str] = None

class ExotelStatus(BaseModel):
    CallSid: str
    From: str
    To: str
    Status: str
    CallDuration: Optional[str] = None
