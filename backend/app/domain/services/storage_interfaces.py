"""Domain interfaces for file storage."""

from typing import Protocol


class StorageService(Protocol):
    """Abstract interface for audio file storage."""

    async def save(self, audio_bytes: bytes, file_id: str) -> None:
        """Save audio bytes to storage using the given logical file ID.
        
        Args:
            audio_bytes: The binary audio data.
            file_id: A logical identifier (e.g. UUID) for the file.
        """
        ...

    async def load(self, file_id: str) -> bytes:
        """Load audio bytes from storage using the logical file ID.
        
        Args:
            file_id: The logical identifier of the file.
            
        Returns:
            The binary audio data.
            
        Raises:
            NotFoundError: If the file does not exist.
        """
        ...

    async def delete(self, file_id: str) -> None:
        """Delete audio bytes from storage.
        
        Args:
            file_id: The logical identifier of the file.
        """
        ...
