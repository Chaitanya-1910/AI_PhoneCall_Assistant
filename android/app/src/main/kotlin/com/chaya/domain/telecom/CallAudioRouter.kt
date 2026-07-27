package com.chaya.domain.telecom

import com.chaya.domain.telecom.model.AudioRoute
import kotlinx.coroutines.flow.StateFlow

interface CallAudioRouter {
    val currentRoute: StateFlow<AudioRoute>
    val availableRoutes: StateFlow<List<AudioRoute>>

    fun setRoute(route: AudioRoute)
}
