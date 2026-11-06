# Walkthrough - Network Audit and Diagnostics

I have implemented comprehensive diagnostic logging to trace the Android networking flow and identify why `POST` requests are not reaching the backend.

## Changes Made

### Network Layer

#### [NEW] [NetworkDiagnosticInterceptor.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/data/remote/interceptor/NetworkDiagnosticInterceptor.kt)
- Logs every outgoing request: `--> SENDING REQUEST: METHOD URL`.
- Logs every incoming response: `<-- RECEIVED RESPONSE (CODE) for: URL`.
- Logs any `IOException` (e.g., Connection Refused, Timeout) with a full stack trace.

#### [MODIFY] [NetworkModule.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/di/NetworkModule.kt)
- Registered `NetworkDiagnosticInterceptor` so it is automatically used by Retrofit.

#### [MODIFY] [ApiClient.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/core/network/ApiClient.kt)
- Added logging of the base URL whenever a Retrofit service is created.

### Data Layer

#### [MODIFY] [CallRepositoryImpl.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/data/repository/CallRepositoryImpl.kt)
- Added logs for:
    - `PREPARING UPLOAD`: File path and size.
    - `CALLING api.processAudio...`: Just before the Retrofit call.
    - `api.processAudio SUCCESS`: Upon successful completion.

### Presentation Layer

#### [MODIFY] [CallViewModel.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/CallViewModel.kt)
- Added logs to trace the entire flow:
    - `startRecording()`
    - `stopRecording()`
    - `executePipeline()`
    - Exception handling with full stack traces (`Timber.e(e, "executePipeline failed")`).

## Verification Results

### Automated Tests
- Executed `./gradlew :app:assembleDebug`
- **Result**: `Build finished successfully.`

## How to Debug

1.  **Open Logcat** in Android Studio.
2.  **Filter by Tag**:
    - `NetworkDiag`: To see exact URLs and response codes.
    - `CallViewModel`: To see the UI -> Repository flow.
    - `ApiClient`: To confirm the base URL.
    - `OkHttp`: To see full request/response bodies.
3.  **Trace the Execution**:
    - If you see `CALLING api.processAudio...` but NO `NetworkDiag` log, the request is hanging or failing inside OkHttp/Retrofit initialization.
    - If you see `executePipeline failed`, the logs will contain the exact exception causing the "Network error" UI.
