# Walkthrough - Fix Unresolved Reference 'Transitions'

I have fixed the build error `Unresolved reference 'Transitions'` in `MainScreen.kt` by expanding the `ChayaMotion` object in `Motion.kt`.

## Changes Made

### [Presentation Layer]

#### [Motion.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/theme/Motion.kt)

- Added nested `Duration`, `Springs`, and `Transitions` objects to `ChayaMotion`.
- Defined `Transitions.FadeIn` and `Transitions.FadeOut` using standard durations.
- Mapped existing top-level properties like `defaultSpring` and `fastFadeIn` to the new nested structures to maintain backward compatibility.
- Added `Duration.Medium` (300ms) and `Duration.Short` (150ms) tokens.

## Verification Results

### Automated Tests
- Ran `:app:compileDebugKotlin`.
- **Result**: The error `Unresolved reference 'Transitions'` in `MainScreen.kt:55:45` is no longer present in the build output.
- *Note*: While there are other unrelated build errors in the project, the specific issue reported has been resolved.
