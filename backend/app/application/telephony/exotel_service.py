import logging
import time
import httpx
from typing import Optional
from fastapi import Response
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import Settings
from app.domain.services.call_pipeline_service import CallPipelineService
from app.domain.services.storage_interfaces import StorageService
from app.schemas.exotel import ExotelIncomingCall, ExotelRecording, ExotelStatus
from app.application.conversation.manager import ConversationManager

logger = logging.getLogger(__name__)

class ExotelService:
    def __init__(
        self,
        settings: Settings,
        pipeline: CallPipelineService,
        storage: StorageService,
        conversation_manager: ConversationManager
    ):
        self.settings = settings
        self.pipeline = pipeline
        self.storage = storage
        self.conversation = conversation_manager
        
    def _build_xml(self, play_url: str, record_action: str) -> Response:
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{play_url}</Play>
    <Record action="{record_action}" timeout="5" />
</Response>"""
        return Response(content=xml, media_type="application/xml")
        
    def _build_error_xml(self) -> Response:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>I'm sorry. I'm experiencing a temporary issue.</Say>
</Response>"""
        return Response(content=xml, media_type="application/xml")

    async def handle_incoming_call(self, call: ExotelIncomingCall) -> Response:
        """Handles the initial call and plays the greeting."""
        logger.info(f"Incoming call from {call.From} (CallSid: {call.CallSid})")
        
        # We don't have a generated greeting audio yet, so we could generate it 
        # or assume we have a pre-recorded greeting file. Let's generate it dynamically!
        greeting_text = "Hello, I am CHAYA, Chaitanya's AI assistant."
        
        try:
            start_time = time.time()
            # Initialize conversation session
            await self.conversation.start_session(call.CallSid)
            
            # Generate TTS for greeting
            greeting_audio = await self.pipeline.tts_service.synthesize(greeting_text)
            
            file_id = f"greeting_{call.CallSid}"
            await self.storage.save(greeting_audio, file_id)
            
            play_url = f"{self.settings.exotel.public_media_url}/{file_id}"
            
            # Action URL needs to point to our recording endpoint
            # In a real app this would be a full URL, we'll construct a relative one assuming Exotel resolves it,
            # or we need the full webhook URL. Assuming the router is mounted at /api/v1/webhooks/exotel
            # We'll just return the relative path if possible, but absolute is safer.
            # I will use a placeholder or assume the user configures the webhook action on the Exotel portal, 
            # but usually `<Record action="url">` needs a full URL. We'll leave it as a relative URL or absolute if we had a base_url.
            
            logger.info(f"Greeting TTS generated in {time.time() - start_time:.2f}s")
            
            return self._build_xml(play_url, "/api/v1/webhooks/exotel/recording")
            
        except Exception as e:
            logger.exception(f"Error handling incoming call: {e}")
            return self._build_error_xml()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _download_recording(self, url: str) -> bytes:
        """Download recording from Exotel with retries."""
        async with httpx.AsyncClient() as client:
            # Exotel requires Basic Auth to download recordings usually, 
            # but sometimes they provide a public short-lived URL.
            # Using credentials from config just in case.
            auth = (self.settings.exotel.api_key, self.settings.exotel.api_token)
            response = await client.get(url, auth=auth)
            response.raise_for_status()
            return response.content

    async def handle_recording(self, recording: ExotelRecording) -> Response:
        """Handles the caller's recorded speech."""
        logger.info(f"Received recording for {recording.CallSid}: {recording.RecordingUrl}")
        start_time = time.time()
        
        try:
            # 1. Download audio
            audio_bytes = await self._download_recording(recording.RecordingUrl)
            
            # 2. Process Turn through existing ConversationManager (handles STT, LLM, TTS)
            turn_result = await self.conversation.process_turn(
                audio_bytes=audio_bytes,
                conversation_id=recording.CallSid,
                request_id=recording.CallSid,
                turn_id=str(int(time.time()))
            )
            
            # If the user was completely silent, we might need to handle empty transcript
            if not turn_result.transcript.strip():
                # CHAYA usually handles empty transcripts within the prompt logic, 
                # but if we want a specific Exotel fallback we can check the response.
                pass
                
            # 3. Save and serve the resulting audio
            file_id = f"resp_{recording.CallSid}_{int(time.time())}"
            await self.storage.save(turn_result.audio_bytes, file_id)
            
            play_url = f"{self.settings.exotel.public_media_url}/{file_id}"
            
            logger.info(f"Total Pipeline Latency: {time.time() - start_time:.2f}s")
            
            return self._build_xml(play_url, "/api/v1/webhooks/exotel/recording")
            
        except Exception as e:
            logger.exception(f"Error handling recording for {recording.CallSid}: {e}")
            return self._build_error_xml()

    async def handle_status(self, status: ExotelStatus) -> Response:
        """Handles call completion or failure."""
        logger.info(f"Call Status Update: {status.CallSid} - {status.Status} - Duration: {status.CallDuration}s")
        if status.Status in ["completed", "failed", "busy", "no-answer"]:
            # Clean up session
            await self.conversation.end_session(status.CallSid)
        
        return Response(status_code=200)
