"""Analyzers and Validators Implementation."""

import json
from pathlib import Path
import structlog

from app.domain.conversation.interfaces import IntentAnalyzer, ResponseValidator, SummaryGenerator
from app.domain.conversation.models import ConversationSummary, IntentResult, MemoryRecord, ValidatedResponse

logger = structlog.get_logger()

class LlmIntentAnalyzer(IntentAnalyzer):
    """Analyzes intent using an LLM via the ConversationManager."""

    def __init__(self, prompts_dir: str = "app/prompts", threshold: float = 0.7) -> None:
        self.threshold = threshold
        filepath = Path(prompts_dir) / "intent.txt"
        self.prompt_template = filepath.read_text(encoding="utf-8").strip() if filepath.exists() else ""

    def prepare_request(self, user_input: str) -> str:
        return self.prompt_template.replace("{{transcript}}", user_input)

    def parse_result(self, llm_response: str) -> IntentResult:
        try:
            # Attempt to parse raw JSON out of the response
            # Some LLMs wrap in ```json ... ```
            cleaned = llm_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            return IntentResult(
                intent=data.get("intent", "UNKNOWN"),
                confidence=float(data.get("confidence", 0.0)),
                priority=data.get("priority", "MEDIUM")
            )
        except Exception as e:
            logger.warning("intent_parse_failed", error=str(e), response=llm_response)
            return IntentResult(intent="UNKNOWN", confidence=0.0, priority="LOW")


class LlmSummaryGenerator(SummaryGenerator):
    """Generates conversation summaries using an LLM via the ConversationManager."""

    def __init__(self, prompts_dir: str = "app/prompts") -> None:
        filepath = Path(prompts_dir) / "summary.txt"
        self.prompt_template = filepath.read_text(encoding="utf-8").strip() if filepath.exists() else ""

    def prepare_request(self, memory: MemoryRecord) -> str:
        history_lines = []
        for turn in memory.conversation_history:
            history_lines.append(f"User: {turn.transcript}")
            if turn.response:
                history_lines.append(f"AI: {turn.response}")
        history_text = "\n".join(history_lines)
        return self.prompt_template.replace("{{history}}", history_text)

    def parse_result(self, llm_response: str) -> ConversationSummary:
        try:
            cleaned = llm_response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            return ConversationSummary(
                caller=data.get("caller", "Unknown"),
                phone=data.get("phone", "Unknown"),
                intent=data.get("intent", "UNKNOWN"),
                priority=data.get("priority", "MEDIUM"),
                summary=data.get("summary", ""),
                action_required=data.get("action_required", ""),
                callback_required=bool(data.get("callback_required", False)),
                confidence=float(data.get("confidence", 0.0))
            )
        except Exception as e:
            logger.warning("summary_parse_failed", error=str(e), response=llm_response)
            return ConversationSummary(
                caller="Unknown", phone="Unknown", intent="UNKNOWN", priority="LOW",
                summary="Failed to generate summary.", action_required="", callback_required=False, confidence=0.0
            )


class ConfigurableResponseValidator(ResponseValidator):
    """Validates responses for length and formatting."""

    def __init__(self, max_length: int = 1000, fallback: str = "I'm sorry, could you repeat that?") -> None:
        self.max_length = max_length
        self.fallback = fallback

    def validate(self, response_text: str) -> ValidatedResponse:
        if not response_text or not response_text.strip():
            return ValidatedResponse(is_valid=False, text=self.fallback, reason="empty")
            
        if len(response_text) > self.max_length:
            # Instead of returning fallback, maybe truncate it or use fallback
            return ValidatedResponse(is_valid=False, text=self.fallback, reason="too_long")
            
        return ValidatedResponse(is_valid=True, text=response_text)
