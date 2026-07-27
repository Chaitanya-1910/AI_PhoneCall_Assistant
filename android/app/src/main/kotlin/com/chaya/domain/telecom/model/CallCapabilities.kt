package com.chaya.domain.telecom.model

data class CallCapabilities(
    val supportsCallScreening: Boolean,
    val supportsInCallService: Boolean,
    val isDefaultDialer: Boolean,
    val supportsCallAudio: Boolean,
    val supportsAnswering: Boolean,
    val supportsHold: Boolean,
    val androidVersion: String,
    val apiLevel: Int
)
