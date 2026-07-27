package com.chaya.domain.telecom

import com.chaya.domain.telecom.model.TelecomCallState
import kotlinx.coroutines.flow.StateFlow

interface CallStateMonitor {
    val activeCallState: StateFlow<TelecomCallState>
}
