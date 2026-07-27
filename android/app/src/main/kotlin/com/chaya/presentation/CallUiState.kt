package com.chaya.presentation

import com.chaya.domain.model.PipelineResult

sealed interface CallUiState {
    object Idle : CallUiState
    object PermissionRequired : CallUiState
    object Recording : CallUiState
    object Uploading : CallUiState
    object Processing : CallUiState
    object Downloading : CallUiState
    
    data class Playing(
        val result: PipelineResult,
        val localAudioPath: String
    ) : CallUiState
    
    object Completed : CallUiState
    
    data class Error(
        val message: String,
        val canRetry: Boolean
    ) : CallUiState
}
