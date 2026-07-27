package com.chaya.presentation.diagnostics

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import android.app.Activity

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DiagnosticsScreen(
    viewModel: DiagnosticsViewModel = hiltViewModel()
) {
    val capabilities by viewModel.capabilities.collectAsState()
    val availableRoutes by viewModel.availableRoutes.collectAsState()
    val currentRoute by viewModel.currentRoute.collectAsState()
    val activeCallState by viewModel.activeCallState.collectAsState()
    val activeAudioSource by viewModel.activeAudioSource.collectAsState()
    val audioCaps by viewModel.audioCapabilities.collectAsState()

    val dialerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            viewModel.loadDiagnostics()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Telecom Diagnostics") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            capabilities?.let { caps ->
                item {
                    Text(text = "Device Info", style = MaterialTheme.typography.titleMedium)
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("OS Version: ${caps.androidVersion}")
                            Text("API Level: ${caps.apiLevel}")
                        }
                    }
                }

                item {
                    Text(text = "Call Lifecycle", style = MaterialTheme.typography.titleMedium)
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("Active State: $activeCallState")
                        }
                    }
                }

                item {
                    Text(text = "Capabilities", style = MaterialTheme.typography.titleMedium)
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            CapabilityRow("Is Default Dialer", caps.isDefaultDialer)
                            CapabilityRow("Supports Call Screening", caps.supportsCallScreening)
                            CapabilityRow("Supports InCallService", caps.supportsInCallService)
                            CapabilityRow("Supports Call Audio Routing", caps.supportsCallAudio)
                            CapabilityRow("Supports Answering", caps.supportsAnswering)
                            CapabilityRow("Supports Call Hold", caps.supportsHold)
                            
                            if (!caps.isDefaultDialer) {
                                Spacer(modifier = Modifier.height(16.dp))
                                Button(
                                    onClick = { 
                                        viewModel.getDialerRequestIntent()?.let { intent ->
                                            dialerLauncher.launch(intent)
                                        }
                                    },
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Text("Set Default Dialer")
                                }
                            }
                        }
                    }
                }
            } ?: item {
                CircularProgressIndicator()
            }

            item {
                Text(text = "Audio Capabilities", style = MaterialTheme.typography.titleMedium)
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Active Source: ${activeAudioSource.javaClass.simpleName}")
                        
                        audioCaps?.let { aCaps ->
                            Spacer(modifier = Modifier.height(16.dp))
                            CapabilityRow("Microphone", aCaps.supportsMicrophone)
                            CapabilityRow("Bluetooth", aCaps.supportsBluetooth)
                            CapabilityRow("Wired Headset", aCaps.supportsWiredHeadset)
                            CapabilityRow("Telecom Audio Stream", aCaps.supportsTelecomAudioStream)
                            
                            aCaps.telecomAudioLimitation?.let { limit ->
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = "Limitation: $limit",
                                    color = MaterialTheme.colorScheme.error,
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                        }
                    }
                }
            }

            item {
                Text(text = "Audio Routing", style = MaterialTheme.typography.titleMedium)
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Current Route: $currentRoute")
                        Spacer(modifier = Modifier.height(8.dp))
                        Text("Available Routes: ${availableRoutes.joinToString()}")
                    }
                }
            }
        }
    }
}

@Composable
private fun CapabilityRow(label: String, supported: Boolean) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = label)
        Text(
            text = if (supported) "YES" else "NO",
            color = if (supported) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error
        )
    }
}
