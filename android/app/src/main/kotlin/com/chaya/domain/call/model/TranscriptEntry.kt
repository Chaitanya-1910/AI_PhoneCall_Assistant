package com.chaya.domain.call.model

data class TranscriptEntry(
    val speaker: Speaker,
    val text: String,
    val timestamp: Long
)
