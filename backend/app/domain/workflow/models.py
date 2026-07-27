from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import uuid
import time

class WorkflowState(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUSPENDED = "SUSPENDED"  # Waiting for human input or external webhook
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATING = "COMPENSATING" # Saga rollback

class WorkflowStep(BaseModel):
    step_id: str
    action_name: str
    status: WorkflowState = WorkflowState.PENDING
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
class SagaWorkflow(BaseModel):
    """
    Represents a long-running distributed transaction / workflow using the Saga pattern.
    """
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    state: WorkflowState = WorkflowState.PENDING
    steps: List[WorkflowStep] = Field(default_factory=list)
    context_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    
    def advance_state(self) -> Optional[WorkflowStep]:
        """Find the next pending step to execute."""
        for step in self.steps:
            if step.status == WorkflowState.PENDING:
                return step
        self.state = WorkflowState.COMPLETED
        return None
