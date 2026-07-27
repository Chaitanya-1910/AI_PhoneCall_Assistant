"""Development testing endpoints."""

import os
import tempfile
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse, Response

from app.api.deps import (
    get_call_pipeline_service,
    get_llm_service,
    get_speech_to_text_service,
    get_text_to_speech_service,
)
from app.domain.services.ai_interfaces import (
    LlmService,
    SpeechToTextService,
    TextToSpeechService,
)
from app.domain.services.call_pipeline_service import CallPipelineService

TEMP_AUDIO_DIR = tempfile.gettempdir()

router = APIRouter()


@router.post("/test-whisper")
async def test_whisper(
    file: Annotated[UploadFile, File()],
    stt_service: Annotated[SpeechToTextService, Depends(get_speech_to_text_service)],
) -> dict[str, str]:
    """Test the Whisper Speech-to-Text service."""
    audio_bytes = await file.read()
    text = await stt_service.transcribe(audio_bytes)
    return {"text": text}


@router.post("/test-gemini")
async def test_gemini(
    prompt: Annotated[str, Form()],
    llm_service: Annotated[LlmService, Depends(get_llm_service)],
    system_prompt: Annotated[str | None, Form()] = None,
    stream: Annotated[bool, Form()] = False,
):
    """Test the configured LLM service (originally Gemini, now generic LLM provider)."""
    if stream:
        async def generate():
            async for chunk in llm_service.generate_response_stream(
                prompt=prompt, system_prompt=system_prompt
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")
    else:
        response = await llm_service.generate_response(
            prompt=prompt, system_prompt=system_prompt
        )
        return {"response": response}


@router.post(
    "/test-elevenlabs",
    response_class=Response,
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "Returns raw audio stream or file.",
        }
    },
)
async def test_elevenlabs(
    text: Annotated[str, Form()],
    tts_service: Annotated[TextToSpeechService, Depends(get_text_to_speech_service)],
    stream: Annotated[bool, Form()] = False,
):
    """Test the ElevenLabs Text-to-Speech service."""
    if stream:
        async def generate():
            async for chunk in tts_service.synthesize_stream(text):
                yield chunk
        return StreamingResponse(generate(), media_type="audio/mpeg")
    else:
        # Synthesize returns bytes. We use Response to automatically
        # set Content-Length so audio players can determine the duration.
        audio_bytes = await tts_service.synthesize(text)
        
        return Response(
            content=audio_bytes, 
            media_type="audio/mpeg",
            headers={
                "Content-Length": str(len(audio_bytes))
            }
        )


@router.post("/test-pipeline")
async def test_pipeline(
    request: Request,
    file: Annotated[UploadFile, File()],
    pipeline_service: Annotated[CallPipelineService, Depends(get_call_pipeline_service)],
) -> dict[str, Any]:
    """Test the complete synchronous Call Pipeline."""
    # Read audio bytes
    audio_bytes = await file.read()
    
    # Generate request_id
    request_id = str(uuid.uuid4())
    
    # Run pipeline
    result = await pipeline_service.process_audio(audio_bytes=audio_bytes, request_id=request_id)
    
    # Save audio temporarily
    audio_filename = f"{request_id}.mp3"
    audio_path = os.path.join(TEMP_AUDIO_DIR, audio_filename)
    with open(audio_path, "wb") as f:
        f.write(result.audio_bytes)
    
    # Construct URL dynamically based on the current request
    audio_url = str(request.url_for("get_temp_audio", audio_id=request_id))

    return {
        "transcript": result.transcript,
        "response": result.response,
        "audio_generated": True,
        "audio_url": audio_url
    }


@router.get("/audio/{audio_id}", name="get_temp_audio")
async def get_temp_audio(audio_id: str):
    """Retrieve temporarily stored audio for dev testing."""
    # Basic path traversal protection
    if "/" in audio_id or "\\" in audio_id or ".." in audio_id:
        raise HTTPException(status_code=400, detail="Invalid audio ID")
        
    audio_path = os.path.join(TEMP_AUDIO_DIR, f"{audio_id}.mp3")
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio not found or expired")
        
    return FileResponse(audio_path, media_type="audio/mpeg", filename=f"{audio_id}.mp3")
