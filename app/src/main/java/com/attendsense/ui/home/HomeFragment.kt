package com.attendsense.ui.home

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.attendsense.R
import com.attendsense.data.api.AttendSenseApi
import com.attendsense.data.api.RetrofitClient
import com.attendsense.data.model.PendingProbeResponse
import com.attendsense.data.model.SessionResponse
import com.attendsense.databinding.FragmentHomeBinding
import com.attendsense.utils.SessionManager
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.launch

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private lateinit var api: AttendSenseApi
    private lateinit var session: SessionManager

    // Probe polling — checks every 30 seconds if a probe is pending
    private val probeHandler = Handler(Looper.getMainLooper())
    private var pendingProbe: PendingProbeResponse? = null

    private val probePollRunnable = object : Runnable {
        override fun run() {
            checkForPendingProbe()
            probeHandler.postDelayed(this, 30_000) // poll every 30 seconds
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        api     = RetrofitClient.getInstance(requireContext()).create(AttendSenseApi::class.java)
        session = SessionManager(requireContext())

        // Show welcome message
        binding.tvWelcome.text = "Welcome, ${session.getFullName()}"

        // Setup RecyclerView
        binding.rvSessions.layoutManager = LinearLayoutManager(requireContext())

        // Pull to refresh
        binding.swipeRefresh.setOnRefreshListener { loadSessions() }

        // Logout
        binding.btnLogout.setOnClickListener {
            session.clearSession()
            findNavController().navigate(R.id.action_home_to_login)
        }

        // History
        binding.btnHistory.setOnClickListener {
            findNavController().navigate(R.id.action_home_to_history)
        }

        // Probe alert banner — navigate to probe screen
        binding.btnRespondProbe.setOnClickListener {
            pendingProbe?.let { probe ->
                val action = HomeFragmentDirections.actionHomeToProbe(
                    probeId   = probe.id,
                    probeType = probe.probeType
                )
                findNavController().navigate(action)
            }
        }

        loadSessions()
        probeHandler.post(probePollRunnable) // start polling immediately
    }

    private fun loadSessions() {
        lifecycleScope.launch {
            try {
                binding.progressBar.visibility = View.VISIBLE
                binding.tvEmpty.visibility     = View.GONE

                val response = api.getAllSessions()

                binding.progressBar.visibility  = View.GONE
                binding.swipeRefresh.isRefreshing = false

                if (response.isSuccessful) {
                    // Only show active sessions
                    val active = response.body()?.filter { it.status == "active" } ?: emptyList()

                    if (active.isEmpty()) {
                        binding.tvEmpty.visibility    = View.VISIBLE
                        binding.rvSessions.visibility = View.GONE
                    } else {
                        binding.tvEmpty.visibility    = View.GONE
                        binding.rvSessions.visibility = View.VISIBLE
                        binding.rvSessions.adapter    = SessionAdapter(active) { session, action ->
                            onSessionAction(session, action)
                        }
                    }
                }
            } catch (e: Exception) {
                binding.progressBar.visibility    = View.GONE
                binding.swipeRefresh.isRefreshing = false
                binding.tvEmpty.text              = "Failed to load sessions."
                binding.tvEmpty.visibility        = View.VISIBLE
            }
        }
    }

    private fun checkForPendingProbe() {
        lifecycleScope.launch {
            try {
                val response = api.getPendingProbe()
                if (response.isSuccessful && response.body()?.hasProbe == true) {
                    pendingProbe = response.body()
                    binding.layoutProbeAlert.visibility = View.VISIBLE
                } else {
                    pendingProbe = null
                    binding.layoutProbeAlert.visibility = View.GONE
                }
            } catch (e: Exception) {
                // Silently fail — don't disrupt the home screen
            }
        }
    }

    private fun onSessionAction(session: SessionResponse, action: String) {
        when (action) {
            "checkin" -> {
                val action = HomeFragmentDirections.actionHomeToCheckin(
                    sessionId   = session.id,
                    sessionName = session.className
                )
                findNavController().navigate(action)
            }
            "checkout" -> {
                val action = HomeFragmentDirections.actionHomeToCheckout(
                    sessionId   = session.id,
                    sessionName = session.className
                )
                findNavController().navigate(action)
            }
        }
    }

    override fun onResume() {
        super.onResume()
        loadSessions()
        checkForPendingProbe() // immediately re-check instead of waiting up to 30s
    }

    override fun onDestroyView() {
        super.onDestroyView()
        probeHandler.removeCallbacks(probePollRunnable) // Stop polling
        _binding = null
    }
}

// ─── SESSION ADAPTER ──────────────────────────────────────────────────────────

class SessionAdapter(
    private val sessions: List<SessionResponse>,
    private val onAction: (SessionResponse, String) -> Unit
) : RecyclerView.Adapter<SessionAdapter.SessionViewHolder>() {

    inner class SessionViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvClassName: TextView     = itemView.findViewById(R.id.tvClassName)
        val tvStartTime: TextView     = itemView.findViewById(R.id.tvStartTime)
        val tvStatus: TextView        = itemView.findViewById(R.id.tvStatus)
        val btnCheckIn: MaterialButton  = itemView.findViewById(R.id.btnCheckIn)
        val btnCheckOut: MaterialButton = itemView.findViewById(R.id.btnCheckOut)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): SessionViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_session, parent, false)
        return SessionViewHolder(view)
    }

    override fun onBindViewHolder(holder: SessionViewHolder, position: Int) {
        val session = sessions[position]
        holder.tvClassName.text = session.className
        holder.tvStartTime.text = "Started: ${session.startTime.take(16).replace("T", " ")}"
        holder.tvStatus.text    = session.status.uppercase()

        holder.btnCheckIn.setOnClickListener  { onAction(session, "checkin") }
        holder.btnCheckOut.setOnClickListener { onAction(session, "checkout") }
    }

    override fun getItemCount() = sessions.size
}