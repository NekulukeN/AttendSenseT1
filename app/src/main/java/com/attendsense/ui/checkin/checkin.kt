package com.attendsense.ui.checkin

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
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
import com.attendsense.databinding.FragmentCheckinBinding
import com.attendsense.utils.CameraHelper
import kotlinx.coroutines.launch

class CheckInFragment : Fragment() {

    private var _binding: FragmentCheckinBinding? = null
    private val binding get() = _binding!!

    private lateinit var api: AttendSenseApi
    private lateinit var cameraHelper: CameraHelper

    // Safe Args — receives sessionId and sessionName from HomeFragment
    private val args: CheckInFragmentArgs by navArgs()

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
        _binding = FragmentCheckinBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        api          = RetrofitClient.getInstance(requireContext()).create(AttendSenseApi::class.java)
        cameraHelper = CameraHelper(requireContext())

        // Show session info in header
        binding.tvTitle.text       = "Check In"
        binding.tvSessionName.text = args.sessionName

        checkCameraPermission()

        // Capture photo and immediately attempt check-in
        binding.btnCapture.setOnClickListener {
            setLoading(true)
            cameraHelper.capturePhoto(
                onCaptured = { file ->
                    lifecycleScope.launch {
                        try {
                            val imagePart = cameraHelper.fileToMultipart(file, "file")
                            val response  = api.checkIn(args.sessionId, imagePart)

                            requireActivity().runOnUiThread {
                                setLoading(false)
                                if (response.isSuccessful) {
                                    showResult("✅ Checked in successfully!", isError = false)
                                    // Return to Home after short delay
                                    binding.root.postDelayed({
                                        findNavController().navigate(R.id.action_checkin_to_home)
                                    }, 1500)
                                } else {
                                    val error = response.errorBody()?.string()
                                        ?: "Check-in failed. Please try again."
                                    showResult("❌ $error", isError = true)
                                    binding.btnCapture.isEnabled = true
                                }
                            }
                        } catch (e: Exception) {
                            requireActivity().runOnUiThread {
                                setLoading(false)
                                showResult("❌ Network error: ${e.message}", isError = true)
                                binding.btnCapture.isEnabled = true
                            }
                        }
                    }
                },
                onError = { msg ->
                    requireActivity().runOnUiThread {
                        setLoading(false)
                        showResult("❌ Capture failed: $msg", isError = true)
                        binding.btnCapture.isEnabled = true
                    }
                }
            )
        }

        binding.btnBack.setOnClickListener {
            findNavController().navigateUp()
        }
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
        binding.btnCapture.isEnabled   = !isLoading
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
        cameraHelper.shutdown()
        _binding = null
    }
}

