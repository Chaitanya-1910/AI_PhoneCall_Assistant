package com.chaya.domain.model

/**
 * Domain representation of backend health status.
 */
data class HealthStatus(
    val status: String,
    val service: String,
    val environment: String,
) {
    val isHealthy: Boolean get() = status == "ok"
}
