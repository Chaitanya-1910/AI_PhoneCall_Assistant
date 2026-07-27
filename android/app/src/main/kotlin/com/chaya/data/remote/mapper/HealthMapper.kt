package com.chaya.data.remote.mapper

import com.chaya.data.remote.dto.HealthResponseDto
import com.chaya.domain.model.HealthStatus

fun HealthResponseDto.toDomain(): HealthStatus = HealthStatus(
    status = status,
    service = service,
    environment = environment,
)
