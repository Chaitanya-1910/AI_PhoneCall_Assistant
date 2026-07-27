package com.chaya.domain.call

import com.chaya.domain.call.model.CallOutcome
import com.chaya.domain.call.model.CallState
import com.chaya.domain.call.model.Caller
import com.chaya.domain.call.model.Speaker
import com.chaya.domain.call.model.TranscriptEntry
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test

class CallManagerTest {

    private lateinit var callManager: CallManager

    @Before
    fun setUp() {
        callManager = CallManagerImpl()
    }

    @Test
    fun `createSession initializes session with correct defaults`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        val session = callManager.createSession(sessionId, caller)

        assertEquals(sessionId, session.sessionId)
        assertEquals(caller, session.caller)
        assertEquals(CallState.INITIALIZING, session.callState)
        assertNotNull(session.startTime)
        assertTrue(session.transcript.isEmpty())
    }

    @Test
    fun `createSession throws exception if session already exists`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        callManager.createSession(sessionId, caller)

        assertThrows(IllegalArgumentException::class.java) {
            callManager.createSession(sessionId, caller)
        }
    }

    @Test
    fun `updateState updates session state correctly`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        callManager.createSession(sessionId, caller)
        
        val updatedSession = callManager.updateState(sessionId, CallState.RINGING)

        assertEquals(CallState.RINGING, updatedSession.callState)
        
        val fetchedSession = callManager.getSession(sessionId)
        assertEquals(CallState.RINGING, fetchedSession?.callState)
    }

    @Test
    fun `updateState throws IllegalStateException if transitioning from ENDED`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        callManager.createSession(sessionId, caller)
        callManager.updateState(sessionId, CallState.ENDED)

        assertThrows(IllegalStateException::class.java) {
            callManager.updateState(sessionId, CallState.RINGING)
        }
    }
    
    @Test
    fun `updateState throws IllegalStateException if transitioning from FAILED`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        callManager.createSession(sessionId, caller)
        callManager.updateState(sessionId, CallState.FAILED)

        assertThrows(IllegalStateException::class.java) {
            callManager.updateState(sessionId, CallState.RINGING)
        }
    }

    @Test
    fun `appendTranscript appends entry to session`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        callManager.createSession(sessionId, caller)
        
        val entry1 = TranscriptEntry(Speaker.CHAYA, "Hello", System.currentTimeMillis())
        callManager.appendTranscript(sessionId, entry1)
        
        val entry2 = TranscriptEntry(Speaker.CALLER, "Hi", System.currentTimeMillis())
        val updatedSession = callManager.appendTranscript(sessionId, entry2)

        assertEquals(2, updatedSession.transcript.size)
        assertEquals(entry1, updatedSession.transcript[0])
        assertEquals(entry2, updatedSession.transcript[1])
    }

    @Test
    fun `finishSession sets endTime and outcome and updates state`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        callManager.createSession(sessionId, caller)
        val finishedSession = callManager.finishSession(sessionId, CallOutcome.COMPLETED)

        assertEquals(CallState.ENDED, finishedSession.callState)
        assertEquals(CallOutcome.COMPLETED, finishedSession.outcome)
        assertNotNull(finishedSession.endTime)
        assertTrue(finishedSession.endTime!! >= finishedSession.startTime!!)
    }

    @Test
    fun `generateSummary generates placeholder when summary is null`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        callManager.createSession(sessionId, caller)
        callManager.appendTranscript(sessionId, TranscriptEntry(Speaker.CHAYA, "Hello", System.currentTimeMillis()))
        callManager.appendTranscript(sessionId, TranscriptEntry(Speaker.CALLER, "I need help", System.currentTimeMillis()))
        
        val summary = callManager.generateSummary(sessionId)

        assertNotNull(summary)
        assertTrue(summary!!.contains("CHAYA: Hello"))
        assertTrue(summary.contains("CALLER: I need help"))
        
        val session = callManager.getSession(sessionId)
        assertEquals(summary, session?.summary)
    }
    
    @Test
    fun `generateSummary returns existing summary if present`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        callManager.createSession(sessionId, caller)
        callManager.appendTranscript(sessionId, TranscriptEntry(Speaker.CHAYA, "Hello", System.currentTimeMillis()))
        
        val initialSummary = callManager.generateSummary(sessionId)
        
        callManager.appendTranscript(sessionId, TranscriptEntry(Speaker.CALLER, "Hi", System.currentTimeMillis()))
        
        val subsequentSummary = callManager.generateSummary(sessionId)
        
        assertEquals(initialSummary, subsequentSummary)
    }
    
    @Test
    fun `generateSummary handles empty transcript gracefully`() {
        val caller = Caller("+1234567890", "Test User")
        val sessionId = "test-session-1"

        callManager.createSession(sessionId, caller)
        
        val summary = callManager.generateSummary(sessionId)

        assertEquals("No transcript available for summarization.", summary)
    }
}
