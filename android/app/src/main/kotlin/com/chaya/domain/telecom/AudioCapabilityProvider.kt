package com.chaya.domain.telecom

import com.chaya.domain.telecom.model.AudioCapabilities

interface AudioCapabilityProvider {
    fun getAudioCapabilities(): AudioCapabilities
}
