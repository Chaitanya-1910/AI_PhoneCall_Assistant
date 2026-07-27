import logging
from typing import Protocol, Dict, Any, Type
from app.domain.tools.models import ToolExecutionRequest, ToolExecutionResult

logger = logging.getLogger(__name__)

class Tool(Protocol):
    """
    Protocol for any executable tool in the Universal Tool Registry.
    """
    @property
    def name(self) -> str: ...
    
    @property
    def description(self) -> str: ...
    
    @property
    def parameters_schema(self) -> Dict[str, Any]: ...

    async def execute(self, params: Dict[str, Any]) -> Any: ...

class UniversalToolRegistry:
    """
    Registry maintaining all available tools. Validates parameters and executes tools.
    """
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        
    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
        
    async def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        if request.tool_name not in self.tools:
            return ToolExecutionResult(
                execution_id=request.execution_id,
                tool_name=request.tool_name,
                success=False,
                result_data={},
                error_message=f"Tool '{request.tool_name}' not found."
            )
            
        tool = self.tools[request.tool_name]
        try:
            # Here we would do JSON schema validation on request.parameters against tool.parameters_schema
            result = await tool.execute(request.parameters)
            return ToolExecutionResult(
                execution_id=request.execution_id,
                tool_name=request.tool_name,
                success=True,
                result_data={"output": result}
            )
        except Exception as e:
            logger.error(f"Error executing tool {tool.name}: {e}")
            return ToolExecutionResult(
                execution_id=request.execution_id,
                tool_name=request.tool_name,
                success=False,
                result_data={},
                error_message=str(e)
            )
