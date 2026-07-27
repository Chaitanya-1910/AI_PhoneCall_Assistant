package com.chaya.di

import com.chaya.core.config.AppConfig
import com.chaya.core.network.ApiClient
import com.chaya.data.remote.api.ChayaApiService
import com.chaya.data.remote.interceptor.RequestIdInterceptor
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.Interceptor
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideInterceptors(
        requestIdInterceptor: RequestIdInterceptor,
    ): Set<Interceptor> = setOf(requestIdInterceptor)

    @Provides
    @Singleton
    fun provideApiClient(
        appConfig: AppConfig,
        interceptors: Set<@JvmSuppressWildcards Interceptor>,
    ): ApiClient = ApiClient(appConfig, interceptors)

    @Provides
    @Singleton
    fun provideChayaApiService(apiClient: ApiClient): ChayaApiService =
        apiClient.createService()
}
