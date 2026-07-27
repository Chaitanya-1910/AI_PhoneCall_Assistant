package com.chaya.domain.call.model

enum class CallState {
    INITIALIZING,
    RINGING,
    WAITING_FOR_AI,
    AI_ANSWERING,
    CONNECTED,
    CONVERSING,
    ENDING,
    ENDED,
    FAILED
}
