package com.chaya.data.telecom

import com.chaya.domain.call.model.TelephonyEvent
import kotlinx.coroutines.flow.Flow

interface AndroidTelephonySource {
    fun observeEvents(): Flow<TelephonyEvent>
}
