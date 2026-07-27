package com.chaya.core.config

import com.chaya.BuildConfig

/**
 * Runtime application configuration.
 * Values are injected at build time; never hardcode secrets here.
 */
data class AppConfig(
    val apiBaseUrl: String,
    val isDebug: Boolean,
) {
    companion object {
        fun fromBuildConfig(): AppConfig = AppConfig(
            apiBaseUrl = BuildConfig.API_BASE_URL,
            isDebug = BuildConfig.DEBUG,
        )
    }
}
