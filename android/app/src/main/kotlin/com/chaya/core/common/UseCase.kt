package com.chaya.core.common

/**
 * Base contract for one-shot domain operations invoked from ViewModels.
 */
interface UseCase<in P, out R> {
    suspend operator fun invoke(params: P): R
}

/**
 * Parameterless use case variant.
 */
interface NoParamUseCase<out R> {
    suspend operator fun invoke(): R
}
