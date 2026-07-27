import logging
from typing import List, Dict, Any
from pydantic import BaseModel
from app.domain.knowledge.models import ExecutionPlan, ExecutionStep

logger = logging.getLogger(__name__)

class HTNTask(BaseModel):
    """A node in the Hierarchical Task Network"""
    task_id: str
    name: str
    description: str
    is_primitive: bool
    sub_tasks: List['HTNTask'] = []
    required_role: str = "ORCHESTRATOR"
    dependencies: List[str] = [] # list of task_ids

class HTNPlanner:
    """
    Hierarchical Task Network Planner.
    Unlike the simple PlanningEngine which outputs linear steps, the HTN Planner
    decomposes complex goals (e.g. "Onboard Client") into a tree of sub-tasks,
    assigning them to specialized Agent Roles (e.g., RESEARCHER, SCHEDULER).
    """
    def decompose_goal(self, high_level_goal: str, context: Dict[str, Any]) -> HTNTask:
        logger.info(f"HTN Planner decomposing goal: {high_level_goal}")
        
        # In a real implementation, this would use an LLM or predefined domain templates to build the network.
        # Stub for "Onboard Client"
        if "onboard" in high_level_goal.lower():
            return HTNTask(
                task_id="root_1",
                name="Onboard New Client",
                description="End-to-end client onboarding workflow",
                is_primitive=False,
                sub_tasks=[
                    HTNTask(
                        task_id="task_1",
                        name="Research Client Company",
                        description="Query the CRM and Web to build a profile.",
                        is_primitive=True,
                        required_role="RESEARCHER"
                    ),
                    HTNTask(
                        task_id="task_2",
                        name="Schedule Kickoff Call",
                        description="Find a mutually agreeable time and send calendar invites.",
                        is_primitive=True,
                        required_role="SCHEDULER",
                        dependencies=["task_1"]
                    )
                ]
            )
            
        return HTNTask(
            task_id="default", 
            name=high_level_goal, 
            description=high_level_goal, 
            is_primitive=True
        )

    def flatten_to_execution_plan(self, htn_root: HTNTask) -> ExecutionPlan:
        """
        Converts the HTN into a flat execution plan for the GoalManager,
        respecting dependencies (topological sort).
        """
        steps = []
        # Simple DFS traversal for stub
        def traverse(node: HTNTask):
            if node.is_primitive:
                steps.append(ExecutionStep(
                    action=node.name,
                    parameters={"required_role": node.required_role, "description": node.description}
                ))
            for child in node.sub_tasks:
                traverse(child)
                
        traverse(htn_root)
        return ExecutionPlan(steps=steps)
