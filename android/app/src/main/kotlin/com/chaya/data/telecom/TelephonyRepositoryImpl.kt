package com.chaya.data.telecom

import com.chaya.domain.call.model.TelephonyEvent
import com.chaya.domain.call.repository.TelephonyRepository
import kotlinx.coroutines.flow.Flow

class TelephonyRepositoryImpl(
    private val telephonySource: AndroidTelephonySource
) : TelephonyRepository {

    override fun observeCallEvents(): Flow<TelephonyEvent> {
        return telephonySource.observeEvents()
    }
}
