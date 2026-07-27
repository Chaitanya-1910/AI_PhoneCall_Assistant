package com.chaya.data.audio

import android.content.Context
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import com.chaya.domain.audio.AudioPlayer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import timber.log.Timber

/**
 * Jetpack Media3 implementation of the AudioPlayer domain interface.
 */
class Media3AudioPlayer(
    private val context: Context
) : AudioPlayer, Player.Listener {

    private var player: ExoPlayer? = null
    
    private val _isPlaying = MutableStateFlow(false)
    override val isPlaying: StateFlow<Boolean> = _isPlaying.asStateFlow()

    init {
        initializePlayer()
    }

    private fun initializePlayer() {
        if (player == null) {
            player = ExoPlayer.Builder(context).build().apply {
                addListener(this@Media3AudioPlayer)
            }
        }
    }

    override fun play(uri: String) {
        try {
            initializePlayer()
            val mediaItem = MediaItem.fromUri(uri)
            player?.apply {
                setMediaItem(mediaItem)
                prepare()
                play()
            }
        } catch (e: Exception) {
            Timber.e(e, "Error playing audio from URI: $uri")
        }
    }

    override fun pause() {
        player?.pause()
    }

    override fun stop() {
        player?.stop()
        player?.clearMediaItems()
        _isPlaying.value = false
    }

    override fun release() {
        player?.removeListener(this)
        player?.release()
        player = null
        _isPlaying.value = false
    }

    override fun onIsPlayingChanged(isPlaying: Boolean) {
        _isPlaying.value = isPlaying
    }

    override fun onPlaybackStateChanged(playbackState: Int) {
        if (playbackState == Player.STATE_ENDED) {
            _isPlaying.value = false
        }
    }
}
