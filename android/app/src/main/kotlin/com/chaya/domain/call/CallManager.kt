package com.chaya.domain.call

import com.chaya.domain.call.model.CallOutcome
import com.chaya.domain.call.model.CallSession
import com.chaya.domain.call.model.CallState
import com.chaya.domain.call.model.Caller
import com.chaya.domain.call.model.TranscriptEntry

interface CallManager {
    fun createSession(sessionId: String, caller: Caller): CallSession
    fun getSession(sessionId: String): CallSession?
    fun updateState(sessionId: String, state: CallState): CallSession
    fun appendTranscript(sessionId: String, entry: TranscriptEntry): CallSession
    fun finishSession(sessionId: String, outcome: CallOutcome): CallSession
    fun generateSummary(sessionId: String): String?
}
