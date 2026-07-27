package com.chaya.data.audio

import android.content.Context
import android.media.AudioDeviceInfo
import android.media.AudioManager
import android.os.Build
import com.chaya.domain.audio.AudioRoute
import com.chaya.domain.audio.AudioRouteManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class AndroidAudioRouteManager(context: Context) : AudioRouteManager {

    private val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
    private val _currentRoute = MutableStateFlow(AudioRoute.SPEAKER)
    override val currentRoute: StateFlow<AudioRoute> = _currentRoute.asStateFlow()

    override fun setRoute(route: AudioRoute) {
        when (route) {
            AudioRoute.SPEAKER -> {
                audioManager.isSpeakerphoneOn = true
                audioManager.isBluetoothScoOn = false
            }
            AudioRoute.EARPIECE -> {
                audioManager.isSpeakerphoneOn = false
                audioManager.isBluetoothScoOn = false
            }
            AudioRoute.BLUETOOTH -> {
                audioManager.startBluetoothSco()
                audioManager.isBluetoothScoOn = true
                audioManager.isSpeakerphoneOn = false
            }
            AudioRoute.WIRED_HEADSET -> {
                audioManager.isSpeakerphoneOn = false
            }
        }
        _currentRoute.value = route
    }
}
