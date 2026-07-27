package com.chaya.domain.model

data class PipelineMetrics(
    val sttLatencyMs: Int,
    val llmLatencyMs: Int,
    val ttsLatencyMs: Int,
    val totalLatencyMs: Int
)

data class PipelineResult(
    val requestId: String,
    val conversationId: String,
    val transcript: String,
    val response: String,
    val audioUrl: String,
    val metrics: PipelineMetrics
)
