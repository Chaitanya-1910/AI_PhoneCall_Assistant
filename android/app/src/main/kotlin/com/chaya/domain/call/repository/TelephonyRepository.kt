package com.chaya.domain.call.repository

import com.chaya.domain.call.model.TelephonyEvent
import kotlinx.coroutines.flow.Flow

interface TelephonyRepository {
    fun observeCallEvents(): Flow<TelephonyEvent>
}
