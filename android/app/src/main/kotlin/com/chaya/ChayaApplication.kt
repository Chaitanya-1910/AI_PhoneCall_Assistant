package com.chaya

import android.app.Application
import com.chaya.core.logging.Logger
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class ChayaApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        Logger.init(isDebug = BuildConfig.DEBUG)
        Logger.i("ChayaApplication", "Application started")
    }
}
