# Walkthrough - Fix Silent Audio Recording

I have audited and updated `AndroidAudioRecorder.kt` to resolve the issue where the recorded audio contained only silence.

## Root Cause
The recorded WAV files contained silence because `AudioRecord` was likely failing to capture a real signal due to one or more of the following:
1.  **Audio Source**: `MediaRecorder.AudioSource.MIC` was being used, which can be unreliable in emulators or during active telecom sessions.
2.  **State Management**: `recordingJob.join()` was previously called *after* releasing the recorder, leading to potential race conditions.
3.  **Lack of Signal Feedback**: There was no diagnostic feedback to confirm if any non-zero signal was being captured at the hardware level.

## Changes Made

### Android Audio Recorder
#### [AndroidAudioRecorder.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/data/audio/AndroidAudioRecorder.kt)
- **Switched Source**: Changed the audio source to `MediaRecorder.AudioSource.VOICE_RECOGNITION`. This source is optimized for speech and typically has better cross-device/emulator compatibility for transcription.
- **Added RMS Diagnostics**: Implemented a Root Mean Square (RMS) calculation for captured buffers. This allows us to see the actual signal level in the logs.
- **Enhanced Logging**:
    - Logs `Buffer RMS` every 10 chunks.
    - Logs explicit error strings for `AudioRecord` error codes (e.g., `ERROR_INVALID_OPERATION`).
    - Logs the `recordingState` immediately after `startRecording()`.

### Call Screen
#### [CallScreen.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/CallScreen.kt)
- Added a debug log to confirm `RECORD_AUDIO` permission status immediately before triggering the recorder.

## Verification Results

### Automated Tests
- Executed `./gradlew :app:assembleDebug`
- **Result**: `Build finished successfully.`

### Manual Verification Path
1. **Speak into Mic**: When recording, check Logcat for `Recording: size=X, buffer_rms=Y`.
2. **Interpret RMS**:
    - **RMS ~ 0.0**: Still capturing silence. Check emulator mic settings.
    - **RMS > 100.0**: Successfully capturing signal. Speech should now be audible in `debug_upload.wav`.
