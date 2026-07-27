package com.chaya.domain.telecom

import android.content.Intent

interface DialerRoleManager {
    fun isDefaultDialer(): Boolean
    
    /**
     * Returns the Intent required to request the default dialer role.
     * The presentation layer should launch this intent using ActivityResultContracts.StartActivityForResult()
     */
    fun createRequestRoleIntent(): Intent?
}
