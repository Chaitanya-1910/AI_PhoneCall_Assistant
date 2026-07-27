package com.chaya.data.telecom

import com.chaya.domain.telecom.CallStateMonitor
import com.chaya.domain.telecom.model.TelecomCallState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AndroidCallStateMonitor @Inject constructor() : CallStateMonitor {
    
    private val _activeCallState = MutableStateFlow(TelecomCallState.IDLE)
    override val activeCallState: StateFlow<TelecomCallState> = _activeCallState.asStateFlow()

    private var currentJob: kotlinx.coroutines.Job? = null
    private val scope = kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Default)

    fun updateStateFlow(stateFlow: StateFlow<TelecomCallState>) {
        currentJob?.cancel()
        currentJob = scope.launch {
            stateFlow.collect { state ->
                _activeCallState.value = state
            }
        }
    }

    fun reset() {
        currentJob?.cancel()
        _activeCallState.value = TelecomCallState.IDLE
    }
}
