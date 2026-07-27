package com.chaya.data.audio

import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import com.chaya.domain.audio.AudioRecorder
import com.chaya.domain.model.audio.AudioSource
import kotlinx.coroutines.*
import timber.log.Timber
import java.io.File
import java.io.FileOutputStream
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.UUID

class AndroidAudioRecorder(
    private val context: Context,
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
) : AudioRecorder {

    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    private var recordingJob: Job? = null
    private var outputFile: File? = null

    private val sampleRate = 16000
    private val channelConfig = AudioFormat.CHANNEL_IN_MONO
    private val audioFormat = AudioFormat.ENCODING_PCM_16BIT
    private val minBufferSize = AudioRecord.getMinBufferSize(sampleRate, channelConfig, audioFormat)

    @SuppressLint("MissingPermission") // Caller is responsible for permissions
    override fun start() {
        if (isRecording) return

        outputFile = File(context.cacheDir, "recording_${UUID.randomUUID()}.wav")

        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            sampleRate,
            channelConfig,
            audioFormat,
            minBufferSize * 2
        )

        if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
            Timber.e("AudioRecord failed to initialize.")
            return
        }

        audioRecord?.startRecording()
        
        if (audioRecord?.recordingState != AudioRecord.RECORDSTATE_RECORDING) {
            Timber.e("AudioRecord failed to start recording. State: ${audioRecord?.recordingState}")
            return
        }
        
        isRecording = true
        Timber.d("Recording started successfully using MIC")

        recordingJob = scope.launch {
            writeAudioDataToFile(outputFile!!)
        }
    }

    override suspend fun stop(): AudioSource.File? {
        if (!isRecording) return null

        isRecording = false
        recordingJob?.join()
        
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        
        outputFile?.let {
            Timber.d("Recording stopped. File size: ${it.length()} bytes")
            if (it.exists() && it.length() > 44) {
                return AudioSource.File(it.absolutePath)
            }
        }
        return null
    }

    override fun cancel() {
        isRecording = false
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        recordingJob?.cancel()
        outputFile?.delete()
        outputFile = null
    }

    private fun writeAudioDataToFile(file: File) {
        val data = ByteArray(minBufferSize)
        var totalAudioLen: Long = 0
        var bufferCount = 0

        FileOutputStream(file).use { os ->
            // Write placeholder header
            writeWavHeader(os, totalAudioLen, totalAudioLen + 36, sampleRate, 1, 16)
            
            while (isRecording) {
                val read = audioRecord?.read(data, 0, minBufferSize) ?: 0
                
                if (read > 0) {
                    os.write(data, 0, read)
                    totalAudioLen += read
                    
                    // Periodic RMS diagnostics (every 10 buffers)
                    if (bufferCount % 10 == 0) {
                        val rms = calculateRMS(data, read)
                        Timber.d("Recording: size=${totalAudioLen}, buffer_rms=${String.format("%.2f", rms)}")
                    }
                    bufferCount++
                } else if (read < 0) {
                    val errorMsg = when (read) {
                        AudioRecord.ERROR_INVALID_OPERATION -> "ERROR_INVALID_OPERATION"
                        AudioRecord.ERROR_BAD_VALUE -> "ERROR_BAD_VALUE"
                        AudioRecord.ERROR_DEAD_OBJECT -> "ERROR_DEAD_OBJECT"
                        else -> "Unknown error: $read"
                    }
                    Timber.e("AudioRecord read error: $errorMsg")
                    isRecording = false
                }
            }
        }

        // Update header with actual sizes
        updateWavHeader(file, totalAudioLen)
        Timber.d("WAV file updated. Total audio bytes: $totalAudioLen")
    }

    private fun calculateRMS(buffer: ByteArray, read: Int): Double {
        var sum = 0.0
        for (i in 0 until read step 2) {
            // Little-endian 16-bit PCM
            val sample = ((buffer[i + 1].toInt() shl 8) or (buffer[i].toInt() and 0xff)).toShort()
            sum += sample.toDouble() * sample.toDouble()
        }
        return if (read > 0) Math.sqrt(sum / (read / 2)) else 0.0
    }

    private fun writeWavHeader(
        out: FileOutputStream,
        totalAudioLen: Long,
        totalDataLen: Long,
        longSampleRate: Int,
        channels: Int,
        byteRate: Int
    ) {
        val header = ByteArray(44)
        header[0] = 'R'.code.toByte() // RIFF/WAVE header
        header[1] = 'I'.code.toByte()
        header[2] = 'F'.code.toByte()
        header[3] = 'F'.code.toByte()
        header[4] = (totalDataLen and 0xff).toByte()
        header[5] = (totalDataLen shr 8 and 0xff).toByte()
        header[6] = (totalDataLen shr 16 and 0xff).toByte()
        header[7] = (totalDataLen shr 24 and 0xff).toByte()
        header[8] = 'W'.code.toByte()
        header[9] = 'A'.code.toByte()
        header[10] = 'V'.code.toByte()
        header[11] = 'E'.code.toByte()
        header[12] = 'f'.code.toByte() // 'fmt ' chunk
        header[13] = 'm'.code.toByte()
        header[14] = 't'.code.toByte()
        header[15] = ' '.code.toByte()
        header[16] = 16 // 4 bytes: size of 'fmt ' chunk
        header[17] = 0
        header[18] = 0
        header[19] = 0
        header[20] = 1 // format = 1
        header[21] = 0
        header[22] = channels.toByte()
        header[23] = 0
        header[24] = (longSampleRate and 0xff).toByte()
        header[25] = (longSampleRate shr 8 and 0xff).toByte()
        header[26] = (longSampleRate shr 16 and 0xff).toByte()
        header[27] = (longSampleRate shr 24 and 0xff).toByte()
        
        val byteR = longSampleRate * channels * (byteRate / 8)
        header[28] = (byteR and 0xff).toByte()
        header[29] = (byteR shr 8 and 0xff).toByte()
        header[30] = (byteR shr 16 and 0xff).toByte()
        header[31] = (byteR shr 24 and 0xff).toByte()
        header[32] = (channels * (byteRate / 8)).toByte() // block align
        header[33] = 0
        header[34] = byteRate.toByte() // bits per sample
        header[35] = 0
        header[36] = 'd'.code.toByte() // data
        header[37] = 'a'.code.toByte()
        header[38] = 't'.code.toByte()
        header[39] = 'a'.code.toByte()
        header[40] = (totalAudioLen and 0xff).toByte()
        header[41] = (totalAudioLen shr 8 and 0xff).toByte()
        header[42] = (totalAudioLen shr 16 and 0xff).toByte()
        header[43] = (totalAudioLen shr 24 and 0xff).toByte()
        
        out.write(header, 0, 44)
    }

    private fun updateWavHeader(file: File, totalAudioLen: Long) {
        val totalDataLen = totalAudioLen + 36
        RandomAccessFile(file, "rw").use { raf ->
            raf.seek(4)
            val buffer = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN)
            buffer.putInt(totalDataLen.toInt())
            raf.write(buffer.array())
            
            raf.seek(40)
            buffer.clear()
            buffer.putInt(totalAudioLen.toInt())
            raf.write(buffer.array())
        }
    }
}
