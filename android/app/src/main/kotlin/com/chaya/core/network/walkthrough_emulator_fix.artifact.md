# Walkthrough - Emulator Networking Fix

I have implemented dynamic API URL switching to ensure the app works seamlessly on both the Android Emulator and physical devices without manual configuration changes.

## Changes Made

### Core Configuration
#### [AppConfig.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/core/config/AppConfig.kt)
- **Emulator Detection**: Added a robust `isEmulator()` helper method using `android.os.Build` properties.
- **Dynamic URL Selection**: Updated `fromBuildConfig()` to automatically redirect networking traffic:
    - If `DEBUG` is true AND `isEmulator()` is true:
        - Replaces `192.168.x.x`, `localhost`, or `127.0.0.1` in the base URL with `10.0.2.2`.
    - Otherwise:
        - Uses the original `BuildConfig.API_BASE_URL`.

### Security Configuration
#### [network_security_config.xml](file:///C:/Projects/CHAYA/android/app/src/debug/res/xml/network_security_config.xml)
- Added `10.0.2.2` and `localhost` to the permitted cleartext domains. This prevents the `Cleartext HTTP traffic not permitted` exception when running in the emulator.

## Verification Results

### Automated Tests
- Executed `./gradlew :app:assembleDebug`
- **Result**: `Build finished successfully.`

## Summary of Logic
| Environment | BuildConfig.API_BASE_URL | Resulting API URL |
| :--- | :--- | :--- |
| **Physical Device** | `http://192.168.0.8:8000` | `http://192.168.0.8:8000` |
| **Emulator (Debug)** | `http://192.168.0.8:8000` | `http://10.0.2.2:8000` |

> [!TIP]
> You can verify the active URL by checking Logcat for the `ApiClient` tag:
> `D/ApiClient: Creating service: ChayaApiService with base URL: http://10.0.2.2:8000/`
