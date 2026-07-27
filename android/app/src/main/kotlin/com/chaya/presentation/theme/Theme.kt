package com.chaya.presentation.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFE94560),
    onPrimary = Color.White,
    secondary = Color(0xFF16213E),
    onSecondary = Color.White,
    background = Color(0xFF1A1A2E),
    onBackground = Color(0xFFEAEAEA),
    surface = Color(0xFF16213E),
    onSurface = Color(0xFFEAEAEA),
)

private val LightColorScheme = lightColorScheme(
    primary = Color(0xFFE94560),
    onPrimary = Color.White,
    secondary = Color(0xFF16213E),
    onSecondary = Color.White,
    background = Color(0xFFF5F5F5),
    onBackground = Color(0xFF1A1A2E),
    surface = Color.White,
    onSurface = Color(0xFF1A1A2E),
)

@Composable
fun ChayaTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = ChayaTypography,
        content = content,
    )
}
