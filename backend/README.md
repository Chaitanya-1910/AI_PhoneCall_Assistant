# CHAYA Backend

FastAPI backend for the CHAYA personal AI phone assistant.

## Structure

```
app/
├── main.py                 # Application entry point
├── core/                   # Cross-cutting concerns
│   ├── config.py           # Pydantic Settings
│   └── logging.py          # Structured logging setup
├── api/                    # HTTP layer
│   ├── deps.py             # FastAPI dependencies
│   └── v1/                 # API version 1
├── domain/                 # Business rules (no I/O)
│   ├── models/             # Domain entities
│   └── services/           # Domain services
├── infrastructure/         # External I/O adapters
│   ├── database/           # PostgreSQL / SQLAlchemy
│   └── external/           # Whisper, Gemini, ElevenLabs
└── schemas/                # Pydantic request/response DTOs
```

## Run

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Configuration

All settings are loaded from environment variables via `app.core.config.Settings`.
Copy the root `.env.example` to `.env` before running.

## Testing

```bash
pytest
```
