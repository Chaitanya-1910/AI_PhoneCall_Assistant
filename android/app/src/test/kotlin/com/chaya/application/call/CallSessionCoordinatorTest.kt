package com.chaya.application.call

import com.chaya.domain.call.CallManager
import com.chaya.domain.call.model.CallOutcome
import com.chaya.domain.call.model.CallSession
import com.chaya.domain.call.model.CallState
import com.chaya.domain.call.model.Caller
import com.chaya.domain.call.model.TelephonyEvent
import com.chaya.domain.call.model.TranscriptEntry
import com.chaya.domain.call.repository.CallerResolver
import com.chaya.domain.call.repository.TelephonyRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import kotlin.time.Duration.Companion.seconds

@OptIn(ExperimentalCoroutinesApi::class)
class CallSessionCoordinatorTest {

    private val testDispatcher = StandardTestDispatcher()
    private val testScope = TestScope(testDispatcher)

    private lateinit var mockCallManager: MockCallManager
    private lateinit var mockTelephonyRepository: MockTelephonyRepository
    private lateinit var mockCallerResolver: MockCallerResolver
    private lateinit var ringTimeoutManager: RingTimeoutManager
    
    private lateinit var coordinator: CallSessionCoordinator

    @Before
    fun setUp() {
        mockCallManager = MockCallManager()
        mockTelephonyRepository = MockTelephonyRepository()
        mockCallerResolver = MockCallerResolver()
        ringTimeoutManager = RingTimeoutManager(15.seconds, testDispatcher)
        
        coordinator = CallSessionCoordinator(
            mockCallManager,
            mockTelephonyRepository,
            mockCallerResolver,
            ringTimeoutManager,
            testDispatcher
        )
    }

    @Test
    fun `IncomingCall creates session and updates state to RINGING`() = testScope.runTest {
        coordinator.start()
        
        mockTelephonyRepository.emitEvent(TelephonyEvent.IncomingCall("123", "session-1"))
        advanceUntilIdle()
        
        val session = mockCallManager.getSession("session-1")!!
        assertEquals("123", session.caller.phoneNumber)
        assertEquals(CallState.RINGING, session.callState)
        
        coordinator.stop()
    }
    
    @Test
    fun `CallAnswered cancels timeout and updates state to CONNECTED`() = testScope.runTest {
        coordinator.start()
        
        mockTelephonyRepository.emitEvent(TelephonyEvent.IncomingCall("123", "session-1"))
        advanceUntilIdle()
        
        mockTelephonyRepository.emitEvent(TelephonyEvent.CallAnswered("session-1"))
        advanceUntilIdle()
        
        val session = mockCallManager.getSession("session-1")!!
        assertEquals(CallState.CONNECTED, session.callState)
        
        coordinator.stop()
    }
    
    @Test
    fun `Ring timeout updates state to WAITING_FOR_AI`() = testScope.runTest {
        coordinator.start()
        
        mockTelephonyRepository.emitEvent(TelephonyEvent.IncomingCall("123", "session-1"))
        
        // Wait for ring timeout
        testScheduler.advanceTimeBy(15001)
        advanceUntilIdle()
        
        val session = mockCallManager.getSession("session-1")!!
        assertEquals(CallState.WAITING_FOR_AI, session.callState)
        
        coordinator.stop()
    }
    
    @Test
    fun `CallDisconnected finishes session`() = testScope.runTest {
        coordinator.start()
        
        mockTelephonyRepository.emitEvent(TelephonyEvent.IncomingCall("123", "session-1"))
        advanceUntilIdle()
        
        mockTelephonyRepository.emitEvent(TelephonyEvent.CallDisconnected("session-1"))
        advanceUntilIdle()
        
        val session = mockCallManager.getSession("session-1")!!
        assertEquals(CallState.ENDED, session.callState)
        assertEquals(CallOutcome.COMPLETED, session.outcome)
        
        coordinator.stop()
    }
}

class MockCallManager : CallManager {
    private val sessions = mutableMapOf<String, CallSession>()
    
    override fun createSession(sessionId: String, caller: Caller): CallSession {
        val session = CallSession(sessionId, caller)
        sessions[sessionId] = session
        return session
    }

    override fun getSession(sessionId: String): CallSession? = sessions[sessionId]

    override fun updateState(sessionId: String, state: CallState): CallSession {
        val session = sessions[sessionId]!!.copy(callState = state)
        sessions[sessionId] = session
        return session
    }

    override fun appendTranscript(sessionId: String, entry: TranscriptEntry): CallSession {
        return sessions[sessionId]!!
    }

    override fun finishSession(sessionId: String, outcome: CallOutcome): CallSession {
        val session = sessions[sessionId]!!.copy(callState = CallState.ENDED, outcome = outcome)
        sessions[sessionId] = session
        return session
    }

    override fun generateSummary(sessionId: String): String? = null
}

class MockTelephonyRepository : TelephonyRepository {
    private val flow = MutableSharedFlow<TelephonyEvent>()
    
    override fun observeCallEvents(): Flow<TelephonyEvent> = flow
    
    suspend fun emitEvent(event: TelephonyEvent) {
        flow.emit(event)
    }
}

class MockCallerResolver : CallerResolver {
    override suspend fun resolveCaller(phoneNumber: String): Caller {
        return Caller(phoneNumber = phoneNumber)
    }
}
