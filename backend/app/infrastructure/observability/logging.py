import logging
import json
from contextvars import ContextVar

# Context var for injecting correlation ID into all logs in the current async task
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="UNKNOWN")

class StructuredJsonFormatter(logging.Formatter):
    """
    Formats logs as JSON for production ingestion (e.g. ELK, Datadog)
    and automatically injects distributed tracing correlation IDs.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": correlation_id_ctx.get()
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def configure_structured_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredJsonFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    
    # Example usage: correlation_id_ctx.set(session_id)
