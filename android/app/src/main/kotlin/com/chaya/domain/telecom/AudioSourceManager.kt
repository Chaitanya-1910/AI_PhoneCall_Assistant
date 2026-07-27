package com.chaya.domain.telecom

import com.chaya.domain.model.audio.AudioSource
import kotlinx.coroutines.flow.StateFlow

interface AudioSourceManager {
    val activeSource: StateFlow<AudioSource>
}
