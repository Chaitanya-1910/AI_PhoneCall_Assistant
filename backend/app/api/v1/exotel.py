import os
from fastapi import APIRouter, Depends, Form, Request, Response, HTTPException
from fastapi.responses import FileResponse
from app.api.deps import get_exotel_service, get_storage_service, get_app_settings
from app.application.telephony.exotel_service import ExotelService
from app.domain.services.storage_interfaces import StorageService
import logging
from app.core.config import Settings
from app.schemas.exotel import ExotelIncomingCall, ExotelRecording, ExotelStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/exotel", tags=["exotel"])
media_router = APIRouter(prefix="/media", tags=["media"])

@router.post("/incoming")
async def exotel_incoming(
    CallSid: str = Form(None),
    From: str = Form(None),
    To: str = Form(None),
    Direction: str = Form(None),
    CallType: str = Form(None),
    DialWhomNumber: str = Form(None),
    TimeCreated: str = Form(None),
    exotel_service: ExotelService = Depends(get_exotel_service)
):
    """Webhook for Exotel incoming call."""
    if not CallSid and not From and not To:
        # Empty request body (e.g., from Swagger)
        return Response(content="<?xml version='1.0'?><Response><Say>Hello, I am CHAYA. Test mode activated.</Say></Response>", media_type="application/xml")
        
    try:
        call = ExotelIncomingCall(
            CallSid=CallSid,
            From=From,
            To=To,
            Direction=Direction,
            CallType=CallType,
            DialWhomNumber=DialWhomNumber,
            TimeCreated=TimeCreated
        )
        return await exotel_service.handle_incoming_call(call)
    except Exception as e:
        logger.exception("Error processing incoming Exotel webhook")
        return Response(content="<?xml version='1.0'?><Response><Say>An error occurred.</Say></Response>", media_type="application/xml")

@router.post("/recording")
async def exotel_recording(
    CallSid: str = Form(None),
    From: str = Form(None),
    To: str = Form(None),
    RecordingUrl: str = Form(None),
    digits: str = Form(None),
    exotel_service: ExotelService = Depends(get_exotel_service)
):
    """Webhook for Exotel recording completion."""
    if not CallSid:
        return Response(content="<?xml version='1.0'?><Response><Say>Test mode activated.</Say></Response>", media_type="application/xml")
        
    try:
        recording = ExotelRecording(
            CallSid=CallSid,
            From=From,
            To=To,
            RecordingUrl=RecordingUrl,
            digits=digits
        )
        return await exotel_service.handle_recording(recording)
    except Exception as e:
        logger.exception("Error processing Exotel recording webhook")
        return Response(content="<?xml version='1.0'?><Response><Say>An error occurred.</Say></Response>", media_type="application/xml")

@router.post("/status")
async def exotel_status(
    CallSid: str = Form(None),
    From: str = Form(None),
    To: str = Form(None),
    Status: str = Form(None),
    CallDuration: str = Form(None),
    exotel_service: ExotelService = Depends(get_exotel_service)
):
    """Webhook for Exotel call status updates."""
    if not CallSid:
        return Response(status_code=200)
        
    try:
        status = ExotelStatus(
            CallSid=CallSid,
            From=From,
            To=To,
            Status=Status,
            CallDuration=CallDuration
        )
        return await exotel_service.handle_status(status)
    except Exception as e:
        logger.exception("Error processing Exotel status webhook")
        return Response(status_code=200) # Exotel expects a 200 OK

@media_router.get("/{filename}")
async def serve_media(
    filename: str,
    storage: StorageService = Depends(get_storage_service)
):
    """Serves the generated MP3 files."""
    try:
        # Load the raw bytes and return them
        audio_bytes = await storage.load(filename.replace(".mp3", ""))
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Media not found")
