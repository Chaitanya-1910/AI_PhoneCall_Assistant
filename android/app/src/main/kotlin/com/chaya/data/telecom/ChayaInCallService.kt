package com.chaya.data.telecom

import android.telecom.Call
import android.telecom.InCallService
import com.chaya.domain.telecom.CallStateMonitor
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class ChayaInCallService : InCallService() {

    @Inject
    lateinit var telecomManager: AndroidTelecomManager

    @Inject
    lateinit var stateMonitor: CallStateMonitor

    private var activeSession: AndroidCallSession? = null

    override fun onCallAdded(call: Call) {
        super.onCallAdded(call)
        
        val session = AndroidCallSession(call)
        activeSession = session
        telecomManager.setActiveSession(session)
        (stateMonitor as? AndroidCallStateMonitor)?.updateStateFlow(session.state)
    }

    override fun onCallRemoved(call: Call) {
        super.onCallRemoved(call)
        
        activeSession?.cleanup()
        activeSession = null
        telecomManager.setActiveSession(null)
        (stateMonitor as? AndroidCallStateMonitor)?.reset()
    }
}
