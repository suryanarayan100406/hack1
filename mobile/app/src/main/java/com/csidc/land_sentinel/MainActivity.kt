package com.example.landsentinel

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val recyclerView = findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)

        // Mock Data for MVP - In production, fetch from /api/violations
        val alerts = listOf(
            Alert("🚨 High Priority Violation", "PLOT-402", "New encroachment detected (12%) in Urla Zone A.", "HIGH"),
            Alert("⚠️ Warning", "PLOT-105", "Layout deviation (5%) observed.", "MEDIUM"),
            Alert("🚨 High Priority Violation", "PLOT-891", "Unauthorized construction started yesterday.", "HIGH"),
            Alert("✅ Compliance Check", "PLOT-332", "Routine audit due for verification.", "LOW")
        )

        recyclerView.adapter = AlertAdapter(alerts)
    }
}
