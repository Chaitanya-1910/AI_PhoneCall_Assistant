package com.chaya.domain.model.audio

/**
 * Represents an abstracted audio source for processing.
 */
sealed interface AudioSource {
    /**
     * Audio captured directly from the device microphone.
     */
    object Microphone : AudioSource

    /**
     * Audio from the telecom stream (active call).
     */
    object Telecom : AudioSource

    /**
     * An audio file on the local filesystem.
     */
    data class File(val filePath: String) : AudioSource

    /**
     * An audio file bundled in the app's raw resources.
     */
    data class RawResource(val resourceId: Int) : AudioSource
}
