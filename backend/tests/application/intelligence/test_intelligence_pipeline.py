import pytest
import asyncio
from app.application.intelligence.event_bus import IntelligenceEventBus
from app.application.intelligence.pipeline import ConversationIntelligencePipeline
from app.application.intelligence.intent_engine import RuleBasedIntentEngine
from app.application.intelligence.entity_extractor import RegexEntityExtractor
from app.application.intelligence.action_engine import RuleBasedActionEngine
from app.application.intelligence.priority_engine import HeuristicPriorityEngine
from app.application.intelligence.summary_engine import MockSummaryEngine
from app.domain.conversation.events import (
    TranscriptFinal, ConversationCompleted, IntentDetected, EntitiesExtracted,
    ActionCreated, PriorityUpdated, SummaryGenerated
)
from app.domain.conversation.memory import LongTermMemory
from app.domain.intelligence.models import CallerIntent, CallUrgency

@pytest.fixture
def intelligence_system():
    bus = IntelligenceEventBus()
    memories = {"session_1": LongTermMemory(session_id="session_1")}
    metrics = {}
    confidences = {}
    
    pipeline = ConversationIntelligencePipeline(
        event_bus=bus,
        intent_engine=RuleBasedIntentEngine(),
        entity_extractor=RegexEntityExtractor(),
        action_engine=RuleBasedActionEngine(),
        priority_engine=HeuristicPriorityEngine(),
        summary_engine=MockSummaryEngine(),
        memories=memories,
        metrics=metrics,
        confidences=confidences
    )
    
    return bus, pipeline, memories

@pytest.mark.asyncio
async def test_intelligence_pipeline_processing(intelligence_system):
    bus, pipeline, memories = intelligence_system
    
    # We will track events that get published to the bus
    received_events = []
    
    async def event_tracker(event):
        received_events.append(event)
        
    bus.subscribe(IntentDetected, event_tracker)
    bus.subscribe(EntitiesExtracted, event_tracker)
    bus.subscribe(ActionCreated, event_tracker)
    bus.subscribe(PriorityUpdated, event_tracker)
    bus.subscribe(SummaryGenerated, event_tracker)
    
    # 1. Simulate a transcript arriving
    await bus.publish(TranscriptFinal(
        session_id="session_1", 
        transcript="Please call me back at 555-0199 about this urgent issue."
    ))
    
    # Allow async tasks in pipeline to run
    await asyncio.sleep(0.1)
    
    # Verify Intent
    intents = [e for e in received_events if isinstance(e, IntentDetected)]
    assert len(intents) == 1
    assert intents[0].intent == CallerIntent.CALLBACK_REQUEST
    
    # Verify Entities
    entities = [e for e in received_events if isinstance(e, EntitiesExtracted)]
    assert len(entities) == 1
    assert len(entities[0].entities) == 1
    assert entities[0].entities[0].value == "555-0199"
    
    # Verify Action Created
    actions = [e for e in received_events if isinstance(e, ActionCreated)]
    assert len(actions) > 0
    assert any(a.action.action_type == "SCHEDULE_CALLBACK" for a in actions)
    
    # Verify Priority
    priorities = [e for e in received_events if isinstance(e, PriorityUpdated)]
    assert len(priorities) == 1
    # Because metrics.interruption_count is 0, heuristic priority should be MEDIUM for a callback
    assert priorities[0].urgency == CallUrgency.MEDIUM
    
    # Verify Memory was updated
    memory = memories["session_1"]
    assert memory.urgency == CallUrgency.MEDIUM
    assert len(memory.actions.actions) > 0
    
    # 2. Simulate conversation completion
    await bus.publish(ConversationCompleted(session_id="session_1"))
    
    await asyncio.sleep(0.1)
    
    # Verify Summary
    summaries = [e for e in received_events if isinstance(e, SummaryGenerated)]
    assert len(summaries) == 1
    assert summaries[0].summary.callback_requirement is True
    
    # Verify Memory has summary
    assert memory.summary is not None
