import logging
import asyncio
from typing import Dict, Any
from app.domain.workflow.models import SagaWorkflow, WorkflowState, WorkflowStep
from app.application.integrations.manager import IntegrationManager
from app.domain.events.models import DomainEvent
from app.application.events.store import EventStore

logger = logging.getLogger(__name__)

class WorkflowEngine:
    """
    Executes Long-Running tasks (Sagas) asynchronously.
    In a real environment, this is powered by Celery or Temporal.
    """
    def __init__(self, integration_manager: IntegrationManager, event_store: EventStore):
        self.integrations = integration_manager
        self.event_store = event_store
        
    async def execute_saga(self, saga: SagaWorkflow):
        logger.info(f"Starting execution of Saga: {saga.name} ({saga.workflow_id})")
        saga.state = WorkflowState.RUNNING
        
        while True:
            next_step = saga.advance_state()
            if not next_step:
                break
                
            logger.info(f"Executing step {next_step.action_name}")
            try:
                # Dispatch to integration or tool
                success = await self.integrations.dispatch("system", next_step.action_name, saga.context_data)
                
                if success:
                    next_step.status = WorkflowState.COMPLETED
                else:
                    raise Exception(f"Action {next_step.action_name} failed.")
                    
            except Exception as e:
                logger.error(f"Saga {saga.workflow_id} failed at step {next_step.step_id}: {e}")
                next_step.status = WorkflowState.FAILED
                next_step.error_message = str(e)
                saga.state = WorkflowState.FAILED
                await self._compensate(saga)
                break
                
        # Emit Domain Event
        event = DomainEvent(
            conversation_id=saga.workflow_id,
            session_id=saga.workflow_id,
            aggregate_id=saga.workflow_id,
            event_type="WorkflowCompleted" if saga.state == WorkflowState.COMPLETED else "WorkflowFailed",
            payload=saga.model_dump()
        )
        await self.event_store.append(event)
        
    async def _compensate(self, saga: SagaWorkflow):
        """Rollback actions for previously completed steps."""
        logger.warning(f"Initiating compensation for Saga {saga.workflow_id}")
        saga.state = WorkflowState.COMPENSATING
        # In reality, we traverse steps in reverse and call their 'undo' action.
