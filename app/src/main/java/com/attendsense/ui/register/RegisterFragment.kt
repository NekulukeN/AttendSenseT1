package com.attendsense.ui.register

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.attendsense.R
import com.attendsense.data.api.AttendSenseApi
import com.attendsense.data.api.RetrofitClient
import com.attendsense.data.model.RegisterRequest
import com.attendsense.databinding.FragmentRegisterBinding
import kotlinx.coroutines.launch

class RegisterFragment : Fragment() {

    private var _binding: FragmentRegisterBinding? = null
    private val binding get() = _binding!!

    private lateinit var api: AttendSenseApi

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentRegisterBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        api = RetrofitClient.getInstance(requireContext()).create(AttendSenseApi::class.java)

        binding.btnRegister.setOnClickListener {
            val fullName        = binding.etFullName.text.toString().trim()
            val studentId       = binding.etStudentId.text.toString().trim()
            val email            = binding.etEmail.text.toString().trim()
            val password         = binding.etPassword.text.toString().trim()
            val confirmPassword  = binding.etConfirmPassword.text.toString().trim()

            if (!validateInputs(fullName, email, password, confirmPassword)) return@setOnClickListener

            performRegister(
                fullName  = fullName,
                studentId = studentId.ifEmpty { null },
                email     = email,
                password  = password
            )
        }

        binding.tvBackToLogin.setOnClickListener {
            findNavController().navigate(R.id.action_register_to_login)
        }
    }

    private fun validateInputs(
        fullName: String,
        email: String,
        password: String,
        confirmPassword: String
    ): Boolean {
        if (fullName.isEmpty()) {
            binding.tilFullName.error = "Full name is required"
            return false
        }
        binding.tilFullName.error = null

        if (email.isEmpty()) {
            binding.tilEmail.error = "Email is required"
            return false
        }
        binding.tilEmail.error = null

        if (password.isEmpty()) {
            binding.tilPassword.error = "Password is required"
            return false
        }
        if (password.length < 6) {
            binding.tilPassword.error = "Password must be at least 6 characters"
            return false
        }
        binding.tilPassword.error = null

        if (confirmPassword != password) {
            binding.tilConfirmPassword.error = "Passwords do not match"
            return false
        }
        binding.tilConfirmPassword.error = null

        return true
    }

    private fun performRegister(
        fullName: String,
        studentId: String?,
        email: String,
        password: String
    ) {
        setLoading(true)

        lifecycleScope.launch {
            try {
                val response = api.register(
                    RegisterRequest(
                        studentId = studentId,
                        fullName  = fullName,
                        email     = email,
                        password  = password,
                        role      = "student"   // self-registration is always as a student
                    )
                )

                setLoading(false)

                if (response.isSuccessful) {
                    showSuccessAndReturnToLogin()
                } else {
                    val errorMsg = response.errorBody()?.string()
                    showError(parseErrorDetail(errorMsg) ?: "Registration failed. Please try again.")
                }

            } catch (e: Exception) {
                setLoading(false)
                showError("Network error: ${e.message}")
            }
        }
    }

    /** FastAPI errors come back as {"detail": "..."} — pull just the message out. */
    private fun parseErrorDetail(raw: String?): String? {
        if (raw.isNullOrEmpty()) return null
        return try {
            val regex = "\"detail\"\\s*:\\s*\"(.*?)\"".toRegex()
            regex.find(raw)?.groupValues?.get(1)
        } catch (e: Exception) {
            null
        }
    }

    private fun showSuccessAndReturnToLogin() {
        binding.tvError.setTextColor(
            resources.getColor(android.R.color.holo_green_dark, null)
        )
        showError("✅ Registration successful! Please log in.")
        binding.root.postDelayed({
            if (isAdded) findNavController().navigate(R.id.action_register_to_login)
        }, 1500)
    }

    private fun setLoading(isLoading: Boolean) {
        binding.progressBar.visibility  = if (isLoading) View.VISIBLE else View.GONE
        binding.btnRegister.isEnabled   = !isLoading
        binding.etFullName.isEnabled    = !isLoading
        binding.etStudentId.isEnabled   = !isLoading
        binding.etEmail.isEnabled       = !isLoading
        binding.etPassword.isEnabled    = !isLoading
        binding.etConfirmPassword.isEnabled = !isLoading
    }

    private fun showError(message: String) {
        binding.tvError.text       = message
        binding.tvError.visibility = View.VISIBLE
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
