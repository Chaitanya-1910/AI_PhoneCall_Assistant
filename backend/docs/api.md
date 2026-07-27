# CHAYA Android API

This document details the production REST API endpoints designed for the Android client.

## Base URL
`http://<host>:<port>/api/v1`

## Error Format

All errors return standard HTTP status codes (`400`, `404`, `422`, `500`, `502`) and follow this JSON structure:

```json
{
    "request_id": "uuid-v4",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Unsupported audio format: audio/flac",
        "stage": "validation"
    }
}
```

The `stage` field will indicate where the failure occurred (`validation`, `stt`, `llm`, `tts`), helping Android developers understand if the issue was user-caused or an external API outage.

---

## 1. Process Call

**Endpoint**: `POST /calls/process`

This is the primary pipeline endpoint. It accepts an audio recording from the user, transcribes it, generates an AI response, synthesizes the response back to audio, and returns a playable URL.

### Request

*   **Content-Type**: `multipart/form-data`
*   **Body**:
    *   `audio` (File, Required): The recorded audio.
    *   `conversation_id` (String, Optional): An existing UUID v4 for continuing a conversation. If omitted, the server will generate a new one.

### Supported Audio Formats (MIME Types)
*   `audio/wav`
*   `audio/x-wav`
*   `audio/mpeg` (mp3)
*   `audio/mp4`
*   `audio/m4a`
*   `audio/aac`
*   `audio/webm`
*   `audio/ogg`

**Note:** Audio file size must be less than the configured maximum (default: 10MB).

### Response (200 OK)

```json
{
    "request_id": "b0a68d09-3221-4d32-bf76-cd209f995af7",
    "conversation_id": "4b68e987-a2f0-4dfd-b4ef-5e76d910a3f6",
    "transcript": "Hello, how are you?",
    "response": "I am doing well, how can I help you today?",
    "audio_url": "http://192.168.0.8:8000/api/v1/calls/audio/3c4155a0-5a39-4d69-a1b7-b08e5e1bb3b7",
    "metrics": {
        "stt_latency_ms": 420,
        "llm_latency_ms": 1150,
        "tts_latency_ms": 380,
        "total_latency_ms": 1950
    }
}
```

---

## 2. Retrieve Audio

**Endpoint**: `GET /calls/audio/{audio_id}`

Retrieves the synthesized audio file returned by the `process` endpoint.

### Request
*   `audio_id` (Path variable): The UUID of the generated audio file.

### Response (200 OK)
*   **Content-Type**: `audio/mpeg`
*   **Body**: Binary audio data (MP3).

### Response (404 Not Found)
Returned if the audio ID is invalid or the temporary file has expired.

```json
{
    "request_id": "673f40d1-0f79-4bc2-af09-54bc7279fb01",
    "error": {
        "code": "NOT_FOUND",
        "message": "Audio file 3c4155a0-5a39-4d69-a1b7-b08e5e1bb3b7 not found",
        "stage": null
    }
}
```
