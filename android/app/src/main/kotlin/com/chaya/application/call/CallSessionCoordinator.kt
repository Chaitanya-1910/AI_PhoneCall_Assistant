package com.chaya.application.call

import com.chaya.domain.call.CallManager
import com.chaya.domain.call.model.CallOutcome
import com.chaya.domain.call.model.CallState
import com.chaya.domain.call.model.TelephonyEvent
import com.chaya.domain.call.repository.CallerResolver
import com.chaya.domain.call.repository.TelephonyRepository
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch

class CallSessionCoordinator(
    private val callManager: CallManager,
    private val telephonyRepository: TelephonyRepository,
    private val callerResolver: CallerResolver,
    private val ringTimeoutManager: RingTimeoutManager,
    private val dispatcher: CoroutineDispatcher = Dispatchers.Default
) {
    private val scope = CoroutineScope(dispatcher)
    private var observationJob: Job? = null
    private var timeoutObservationJob: Job? = null

    fun start() {
        observationJob?.cancel()
        observationJob = scope.launch {
            telephonyRepository.observeCallEvents().collect { event ->
                handleTelephonyEvent(event)
            }
        }

        timeoutObservationJob?.cancel()
        timeoutObservationJob = scope.launch {
            ringTimeoutManager.timeoutEvents.collect { sessionId ->
                handleRingTimeout(sessionId)
            }
        }
    }

    fun stop() {
        observationJob?.cancel()
        observationJob = null
        timeoutObservationJob?.cancel()
        timeoutObservationJob = null
        ringTimeoutManager.cancelTimer()
    }

    private suspend fun handleTelephonyEvent(event: TelephonyEvent) {
        when (event) {
            is TelephonyEvent.IncomingCall -> {
                val caller = callerResolver.resolveCaller(event.number)
                callManager.createSession(event.sessionId, caller)
                callManager.updateState(event.sessionId, CallState.RINGING)
                ringTimeoutManager.startTimer(event.sessionId)
            }
            is TelephonyEvent.CallAnswered -> {
                ringTimeoutManager.cancelTimer()
                // At this point we assume AI or User answered. 
                // Based on "Wait for AI", let's move to CONNECTED
                callManager.updateState(event.sessionId, CallState.CONNECTED)
            }
            is TelephonyEvent.CallDisconnected -> {
                ringTimeoutManager.cancelTimer()
                callManager.finishSession(event.sessionId, CallOutcome.COMPLETED)
            }
            is TelephonyEvent.CallFailed -> {
                ringTimeoutManager.cancelTimer()
                callManager.finishSession(event.sessionId, CallOutcome.FAILED)
            }
            is TelephonyEvent.MissedCall -> {
                ringTimeoutManager.cancelTimer()
                callManager.finishSession(event.sessionId, CallOutcome.MISSED)
            }
            is TelephonyEvent.CallRejected -> {
                ringTimeoutManager.cancelTimer()
                callManager.finishSession(event.sessionId, CallOutcome.DECLINED)
            }
            is TelephonyEvent.OutgoingCallStarted -> {
                val caller = callerResolver.resolveCaller(event.number)
                callManager.createSession(event.sessionId, caller)
                callManager.updateState(event.sessionId, CallState.INITIALIZING) // Or RINGING
            }
            is TelephonyEvent.UnknownState -> {
                // Log or ignore
            }
        }
    }

    private fun handleRingTimeout(sessionId: String) {
        // "When the ring timeout expires, emit a coordinator-level AI takeover request. 
        // Do not implement automatic call answering yet."
        callManager.updateState(sessionId, CallState.WAITING_FOR_AI)
    }
}
