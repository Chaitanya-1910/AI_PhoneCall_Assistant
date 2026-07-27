package com.chaya.domain.call.model

data class Caller(
    val phoneNumber: String,
    val displayName: String? = null,
    val isKnownContact: Boolean = false,
    val contactId: String? = null
)
