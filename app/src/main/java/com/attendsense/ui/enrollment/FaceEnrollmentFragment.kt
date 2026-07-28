package com.attendsense.ui.enrollment

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
import com.attendsense.R
import com.attendsense.data.api.AttendSenseApi
import com.attendsense.data.api.RetrofitClient
import com.attendsense.databinding.FragmentFaceEnrollmentBinding
import com.attendsense.utils.CameraHelper
import kotlinx.coroutines.launch
import java.io.File

class FaceEnrollmentFragment : Fragment() {

    private var _binding: FragmentFaceEnrollmentBinding? = null
    private val binding get() = _binding!!

    private lateinit var api: AttendSenseApi
    private lateinit var cameraHelper: CameraHelper
    private var capturedFile: File? = null

    // Camera permission launcher
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) startCamera()
        else showStatus("Camera permission is required.", isError = true)
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentFaceEnrollmentBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        api          = RetrofitClient.getInstance(requireContext()).create(AttendSenseApi::class.java)
        cameraHelper = CameraHelper(requireContext())

        checkCameraPermission()

        // Capture photo
        binding.btnCapture.setOnClickListener {
            binding.btnCapture.isEnabled = false
            cameraHelper.capturePhoto(
                onCaptured = { file ->
                    capturedFile = file
                    requireActivity().runOnUiThread {
                        showStatus("Photo captured! Tap Enroll Face to continue.", isError = false)
                        binding.btnCapture.visibility = View.GONE
                        binding.btnEnroll.visibility  = View.VISIBLE
                        binding.btnRetake.visibility  = View.VISIBLE
                    }
                },
                onError = { msg ->
                    requireActivity().runOnUiThread {
                        binding.btnCapture.isEnabled = true
                        showStatus("Capture failed: $msg", isError = true)
                    }
                }
            )
        }

        // Enroll face — upload to /face/enroll
        binding.btnEnroll.setOnClickListener {
            val file = capturedFile ?: return@setOnClickListener
            enrollFace(file)
        }

        // Retake — reset UI and let user capture again
        binding.btnRetake.setOnClickListener {
            capturedFile = null
            binding.btnCapture.visibility = View.VISIBLE
            binding.btnCapture.isEnabled  = true
            binding.btnEnroll.visibility  = View.GONE
            binding.btnRetake.visibility  = View.GONE
            binding.tvStatus.visibility   = View.GONE
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

    private fun enrollFace(file: File) {
        setLoading(true)

        lifecycleScope.launch {
            try {
                val imagePart = cameraHelper.fileToMultipart(file, "file")
                val response  = api.enrollFace(imagePart)

                setLoading(false)

                if (response.isSuccessful) {
                    showStatus("✅ Face enrolled successfully!", isError = false)
                    // Wait a moment then navigate to Home
                    binding.root.postDelayed({
                        findNavController().navigate(R.id.action_enrollment_to_home)
                    }, 1500)
                } else {
                    val errorMsg = response.errorBody()?.string() ?: "Enrollment failed"
                    showStatus("❌ $errorMsg", isError = true)
                    // Show retake option on failure
                    binding.btnRetake.visibility = View.VISIBLE
                    binding.btnEnroll.visibility = View.GONE
                }
            } catch (e: Exception) {
                setLoading(false)
                showStatus("❌ Network error: ${e.message}", isError = true)
            }
        }
    }

    private fun setLoading(isLoading: Boolean) {
        binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        binding.btnEnroll.isEnabled    = !isLoading
        binding.btnRetake.isEnabled    = !isLoading
    }

    private fun showStatus(message: String, isError: Boolean) {
        binding.tvStatus.text      = message
        binding.tvStatus.setTextColor(
            ContextCompat.getColor(
                requireContext(),
                if (isError) android.R.color.holo_red_light
                else android.R.color.holo_green_light
            )
        )
        binding.tvStatus.visibility = View.VISIBLE
    }

    override fun onDestroyView() {
        super.onDestroyView()
        cameraHelper.shutdown()
        _binding = null
    }
}