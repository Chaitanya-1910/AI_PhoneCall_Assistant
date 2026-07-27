from typing import Protocol, Dict, Any, List

class IntegrationAdapter(Protocol):
    """
    Base protocol for enterprise integrations (Calendar, Slack, CRM).
    """
    async def execute_action(self, action_name: str, payload: Dict[str, Any]) -> bool:
        ...

class IntegrationManager:
    """
    Manages a registry of integration adapters available for a specific tenant.
    """
    def __init__(self):
        self.adapters: Dict[str, IntegrationAdapter] = {}
        
    def register(self, name: str, adapter: IntegrationAdapter):
        self.adapters[name] = adapter
        
    async def dispatch(self, integration_name: str, action_name: str, payload: Dict[str, Any]) -> bool:
        if integration_name not in self.adapters:
            raise ValueError(f"Integration {integration_name} not found.")
        return await self.adapters[integration_name].execute_action(action_name, payload)

class GoogleCalendarAdapter(IntegrationAdapter):
    async def execute_action(self, action_name: str, payload: Dict[str, Any]) -> bool:
        # Stub: Call Google Calendar API
        print(f"GoogleCalendarAdapter executing {action_name} with {payload}")
        return True

class SlackAdapter(IntegrationAdapter):
    async def execute_action(self, action_name: str, payload: Dict[str, Any]) -> bool:
        # Stub: Send Slack message
        print(f"SlackAdapter executing {action_name} with {payload}")
        return True
