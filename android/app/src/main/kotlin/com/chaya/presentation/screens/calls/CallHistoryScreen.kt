package com.chaya.presentation.screens.calls

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowForwardIos
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.SentimentSatisfied
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.chaya.presentation.components.ChayaCard

@Composable
fun CallHistoryScreen() {
    val mockCalls = listOf(
        CallHistoryItem("John Doe", "10:30 AM", "2m 45s", "POSITIVE", "Recruiter"),
        CallHistoryItem("Jane Smith", "Yesterday", "5m 12s", "NEUTRAL", "Friend"),
        CallHistoryItem("Unknown", "Monday", "0m 45s", "NEGATIVE", "Spam"),
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
    ) {
        Text("Call History", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(24.dp))
        
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(mockCalls) { call ->
                CallCard(call)
            }
        }
    }
}

@Composable
private fun CallCard(call: CallHistoryItem) {
    ChayaCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .padding(8.dp),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Filled.Call, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
            }
            
            Column(modifier = Modifier.weight(1f).padding(horizontal = 12.dp)) {
                Text(call.name, style = MaterialTheme.typography.titleMedium)
                Text("${call.time} • ${call.duration}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            
            Badge(
                containerColor = MaterialTheme.colorScheme.primaryContainer,
                contentColor = MaterialTheme.colorScheme.onPrimaryContainer
            ) {
                Text(call.category, modifier = Modifier.padding(4.dp))
            }
            
            Spacer(modifier = Modifier.width(8.dp))
            
            Icon(
                Icons.Filled.ArrowForwardIos,
                contentDescription = null,
                modifier = Modifier.size(16.dp),
                tint = MaterialTheme.colorScheme.outline
            )
        }
    }
}

data class CallHistoryItem(
    val name: String,
    val time: String,
    val duration: String,
    val sentiment: String,
    val category: String
)
