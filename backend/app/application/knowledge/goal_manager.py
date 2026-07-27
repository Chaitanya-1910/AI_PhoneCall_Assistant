import uuid
from typing import Dict, List
from app.domain.knowledge.models import Goal, ExecutionPlan, ExecutionPriority

class GoalManager:
    """
    Maintains active conversation goals based on execution plans.
    """
    def __init__(self):
        self._goals: Dict[str, Goal] = {}
        
    def apply_plan(self, plan: ExecutionPlan) -> None:
        """Adds goals based on the execution plan."""
        for step in plan.steps:
            if step.decision == "PROCEED":
                continue
                
            goal_desc = step.decision.value
            # Deduplicate active goals
            existing = [g for g in self._goals.values() if g.description == goal_desc and not g.is_completed]
            
            if not existing:
                goal_id = str(uuid.uuid4())
                self._goals[goal_id] = Goal(
                    goal_id=goal_id,
                    description=goal_desc,
                    priority=step.priority
                )

    def mark_completed(self, goal_id: str) -> None:
        if goal_id in self._goals:
            self._goals[goal_id].is_completed = True
            
    def get_pending_goals(self) -> List[Goal]:
        # Sort by priority descending
        pending = [g for g in self._goals.values() if not g.is_completed]
        pending.sort(key=lambda x: x.priority.value, reverse=True)
        return pending
