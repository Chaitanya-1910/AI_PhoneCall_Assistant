package com.chaya.presentation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.*
import com.chaya.presentation.navigation.Routes

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    
    val items = listOf(
        NavigationItem("Home", Routes.HOME, Icons.Filled.Home),
        NavigationItem("Calls", Routes.CALLS, Icons.Filled.History),
        NavigationItem("Summaries", Routes.SUMMARIES, Icons.Filled.Description),
        NavigationItem("Settings", Routes.SETTINGS, Icons.Filled.Settings),
        NavigationItem("Profile", Routes.PROFILE, Icons.Filled.Person),
    )

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
                tonalElevation = 0.dp
            ) {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination
                
                items.forEach { item ->
                    NavigationBarItem(
                        icon = { Icon(item.icon, contentDescription = item.label) },
                        label = { Text(item.label) },
                        selected = currentDestination?.hierarchy?.any { it.route == item.route } == true,
                        onClick = {
                            navController.navigate(item.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Routes.HOME,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Routes.HOME) { PlaceholderScreen("Home Dashboard") }
            composable(Routes.CALLS) { PlaceholderScreen("Call History") }
            composable(Routes.SUMMARIES) { PlaceholderScreen("AI Summaries") }
            composable(Routes.SETTINGS) { PlaceholderScreen("Settings") }
            composable(Routes.PROFILE) { PlaceholderScreen("Profile") }
            
            // We'll add real screens next
        }
    }
}

data class NavigationItem(val label: String, val route: String, val icon: ImageVector)

@Composable
fun PlaceholderScreen(name: String) {
    Surface(modifier = Modifier.fillMaxSize()) {
        Box(contentAlignment = androidx.compose.ui.Alignment.Center) {
            Text(name, style = MaterialTheme.typography.headlineMedium)
        }
    }
}
