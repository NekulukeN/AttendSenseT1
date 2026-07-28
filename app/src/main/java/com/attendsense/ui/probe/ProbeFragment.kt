package com.attendsense.ui.probe

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.CountDownTimer
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.attendsense.R
import com.attendsense.data.api.AttendSenseApi
import com.attendsense.data.api.RetrofitClient
import com.attendsense.databinding.FragmentProbeBinding
import com.attendsense.utils.CameraHelper
import kotlinx.coroutines.launch

class ProbeFragment : Fragment() {

    private var _binding: FragmentProbeBinding? = null
    private val binding get() = _binding!!

    private lateinit var api: AttendSenseApi
    private lateinit var cameraHelper: CameraHelper

    // Safe Args — receives probeId and probeType from HomeFragment
    private val args: ProbeFragmentArgs by navArgs()

    private var countDownTimer: CountDownTimer? = null

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) startCamera()
        else showResult("Camera permission is required.", isError = true)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProbeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        api          = RetrofitClient.getInstance(requireContext()).create(AttendSenseApi::class.java)
        cameraHelper = CameraHelper(requireContext())

        // Show the action the student needs to perform
        setupActionUI(args.probeType)

        checkCameraPermission()

        // Start 2 minute countdown — matches backend expiry time
        startCountdown()

        // Capture and respond
        binding.btnRespond.setOnClickListener {
            setLoading(true)
            cameraHelper.capturePhoto(
                onCaptured = { file ->
                    lifecycleScope.launch {
                        try {
                            val imagePart = cameraHelper.fileToMultipart(file, "file")
                            val response  = api.respondToProbe(args.probeId, imagePart)

                            requireActivity().runOnUiThread {
                                setLoading(false)
                                countDownTimer?.cancel()

                                if (response.isSuccessful) {
                                    showResult("✅ Probe passed! Attendance confirmed.", isError = false)
                                    binding.btnRespond.isEnabled = false
                                    binding.root.postDelayed({
                                        findNavController().navigate(R.id.action_probe_to_home)
                                    }, 1500)
                                } else {
                                    val error = response.errorBody()?.string()
                                        ?: "Response failed. Try again."
                                    showResult("❌ $error", isError = true)
                                    binding.btnRespond.isEnabled = true
                                }
                            }
                        } catch (e: Exception) {
                            requireActivity().runOnUiThread {
                                setLoading(false)
                                showResult("❌ Network error: ${e.message}", isError = true)
                                binding.btnRespond.isEnabled = true
                            }
                        }
                    }
                },
                onError = { msg ->
                    requireActivity().runOnUiThread {
                        setLoading(false)
                        showResult("❌ Capture failed: $msg", isError = true)
                        binding.btnRespond.isEnabled = true
                    }
                }
            )
        }

        binding.btnBack.setOnClickListener {
            countDownTimer?.cancel()
            findNavController().navigateUp()
        }
    }

    /**
     * Sets the icon, label and description based on the probe type
     * received from the backend: blink | smile | turn_left | turn_right
     */
    private fun setupActionUI(probeType: String) {
        when (probeType) {
            "blink" -> {
                binding.tvActionIcon.text  = "👁"
                binding.tvActionLabel.text = "BLINK"
                binding.tvActionDesc.text  = "Blink your eyes clearly while looking at the camera"
            }
            "smile" -> {
                binding.tvActionIcon.text  = "😊"
                binding.tvActionLabel.text = "SMILE"
                binding.tvActionDesc.text  = "Give a clear smile while looking at the camera"
            }
            "turn_left" -> {
                binding.tvActionIcon.text  = "⬅️"
                binding.tvActionLabel.text = "TURN LEFT"
                binding.tvActionDesc.text  = "Turn your head to the left slowly"
            }
            "turn_right" -> {
                binding.tvActionIcon.text  = "➡️"
                binding.tvActionLabel.text = "TURN RIGHT"
                binding.tvActionDesc.text  = "Turn your head to the right slowly"
            }
            else -> {
                binding.tvActionIcon.text  = "👤"
                binding.tvActionLabel.text = probeType.uppercase()
                binding.tvActionDesc.text  = "Perform the requested action"
            }
        }
    }

    /**
     * 2 minute countdown — matches the backend's probe expiry window.
     * When it hits 0 the probe has expired on the backend side,
     * so we disable the respond button and go back to Home.
     */
    private fun startCountdown() {
        countDownTimer = object : CountDownTimer(120_000, 1000) {
            override fun onTick(millisUntilFinished: Long) {
                val minutes = millisUntilFinished / 1000 / 60
                val seconds = (millisUntilFinished / 1000) % 60
                binding.tvCountdown.text = String.format("%d:%02d", minutes, seconds)

                // Turn countdown red in last 30 seconds
                if (millisUntilFinished <= 30_000) {
                    binding.tvCountdown.setTextColor(
                        ContextCompat.getColor(requireContext(), android.R.color.holo_red_light)
                    )
                }
            }

            override fun onFinish() {
                binding.tvCountdown.text         = "0:00 — Expired"
                binding.btnRespond.isEnabled     = false
                showResult("⏱ Time's up! This probe has expired.", isError = true)
                // Return to Home after a moment
                binding.root.postDelayed({
                    if (isAdded) findNavController().navigate(R.id.action_probe_to_home)
                }, 2000)
            }
        }.start()
    }

    private fun checkCameraPermission() {
        when {
            ContextCompat.checkSelfPermission(
                requireContext(), Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> startCamera()
            else -> requestPermissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    private fun startCamera() {
        cameraHelper.startPreview(binding.previewView, viewLifecycleOwner)
    }

    private fun setLoading(isLoading: Boolean) {
        binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        binding.btnRespond.isEnabled   = !isLoading
    }

    private fun showResult(message: String, isError: Boolean) {
        binding.tvResult.text = message
        binding.tvResult.setTextColor(
            ContextCompat.getColor(
                requireContext(),
                if (isError) android.R.color.holo_red_light
                else android.R.color.holo_green_light
            )
        )
        binding.tvResult.visibility = View.VISIBLE
    }

    override fun onDestroyView() {
        super.onDestroyView()
        countDownTimer?.cancel()
        cameraHelper.shutdown()
        _binding = null
    }
}

