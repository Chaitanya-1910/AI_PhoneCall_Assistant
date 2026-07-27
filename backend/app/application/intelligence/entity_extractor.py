from typing import Protocol, List
from app.domain.intelligence.models import ExtractedEntity, EntityType
import re

class EntityExtractor(Protocol):
    async def extract_entities(self, transcript: str) -> List[ExtractedEntity]:
        """Extracts structured entities from a transcript."""
        ...

class RegexEntityExtractor(EntityExtractor):
    async def extract_entities(self, transcript: str) -> List[ExtractedEntity]:
        entities = []
        
        # Super naive regexes for testing
        phone_match = re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", transcript)
        if phone_match:
            entities.append(ExtractedEntity(entity_type=EntityType.PHONE_NUMBER, value=phone_match.group(0)))
            
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", transcript)
        if email_match:
            entities.append(ExtractedEntity(entity_type=EntityType.EMAIL, value=email_match.group(0)))
            
        return entities
