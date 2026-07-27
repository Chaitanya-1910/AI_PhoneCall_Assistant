package com.chaya.domain.call.model

sealed class TelephonyEvent {
    data class IncomingCall(val number: String, val sessionId: String) : TelephonyEvent()
    data class OutgoingCallStarted(val number: String, val sessionId: String) : TelephonyEvent()
    data class CallAnswered(val sessionId: String) : TelephonyEvent()
    data class CallDisconnected(val sessionId: String, val reason: String? = null) : TelephonyEvent()
    data class CallFailed(val sessionId: String, val error: String? = null) : TelephonyEvent()
    data class MissedCall(val sessionId: String, val number: String) : TelephonyEvent()
    data class CallRejected(val sessionId: String) : TelephonyEvent()
    data class UnknownState(val sessionId: String, val state: String) : TelephonyEvent()
}
