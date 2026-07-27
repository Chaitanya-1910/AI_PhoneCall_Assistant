package com.chaya.di

import android.content.Context
import com.chaya.data.telecom.AndroidCallAudioRouter
import com.chaya.data.telecom.AndroidCallCapabilityProvider
import com.chaya.data.telecom.AndroidCallStateMonitor
import com.chaya.domain.telecom.CallAudioRouter
import com.chaya.domain.telecom.CallCapabilityProvider
import com.chaya.domain.telecom.CallStateMonitor
import com.chaya.domain.telecom.DialerRoleManager
import com.chaya.domain.telecom.TelecomManager
import com.chaya.domain.telecom.AudioCapabilityProvider
import com.chaya.domain.telecom.AudioSourceManager
import com.chaya.data.telecom.AndroidDialerRoleManager
import com.chaya.data.telecom.AndroidTelecomManager
import com.chaya.data.telecom.AndroidAudioCapabilityProvider
import com.chaya.data.telecom.AndroidAudioSourceManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object TelecomModule {

    @Provides
    @Singleton
    fun provideCallCapabilityProvider(
        @ApplicationContext context: Context
    ): CallCapabilityProvider {
        return AndroidCallCapabilityProvider(context)
    }

    @Provides
    @Singleton
    fun provideCallAudioRouter(
        @ApplicationContext context: Context
    ): CallAudioRouter {
        return AndroidCallAudioRouter(context)
    }

    @Provides
    @Singleton
    fun provideCallStateMonitor(
        monitor: AndroidCallStateMonitor
    ): CallStateMonitor {
        return monitor
    }

    @Provides
    @Singleton
    fun provideDialerRoleManager(
        @ApplicationContext context: Context
    ): DialerRoleManager {
        return AndroidDialerRoleManager(context)
    }

    @Provides
    @Singleton
    fun provideTelecomManager(
        androidTelecomManager: AndroidTelecomManager
    ): TelecomManager {
        return androidTelecomManager
    }

    @Provides
    @Singleton
    fun provideAudioCapabilityProvider(
        @ApplicationContext context: Context,
        dialerRoleManager: DialerRoleManager
    ): AudioCapabilityProvider {
        return AndroidAudioCapabilityProvider(context, dialerRoleManager)
    }

    @Provides
    @Singleton
    fun provideAudioSourceManager(
        androidAudioSourceManager: AndroidAudioSourceManager
    ): AudioSourceManager {
        return androidAudioSourceManager
    }
}
