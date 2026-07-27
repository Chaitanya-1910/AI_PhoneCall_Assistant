package com.chaya.data.repository

import android.content.Context
import com.chaya.data.remote.api.ChayaApiService
import com.chaya.domain.model.ChayaException
import com.chaya.domain.model.PipelineMetrics
import com.chaya.domain.model.PipelineResult
import com.chaya.domain.model.audio.AudioSource
import com.chaya.domain.repository.CallRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.HttpException
import timber.log.Timber
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.util.UUID
import javax.inject.Inject
import dagger.hilt.android.qualifiers.ApplicationContext

class CallRepositoryImpl @Inject constructor(
    private val api: ChayaApiService,
    @ApplicationContext private val context: Context
) : CallRepository {

    init {
        cleanupOldAudioFiles()
    }

    override suspend fun processAudio(audioSource: AudioSource, conversationId: String?): PipelineResult {
        var audioFile: File? = null
        return try {
            audioFile = getAudioFileFromSource(audioSource)
            
            Timber.d("Uploading audio file: ${audioFile.absolutePath}, size: ${audioFile.length()} bytes")
            
            val requestFile = audioFile.asRequestBody("audio/wav".toMediaTypeOrNull())
            val audioPart = MultipartBody.Part.createFormData("audio", "recording.wav", requestFile)
            
            val convIdPart = conversationId?.toRequestBody("text/plain".toMediaTypeOrNull())
            
            val responseDto = api.processAudio(audioPart, convIdPart)
            
            PipelineResult(
                requestId = responseDto.requestId,
                conversationId = responseDto.conversationId,
                transcript = responseDto.transcript,
                response = responseDto.response,
                audioUrl = responseDto.audioUrl,
                metrics = PipelineMetrics(
                    sttLatencyMs = responseDto.metrics.sttLatencyMs,
                    llmLatencyMs = responseDto.metrics.llmLatencyMs,
                    ttsLatencyMs = responseDto.metrics.ttsLatencyMs,
                    totalLatencyMs = responseDto.metrics.totalLatencyMs
                )
            )
        } catch (e: Exception) {
            handleException(e)
        } finally {
            try {
                audioFile?.delete()
            } catch (e: Exception) {
                Timber.w(e, "Failed to delete temporary upload file")
            }
        }
    }

    override suspend fun downloadAudio(url: String): String = withContext(Dispatchers.IO) {
        try {
            cleanupOldAudioFiles()
            
            val responseBody = api.downloadAudio(url)
            val cacheFile = File(context.cacheDir, "audio_${UUID.randomUUID()}.mp3")
            
            responseBody.byteStream().use { inputStream ->
                FileOutputStream(cacheFile).use { outputStream ->
                    inputStream.copyTo(outputStream)
                }
            }
            
            cacheFile.absolutePath
        } catch (e: Exception) {
            handleException(e)
        }
    }
    
    private suspend fun getAudioFileFromSource(source: AudioSource): File = withContext(Dispatchers.IO) {
        when (source) {
            is AudioSource.File -> File(source.filePath)
            is AudioSource.RawResource -> {
                val cacheFile = File(context.cacheDir, "temp_upload.mp3")
                context.resources.openRawResource(source.resourceId).use { inputStream ->
                    FileOutputStream(cacheFile).use { outputStream ->
                        inputStream.copyTo(outputStream)
                    }
                }
                cacheFile
            }
            is AudioSource.Microphone -> throw UnsupportedOperationException("Microphone source not yet implemented")
            is AudioSource.Telecom -> throw UnsupportedOperationException("Telecom stream source not yet implemented")
        }
    }
    
    private fun cleanupOldAudioFiles() {
        try {
            val files = context.cacheDir.listFiles { _, name -> 
                (name.startsWith("audio_") && name.endsWith(".mp3")) ||
                (name.startsWith("recording_") && name.endsWith(".wav")) ||
                name == "temp_upload.mp3"
            }
            val expirationTime = System.currentTimeMillis() - (60 * 60 * 1000) // 1 hour
            files?.forEach { file -> 
                if (file.lastModified() < expirationTime) {
                    file.delete()
                }
            }
        } catch (e: Exception) {
            Timber.w(e, "Failed to cleanup old audio files")
        }
    }

    private fun handleException(e: Exception): Nothing {
        Timber.e(e, "Network operation failed")
        when (e) {
            is IOException -> throw ChayaException.TransientFailure("Network error. Please check your connection.", e)
            is HttpException -> {
                val code = e.code()
                if (code in listOf(502, 503, 504)) {
                    throw ChayaException.TransientFailure("Server is temporarily unavailable. Please try again.", e)
                } else {
                    throw ChayaException.FatalFailure("Server error occurred ($code).", e)
                }
            }
            is ChayaException -> throw e
            else -> throw ChayaException.FatalFailure("An unexpected error occurred.", e)
        }
    }
}
