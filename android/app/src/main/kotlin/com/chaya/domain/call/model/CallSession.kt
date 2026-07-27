package com.chaya.domain.call.model

data class CallSession(
    val sessionId: String,
    val caller: Caller,
    val callState: CallState = CallState.INITIALIZING,
    val startTime: Long? = null,
    val endTime: Long? = null,
    val transcript: List<TranscriptEntry> = emptyList(),
    val summary: String? = null,
    val requiresCallback: Boolean = false,
    val priority: CallPriority = CallPriority.NORMAL,
    val outcome: CallOutcome? = null,
    val metadata: CallMetadata = CallMetadata()
)
