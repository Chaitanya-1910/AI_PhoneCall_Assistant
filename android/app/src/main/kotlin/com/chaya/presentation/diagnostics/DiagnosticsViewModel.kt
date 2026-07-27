package com.chaya.presentation.diagnostics

import androidx.lifecycle.ViewModel
import com.chaya.domain.telecom.CallAudioRouter
import com.chaya.domain.telecom.CallCapabilityProvider
import com.chaya.domain.telecom.CallStateMonitor
import com.chaya.domain.telecom.DialerRoleManager
import com.chaya.domain.telecom.AudioCapabilityProvider
import com.chaya.domain.telecom.AudioSourceManager
import com.chaya.domain.model.audio.AudioSource
import com.chaya.domain.telecom.model.AudioRoute
import com.chaya.domain.telecom.model.CallCapabilities
import com.chaya.domain.telecom.model.TelecomCallState
import com.chaya.domain.telecom.model.AudioCapabilities
import dagger.hilt.android.lifecycle.HiltViewModel
import android.content.Intent
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class DiagnosticsViewModel @Inject constructor(
    private val capabilityProvider: CallCapabilityProvider,
    private val audioRouter: CallAudioRouter,
    private val dialerRoleManager: DialerRoleManager,
    private val stateMonitor: CallStateMonitor,
    private val audioCapabilityProvider: AudioCapabilityProvider,
    private val audioSourceManager: AudioSourceManager
) : ViewModel() {

    private val _capabilities = MutableStateFlow<CallCapabilities?>(null)
    val capabilities: StateFlow<CallCapabilities?> = _capabilities.asStateFlow()

    private val _audioCapabilities = MutableStateFlow<AudioCapabilities?>(null)
    val audioCapabilities: StateFlow<AudioCapabilities?> = _audioCapabilities.asStateFlow()

    val availableRoutes: StateFlow<List<AudioRoute>> = audioRouter.availableRoutes
    val currentRoute: StateFlow<AudioRoute> = audioRouter.currentRoute

    val activeCallState: StateFlow<TelecomCallState> = stateMonitor.activeCallState
    val activeAudioSource: StateFlow<AudioSource> = audioSourceManager.activeSource

    init {
        loadDiagnostics()
    }

    fun loadDiagnostics() {
        _capabilities.value = capabilityProvider.getCapabilities()
        _audioCapabilities.value = audioCapabilityProvider.getAudioCapabilities()
    }

    fun getDialerRequestIntent(): Intent? {
        return dialerRoleManager.createRequestRoleIntent()
    }
}
