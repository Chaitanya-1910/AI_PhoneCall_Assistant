package com.chaya.data.remote.interceptor

import okhttp3.Interceptor
import okhttp3.Response
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Propagates a correlation ID to the backend for distributed tracing.
 * Mirrors backend RequestContextMiddleware (X-Request-ID).
 */
@Singleton
class RequestIdInterceptor @Inject constructor() : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .header(REQUEST_ID_HEADER, UUID.randomUUID().toString())
            .build()
        return chain.proceed(request)
    }

    companion object {
        const val REQUEST_ID_HEADER = "X-Request-ID"
    }
}
