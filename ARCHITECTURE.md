# CHAYA Architecture

This document describes the architectural decisions and layer responsibilities for the CHAYA monorepo. It reflects the refinement pass applied before feature implementation.

## Design Principles

1. **Clean Architecture** — dependencies point inward; domain has no framework imports.
2. **SOLID** — single-responsibility use cases/services; repository interfaces for swappable I/O.
3. **MVVM (Android)** — ViewModels expose `UiState`; Compose observes `StateFlow`.
4. **Configuration over hardcoding** — secrets and URLs via environment variables / `local.properties`.
5. **Observability from day one** — request correlation IDs on both client and server.

---

## Monorepo Layout

```
CHAYA/
├── android/                 # Kotlin client
├── backend/                 # FastAPI server
├── docker-compose.yml       # Local PostgreSQL
├── .env.example             # Backend secrets template
└── ARCHITECTURE.md          # This file
```

---

## Backend Layers

```
HTTP Request
    │
    ▼
┌─────────────────────────────────────┐
│  api/                               │  Routes, deps, exception handlers
│  ├── v1/endpoints/                  │  Thin handlers — delegate immediately
│  └── exception_handlers.py          │  ChayaError → HTTP status mapping
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  domain/                            │  Pure business logic
│  ├── models/                        │  Domain entities (dataclasses)
│  ├── services/                      │  Orchestration, no I/O
│  └── repositories/                  │  Persistence contracts (Protocol)
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  infrastructure/                    │  Framework & external adapters
│  ├── database/                      │  SQLAlchemy async engine/session
│  ├── repositories/                  │  Repository implementations
│  └── external/                      │  Whisper, Gemini, ElevenLabs
└─────────────────────────────────────┘
```

### Cross-Cutting (backend)

| Module | Responsibility |
|--------|----------------|
| `core/config.py` | Flat env vars + grouped config objects (`settings.database`, `settings.gemini`) |
| `core/exceptions.py` | `ChayaError` hierarchy with machine-readable codes |
| `core/middleware.py` | `RequestContextMiddleware` — X-Request-ID + access logs |
| `core/logging.py` | structlog (JSON in prod, console in dev) |
| `schemas/` | Pydantic DTOs for API request/response contracts |

### Request Flow (example: health check)

```
GET /api/v1/health
  → health_check()              [api/v1/endpoints/health.py]
  → HealthService.get_status()  [domain/services/health_service.py]
  → HealthResponse              [schemas/common.py]
```

Future endpoints follow the same pattern: **endpoint → domain service → repository/external adapter**.

### Configuration Groups

Environment variables remain flat (e.g. `GEMINI_API_KEY`), but code accesses them through grouped views:

```python
settings.gemini.api_key
settings.whisper.model
settings.elevenlabs.is_configured
settings.database.url
```

Production startup validates required secrets via Pydantic `model_validator`.

### Testing Strategy

- `create_app(init_database=False)` — unit tests skip DB pool
- `override_settings()` — inject test configuration
- Health and config tests run without PostgreSQL

---

## Android Layers

```
Compose UI
    │
    ▼
┌─────────────────────────────────────┐
│  presentation/                      │  Screens, ViewModels, navigation
│  ├── common/UiState                 │  Idle | Loading | Success | Error
│  ├── common/BaseViewModel           │  Coroutine safety + dispatchers
│  ├── navigation/                    │  NavHost, route constants
│  └── feature/                       │  Feature modules (future)
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  domain/                            │  Pure Kotlin
│  ├── model/                         │  Domain models
│  ├── repository/                    │  Repository interfaces
│  └── usecase/                       │  Single-responsibility operations
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  data/                              │  I/O implementations
│  ├── remote/                        │  Retrofit, DTOs, mappers, interceptors
│  ├── local/                         │  Room (future)
│  └── repository/                    │  Repository implementations
└─────────────────────────────────────┘
```

### Cross-Cutting (Android)

| Module | Responsibility |
|--------|----------------|
| `core/config/AppConfig` | Build-time config from `BuildConfig` |
| `core/common/Result` | Operation outcome wrapper |
| `core/network/safeApiCall` | Exception → `Result.Error` mapping |
| `di/DispatchersModule` | `@IoDispatcher`, `@DefaultDispatcher`, `@MainDispatcher` |
| `data/remote/interceptor/RequestIdInterceptor` | Sends `X-Request-ID` to backend |

### Build Variants & Network Security

| Variant | Cleartext HTTP | API URL |
|---------|----------------|---------|
| debug | Allowed for `192.168.0.8` | `local.properties` → `CHAYA_API_BASE_URL` |
| release | Disabled | HTTPS required |

---

## Correlation IDs

Both platforms propagate `X-Request-ID`:

- **Android**: `RequestIdInterceptor` generates UUID per request
- **Backend**: `RequestContextMiddleware` reads or generates ID, binds to structlog context, returns in response header

This enables end-to-end log tracing before a dedicated APM tool is added.

---

## Error Handling

### Backend

All application errors extend `ChayaError` with a `code` field. Global handlers map codes to HTTP status and return a consistent envelope:

```json
{
  "error": { "code": "NOT_FOUND", "message": "..." },
  "request_id": "uuid"
}
```

### Android

- Network layer: `safeApiCall` → `Result.Error`
- Presentation layer: `Result` → `UiState.Error`
- ViewModels inherit `BaseViewModel` for uncaught coroutine logging

---

## Dependency Injection

| Platform | Mechanism |
|----------|-----------|
| Backend | FastAPI `Depends()` + factory functions in `api/deps.py` |
| Android | Hilt modules: `AppModule`, `NetworkModule`, `RepositoryModule`, `DispatchersModule` |

---

## Local Development

```bash
# Start PostgreSQL
docker compose up -d

# Backend
cd backend && uvicorn app.main:app --reload

# Android — open android/ in Android Studio
```

---

## Future Package Responsibilities

| Package | Next implementation phase |
|---------|---------------------------|
| `backend/infrastructure/external/whisper/` | Audio → text transcription |
| `backend/infrastructure/external/gemini/` | LLM prompt + response |
| `backend/infrastructure/external/elevenlabs/` | Text → speech synthesis |
| `backend/infrastructure/repositories/` | Call session, transcript persistence |
| `backend/domain/services/` | Call pipeline orchestration |
| `android/presentation/feature/` | Call UI, settings, history |
| `android/data/local/` | Room cache for offline transcripts |
| `android/domain/usecase/` | Call monitoring, audio streaming |

---

## What Is Explicitly Not Implemented

- Gemini, Whisper, ElevenLabs integrations
- Database tables and Alembic migrations
- Authentication
- Call detection
- Feature UI screens

These will be built on top of this skeleton after architecture approval.
