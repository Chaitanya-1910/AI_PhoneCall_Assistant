package com.chaya.domain.usecase

import com.chaya.domain.model.PipelineResult
import com.chaya.domain.model.audio.AudioSource
import com.chaya.domain.repository.CallRepository
import javax.inject.Inject

class ProcessAudioUseCase @Inject constructor(
    private val repository: CallRepository
) {
    suspend operator fun invoke(audioSource: AudioSource, conversationId: String? = null): PipelineResult {
        return repository.processAudio(audioSource, conversationId)
    }
}
