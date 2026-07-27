package com.chaya.data.remote.api

import com.chaya.data.remote.dto.HealthResponseDto
import com.chaya.data.remote.dto.PipelineResponseDto
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Streaming
import retrofit2.http.Url

/**
 * Retrofit service definition for CHAYA backend API.
 */
interface ChayaApiService {

    @GET("api/v1/health")
    suspend fun getHealth(): HealthResponseDto

    @Multipart
    @POST("api/v1/calls/process")
    suspend fun processAudio(
        @Part audio: MultipartBody.Part,
        @Part("conversation_id") conversationId: RequestBody? = null
    ): PipelineResponseDto

    @Streaming
    @GET
    suspend fun downloadAudio(@Url fileUrl: String): ResponseBody
}
