package com.chaya.domain.repository

import com.chaya.domain.model.PipelineResult
import com.chaya.domain.model.audio.AudioSource

interface CallRepository {
    
    /**
     * Uploads an audio source to the backend to process the AI pipeline.
     */
    suspend fun processAudio(audioSource: AudioSource, conversationId: String? = null): PipelineResult
    
    /**
     * Downloads an audio file from the backend and returns the local file URI/path.
     */
    suspend fun downloadAudio(url: String): String
}
