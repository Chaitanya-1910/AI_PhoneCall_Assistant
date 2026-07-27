# Implementation Plan - Fix Silent Audio Recording

The app captures audio files, but they contain silence (zeros). This plan aims to diagnose the signal level and fix the `AudioRecord` configuration to capture real speech.

## Proposed Changes

### [Audio Data Layer]

#### [MODIFY] [AndroidAudioRecorder.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/data/audio/AndroidAudioRecorder.kt)
- Switch `MediaRecorder.AudioSource.MIC` to `MediaRecorder.AudioSource.VOICE_RECOGNITION` for better STT compatibility.
- Add an RMS (Root Mean Square) calculation to measure signal amplitude.
- Log the RMS value and `AudioRecord` state for every buffer read.
- Fail explicitly if `AudioRecord.read()` returns an error code.

### [Call Presentation Layer]

#### [MODIFY] [CallScreen.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/CallScreen.kt)
- Add a log to verify the permission status immediately before `viewModel.startRecording()`.

## Verification Plan

### Automated Tests
- Run `./gradlew :app:assembleDebug` to verify no syntax errors.

### Manual Verification
- Deploy to the emulator.
- Open Logcat and filter for "AndroidAudioRecorder".
- Speak into the microphone and check for `Buffer RMS` values significantly greater than 0.
- Verify that `debug_upload.wav` on the backend now contains audible speech.
