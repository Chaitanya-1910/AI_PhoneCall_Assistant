"""Local filesystem storage adapter."""

import asyncio
import os
import tempfile
import time
from pathlib import Path

import structlog

from app.core.config import StorageConfig
from app.core.exceptions import NotFoundError
from app.domain.services.storage_interfaces import StorageService

logger = structlog.get_logger()


class LocalStorageAdapter(StorageService):
    """Temporary local storage adapter for audio files."""

    def __init__(self, config: StorageConfig) -> None:
        self.config = config
        self.base_dir = Path(tempfile.gettempdir()) / "chaya_audio"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, audio_bytes: bytes, file_id: str) -> None:
        """Save audio to a local temporary directory."""
        file_path = self._get_file_path(file_id)
        
        def _write():
            with open(file_path, "wb") as f:
                f.write(audio_bytes)
                
        await asyncio.to_thread(_write)
        logger.debug("audio_saved", file_id=file_id)

    async def load(self, file_id: str) -> bytes:
        """Load audio from the local temporary directory."""
        file_path = self._get_file_path(file_id)
        
        if not file_path.exists():
            raise NotFoundError(f"Audio file {file_id} not found")
            
        def _read():
            with open(file_path, "rb") as f:
                return f.read()
                
        audio_bytes = await asyncio.to_thread(_read)
        return audio_bytes

    async def delete(self, file_id: str) -> None:
        """Delete audio from the local directory."""
        file_path = self._get_file_path(file_id)
        
        def _delete():
            if file_path.exists():
                file_path.unlink()
                
        await asyncio.to_thread(_delete)
        logger.debug("audio_deleted", file_id=file_id)

    def _get_file_path(self, file_id: str) -> Path:
        """Get safe absolute path for the given file_id."""
        clean_id = os.path.basename(file_id)
        return self.base_dir / f"{clean_id}.mp3"

    async def cleanup_expired(self) -> int:
        """Background task helper to remove files older than the expiration config."""
        deleted_count = 0
        now = time.time()
        
        def _cleanup():
            nonlocal deleted_count
            for file_path in self.base_dir.glob("*.mp3"):
                try:
                    stats = file_path.stat()
                    if now - stats.st_mtime > self.config.audio_expiration_seconds:
                        file_path.unlink()
                        deleted_count += 1
                except Exception as e:
                    logger.warning("cleanup_failed_for_file", path=str(file_path), error=str(e))
                    
        await asyncio.to_thread(_cleanup)
        if deleted_count > 0:
            logger.info("expired_audio_cleaned", count=deleted_count)
        return deleted_count
