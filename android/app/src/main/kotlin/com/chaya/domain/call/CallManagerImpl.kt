package com.chaya.domain.call

import com.chaya.domain.call.model.CallOutcome
import com.chaya.domain.call.model.CallSession
import com.chaya.domain.call.model.CallState
import com.chaya.domain.call.model.Caller
import com.chaya.domain.call.model.TranscriptEntry
import java.util.concurrent.ConcurrentHashMap

class CallManagerImpl : CallManager {
    private val sessions = ConcurrentHashMap<String, CallSession>()

    override fun createSession(sessionId: String, caller: Caller): CallSession {
        require(!sessions.containsKey(sessionId)) { "Session $sessionId already exists" }
        
        val session = CallSession(
            sessionId = sessionId,
            caller = caller,
            callState = CallState.INITIALIZING,
            startTime = System.currentTimeMillis()
        )
        sessions[sessionId] = session
        return session
    }

    override fun getSession(sessionId: String): CallSession? {
        return sessions[sessionId]
    }

    override fun updateState(sessionId: String, state: CallState): CallSession {
        val session = getExistingSession(sessionId)
        
        // Basic state validation logic could go here
        // For example, cannot go from ENDED to RINGING
        if (session.callState == CallState.ENDED || session.callState == CallState.FAILED) {
             throw IllegalStateException("Cannot transition from ${session.callState} to $state")
        }
        
        val updatedSession = session.copy(callState = state)
        sessions[sessionId] = updatedSession
        return updatedSession
    }

    override fun appendTranscript(sessionId: String, entry: TranscriptEntry): CallSession {
        val session = getExistingSession(sessionId)
        
        val newTranscript = session.transcript + entry
        val updatedSession = session.copy(transcript = newTranscript)
        sessions[sessionId] = updatedSession
        return updatedSession
    }

    override fun finishSession(sessionId: String, outcome: CallOutcome): CallSession {
        val session = getExistingSession(sessionId)
        
        val updatedSession = session.copy(
            callState = CallState.ENDED,
            endTime = System.currentTimeMillis(),
            outcome = outcome
        )
        sessions[sessionId] = updatedSession
        return updatedSession
    }

    override fun generateSummary(sessionId: String): String? {
        val session = getExistingSession(sessionId)
        
        if (session.summary != null) {
            return session.summary
        }
        
        if (session.transcript.isEmpty()) {
            return "No transcript available for summarization."
        }
        
        // Generate a placeholder summary from the first few entries
        val placeholder = session.transcript
            .take(3)
            .joinToString(separator = "\n") { "${it.speaker.name}: ${it.text}" }
            
        val summaryText = "Summary based on initial exchange:\n$placeholder"
        val updatedSession = session.copy(summary = summaryText)
        sessions[sessionId] = updatedSession
        return summaryText
    }
    
    private fun getExistingSession(sessionId: String): CallSession {
        return sessions[sessionId] ?: throw IllegalArgumentException("Session $sessionId not found")
    }
}
