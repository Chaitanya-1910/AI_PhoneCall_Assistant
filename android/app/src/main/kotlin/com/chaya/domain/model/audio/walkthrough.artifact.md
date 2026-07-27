# Walkthrough - Resolved Unresolved Reference 'CallAudioSource'

I have resolved the compile error `Unresolved reference 'CallAudioSource'` by unifying the missing `CallAudioSource` model into the existing `AudioSource` sealed interface.

## Changes Made

### Domain Model
#### [AudioSource.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/domain/model/audio/AudioSource.kt)
- Added `Telecom` object to the `AudioSource` sealed interface to support call-based audio streams.

### Telecom Data & Domain Layers
#### [AudioSourceManager.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/domain/telecom/AudioSourceManager.kt)
- Updated the interface to return `StateFlow<AudioSource>` instead of the non-existent `CallAudioSource`.

#### [AndroidAudioSourceManager.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/data/telecom/AndroidAudioSourceManager.kt)
- Migrated state management to use `AudioSource`.
- Mapped state transitions:
    - `CallAudioSource.MicrophoneAudioSource` -> `AudioSource.Microphone`
    - `CallAudioSource.TelecomAudioSource` -> `AudioSource.Telecom`

### Presentation Layer
#### [DiagnosticsViewModel.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/diagnostics/DiagnosticsViewModel.kt)
- Updated property type for `activeAudioSource` to `AudioSource`.

### Repository Layer
#### [CallRepositoryImpl.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/data/repository/CallRepositoryImpl.kt)
- Added an exhaustive branch for `is AudioSource.Telecom` in the `getAudioFileFromSource` method.

## Verification Results

### Automated Tests
- Executed `./gradlew :app:compileDebugKotlin`
- **Result**: `BUILD SUCCESSFUL`

> [!NOTE]
> The implementation preserves all existing business logic for state transitions based on call state and device capabilities.
