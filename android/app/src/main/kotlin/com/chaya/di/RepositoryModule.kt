package com.chaya.di

import com.chaya.data.repository.CallRepositoryImpl
import com.chaya.data.repository.HealthRepositoryImpl
import com.chaya.domain.repository.CallRepository
import com.chaya.domain.repository.HealthRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindHealthRepository(
        impl: HealthRepositoryImpl,
    ): HealthRepository

    @Binds
    @Singleton
    abstract fun bindCallRepository(
        impl: CallRepositoryImpl,
    ): CallRepository
}
