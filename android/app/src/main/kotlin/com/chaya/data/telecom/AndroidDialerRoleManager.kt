package com.chaya.data.telecom

import android.app.role.RoleManager
import android.content.Context
import android.content.Intent
import android.os.Build
import android.telecom.TelecomManager
import com.chaya.domain.telecom.DialerRoleManager
import javax.inject.Inject

class AndroidDialerRoleManager @Inject constructor(
    private val context: Context
) : DialerRoleManager {

    private val telecomManager = context.getSystemService(Context.TELECOM_SERVICE) as TelecomManager

    override fun isDefaultDialer(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            telecomManager.defaultDialerPackage == context.packageName
        } else {
            false
        }
    }

    override fun createRequestRoleIntent(): Intent? {
        if (isDefaultDialer()) return null

        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roleManager = context.getSystemService(Context.ROLE_SERVICE) as RoleManager
            if (roleManager.isRoleAvailable(RoleManager.ROLE_DIALER)) {
                roleManager.createRequestRoleIntent(RoleManager.ROLE_DIALER)
            } else {
                null
            }
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER).apply {
                putExtra(TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, context.packageName)
            }
        } else {
            null
        }
    }
}
