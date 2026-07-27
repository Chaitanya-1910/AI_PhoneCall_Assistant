package com.chaya.presentation.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.chaya.presentation.CallScreen
import com.chaya.presentation.CallViewModel

/**
 * Root navigation host.
 * Feature composable destinations register in this graph.
 */
@Composable
fun ChayaNavGraph() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Routes.ROOT,
    ) {
        composable(Routes.ROOT) {
            val viewModel: CallViewModel = hiltViewModel()
            CallScreen(viewModel = viewModel)
        }
    }
}
