# Implementation Plan - Network Audit and Diagnostics

The Android application is reportedly not sending `POST` requests to the backend, despite `GET` requests (like health checks) working. This plan adds comprehensive diagnostic logging to trace the network flow and identify the failure point.

## Proposed Changes

### [Network Layer]

#### [NEW] [NetworkDiagnosticInterceptor.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/data/remote/interceptor/NetworkDiagnosticInterceptor.kt)
- Create a new interceptor to log:
    - Outgoing request URL and method.
    - Incoming response status code.
    - Any `IOException` encountered during the call.

#### [MODIFY] [NetworkModule.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/di/NetworkModule.kt)
- Inject and include `NetworkDiagnosticInterceptor` in the set of interceptors provided to `ApiClient`.

#### [MODIFY] [ApiClient.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/core/network/ApiClient.kt)
- Add logging in the `init` block (or when `retrofit` is initialized) to print the `appConfig.apiBaseUrl`.
- Ensure `HttpLoggingInterceptor` is correctly logging at `BODY` level in debug builds.

### [Data Layer]

#### [MODIFY] [CallRepositoryImpl.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/data/repository/CallRepositoryImpl.kt)
- Add `Timber.d` logs before calling `api.processAudio`.
- Wrap the API call in a block that logs the response or the full stack trace of any exception.

### [Presentation Layer]

#### [MODIFY] [CallViewModel.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/CallViewModel.kt)
- Add logs in `startRecording`, `stopRecording`, and `executePipeline` to track execution through the ViewModel.

## Verification Plan

### Automated Tests
- Build the project: `./gradlew :app:assembleDebug`.

### Manual Verification
1.  **Application Startup**: Check Logcat for the "Base URL" log from `ApiClient`.
2.  **Mic Button Click**: Observe logs for `startRecording`.
3.  **Recording Stop**: Observe logs for `stopRecording` and `executePipeline`.
4.  **Network Request**:
    - Observe `NetworkDiagnosticInterceptor` and `HttpLoggingInterceptor` logs.
    - Verify if the `POST` request to `api/v1/calls/process` is initiated.
    - If it fails, capture the full stack trace from `CallRepositoryImpl` logs.
5.  **Identify Failure**: Use the logs to determine if the issue is in:
    - UseCase/Repository invocation.
    - Multipart body creation.
    - Retrofit execution.
    - Network connectivity/DNS/SSL.
