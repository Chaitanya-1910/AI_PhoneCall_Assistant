package com.chaya.application.call

import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import kotlin.time.Duration.Companion.seconds

@OptIn(ExperimentalCoroutinesApi::class)
class RingTimeoutManagerTest {

    private val testDispatcher = StandardTestDispatcher()
    private val testScope = TestScope(testDispatcher)

    @Test
    fun `startTimer emits timeout event after configured duration`() = testScope.runTest {
        val manager = RingTimeoutManager(15.seconds, testDispatcher)
        val sessionId = "session-1"

        var emittedSessionId: String? = null
        val job = launch {
            emittedSessionId = manager.timeoutEvents.first()
        }

        manager.startTimer(sessionId)
        
        // Advance time just before timeout
        advanceTimeBy(14000)
        assertTrue(emittedSessionId == null)
        
        // Advance time to timeout
        advanceTimeBy(1001)
        assertEquals(sessionId, emittedSessionId)
        
        job.cancel()
    }

    @Test
    fun `cancelTimer prevents timeout event from emitting`() = testScope.runTest {
        val manager = RingTimeoutManager(15.seconds, testDispatcher)
        val sessionId = "session-1"

        var emitted = false
        val job = launch {
            manager.timeoutEvents.collect {
                emitted = true
            }
        }

        manager.startTimer(sessionId)
        
        // Advance time slightly
        advanceTimeBy(5000)
        
        // Cancel timer
        manager.cancelTimer()
        
        // Advance past original timeout
        advanceTimeBy(15000)
        
        assertTrue(!emitted)
        
        job.cancel()
    }
}
