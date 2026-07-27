from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.repository.memory_repository import MemoryRepository
from app.domain.memory.models import PersistentMemory, CallerProfile, ConversationHistory
from app.domain.knowledge.models import KnowledgeGraph
from app.infrastructure.database.models import SQLAlchemyCallerProfile, SQLAlchemyConversationHistory

class SqlAlchemyMemoryRepository(MemoryRepository):
    """
    PostgreSQL-backed repository for PersistentMemory and CallerProfiles.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_profile(self, caller_id: str) -> Optional[CallerProfile]:
        result = await self.session.execute(
            select(SQLAlchemyCallerProfile).where(SQLAlchemyCallerProfile.caller_id == caller_id)
        )
        db_model = result.scalar_one_or_none()
        
        if db_model:
            return CallerProfile(
                caller_id=db_model.caller_id,
                name=db_model.name,
                phone_numbers=db_model.phone_numbers,
                organizations=db_model.organizations,
                relationship=db_model.relationship,
                preferred_language=db_model.preferred_language,
                preferred_callback_time=db_model.preferred_callback_time,
                communication_style=db_model.communication_style,
                previous_topics=db_model.previous_topics
            )
        return None
        
    async def save_memory(self, memory: PersistentMemory) -> None:
        # Merge Caller Profile
        db_profile = SQLAlchemyCallerProfile(
            caller_id=memory.caller_profile.caller_id,
            name=memory.caller_profile.name,
            phone_numbers=memory.caller_profile.phone_numbers,
            organizations=memory.caller_profile.organizations,
            relationship=memory.caller_profile.relationship,
            preferred_language=memory.caller_profile.preferred_language,
            preferred_callback_time=memory.caller_profile.preferred_callback_time,
            communication_style=memory.caller_profile.communication_style,
            previous_topics=memory.caller_profile.previous_topics
        )
        await self.session.merge(db_profile)
        
        # Merge Histories
        for hist in memory.history:
            db_hist = SQLAlchemyConversationHistory(
                session_id=hist.session_id,
                caller_id=memory.caller_profile.caller_id,
                timestamp=hist.timestamp,
                summary=hist.summary,
                outcome=hist.outcome,
                knowledge_graph_dump=hist.knowledge_graph.model_dump()
            )
            await self.session.merge(db_hist)
            
    async def get_memory_by_phone(self, phone_number: str) -> Optional[PersistentMemory]:
        # Simple lookup for prototype. In reality, we'd use JSONB operators.
        result = await self.session.execute(select(SQLAlchemyCallerProfile))
        profiles = result.scalars().all()
        
        matched_profile = next((p for p in profiles if phone_number in p.phone_numbers), None)
        
        if matched_profile:
            # Reconstruct PersistentMemory
            histories = await self.session.execute(
                select(SQLAlchemyConversationHistory)
                .where(SQLAlchemyConversationHistory.caller_id == matched_profile.caller_id)
            )
            db_histories = histories.scalars().all()
            
            domain_profile = await self.get_profile(matched_profile.caller_id)
            domain_histories = [
                ConversationHistory(
                    session_id=h.session_id,
                    timestamp=h.timestamp,
                    summary=h.summary,
                    outcome=h.outcome,
                    knowledge_graph=KnowledgeGraph(**h.knowledge_graph_dump)
                ) for h in db_histories
            ]
            
            return PersistentMemory(
                caller_profile=domain_profile,
                history=domain_histories
            )
            
        return None
