package com.chaya.domain.audio

import com.chaya.domain.model.audio.AudioSource

/**
 * Domain interface for recording audio from the device microphone.
 */
interface AudioRecorder {
    /**
     * Starts recording audio.
     */
    fun start()

    /**
     * Stops recording and returns the AudioSource representing the recorded file.
     */
    suspend fun stop(): AudioSource.File?

    /**
     * Cancels the current recording and discards the file.
     */
    fun cancel()
}
