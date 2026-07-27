package com.chaya.data.telecom

import android.telecom.Call
import com.chaya.domain.telecom.CallSession
import com.chaya.domain.telecom.model.TelecomCallState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class AndroidCallSession(private val nativeCall: Call) : CallSession {

    override val callId: String = nativeCall.toString()
    
    private val _state = MutableStateFlow(mapNativeState(nativeCall.state))
    override val state: StateFlow<TelecomCallState> = _state.asStateFlow()

    override val callerDisplayName: String?
        get() = nativeCall.details?.callerDisplayName?.toString()

    override val callerNumber: String?
        get() = nativeCall.details?.handle?.schemeSpecificPart

    private val callback = object : Call.Callback() {
        override fun onStateChanged(call: Call, state: Int) {
            _state.value = mapNativeState(state)
        }
    }

    init {
        nativeCall.registerCallback(callback)
    }

    override fun answer() {
        nativeCall.answer(nativeCall.details?.videoState ?: 0)
    }

    override fun reject() {
        nativeCall.reject(false, null)
    }

    override fun disconnect() {
        nativeCall.disconnect()
    }

    override fun hold() {
        nativeCall.hold()
    }

    override fun unhold() {
        nativeCall.unhold()
    }

    fun cleanup() {
        nativeCall.unregisterCallback(callback)
    }

    private fun mapNativeState(nativeState: Int): TelecomCallState {
        return when (nativeState) {
            Call.STATE_RINGING -> TelecomCallState.RINGING
            Call.STATE_ACTIVE -> TelecomCallState.ACTIVE
            Call.STATE_HOLDING -> TelecomCallState.HOLD
            Call.STATE_DISCONNECTED -> TelecomCallState.DISCONNECTED
            Call.STATE_DIALING, Call.STATE_CONNECTING -> TelecomCallState.ANSWERING
            else -> TelecomCallState.IDLE
        }
    }
}
