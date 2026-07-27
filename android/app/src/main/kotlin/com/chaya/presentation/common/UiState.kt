package com.chaya.presentation.common

/**
 * Standard UI state wrapper for Compose screens.
 * Every feature ViewModel exposes StateFlow of UiState.
 */
sealed interface UiState<out T> {
    data object Idle : UiState<Nothing>
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String, val retry: (() -> Unit)? = null) : UiState<Nothing>
}
