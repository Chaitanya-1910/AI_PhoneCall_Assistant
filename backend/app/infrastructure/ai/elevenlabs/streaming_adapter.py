import asyncio
from typing import AsyncGenerator
import logging
from app.domain.conversation.ai_services import TextToSpeechService
from app.domain.conversation.cancellation import CancellationToken
from app.domain.conversation.events import SpeechChunkGenerated, SpeechCompleted
from app.infrastructure.ai.elevenlabs.adapter import ElevenLabsAdapter

logger = logging.getLogger(__name__)

class StreamingElevenLabsAdapter(TextToSpeechService):
    """
    Thin wrapper over ElevenLabsAdapter to adapt it to the streaming protocol.
    Converts audio chunks into SpeechChunkGenerated and SpeechCompleted events.
    Respects cooperative cancellation.
    """
    def __init__(self, elevenlabs_adapter: ElevenLabsAdapter):
        self._adapter = elevenlabs_adapter

    async def synthesize(
        self, 
        session_id: str, 
        text: str,
        cancellation_token: CancellationToken
    ) -> AsyncGenerator[SpeechChunkGenerated | SpeechCompleted, None]:
        
        try:
            stream = self._adapter.synthesize_stream(text=text)
            
            async for chunk in stream:
                if cancellation_token.is_cancelled:
                    logger.info(f"ElevenLabs synthesis cancelled for session {session_id}")
                    break
                    
                yield SpeechChunkGenerated(session_id=session_id, audio_data=chunk)
                
                # Yield control to allow cancellation checks
                await asyncio.sleep(0)
                
            if not cancellation_token.is_cancelled:
                yield SpeechCompleted(session_id=session_id)
                
        except Exception as e:
            logger.error(f"ElevenLabs streaming failed for session {session_id}: {e}")
            raise
