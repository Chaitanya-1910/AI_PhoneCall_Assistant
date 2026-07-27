package com.chaya.presentation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.chaya.domain.model.ChayaException
import com.chaya.domain.model.audio.AudioSource
import com.chaya.domain.audio.AudioPlayer
import com.chaya.domain.audio.AudioRecorder
import com.chaya.domain.audio.AudioFocusManager
import com.chaya.domain.audio.AudioSessionManager
import com.chaya.domain.usecase.DownloadAudioUseCase
import com.chaya.domain.usecase.ProcessAudioUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import java.io.File
import javax.inject.Inject
import kotlinx.coroutines.delay

@HiltViewModel
class CallViewModel @Inject constructor(
    private val processAudioUseCase: ProcessAudioUseCase,
    private val downloadAudioUseCase: DownloadAudioUseCase,
    private val audioPlayer: AudioPlayer,
    private val audioRecorder: AudioRecorder,
    private val audioFocusManager: AudioFocusManager,
    private val audioSessionManager: AudioSessionManager
) : ViewModel() {

    private val _uiState = MutableStateFlow<CallUiState>(CallUiState.Idle)
    val uiState: StateFlow<CallUiState> = _uiState.asStateFlow()

    private var currentSource: AudioSource? = null
    private var lastLocalAudioPath: String? = null

    init {
        audioPlayer.isPlaying.onEach { isPlaying ->
            val currentState = _uiState.value
            if (!isPlaying && currentState is CallUiState.Playing) {
                // Playback finished
                cleanupPlayback()
                _uiState.value = CallUiState.Completed
                delay(1500) // Brief pause to show success animation
                if (_uiState.value is CallUiState.Completed) {
                    _uiState.value = CallUiState.Idle
                }
            }
        }.launchIn(viewModelScope)
    }

    fun requirePermission() {
        _uiState.value = CallUiState.PermissionRequired
    }

    fun onPermissionGranted() {
        if (_uiState.value is CallUiState.PermissionRequired) {
            _uiState.value = CallUiState.Idle
        }
    }

    fun startRecording() {
        cleanupPlayback() // ensure any old files are gone
        audioFocusManager.requestFocus()
        audioSessionManager.startSession()
        audioRecorder.start()
        _uiState.value = CallUiState.Recording
    }

    fun stopRecording() {
        viewModelScope.launch {
            val fileSource = audioRecorder.stop()
            audioSessionManager.endSession()
            audioFocusManager.abandonFocus()
            
            if (fileSource != null) {
                processAudio(fileSource)
            } else {
                _uiState.value = CallUiState.Error("Failed to save recording.", false)
            }
        }
    }

    fun cancelRecording() {
        audioRecorder.cancel()
        audioSessionManager.endSession()
        audioFocusManager.abandonFocus()
        cleanupPlayback()
        _uiState.value = CallUiState.Idle
    }

    private fun processAudio(source: AudioSource) {
        currentSource = source
        executePipeline(source)
    }

    fun retry() {
        currentSource?.let { executePipeline(it) } ?: run {
            _uiState.value = CallUiState.Idle
        }
    }

    private fun executePipeline(source: AudioSource) {
        viewModelScope.launch {
            try {
                // 1. Upload & Process
                _uiState.value = CallUiState.Uploading
                // Simulating uploading vs processing transition is tricky as it's a single HTTP call.
                // We'll set Processing after a brief delay to simulate the state transition for UI purposes,
                // or just rely on the UI to show a generic processing state. 
                // Since processAudioUseCase handles both upload and wait-for-response, we'll set Processing.
                _uiState.value = CallUiState.Processing
                val result = processAudioUseCase(source)
                
                // 2. Download MP3
                _uiState.value = CallUiState.Downloading
                val localPath = downloadAudioUseCase(result.audioUrl)
                lastLocalAudioPath = localPath
                
                // 3. Play MP3 automatically
                _uiState.value = CallUiState.Playing(result, localPath)
                audioFocusManager.requestFocus()
                audioPlayer.play(localPath)
                
            } catch (e: Exception) {
                val canRetry = e is ChayaException.TransientFailure
                val msg = e.message ?: "An unknown error occurred"
                _uiState.value = CallUiState.Error(msg, canRetry)
                cleanupPlayback() // clean up in case of failure mid-way
            }
        }
    }

    private fun cleanupPlayback() {
        audioPlayer.stop()
        audioPlayer.release()
        audioFocusManager.abandonFocus()
        lastLocalAudioPath?.let { path ->
            try {
                val file = File(path)
                if (file.exists()) {
                    file.delete()
                }
            } catch (e: Exception) {
                // Ignore cleanup errors
            }
            lastLocalAudioPath = null
        }
    }

    override fun onCleared() {
        super.onCleared()
        cleanupPlayback()
        audioRecorder.cancel()
        audioSessionManager.endSession()
    }
}
