package com.chaya.domain.call.repository

import com.chaya.domain.call.model.Caller

interface CallerResolver {
    suspend fun resolveCaller(phoneNumber: String): Caller
}
