package com.chaya.data.telecom

import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.telecom.TelecomManager
import com.chaya.domain.telecom.CallCapabilityProvider
import com.chaya.domain.telecom.model.CallCapabilities
import javax.inject.Inject

class AndroidCallCapabilityProvider @Inject constructor(
    private val context: Context
) : CallCapabilityProvider {

    override fun getCapabilities(): CallCapabilities {
        val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager
        val pm = context.packageManager

        // Check if we are default dialer
        val isDefaultDialer = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            telecomManager.defaultDialerPackage == context.packageName
        } else {
            false
        }

        // Check call screening support
        val supportsCallScreening = Build.VERSION.SDK_INT >= Build.VERSION_CODES.N

        // Check InCallService support (Requires M+ and often default dialer)
        val supportsInCallService = Build.VERSION.SDK_INT >= Build.VERSION_CODES.M

        // Check permissions for answering
        val hasAnswerPermission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.checkSelfPermission(android.Manifest.permission.ANSWER_PHONE_CALLS) == PackageManager.PERMISSION_GRANTED
        } else {
            false
        }

        return CallCapabilities(
            supportsCallScreening = supportsCallScreening,
            supportsInCallService = supportsInCallService,
            isDefaultDialer = isDefaultDialer,
            supportsCallAudio = true, // We have RECORD_AUDIO and AudioManager
            supportsAnswering = hasAnswerPermission && (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O),
            supportsHold = isDefaultDialer, // Usually requires default dialer or ConnectionService
            androidVersion = "Android ${Build.VERSION.RELEASE}",
            apiLevel = Build.VERSION.SDK_INT
        )
    }
}
