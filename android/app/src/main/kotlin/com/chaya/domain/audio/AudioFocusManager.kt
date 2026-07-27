package com.chaya.domain.audio

/**
 * Domain interface for managing audio focus (e.g. ducking other apps when speaking/recording).
 */
interface AudioFocusManager {
    fun requestFocus(): Boolean
    fun abandonFocus()
}
