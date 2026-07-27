package com.chaya.domain.telecom

import com.chaya.domain.telecom.model.CallCapabilities

interface CallCapabilityProvider {
    fun getCapabilities(): CallCapabilities
}
