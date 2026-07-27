package com.chaya.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class PipelineMetricsDto(
    @SerialName("stt_latency_ms") val sttLatencyMs: Int,
    @SerialName("llm_latency_ms") val llmLatencyMs: Int,
    @SerialName("tts_latency_ms") val ttsLatencyMs: Int,
    @SerialName("total_latency_ms") val totalLatencyMs: Int
)

@Serializable
data class PipelineResponseDto(
    @SerialName("request_id") val requestId: String,
    @SerialName("conversation_id") val conversationId: String,
    val transcript: String,
    val response: String,
    @SerialName("audio_url") val audioUrl: String,
    val metrics: PipelineMetricsDto
)

@Serializable
data class ErrorDetailDto(
    val code: String,
    val message: String,
    val stage: String? = null
)

@Serializable
data class ErrorResponseDto(
    @SerialName("request_id") val requestId: String?,
    val error: ErrorDetailDto
)
