from app.domain.memory.models import PersistentMemory
import time

class PrivacyManager:
    """
    Enforces retention policies, masks sensitive data, and manages expirations.
    """
    RETENTION_SECONDS = 365 * 24 * 60 * 60  # 1 Year
    
    @classmethod
    def enforce_retention(cls, memory: PersistentMemory) -> PersistentMemory:
        current_time = time.time()
        # Keep histories that are newer than RETENTION_SECONDS
        memory.history = [
            h for h in memory.history 
            if (current_time - h.timestamp) < cls.RETENTION_SECONDS
        ]
        return memory
        
    @classmethod
    def mask_sensitive_data(cls, memory: PersistentMemory) -> PersistentMemory:
        # PII Masking logic goes here (e.g. removing credit card numbers from transcripts)
        return memory
