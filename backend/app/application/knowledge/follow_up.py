from app.domain.knowledge.models import Goal
from typing import List

class FollowUpManager:
    """
    Determines if CHAYA should continue asking questions or finish the conversation.
    """
    
    @classmethod
    def requires_follow_up(cls, pending_goals: List[Goal], completeness_score: float) -> bool:
        if pending_goals:
            return True
        if completeness_score < 100.0:
            return True
            
        return False
