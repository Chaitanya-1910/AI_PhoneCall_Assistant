package com.chaya.data.telecom

import com.chaya.domain.telecom.CallSession
import com.chaya.domain.telecom.TelecomManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AndroidTelecomManager @Inject constructor() : TelecomManager {

    private val _activeSession = MutableStateFlow<CallSession?>(null)
    override val activeSession: StateFlow<CallSession?> = _activeSession.asStateFlow()

    fun setActiveSession(session: CallSession?) {
        _activeSession.value = session
    }
}
