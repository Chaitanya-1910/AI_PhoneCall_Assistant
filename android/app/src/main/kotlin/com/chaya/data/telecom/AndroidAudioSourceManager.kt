package com.chaya.data.telecom

import com.chaya.domain.model.audio.AudioSource
import com.chaya.domain.telecom.AudioCapabilityProvider
import com.chaya.domain.telecom.AudioSourceManager
import com.chaya.domain.telecom.CallStateMonitor
import com.chaya.domain.telecom.model.TelecomCallState
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AndroidAudioSourceManager @Inject constructor(
    private val capabilityProvider: AudioCapabilityProvider,
    private val callStateMonitor: CallStateMonitor
) : AudioSourceManager {

    private val _activeSource = MutableStateFlow<AudioSource>(AudioSource.Microphone)
    override val activeSource: StateFlow<AudioSource> = _activeSource.asStateFlow()

    private val scope = CoroutineScope(Dispatchers.Default)

    init {
        scope.launch {
            callStateMonitor.activeCallState.collect { state ->
                updateSourceBasedOnState(state)
            }
        }
    }

    private fun updateSourceBasedOnState(state: TelecomCallState) {
        val caps = capabilityProvider.getAudioCapabilities()

        if (state == TelecomCallState.ACTIVE) {
            if (caps.supportsTelecomAudioStream) {
                _activeSource.value = AudioSource.Telecom
            } else {
                // Fallback gracefully without crashing
                _activeSource.value = AudioSource.Microphone
            }
        } else {
            _activeSource.value = AudioSource.Microphone
        }
    }
}
