package com.chaya.domain.audio

import kotlinx.coroutines.flow.Flow

/**
 * Domain interface for playing audio.
 * Decouples the ViewModel from the underlying ExoPlayer/Media3 implementation.
 */
interface AudioPlayer {
    
    /**
     * Flow of the current playback state (e.g. playing, paused, completed).
     */
    val isPlaying: Flow<Boolean>

    /**
     * Prepares and starts playback of the audio at the specified URI.
     */
    fun play(uri: String)
    
    /**
     * Pauses the current playback.
     */
    fun pause()
    
    /**
     * Stops playback and resets the player.
     */
    fun stop()
    
    /**
     * Releases any resources held by the player.
     */
    fun release()
}
