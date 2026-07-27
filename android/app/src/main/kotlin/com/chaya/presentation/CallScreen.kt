package com.chaya.presentation

import android.Manifest
import android.content.pm.PackageManager
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.delay

@Composable
fun CallScreen(
    viewModel: CallViewModel
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current
    var hasRecordPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.RECORD_AUDIO
            ) == PackageManager.PERMISSION_GRANTED
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        Log.d("CallScreen", "Permission result: isGranted=$isGranted")
        hasRecordPermission = isGranted
        if (isGranted) {
            viewModel.onPermissionGranted()
        }
    }

    LaunchedEffect(hasRecordPermission) {
        if (!hasRecordPermission) {
            viewModel.requirePermission()
        } else {
            viewModel.onPermissionGranted()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        when (val state = uiState) {
            is CallUiState.PermissionRequired -> {
                Icon(
                    Icons.Filled.Mic,
                    contentDescription = "Mic",
                    modifier = Modifier.size(64.dp),
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text("Microphone access is required", style = MaterialTheme.typography.titleMedium)
                Spacer(modifier = Modifier.height(24.dp))
                Button(onClick = {
                    Log.d("CallScreen", "Launching RECORD_AUDIO permission request")
                    permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                }) {
                    Text("Grant Permission")
                }
            }

            is CallUiState.Idle -> {
                IdleStateView(onStartRecording = {
                    val status = ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO)
                    Log.d("CallScreen", "Starting recording. Permission status: $status")
                    viewModel.startRecording()
                })
            }

            is CallUiState.Recording -> {
                RecordingStateView(
                    onStop = { viewModel.stopRecording() },
                    onCancel = { viewModel.cancelRecording() }
                )
            }

            is CallUiState.Uploading -> {
                ProcessingStateView("Uploading audio...")
            }

            is CallUiState.Processing -> {
                ProcessingStateView("CHAYA is thinking...")
            }

            is CallUiState.Downloading -> {
                ProcessingStateView("Downloading response...")
            }

            is CallUiState.Playing -> {
                PlayingStateView(state.result.transcript, state.result.response)
            }

            is CallUiState.Completed -> {
                CompletedStateView()
            }

            is CallUiState.Error -> {
                ErrorStateView(
                    message = state.message,
                    canRetry = state.canRetry,
                    onRetry = { viewModel.retry() },
                    onCancel = { viewModel.cancelRecording() }
                )
            }
        }
    }
}

@Composable
fun IdleStateView(onStartRecording: () -> Unit) {
    LargeFloatingActionButton(
        onClick = onStartRecording,
        modifier = Modifier.size(120.dp),
        shape = CircleShape,
        containerColor = MaterialTheme.colorScheme.primaryContainer
    ) {
        Icon(
            Icons.Filled.Mic,
            contentDescription = "Start Recording",
            modifier = Modifier.size(48.dp)
        )
    }
    Spacer(modifier = Modifier.height(32.dp))
    Text("Tap to speak", style = MaterialTheme.typography.titleLarge)
}

@Composable
fun RecordingStateView(onStop: () -> Unit, onCancel: () -> Unit) {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )

    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier.size(160.dp)
    ) {
        Box(
            modifier = Modifier
                .size(120.dp)
                .scale(scale)
                .background(
                    MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.5f),
                    CircleShape
                )
        )
        LargeFloatingActionButton(
            onClick = onStop,
            modifier = Modifier.size(96.dp),
            shape = CircleShape,
            containerColor = MaterialTheme.colorScheme.error
        ) {
            Icon(
                Icons.Filled.Stop,
                contentDescription = "Stop Recording",
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.onError
            )
        }
    }
    Spacer(modifier = Modifier.height(32.dp))
    Text(
        "Listening...",
        style = MaterialTheme.typography.titleLarge,
        color = MaterialTheme.colorScheme.error
    )
    Spacer(modifier = Modifier.height(32.dp))
    TextButton(onClick = onCancel) {
        Text("Cancel")
    }
}

@Composable
fun ProcessingStateView(message: String) {
    CircularProgressIndicator(
        modifier = Modifier.size(64.dp),
        color = MaterialTheme.colorScheme.primary
    )
    Spacer(modifier = Modifier.height(32.dp))
    Text(message, style = MaterialTheme.typography.titleMedium)
}

@Composable
fun PlayingStateView(transcript: String, response: String) {
    val infiniteTransition = rememberInfiniteTransition(label = "eq")
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(400, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            Icons.Filled.VolumeUp,
            contentDescription = "Playing",
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.primary.copy(alpha = alpha)
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            "Speaking...",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(32.dp))
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    "You said:",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(transcript, style = MaterialTheme.typography.bodyLarge)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    "CHAYA:",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    response,
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
        }
    }
}

@Composable
fun CompletedStateView() {
    Icon(
        Icons.Filled.Check,
        contentDescription = "Success",
        modifier = Modifier.size(80.dp),
        tint = MaterialTheme.colorScheme.primary
    )
    Spacer(modifier = Modifier.height(16.dp))
    Text("Done", style = MaterialTheme.typography.titleMedium)
}

@Composable
fun ErrorStateView(message: String, canRetry: Boolean, onRetry: () -> Unit, onCancel: () -> Unit) {
    Icon(
        Icons.Filled.Warning,
        contentDescription = "Error",
        modifier = Modifier.size(80.dp),
        tint = MaterialTheme.colorScheme.error
    )
    Spacer(modifier = Modifier.height(16.dp))
    Text("Oops!", style = MaterialTheme.typography.titleLarge)
    Spacer(modifier = Modifier.height(8.dp))
    Text(
        message,
        style = MaterialTheme.typography.bodyMedium,
        color = MaterialTheme.colorScheme.error
    )

    Spacer(modifier = Modifier.height(32.dp))
    if (canRetry) {
        Button(onClick = onRetry) {
            Text("Retry")
        }
        Spacer(modifier = Modifier.height(8.dp))
    }
    TextButton(onClick = onCancel) {
        Text("Go Back")
    }
}

