"""Prompt Loader Implementation."""

from pathlib import Path
from app.domain.conversation.interfaces import PromptManager
from app.domain.conversation.models import ConversationContext, PromptResponse

class FilePromptManager(PromptManager):
    """Loads prompt templates from the filesystem and injects context."""

    def __init__(self, prompts_dir: str = "app/prompts") -> None:
        self.prompts_dir = Path(prompts_dir)
        self.system = self._load("system.txt")
        self.personality = self._load("personality.txt")
        self.safety = self._load("safety.txt")

    def _load(self, filename: str) -> str:
        filepath = self.prompts_dir / filename
        if filepath.exists():
            return filepath.read_text(encoding="utf-8").strip()
        return ""

    def build_prompt(self, context: ConversationContext, user_input: str) -> PromptResponse:
        """Combine templates and dynamic context into a single prompt."""
        parts = []
        
        if self.system:
            parts.append(self.system)
        if self.personality:
            parts.append(self.personality)
        if self.safety:
            parts.append(self.safety)
            
        parts.append(f"Caller Info:\n{context.caller_info}")
        
        if context.pending_actions:
            parts.append(f"Pending Actions:\n{context.pending_actions}")
            
        if context.history_text:
            parts.append(f"Conversation History:\n{context.history_text}")
            
        parts.append(f"User Input:\n{user_input}")
        
        final_prompt = "\n\n".join(parts)
        return PromptResponse(final_prompt=final_prompt)
