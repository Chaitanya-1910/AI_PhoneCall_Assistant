package com.chaya.domain.audio

import kotlinx.coroutines.flow.Flow

enum class AudioRoute {
    SPEAKER,
    WIRED_HEADSET,
    BLUETOOTH,
    EARPIECE
}

/**
 * Domain interface for detecting and managing audio routes.
 */
interface AudioRouteManager {
    val currentRoute: Flow<AudioRoute>
    
    fun setRoute(route: AudioRoute)
}
