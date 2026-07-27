package com.chaya.domain.telecom

import kotlinx.coroutines.flow.StateFlow

interface TelecomManager {
    val activeSession: StateFlow<CallSession?>
}
