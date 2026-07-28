package com.attendsense.ui.history

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.attendsense.R
import com.attendsense.data.api.AttendSenseApi
import com.attendsense.data.api.RetrofitClient
import com.attendsense.data.model.AttendanceLogResponse
import com.attendsense.databinding.FragmentHistoryBinding
import kotlinx.coroutines.launch

class AttendanceHistoryFragment : Fragment() {

    private var _binding: FragmentHistoryBinding? = null
    private val binding get() = _binding!!

    private lateinit var api: AttendSenseApi

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHistoryBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        api = RetrofitClient.getInstance(requireContext()).create(AttendSenseApi::class.java)

        binding.rvAttendance.layoutManager = LinearLayoutManager(requireContext())

        binding.btnBack.setOnClickListener {
            findNavController().navigateUp()
        }

        binding.swipeRefresh.setOnRefreshListener { loadHistory() }

        loadHistory()
    }

    private fun loadHistory() {
        lifecycleScope.launch {
            try {
                binding.progressBar.visibility = View.VISIBLE
                binding.tvEmpty.visibility     = View.GONE
                binding.layoutStats.visibility = View.GONE

                val response = api.getMyAttendance()

                binding.progressBar.visibility    = View.GONE
                binding.swipeRefresh.isRefreshing = false

                if (response.isSuccessful) {
                    val logs = response.body() ?: emptyList()

                    if (logs.isEmpty()) {
                        binding.tvEmpty.visibility = View.VISIBLE
                        return@launch
                    }

                    // Calculate summary stats
                    val presentCount = logs.count { it.status == "present" }
                    val lateCount    = logs.count { it.status == "late" }
                    val absentCount  = logs.count { it.status == "absent" }

                    binding.tvPresentCount.text  = presentCount.toString()
                    binding.tvLateCount.text     = lateCount.toString()
                    binding.tvAbsentCount.text   = absentCount.toString()
                    binding.layoutStats.visibility = View.VISIBLE

                    // Populate list
                    binding.rvAttendance.adapter = AttendanceAdapter(logs)

                } else {
                    binding.tvEmpty.text       = "Failed to load attendance."
                    binding.tvEmpty.visibility = View.VISIBLE
                }

            } catch (e: Exception) {
                binding.progressBar.visibility    = View.GONE
                binding.swipeRefresh.isRefreshing = false
                binding.tvEmpty.text              = "Network error: ${e.message}"
                binding.tvEmpty.visibility        = View.VISIBLE
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

// ─── ATTENDANCE ADAPTER ───────────────────────────────────────────────────────

class AttendanceAdapter(
    private val logs: List<AttendanceLogResponse>
) : RecyclerView.Adapter<AttendanceAdapter.AttendanceViewHolder>() {

    inner class AttendanceViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvClassName: TextView = itemView.findViewById(R.id.tvClassName)
        val tvCheckIn: TextView   = itemView.findViewById(R.id.tvCheckIn)
        val tvCheckOut: TextView  = itemView.findViewById(R.id.tvCheckOut)
        val tvStatus: TextView    = itemView.findViewById(R.id.tvStatus)
        val statusBar: View       = itemView.findViewById(R.id.statusBar)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AttendanceViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_attendance_log, parent, false)
        return AttendanceViewHolder(view)
    }

    override fun onBindViewHolder(holder: AttendanceViewHolder, position: Int) {
        val log = logs[position]

        holder.tvClassName.text = log.className ?: "Session #${log.sessionId}"
        holder.tvCheckIn.text   = "Check in:  ${formatTime(log.checkInTime)}"
        holder.tvCheckOut.text  = "Check out: ${formatTime(log.checkOutTime)}"
        holder.tvStatus.text    = log.status.uppercase()

        // Colour the status bar and badge based on attendance status
        when (log.status) {
            "present" -> {
                val color = Color.parseColor("#388E3C")
                holder.statusBar.setBackgroundColor(color)
                holder.tvStatus.setBackgroundResource(R.drawable.bg_badge_active)
            }
            "late" -> {
                val color = Color.parseColor("#F57F17")
                holder.statusBar.setBackgroundColor(color)
                holder.tvStatus.setBackgroundResource(R.drawable.bg_badge_late)
            }
            "absent" -> {
                val color = Color.parseColor("#D32F2F")
                holder.statusBar.setBackgroundColor(color)
                holder.tvStatus.setBackgroundResource(R.drawable.bg_badge_absent)
            }
        }
    }

    override fun getItemCount() = logs.size

    private fun formatTime(time: String?): String {
        if (time == null) return "--"
        return try {
            // Format: "2024-01-15T14:30:00" → "2024-01-15  14:30"
            time.take(16).replace("T", "  ")
        } catch (e: Exception) {
            time
        }
    }
}

