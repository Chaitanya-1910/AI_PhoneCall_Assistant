"""Production endpoints for Android Call Integration."""

import uuid
from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response

from app.api.deps import get_app_settings, get_conversation_manager, get_storage_service
from app.core.config import Settings
from app.core.exceptions import NotFoundError, ValidationError
from app.application.conversation.manager import ConversationManager
from app.domain.services.storage_interfaces import StorageService

router = APIRouter()

ALLOWED_AUDIO_TYPES = {
    "audio/wav",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/m4a",
    "audio/aac",
    "audio/webm",
    "audio/ogg",
}


@router.post("/process", response_model=None)
async def process_call(
    request: Request,
    audio: Annotated[UploadFile, File(...)],
    conversation_manager: Annotated[ConversationManager, Depends(get_conversation_manager)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    settings: Annotated[Settings, Depends(get_app_settings)],
    conversation_id: Annotated[str | None, Form()] = None,
) -> dict[str, Any]:
    """
    Process an incoming audio message from an Android client.
    
    Returns the transcript, AI response, and a URL to retrieve the synthesized audio.
    """
    if audio.content_type not in ALLOWED_AUDIO_TYPES:
        raise ValidationError(f"Unsupported audio format: {audio.content_type}")
        
    audio_bytes = await audio.read()

    # DIAGNOSTIC LOGGING
    logger = structlog.get_logger()
    logger.info(
        "audio_upload_received",
        filename=audio.filename,
        size_bytes=len(audio_bytes),
        content_type=audio.content_type
    )

    # Save for manual inspection
    with open("debug_upload.wav", "wb") as f:
        f.write(audio_bytes)

    if not audio_bytes:
        raise ValidationError("Audio file is empty")
        
    max_size_bytes = settings.storage.max_audio_upload_size_mb * 1024 * 1024
    if len(audio_bytes) > max_size_bytes:
        raise ValidationError(f"Audio file exceeds {settings.storage.max_audio_upload_size_mb}MB limit")
        
    # Generate or reuse conversation ID
    conv_id = conversation_id or str(uuid.uuid4())
    # Request ID per request
    req_id = str(uuid.uuid4())
    
    # Process via ConversationManager
    result = await conversation_manager.process_turn(
        audio_bytes=audio_bytes, 
        conversation_id=conv_id,
        request_id=req_id,
        turn_id=str(uuid.uuid4())
    )
    
    # Save the output audio
    # For storage we generate a specific audio_id
    audio_id = str(uuid.uuid4())
    await storage_service.save(result.audio_bytes, audio_id)
    
    audio_url = str(request.url_for("get_call_audio", audio_id=audio_id))
    
    return {
        "request_id": req_id,
        "conversation_id": conv_id,
        "transcript": result.transcript,
        "response": result.response,
        "audio_url": audio_url,
        "intent": result.intent,
        "intent_confidence": result.intent_confidence,
        "summary": result.summary,
        "metrics": result.metrics
    }


@router.get("/audio/{audio_id}", name="get_call_audio")
async def get_call_audio(
    audio_id: str,
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> Response:
    """Retrieve the generated audio response."""
    try:
        audio_bytes = await storage_service.load(audio_id)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
