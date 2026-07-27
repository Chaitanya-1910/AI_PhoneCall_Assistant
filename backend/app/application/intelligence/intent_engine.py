from typing import Protocol
from app.domain.intelligence.models import CallerIntent
import re

class IntentEngine(Protocol):
    async def extract_intent(self, transcript: str) -> CallerIntent:
        """Analyzes a transcript and returns the caller's intent."""
        ...

class RuleBasedIntentEngine(IntentEngine):
    async def extract_intent(self, transcript: str) -> CallerIntent:
        text = transcript.lower()
        if re.search(r"\b(call.*back|return.*call)\b", text):
            return CallerIntent.CALLBACK_REQUEST
        if re.search(r"\b(book|schedule|appointment)\b", text):
            return CallerIntent.APPOINTMENT_REQUEST
        if re.search(r"\b(message|tell him|tell her)\b", text):
            return CallerIntent.MESSAGE_FOR_USER
        if re.search(r"\b(urgent|emergency|asap)\b", text):
            return CallerIntent.URGENT_REQUEST
        if re.search(r"\b(how|what|where|who)\b", text):
            return CallerIntent.GENERAL_QUERY
        
        return CallerIntent.UNKNOWN
