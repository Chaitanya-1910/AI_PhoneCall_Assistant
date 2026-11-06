package com.chaya.data.remote.interceptor

import com.chaya.core.logging.Logger
import okhttp3.Interceptor
import okhttp3.Response
import java.io.IOException
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Diagnostic interceptor to log every request and response.
 */
@Singleton
class NetworkDiagnosticInterceptor @Inject constructor() : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val url = request.url.toString()
        val method = request.method

        Logger.d("NetworkDiag", "--> SENDING REQUEST: $method $url")
        
        return try {
            val response = chain.proceed(request)
            val code = response.code
            Logger.d("NetworkDiag", "<-- RECEIVED RESPONSE ($code) for: $url")
            response
        } catch (e: IOException) {
            Logger.e("NetworkDiag", "!!! NETWORK ERROR for: $url", e)
            throw e
        }
    }
}
