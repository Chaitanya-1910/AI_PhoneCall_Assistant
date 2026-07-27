package com.chaya.core.network

import com.chaya.core.common.Result
import com.chaya.di.IoDispatcher
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext
import retrofit2.HttpException
import java.io.IOException
import java.net.SocketTimeoutException

/**
 * Safely execute a network call and map exceptions to [Result].
 */
suspend fun <T> safeApiCall(
    dispatcher: CoroutineDispatcher,
    call: suspend () -> T,
): Result<T> = withContext(dispatcher) {
    try {
        Result.Success(call())
    } catch (e: HttpException) {
        Result.Error(e, "HTTP ${e.code()}: ${e.message()}")
    } catch (e: SocketTimeoutException) {
        Result.Error(e, "Request timed out")
    } catch (e: IOException) {
        Result.Error(e, "Network error: ${e.message}")
    } catch (e: Exception) {
        Result.Error(e, e.message ?: "Unknown error")
    }
}
