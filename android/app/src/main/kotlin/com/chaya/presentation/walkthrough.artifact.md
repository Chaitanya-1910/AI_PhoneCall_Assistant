# Walkthrough - Fix Missing Permission Dialog

I have resolved the issue where clicking the "Grant Permission" button did not trigger the Android permission dialog.

## Changes Made

### App Manifest
#### [AndroidManifest.xml](file:///C:/Projects/CHAYA/android/app/src/AndroidManifest.xml)
- Added `<uses-permission android:name="android.permission.RECORD_AUDIO" />`.
- **Root Cause**: The system ignores runtime permission requests if the permission is not also declared in the manifest.

### Call Screen
#### [CallScreen.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/CallScreen.kt)
- **Logging**: Added `Log.d` statements to track the permission request lifecycle:
    - Before `permissionLauncher.launch()`.
    - Inside the callback with the `isGranted` result.
- **Verification**: Confirmed that `permissionLauncher` is correctly initialized using `rememberLauncherForActivityResult`.
- **Bypass Logic**: Verified that the existing `LaunchedEffect` correctly checks the permission state on composition and bypasses the `PermissionRequired` state if `RECORD_AUDIO` is already granted.

## Verification Results

### Automated Tests
- Executed `./gradlew :app:assembleDebug`
- **Result**: `Build finished successfully.`

### Manual Verification Path
1. **Launch App**: The app should now correctly transition between the Permission and Idle screens based on existing grants.
2. **Click Button**: Clicking "Grant Permission" will now invoke the system dialog because it is declared in the manifest.
3. **Logcat**: Filter for "CallScreen" to see:
    - `Launching RECORD_AUDIO permission request`
    - `Permission result: isGranted=true` (or false)
