package com.chaya.data.repository

import com.chaya.core.common.Result
import com.chaya.core.network.safeApiCall
import com.chaya.data.remote.api.ChayaApiService
import com.chaya.data.remote.mapper.toDomain
import com.chaya.di.IoDispatcher
import com.chaya.domain.model.HealthStatus
import com.chaya.domain.repository.HealthRepository
import kotlinx.coroutines.CoroutineDispatcher
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class HealthRepositoryImpl @Inject constructor(
    private val apiService: ChayaApiService,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher,
) : HealthRepository {

    override suspend fun getHealthStatus(): Result<HealthStatus> =
        safeApiCall(ioDispatcher) { apiService.getHealth().toDomain() }
}
