package com.chaya.domain.audio

/**
 * Domain interface for configuring the Android audio session (e.g. MODE_IN_COMMUNICATION).
 */
interface AudioSessionManager {
    fun startSession()
    fun endSession()
}
