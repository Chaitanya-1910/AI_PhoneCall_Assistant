package com.chaya.di

import android.content.Context
import com.chaya.data.audio.AndroidAudioFocusManager
import com.chaya.data.audio.AndroidAudioRecorder
import com.chaya.data.audio.AndroidAudioRouteManager
import com.chaya.data.audio.AndroidAudioSessionManager
import com.chaya.data.audio.Media3AudioPlayer
import com.chaya.domain.audio.AudioFocusManager
import com.chaya.domain.audio.AudioPlayer
import com.chaya.domain.audio.AudioRecorder
import com.chaya.domain.audio.AudioRouteManager
import com.chaya.domain.audio.AudioSessionManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AudioModule {

    @Provides
    @Singleton
    fun provideAudioPlayer(
        @ApplicationContext context: Context
    ): AudioPlayer {
        return Media3AudioPlayer(context)
    }

    @Provides
    @Singleton
    fun provideAudioRecorder(
        @ApplicationContext context: Context
    ): AudioRecorder {
        return AndroidAudioRecorder(context)
    }

    @Provides
    @Singleton
    fun provideAudioFocusManager(
        @ApplicationContext context: Context
    ): AudioFocusManager {
        return AndroidAudioFocusManager(context)
    }

    @Provides
    @Singleton
    fun provideAudioRouteManager(
        @ApplicationContext context: Context
    ): AudioRouteManager {
        return AndroidAudioRouteManager(context)
    }

    @Provides
    @Singleton
    fun provideAudioSessionManager(
        @ApplicationContext context: Context
    ): AudioSessionManager {
        return AndroidAudioSessionManager(context)
    }
}
