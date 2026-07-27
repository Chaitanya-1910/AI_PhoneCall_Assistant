from typing import Optional
from app.domain.services.ai_interfaces import LargeLanguageModel
from app.domain.agent.models import AgentProfile

class AIProviderRouter:
    """
    Dynamically routes AI generation requests to the optimal LLM provider
    based on the Agent's profile, the complexity of the task, and cost/latency requirements.
    """
    def __init__(self, providers: dict[str, LargeLanguageModel]):
        # providers maps a model identifier (e.g., 'gpt-4o', 'llama-3-70b') to its implementation
        self.providers = providers
        self.default_model = "llama-3-70b" # Default to fast/cheap for simple turns
        
    def route_for_agent(self, agent: AgentProfile) -> LargeLanguageModel:
        """
        Selects the LLM based on the agent's preferred model.
        e.g., The 'RESEARCHER' agent might need 'gpt-4o' for complex tool use.
        """
        model_name = agent.preferred_model
        if model_name in self.providers:
            return self.providers[model_name]
            
        return self.providers.get(self.default_model)
        
    def route_for_task(self, complexity_score: float) -> LargeLanguageModel:
        """
        Selects the LLM dynamically based on task complexity (0.0 to 1.0).
        """
        if complexity_score > 0.8:
            return self.providers.get("gpt-4o")
        return self.providers.get(self.default_model)
