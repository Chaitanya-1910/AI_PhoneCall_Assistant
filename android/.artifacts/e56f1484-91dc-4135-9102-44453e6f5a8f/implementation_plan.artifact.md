# Fix Compilation Errors in CHAYA Project

The project is currently failing to build due to several compilation errors in `BottomSheet.kt`, `HomeScreen.kt`, and `HomeViewModel.kt`.

## Proposed Changes

### Design System Component

#### [MODIFY] [BottomSheet.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/components/designsystem/BottomSheet.kt)
- Fix the `ModalBottomSheet` call:
    - Change the `windowInsets` parameter to `contentWindowInsets`.
    - Provide `contentWindowInsets` as a `@Composable` lambda returning `WindowInsets`.
    - Ensure all `@Composable` property accesses (like `MaterialTheme.colorScheme.surface` and `WindowInsets.navigationBars`) are in a valid context.

### Presentation Layer

#### [MODIFY] [HomeScreen.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/screens/home/HomeScreen.kt)
- Fix `RecentCallItem` component:
    - Handle nullability of `session.startTime` when creating a `Date` object for formatting.
    - Change `session.caller.name` to `session.caller.displayName` to match the `Caller` data model.

#### [MODIFY] [HomeViewModel.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/screens/home/HomeViewModel.kt)
- Fix `loadDashboardData` function:
    - Handle nullability of `it.startTime` when filtering calls using `isToday(Long)`.

## Verification Plan

### Automated Tests
- Run `./gradlew :app:compileDebugKotlin` to verify that all reported compilation errors are resolved.

### Manual Verification
- None required for build fix, but UI should be checked once deployable.
