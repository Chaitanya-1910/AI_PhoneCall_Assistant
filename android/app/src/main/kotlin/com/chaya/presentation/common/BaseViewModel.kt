package com.chaya.presentation.common

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.chaya.core.logging.Logger
import com.chaya.di.DefaultDispatcher
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Base ViewModel with shared coroutine error handling and dispatcher injection.
 */
abstract class BaseViewModel(
    @DefaultDispatcher protected val defaultDispatcher: CoroutineDispatcher,
) : ViewModel() {

    protected val exceptionHandler = CoroutineExceptionHandler { _, throwable ->
        onUncaughtException(throwable)
    }

    protected open fun onUncaughtException(throwable: Throwable) {
        Logger.e("BaseViewModel", "Uncaught coroutine exception", throwable)
    }

    protected fun launchSafe(block: suspend () -> Unit) {
        viewModelScope.launch(exceptionHandler) {
            block()
        }
    }

    protected suspend fun <T> onDefault(block: suspend () -> T): T =
        withContext(defaultDispatcher) { block() }

    protected fun <T> mutableStateOf(initial: T): MutableStateFlow<T> = MutableStateFlow(initial)

    protected fun <T> StateFlow<T>.readOnly(): StateFlow<T> = this
}
