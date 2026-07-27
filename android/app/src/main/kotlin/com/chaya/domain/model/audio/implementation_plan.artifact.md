# Implementation Plan - Fix Unresolved Reference 'CallAudioSource'

The project is failing to compile because `CallAudioSource` is referenced but its definition is missing. Inspection reveals that a similar model `AudioSource` exists, which likely replaced or was intended to absorb `CallAudioSource`.

## Proposed Changes

### [Domain Model]

#### [MODIFY] [AudioSource.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/domain/model/audio/AudioSource.kt)
- Add `Telecom` object to the `AudioSource` sealed interface to represent the telecom audio stream.
- Ensure naming consistency (e.g., `Microphone` instead of `MicrophoneAudioSource`).

### [Telecom Data Layer]

#### [MODIFY] [AndroidAudioSourceManager.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/data/telecom/AndroidAudioSourceManager.kt)
- Update imports from `CallAudioSource` to `AudioSource`.
- Replace `CallAudioSource.MicrophoneAudioSource` with `AudioSource.Microphone`.
- Replace `CallAudioSource.TelecomAudioSource` with `AudioSource.Telecom`.
- Update all type references from `CallAudioSource` to `AudioSource`.

### [Telecom Domain Layer]

#### [MODIFY] [AudioSourceManager.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/domain/telecom/AudioSourceManager.kt)
- Update imports from `CallAudioSource` to `AudioSource`.
- Update the `activeSource` property type to `StateFlow<AudioSource>`.

### [Presentation Layer]

#### [MODIFY] [DiagnosticsViewModel.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/diagnostics/DiagnosticsViewModel.kt)
- Update imports from `CallAudioSource` to `AudioSource`.
- Update the `activeAudioSource` property type to `StateFlow<AudioSource>`.

## Verification Plan

### Automated Tests
- Run `./gradlew :app:compileDebugKotlin` to verify that the unresolved reference error is resolved and no new errors are introduced in these files.

### Manual Verification
- Verify that the `DiagnosticsViewModel` correctly reflects the active audio source if it can be observed in the UI (out of scope for this task but good to keep in mind).
