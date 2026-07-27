from typing import Protocol, List
from app.domain.intelligence.models import CallerIntent, ExtractedEntity, StructuredAction, ActionType

class ActionEngine(Protocol):
    async def generate_actions(self, intent: CallerIntent, entities: List[ExtractedEntity]) -> List[StructuredAction]:
        """Converts intents and entities into concrete actions."""
        ...

class RuleBasedActionEngine(ActionEngine):
    async def generate_actions(self, intent: CallerIntent, entities: List[ExtractedEntity]) -> List[StructuredAction]:
        actions = []
        
        if intent == CallerIntent.CALLBACK_REQUEST:
            phone = next((e.value for e in entities if e.entity_type == "PHONE_NUMBER"), None)
            if phone:
                actions.append(StructuredAction(
                    action_type=ActionType.SCHEDULE_CALLBACK,
                    payload={"phone_number": phone}
                ))
            else:
                actions.append(StructuredAction(
                    action_type=ActionType.CREATE_TASK,
                    payload={"description": "Call the user back, phone number unknown."}
                ))
                
        if intent == CallerIntent.URGENT_REQUEST:
            actions.append(StructuredAction(
                action_type=ActionType.FLAG_URGENT,
                payload={"reason": "Urgent request detected."}
            ))
            
        if not actions:
            actions.append(StructuredAction(action_type=ActionType.NO_ACTION))
            
        return actions
