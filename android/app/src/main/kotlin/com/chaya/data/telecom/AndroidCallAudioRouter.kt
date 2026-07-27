package com.chaya.data.telecom

import android.content.Context
import android.media.AudioManager
import com.chaya.domain.telecom.CallAudioRouter
import com.chaya.domain.telecom.model.AudioRoute
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

class AndroidCallAudioRouter @Inject constructor(
    private val context: Context
) : CallAudioRouter {

    private val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager

    private val _currentRoute = MutableStateFlow(AudioRoute.SPEAKER)
    override val currentRoute: StateFlow<AudioRoute> = _currentRoute.asStateFlow()

    private val _availableRoutes = MutableStateFlow(
        listOf(AudioRoute.SPEAKER, AudioRoute.EARPIECE, AudioRoute.BLUETOOTH, AudioRoute.WIRED_HEADSET)
    )
    override val availableRoutes: StateFlow<List<AudioRoute>> = _availableRoutes.asStateFlow()

    override fun setRoute(route: AudioRoute) {
        // Simplified route setting for diagnostics/phase 7
        _currentRoute.value = route
        when (route) {
            AudioRoute.SPEAKER -> audioManager.isSpeakerphoneOn = true
            AudioRoute.EARPIECE -> audioManager.isSpeakerphoneOn = false
            AudioRoute.BLUETOOTH -> audioManager.startBluetoothSco()
            AudioRoute.WIRED_HEADSET -> audioManager.isSpeakerphoneOn = false
        }
    }
}
