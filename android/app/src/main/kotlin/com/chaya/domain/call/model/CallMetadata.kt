package com.chaya.domain.call.model

data class CallMetadata(
    val language: String? = null,
    val recordingDuration: Long? = null,
    val aiModel: String? = null,
    val notes: String? = null
)
