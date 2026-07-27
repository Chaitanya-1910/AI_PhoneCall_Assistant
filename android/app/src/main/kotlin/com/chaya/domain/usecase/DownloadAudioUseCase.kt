package com.chaya.domain.usecase

import com.chaya.domain.repository.CallRepository
import javax.inject.Inject

class DownloadAudioUseCase @Inject constructor(
    private val repository: CallRepository
) {
    suspend operator fun invoke(url: String): String {
        return repository.downloadAudio(url)
    }
}
