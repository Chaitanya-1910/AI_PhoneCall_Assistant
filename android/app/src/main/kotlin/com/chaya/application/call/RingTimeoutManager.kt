package com.chaya.application.call

import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds

class RingTimeoutManager(
    private val defaultTimeout: Duration = 15.seconds,
    private val dispatcher: CoroutineDispatcher = Dispatchers.Default
) {
    private val scope = CoroutineScope(dispatcher)
    private var timeoutJob: Job? = null

    private val _timeoutEvents = MutableSharedFlow<String>()
    val timeoutEvents: SharedFlow<String> = _timeoutEvents.asSharedFlow()

    fun startTimer(sessionId: String, timeout: Duration = defaultTimeout) {
        timeoutJob?.cancel()
        timeoutJob = scope.launch {
            delay(timeout)
            _timeoutEvents.emit(sessionId)
        }
    }

    fun cancelTimer() {
        timeoutJob?.cancel()
        timeoutJob = null
    }
}
