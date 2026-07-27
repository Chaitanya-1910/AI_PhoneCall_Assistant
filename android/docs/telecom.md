# Android Telecom Integration Layer

This document outlines the Telecom capability layer for the CHAYA Android client (Phase 7).

## Architecture

The Telecom logic is firmly grounded in Clean Architecture principles:

*   **Domain**: Defines capability models (`CallCapabilities`), states (`TelecomCallState`), and routing constants (`AudioRoute`). It provides pure interfaces (`CallSession`, `CallCapabilityProvider`, `TelecomManager`, `CallAudioRouter`, `CallStateMonitor`).
*   **Infrastructure (Data)**: The `Android*` adapter classes implement these interfaces by deeply integrating with `android.telecom.TelecomManager`, `android.media.AudioManager`, and OS version checks.
*   **Presentation**: Diagnostics UI exposes the raw Android capability facts to developers without tying the logic to specific UI screens.

## Supported Android APIs

*   **InCallService**: Supported strictly on Android M (API 23) and above. CHAYA must be set as the Default Dialer by the user to leverage this.
*   **CallScreeningService**: Supported on Android N (API 24) and above. Allows intercepting and silently rejecting spam without ringing.
*   **Audio Routing**: Relies on `AudioManager` (SCO Bluetooth routing, Speakerphone toggles) alongside `ConnectionService`/`InCallService` native audio streams.
*   **Answering Calls**: Requires `ANSWER_PHONE_CALLS` permission (Android O / API 26+) or system-level intents.

## Capability Detection

We never blindly assume access. The `AndroidCallCapabilityProvider` verifies:
*   OS Version (`Build.VERSION.SDK_INT`)
*   Granted manifest permissions.
*   Default Dialer package identity via `TelecomManager.defaultDialerPackage`.

This defensive strategy prevents `SecurityExceptions` and hard crashes on strict OEM environments.

## Limitations & OEM Restrictions

*   Certain OEMs (e.g., Xiaomi, Samsung) aggressively kill background services, which can sever the `InCallService` connection.
*   Without being the Default Dialer, CHAYA cannot reliably answer or record call audio on Android 10+ due to `VoiceCommunication` capture restrictions.
*   We do not bypass standard OS permission prompts.

## Extension Points

Before live integration is permitted (Phase 8), we must:
1.  Launch the `ACTION_CHANGE_DEFAULT_DIALER` intent and let the user opt-in.
2.  Implement the actual `InCallService` class extending `android.telecom.InCallService`.
3.  Implement the `CallScreeningService` to intercept calls.
4.  Pipe the system's live audio byte stream down into our existing `CallRepositoryImpl` which connects directly to the backend `ConversationManager`.
