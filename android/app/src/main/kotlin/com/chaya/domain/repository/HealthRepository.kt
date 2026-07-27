package com.chaya.domain.repository

import com.chaya.core.common.Result
import com.chaya.domain.model.HealthStatus

/**
 * Contract for backend connectivity and health checks.
 */
interface HealthRepository {
    suspend fun getHealthStatus(): Result<HealthStatus>
}
