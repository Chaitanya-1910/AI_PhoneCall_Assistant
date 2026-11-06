# Fix Unresolved Reference 'Transitions' in ChayaMotion

The build error `Unresolved reference 'Transitions'` in `MainScreen.kt` is caused by missing nested objects and members in the `ChayaMotion` object defined in `Motion.kt`. Several other components (`PremiumDialog.kt`, `PremiumButton.kt`) also reference missing members like `Duration` and `Springs`.

## Proposed Changes

### [Presentation Layer]

#### [MODIFY] [Motion.kt](file:///C:/Projects/CHAYA/android/app/src/main/kotlin/com/chaya/presentation/theme/Motion.kt)

Expand the `ChayaMotion` object to include:
- `Duration` object with `Short`, `Medium`, and `Long` constants.
- `Springs` object with `Default` and `Emphasized` specs.
- `Transitions` object with `FadeIn` and `FadeOut` animations.
- Retain existing top-level properties (`defaultSpring`, `emphasizedSpring`, `layoutSpring()`, `fastFadeIn`, `fastFadeOut`) for backward compatibility with other components.

## Verification Plan

### Automated Tests
- Run `:app:compileDebugKotlin` to ensure the project builds successfully.

### Manual Verification
- None required as this is a build-time fix.
