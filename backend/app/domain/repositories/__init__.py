"""Repository interface contracts."""

from typing import Protocol, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(Protocol[T, ID]):
    """Base repository contract for persistence operations."""

    async def get_by_id(self, entity_id: ID) -> T | None: ...

    async def save(self, entity: T) -> T: ...

    async def delete(self, entity_id: ID) -> None: ...
