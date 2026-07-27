# CHAYA Android Client

Kotlin + Jetpack Compose client following MVVM and Clean Architecture.

## Structure

```
app/src/main/kotlin/com/chaya/
├── ChayaApplication.kt       # Hilt application entry
├── MainActivity.kt           # Compose host (no feature screens yet)
├── di/                       # Hilt modules
├── core/                     # Shared utilities
│   ├── common/
│   ├── config/
│   ├── logging/
│   └── network/
├── data/                     # Data layer (repositories, remote, local)
├── domain/                   # Domain layer (models, use cases)
└── presentation/             # UI layer (theme, navigation, ViewModels)
```

## Setup

1. Open this directory in Android Studio.
2. Ensure `local.properties` contains your SDK path and optional API URL:
   ```
   sdk.dir=C\:\\Users\\YourName\\AppData\\Local\\Android\\Sdk
   CHAYA_API_BASE_URL=http://192.168.0.8:8000
   ```
3. Sync Gradle and run.

## Architecture

- **Presentation**: Compose UI, ViewModels, navigation
- **Domain**: Pure Kotlin business logic, use cases, repository interfaces
- **Data**: Retrofit API, Room (future), repository implementations

## Build Variants

| Variant | API URL |
|---------|---------|
| debug | `CHAYA_API_BASE_URL` from local.properties or emulator default |
| release | Configured via build config (override in CI) |
