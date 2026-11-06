package com.chaya.di

import com.chaya.domain.call.CallManager
import com.chaya.domain.call.CallManagerImpl
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class CallModule {

    @Binds
    @Singleton
    abstract fun bindCallManager(
        impl: CallManagerImpl
    ): CallManager
}
