package com.chaya.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class HealthResponseDto(
    val status: String,
    val service: String,
    val environment: String,
)
