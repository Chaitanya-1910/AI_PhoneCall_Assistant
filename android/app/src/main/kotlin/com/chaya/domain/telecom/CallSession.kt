package com.chaya.domain.telecom

import com.chaya.domain.telecom.model.TelecomCallState
import kotlinx.coroutines.flow.StateFlow

interface CallSession {
    val callId: String
    val state: StateFlow<TelecomCallState>
    val callerDisplayName: String?
    val callerNumber: String?

    fun answer()
    fun reject()
    fun disconnect()
    fun hold()
    fun unhold()
}
