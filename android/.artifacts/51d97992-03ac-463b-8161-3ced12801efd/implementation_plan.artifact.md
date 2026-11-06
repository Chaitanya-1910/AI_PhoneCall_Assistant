# Fix Compilation Errors related to Nullable startTime in CallSession

The project is failing to compile because `CallSession.startTime` is a nullable `Long?`, but it's being used in contexts where a non-nullable `Long` is required (e.g., `java.util.Date` constructor, function parameters, and sorting).

## Proposed Changes

### [Domain Layer]

#### [MODIFY] [CallManagerImpl.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/domain/call/CallManagerImpl.kt)
- Update `getAllSessions` to handle nullable `startTime` during sorting.

### [Presentation Layer]

#### [MODIFY] [HomeScreen.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/screens/home/HomeScreen.kt)
- Safely format the timestamp in `RecentCallItem`, handling the case where `startTime` might be null.

#### [MODIFY] [HomeViewModel.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/screens/home/HomeViewModel.kt)
- Update `isToday` to accept a nullable `Long?` and handle it gracefully.
- Update the usage of `isToday` in `loadDashboardData` if necessary (though updating the signature should suffice).

## Verification Plan

### Automated Tests
- Run `./gradlew :app:compileDebugKotlin` to ensure all compilation errors are resolved.
- Run existing unit tests: `./gradlew :app:testDebugUnitTest`.

### Manual Verification
- Deploy the app to an emulator/device and verify that the "Recent Calls" section on the Dashboard displays timestamps correctly (or "N/A" if missing).
