from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.repositories.memory_repository import SqlAlchemyMemoryRepository
import logging

logger = logging.getLogger(__name__)

class MemoryUnitOfWork:
    """
    Manages atomic transactional boundaries across repositories.
    """
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: AsyncSession = None
        self.memory_repo: SqlAlchemyMemoryRepository = None

    async def __aenter__(self):
        self.session = self.session_factory()
        self.memory_repo = SqlAlchemyMemoryRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        if exc_type:
            logger.error(f"Rolling back transaction due to {exc_type}: {exc_val}")
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
