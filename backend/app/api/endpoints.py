from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.domain.workflow.models import SagaWorkflow

router = APIRouter()

# Stub dependencies
def get_workflow_engine():
    pass

@router.post("/api/v1/agents/spawn", response_model=Dict[str, Any])
async def spawn_agent(role: str, task_description: str):
    """Admin API to manually spawn a sub-agent."""
    return {"status": "success", "agent_id": "agent_123", "role": role}

@router.get("/api/v1/workflows/active", response_model=List[SagaWorkflow])
async def get_active_workflows(engine = Depends(get_workflow_engine)):
    """Dashboard API to visualize active long-running Sagas."""
    return []

@router.post("/api/v1/tools/registry")
async def register_tool(tool_name: str, schema: Dict[str, Any]):
    """Admin API to dynamically add a new tool to the tenant's registry."""
    return {"status": "success", "tool_name": tool_name}
