package com.example.landsentinel

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.recyclerview.widget.RecyclerView

class AlertAdapter(private val alerts: List<Alert>) : RecyclerView.Adapter<AlertAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tvAlertTitle)
        val tvPlotId: TextView = view.findViewById(R.id.tvPlotId)
        val tvDesc: TextView = view.findViewById(R.id.tvDesc)
        val btnVerify: Button = view.findViewById(R.id.btnVerify)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_alert, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val alert = alerts[position]
        holder.tvTitle.text = alert.title
        holder.tvPlotId.text = alert.plotId
        holder.tvDesc.text = alert.description

        holder.btnVerify.setOnClickListener {
            Toast.makeText(holder.itemView.context, "Opening Map for ${alert.plotId}...", Toast.LENGTH_SHORT).show()
            // Intent to open deep link or map activity would go here
        }
    }

    override fun getItemCount() = alerts.size
}
