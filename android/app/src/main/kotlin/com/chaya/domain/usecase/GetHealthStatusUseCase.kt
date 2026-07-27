package com.chaya.domain.usecase

import com.chaya.core.common.NoParamUseCase
import com.chaya.core.common.Result
import com.chaya.domain.model.HealthStatus
import com.chaya.domain.repository.HealthRepository
import javax.inject.Inject

class GetHealthStatusUseCase @Inject constructor(
    private val healthRepository: HealthRepository,
) : NoParamUseCase<Result<HealthStatus>> {

    override suspend fun invoke(): Result<HealthStatus> =
        healthRepository.getHealthStatus()
}
