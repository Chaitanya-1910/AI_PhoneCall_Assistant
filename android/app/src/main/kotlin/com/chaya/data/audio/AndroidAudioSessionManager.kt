package com.chaya.data.audio

import android.content.Context
import android.media.AudioManager
import com.chaya.domain.audio.AudioSessionManager

class AndroidAudioSessionManager(context: Context) : AudioSessionManager {
    
    private val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
    private var previousMode = AudioManager.MODE_NORMAL

    override fun startSession() {
        previousMode = audioManager.mode
        audioManager.mode = AudioManager.MODE_IN_COMMUNICATION
    }

    override fun endSession() {
        audioManager.mode = previousMode
    }
}
