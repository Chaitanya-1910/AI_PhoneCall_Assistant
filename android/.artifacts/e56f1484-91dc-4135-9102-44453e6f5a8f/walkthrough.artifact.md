# Walkthrough - Fixed ModalBottomSheet windowInsets parameter

I have fixed the compilation error in `BottomSheet.kt` caused by the renamed `windowInsets` parameter in `ModalBottomSheet`.

## Changes Made

### [Component Name]

#### [BottomSheet.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/components/designsystem/BottomSheet.kt)

```diff
-        windowInsets = WindowInsets.navigationBars,
+        contentWindowInsets = { WindowInsets.navigationBars },
```

## Verification Results

### Automated Tests
- Ran `:app:compileDebugKotlin`.
- The error in `BottomSheet.kt` is resolved.

> [!NOTE]
> While the specific error in `BottomSheet.kt` is fixed, there are other unrelated compilation errors in `HomeScreen.kt` and `HomeViewModel.kt` that prevent a full project build.
