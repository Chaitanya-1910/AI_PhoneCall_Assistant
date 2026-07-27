package com.chaya.core.logging

import timber.log.Timber

/**
 * Centralized logging facade.
 * Routes to Timber in debug; can be extended for crash reporting in release.
 */
object Logger {

    fun init(isDebug: Boolean) {
        if (isDebug) {
            Timber.plant(Timber.DebugTree())
        } else {
            Timber.plant(ReleaseTree())
        }
    }

    fun d(tag: String, message: String) = Timber.tag(tag).d(message)
    fun i(tag: String, message: String) = Timber.tag(tag).i(message)
    fun w(tag: String, message: String, throwable: Throwable? = null) =
        Timber.tag(tag).w(throwable, message)

    fun e(tag: String, message: String, throwable: Throwable? = null) =
        Timber.tag(tag).e(throwable, message)

    private class ReleaseTree : Timber.Tree() {
        override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
            if (priority >= android.util.Log.ERROR) {
                // Future: forward to crash reporting service
            }
        }
    }
}
