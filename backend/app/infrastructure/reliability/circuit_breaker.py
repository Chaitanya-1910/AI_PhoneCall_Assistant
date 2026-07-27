import asyncio
import logging
import time
from typing import Callable, Any

logger = logging.getLogger(__name__)

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    Robust fault tolerance for AI Providers.
    Opens circuit after failure_threshold, preventing cascading failures.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout_sec: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_sec
        self.failures = 0
        self.last_failure_time = 0.0
        self.is_open = False
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.is_open:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info("Circuit breaker half-open. Attempting recovery...")
                self.is_open = False
            else:
                raise CircuitBreakerOpenException("Circuit breaker is open. Fast failing request.")
                
        try:
            result = await func(*args, **kwargs)
            self.failures = 0 # reset on success
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.is_open = True
                logger.error(f"Circuit breaker OPENED after {self.failures} failures.")
            raise e
