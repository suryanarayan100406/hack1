package com.example.landsentinel

data class Alert(
    val title: String,
    val plotId: String,
    val description: String,
    val severity: String // HIGH, MEDIUM, LOW
)
