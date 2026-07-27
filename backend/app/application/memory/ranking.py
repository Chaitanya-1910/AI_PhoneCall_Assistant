from typing import List
from app.domain.memory.models import ConversationHistory

class MemoryRanking:
    """
    Ranks retrieved conversation histories by relevance and recency.
    """
    
    @classmethod
    def rank_histories(cls, histories: List[ConversationHistory]) -> List[ConversationHistory]:
        # For now, simply sort by timestamp descending (most recent first)
        # Future enhancement: sort by semantic relevance or outcome priority
        return sorted(histories, key=lambda h: h.timestamp, reverse=True)
