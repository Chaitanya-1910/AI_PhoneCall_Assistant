# CHAYA

Production-grade personal AI phone assistant.

CHAYA listens to phone calls, transcribes speech, generates AI responses via Gemini, and speaks back through ElevenLabs TTS.

## Architecture

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for layer diagrams, design decisions, and package responsibilities.

```
CHAYA/
├── android/          # Kotlin + Jetpack Compose client (MVVM, Clean Architecture)
├── backend/          # Python FastAPI server (Clean Architecture)
├── docker-compose.yml # Local PostgreSQL
├── .env.example      # Environment variable template
├── ARCHITECTURE.md   # Architecture reference
└── README.md
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Android | Kotlin, Jetpack Compose, MVVM, Material 3, Hilt |
| Backend | Python 3.12+, FastAPI, Pydantic Settings, structlog |
| Database | PostgreSQL (SQLAlchemy async, Alembic) |
| STT | Faster-Whisper |
| LLM | Google Gemini |
| TTS | ElevenLabs |

## Prerequisites

- **Android**: JDK 17+, Android Studio Ladybug or newer
- **Backend**: Python 3.12+, Docker (for PostgreSQL)
- **Tools**: Git

## Quick Start

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp ../.env.example ../.env
# Edit .env with your values

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: `GET http://192.168.0.8:8000/api/v1/health`

Run tests:

```bash
pytest
```

### 3. Android

1. Open `android/` in Android Studio.
2. Copy `android/local.properties.example` → `android/local.properties`.
3. Set SDK path and API URL:
   ```
   sdk.dir=C\:\\Users\\YourName\\AppData\\Local\\Android\\Sdk
   CHAYA_API_BASE_URL=http://192.168.0.8:8000
   ```
4. Sync Gradle and run on emulator or device.

## Environment Variables

See [`.env.example`](.env.example) for all configuration options. Never commit `.env` files.

Production startup validates that `GEMINI_API_KEY`, `ELEVENLABS_API_KEY`, and `ELEVENLABS_VOICE_ID` are set when `APP_ENV=production`.

## Project Status

This repository contains the **architecture skeleton only** (refinement pass complete). The following are not yet implemented:

- Gemini, Whisper, and ElevenLabs integrations
- Database schema and migrations
- Authentication
- Business logic and UI screens
- Call detection

## License

Private — personal project.
# AI-Assistant
