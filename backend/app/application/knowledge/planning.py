from typing import List
from app.domain.knowledge.models import ExecutionPlan, ExecutionStep, ExecutionDecision, ExecutionPriority

class PlanningEngine:
    """
    Converts reasoning missing information into a deterministic ExecutionPlan.
    """
    
    @classmethod
    def create_plan(cls, missing_info: List[str]) -> ExecutionPlan:
        steps = []
        
        for missing in missing_info:
            if missing == "PHONE_NUMBER":
                steps.append(ExecutionStep(
                    decision=ExecutionDecision.COLLECT_PHONE_NUMBER,
                    priority=ExecutionPriority.HIGH,
                    context={"reason": "Callback request requires a phone number."}
                ))
            elif missing == "DATE":
                steps.append(ExecutionStep(
                    decision=ExecutionDecision.COLLECT_DATE,
                    priority=ExecutionPriority.HIGH,
                    context={"reason": "Appointment request requires a date."}
                ))
            elif missing == "LOCATION":
                steps.append(ExecutionStep(
                    decision=ExecutionDecision.COLLECT_MEETING_LOCATION,
                    priority=ExecutionPriority.MEDIUM,
                    context={"reason": "Appointment request requires a location."}
                ))
                
        if not steps:
            steps.append(ExecutionStep(
                decision=ExecutionDecision.PROCEED,
                priority=ExecutionPriority.LOW
            ))
            
        return ExecutionPlan(steps=steps)
