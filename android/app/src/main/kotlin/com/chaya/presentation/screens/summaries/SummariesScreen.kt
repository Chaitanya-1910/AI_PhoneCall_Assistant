package com.chaya.presentation.screens.summaries

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.chaya.presentation.components.ChayaCard

@Composable
fun SummariesScreen() {
    val mockSummaries = listOf(
        SummaryItem("Interview with Acme Corp", "Today", "Job interview regarding the Senior Android role. Next step: Technical round."),
        SummaryItem("Call from Mom", "Yesterday", "Personal call. She's asking about the weekend plans."),
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
    ) {
        Text("AI Summaries", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(24.dp))
        
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            items(mockSummaries) { summary ->
                SummaryCard(summary)
            }
        }
    }
}

@Composable
private fun SummaryCard(summary: SummaryItem) {
    ChayaCard {
        Row {
            Icon(Icons.Filled.AutoAwesome, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(summary.title, style = MaterialTheme.typography.titleMedium)
                Text(summary.date, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(modifier = Modifier.height(8.dp))
                Text(summary.content, style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}

data class SummaryItem(val title: String, val date: String, val content: String)
