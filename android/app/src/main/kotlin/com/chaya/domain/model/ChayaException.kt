package com.chaya.domain.model

sealed class ChayaException(message: String, cause: Throwable? = null) : Exception(message, cause) {
    
    /**
     * Network/Timeout or Server issues (502, 503, 504) that are safe to retry.
     */
    class TransientFailure(message: String, cause: Throwable? = null) : ChayaException(message, cause)
    
    /**
     * Client errors (400, 422, etc.) or unknown critical errors that shouldn't be retried.
     */
    class FatalFailure(message: String, cause: Throwable? = null) : ChayaException(message, cause)
}
