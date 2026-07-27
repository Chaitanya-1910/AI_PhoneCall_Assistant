package com.chaya.domain.telecom.model

data class AudioCapabilities(
    val supportsMicrophone: Boolean,
    val supportsBluetooth: Boolean,
    val supportsWiredHeadset: Boolean,
    val supportsSpeaker: Boolean,
    val supportsTelecomAudioStream: Boolean,
    val telecomAudioLimitation: String?
)
