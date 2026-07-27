import pytest
import asyncio
from app.application.intelligence.event_bus import IntelligenceEventBus
from app.application.intelligence.pipeline import ConversationIntelligencePipeline
from app.application.intelligence.intent_engine import RuleBasedIntentEngine
from app.application.intelligence.entity_extractor import RegexEntityExtractor
from app.application.intelligence.action_engine import RuleBasedActionEngine
from app.application.intelligence.priority_engine import HeuristicPriorityEngine
from app.application.intelligence.summary_engine import MockSummaryEngine
from app.application.memory.retrieval import MemoryRetrievalEngine
from app.infrastructure.persistence.in_memory_memory_repository import InMemoryMemoryRepository
from app.domain.conversation.events import (
    TranscriptFinal, ConversationCompleted, FollowUpRequired,
    MemoryStored, GoalCreated, PlanCreated, KnowledgeGraphUpdated, ConversationIncomplete
)
from app.domain.conversation.memory import LongTermMemory

@pytest.fixture
def memory_repo():
    return InMemoryMemoryRepository()

@pytest.fixture
def intelligence_system(memory_repo):
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
        memory_retrieval_engine=MemoryRetrievalEngine(memory_repo),
        memories=memories,
        metrics=metrics,
        confidences=confidences
    )
    
    return bus, pipeline, memories, memory_repo

@pytest.mark.asyncio
async def test_knowledge_and_memory_pipeline(intelligence_system):
    bus, pipeline, memories, repo = intelligence_system
    
    received_events = []
    async def event_tracker(event):
        received_events.append(event)
        
    bus.subscribe(KnowledgeGraphUpdated, event_tracker)
    bus.subscribe(PlanCreated, event_tracker)
    bus.subscribe(FollowUpRequired, event_tracker)
    bus.subscribe(MemoryStored, event_tracker)
    
    # 1. Provide an intent (callback) without a phone number
    await bus.publish(TranscriptFinal(
        session_id="session_1", 
        transcript="Please call me back. This is John."
    ))
    
    await asyncio.sleep(0.1)
    
    # Verify Graph Updated
    graphs = [e for e in received_events if isinstance(e, KnowledgeGraphUpdated)]
    assert len(graphs) == 1
    
    # Verify Plan Created
    plans = [e for e in received_events if isinstance(e, PlanCreated)]
    assert len(plans) == 1
    
    # Verify Follow Up Required
    # Because intent is CALLBACK but there is no phone number regex matched, FollowUpRequired should be emitted
    follow_ups = [e for e in received_events if isinstance(e, FollowUpRequired)]
    assert len(follow_ups) == 1
    
    # Check GoalManager
    goal_manager = pipeline.goal_managers["session_1"]
    pending_goals = goal_manager.get_pending_goals()
    assert len(pending_goals) > 0
    assert pending_goals[0].description == "COLLECT_PHONE_NUMBER"
    
    # 2. Simulate providing phone number
    await bus.publish(TranscriptFinal(
        session_id="session_1", 
        transcript="My number is 555-0199."
    ))
    
    await asyncio.sleep(0.1)
    
    # 3. Simulate Conversation Complete
    await bus.publish(ConversationCompleted(session_id="session_1"))
    
    await asyncio.sleep(0.1)
    
    # Verify Memory was stored
    memories_stored = [e for e in received_events if isinstance(e, MemoryStored)]
    assert len(memories_stored) == 1
    
    # Verify Repository has it
    saved_profile = await repo.get_profile("unknown")
    assert saved_profile is not None
    # Verify PreferenceManager added topics
    assert len(saved_profile.previous_topics) > 0
