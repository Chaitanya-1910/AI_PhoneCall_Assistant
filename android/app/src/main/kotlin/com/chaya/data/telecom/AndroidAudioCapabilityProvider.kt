package com.chaya.data.telecom

import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import com.chaya.domain.telecom.AudioCapabilityProvider
import com.chaya.domain.telecom.DialerRoleManager
import com.chaya.domain.telecom.model.AudioCapabilities
import javax.inject.Inject

class AndroidAudioCapabilityProvider @Inject constructor(
    private val context: Context,
    private val dialerRoleManager: DialerRoleManager
) : AudioCapabilityProvider {

    override fun getAudioCapabilities(): AudioCapabilities {
        val pm = context.packageManager

        val supportsMic = pm.hasSystemFeature(PackageManager.FEATURE_MICROPHONE) &&
                context.checkSelfPermission(android.Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED
                
        val supportsBluetooth = pm.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH)
        val supportsWiredHeadset = pm.hasSystemFeature(PackageManager.FEATURE_AUDIO_OUTPUT)

        // Starting in Android 10 (API 29), VOICE_COMMUNICATION is restricted to system apps or the Default Dialer.
        val isDefaultDialer = dialerRoleManager.isDefaultDialer()
        
        val supportsTelecomAudioStream: Boolean
        val telecomAudioLimitation: String?

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            if (isDefaultDialer) {
                supportsTelecomAudioStream = true
                telecomAudioLimitation = null
            } else {
                supportsTelecomAudioStream = false
                telecomAudioLimitation = "Requires Default Dialer on Android 10+"
            }
        } else {
            // Pre-Android 10
            supportsTelecomAudioStream = true
            telecomAudioLimitation = null
        }

        return AudioCapabilities(
            supportsMicrophone = supportsMic,
            supportsBluetooth = supportsBluetooth,
            supportsWiredHeadset = supportsWiredHeadset,
            supportsSpeaker = true,
            supportsTelecomAudioStream = supportsTelecomAudioStream,
            telecomAudioLimitation = telecomAudioLimitation
        )
    }
}
