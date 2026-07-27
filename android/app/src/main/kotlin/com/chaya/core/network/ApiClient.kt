package com.chaya.core.network

import com.chaya.core.config.AppConfig
import com.chaya.core.logging.Logger
import kotlinx.serialization.json.Json
import okhttp3.Interceptor
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ApiClient @Inject constructor(
    private val appConfig: AppConfig,
    private val interceptors: Set<@JvmSuppressWildcards Interceptor>,
) {
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        encodeDefaults = true
    }

    private val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(NETWORK_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(NETWORK_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(NETWORK_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .apply {
                interceptors.forEach(::addInterceptor)
                if (appConfig.isDebug) {
                    addInterceptor(
                        HttpLoggingInterceptor { message ->
                            Logger.d("OkHttp", message)
                        }.apply {
                            level = HttpLoggingInterceptor.Level.BODY
                        },
                    )
                }
            }
            .build()
    }

    val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(appConfig.apiBaseUrl.ensureTrailingSlash())
            .client(okHttpClient)
            .addConverterFactory(json.asConverterFactory(JSON_MEDIA_TYPE))
            .build()
    }

    inline fun <reified T> createService(): T = retrofit.create(T::class.java)

    private fun String.ensureTrailingSlash(): String =
        if (endsWith("/")) this else "$this/"

    companion object {
        private const val NETWORK_TIMEOUT_SECONDS = 30L
        private val JSON_MEDIA_TYPE = "application/json".toMediaType()
    }
}
