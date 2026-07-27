import asyncio
import logging
from typing import Dict
from app.application.intelligence.event_bus import IntelligenceEventBus
from app.domain.conversation.events import (
    TranscriptFinal, ConversationCompleted, IntentDetected, 
    EntitiesExtracted, ActionCreated, PriorityUpdated, SummaryGenerated,
    KnowledgeGraphUpdated, ReasoningCompleted, PlanCreated, GoalCreated,
    ConversationComplete, ConversationIncomplete, FollowUpRequired, MemoryStored
)
from app.domain.conversation.metrics import ConversationMetrics
from app.domain.conversation.confidence import ConversationConfidence
from app.domain.conversation.memory import LongTermMemory
from app.domain.knowledge.models import KnowledgeGraph, ValidatedKnowledgeGraph
from app.domain.memory.models import ConversationHistory
from app.application.intelligence.intent_engine import IntentEngine
from app.application.intelligence.entity_extractor import EntityExtractor
from app.application.intelligence.action_engine import ActionEngine
from app.application.intelligence.priority_engine import PriorityEngine
from app.application.intelligence.summary_engine import SummaryEngine
from app.application.knowledge.builder import KnowledgeGraphBuilder
from app.application.knowledge.validator import ConsistencyValidator
from app.application.knowledge.reasoning import ReasoningEngine
from app.application.knowledge.planning import PlanningEngine
from app.application.knowledge.goal_manager import GoalManager
from app.application.knowledge.completeness import ConversationCompleteness
from app.application.knowledge.follow_up import FollowUpManager
from app.application.memory.retrieval import MemoryRetrievalEngine
from app.application.memory.preferences import PreferenceManager
import time

logger = logging.getLogger(__name__)

class ConversationIntelligencePipeline:
    """
    Subscribes to ConversationEvents and orchestrates the Intelligence and Knowledge Engines asynchronously.
    """
    def __init__(
        self,
        event_bus: IntelligenceEventBus,
        intent_engine: IntentEngine,
        entity_extractor: EntityExtractor,
        action_engine: ActionEngine,
        priority_engine: PriorityEngine,
        summary_engine: SummaryEngine,
        memory_retrieval_engine: MemoryRetrievalEngine,
        memories: Dict[str, LongTermMemory],
        metrics: Dict[str, ConversationMetrics],
        confidences: Dict[str, ConversationConfidence]
    ):
        self.bus = event_bus
        self.intent_engine = intent_engine
        self.entity_extractor = entity_extractor
        self.action_engine = action_engine
        self.priority_engine = priority_engine
        self.summary_engine = summary_engine
        self.memory_retrieval_engine = memory_retrieval_engine
        
        self.memories = memories
        self.metrics = metrics
        self.confidences = confidences
        
        # State for Knowledge Graph and Goals per session
        self.knowledge_graphs: Dict[str, KnowledgeGraph] = {}
        self.goal_managers: Dict[str, GoalManager] = {}
        
        # Subscribe to Orchestrator events
        self.bus.subscribe(TranscriptFinal, self.handle_transcript_final)
        self.bus.subscribe(ConversationCompleted, self.handle_conversation_completed)

    def _get_goal_manager(self, session_id: str) -> GoalManager:
        if session_id not in self.goal_managers:
            self.goal_managers[session_id] = GoalManager()
        return self.goal_managers[session_id]
        
    def _get_knowledge_graph(self, session_id: str) -> KnowledgeGraph:
        if session_id not in self.knowledge_graphs:
            self.knowledge_graphs[session_id] = KnowledgeGraph()
        return self.knowledge_graphs[session_id]

    async def handle_transcript_final(self, event: TranscriptFinal) -> None:
        """Complete Phase 7.5 & 7.6 Pipeline Execution"""
        logger.info(f"Intelligence Pipeline processing transcript for session {event.session_id}")
        
        # 1. Intent and Entity Extraction
        intent_task = asyncio.create_task(self.intent_engine.extract_intent(event.transcript))
        entity_task = asyncio.create_task(self.entity_extractor.extract_entities(event.transcript))
        intent, entities = await asyncio.gather(intent_task, entity_task)
        
        await self.bus.publish(IntentDetected(session_id=event.session_id, intent=intent))
        await self.bus.publish(EntitiesExtracted(session_id=event.session_id, entities=entities))
        
        # 2. Action and Priority Generation
        metrics = self.metrics.get(event.session_id, ConversationMetrics(session_id=event.session_id))
        confidence = self.confidences.get(event.session_id, ConversationConfidence())
        action_task = asyncio.create_task(self.action_engine.generate_actions(intent, entities))
        priority_task = asyncio.create_task(self.priority_engine.calculate_urgency(intent, entities, metrics, confidence))
        actions, priority = await asyncio.gather(action_task, priority_task)
        
        memory = self.memories.get(event.session_id)
        if memory:
            memory.apply_priority_changed(priority)
            for action in actions:
                memory.apply_action_added(action)
                await self.bus.publish(ActionCreated(session_id=event.session_id, action=action))
        await self.bus.publish(PriorityUpdated(session_id=event.session_id, urgency=priority))
        
        # 3. Knowledge Graph Update
        graph = self._get_knowledge_graph(event.session_id)
        updated_graph = KnowledgeGraphBuilder.update_graph(graph, entities, actions)
        self.knowledge_graphs[event.session_id] = updated_graph
        await self.bus.publish(KnowledgeGraphUpdated(session_id=event.session_id))
        
        # 4. Consistency Validation & Reasoning
        validated_graph = ConsistencyValidator.validate(updated_graph)
        missing_info = ReasoningEngine.infer_missing_information(validated_graph, intent)
        await self.bus.publish(ReasoningCompleted(session_id=event.session_id))
        
        # 5. Planning Engine
        plan = PlanningEngine.create_plan(missing_info)
        await self.bus.publish(PlanCreated(session_id=event.session_id))
        
        # 6. Goal Manager
        goal_manager = self._get_goal_manager(event.session_id)
        goal_manager.apply_plan(plan)
        # Note: In a full system, we'd check if the graph satisfies existing goals and mark completed.
        pending_goals = goal_manager.get_pending_goals()
        
        # 7. Completeness & Follow Up
        completeness = ConversationCompleteness.calculate(validated_graph, intent)
        needs_follow_up = FollowUpManager.requires_follow_up(pending_goals, completeness)
        
        if needs_follow_up:
            await self.bus.publish(ConversationIncomplete(session_id=event.session_id))
            await self.bus.publish(FollowUpRequired(session_id=event.session_id))
        else:
            await self.bus.publish(ConversationComplete(session_id=event.session_id))
            
        # The goal manager state can be injected back into ConversationContext for the Orchestrator/LLM to use

    async def handle_conversation_completed(self, event: ConversationCompleted) -> None:
        """Phase 7.6: Generate summary and store persistent memory."""
        logger.info(f"Intelligence Pipeline generating summary and saving memory for {event.session_id}")
        
        memory = self.memories.get(event.session_id)
        if not memory:
            return
            
        # Generate Summary
        summary = await self.summary_engine.generate_summary(memory)
        memory.apply_summary_created(summary)
        await self.bus.publish(SummaryGenerated(session_id=event.session_id, summary=summary))
        
        # 8. Persistent Memory & Profile Update
        # Assume caller phone is in memory facts or we pass it explicitly. Using dummy phone for now.
        phone_number = memory.facts.facts.get("caller_phone", "unknown")
        persistent_memory = await self.memory_retrieval_engine.retrieve_for_call(phone_number)
        
        # Update Preferences
        updated_profile = PreferenceManager.update_preferences(persistent_memory.caller_profile, summary)
        persistent_memory.caller_profile = updated_profile
        
        # Append Conversation History
        history = ConversationHistory(
            session_id=event.session_id,
            timestamp=time.time(),
            summary=summary.detailed_summary,
            outcome=summary.urgency_assessment.value,
            knowledge_graph=self._get_knowledge_graph(event.session_id)
        )
        persistent_memory.history.append(history)
        
        # Save to Repository
        await self.memory_retrieval_engine.repository.save_memory(persistent_memory)
        await self.bus.publish(MemoryStored(session_id=event.session_id))
