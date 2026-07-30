package com.attendsense.ui.login

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
import com.attendsense.data.model.LoginRequest
import com.attendsense.databinding.FragmentLoginBinding
import com.attendsense.utils.SessionManager
import kotlinx.coroutines.launch

class LoginFragment : Fragment() {

    private var _binding: FragmentLoginBinding? = null
    private val binding get() = _binding!!

    private lateinit var api: AttendSenseApi
    private lateinit var session: SessionManager

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLoginBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        api = RetrofitClient.getInstance(requireContext()).create(AttendSenseApi::class.java)
        session = SessionManager(requireContext())

        binding.btnLogin.setOnClickListener {
            val email    = binding.etEmail.text.toString().trim()
            val password = binding.etPassword.text.toString().trim()

            if (!validateInputs(email, password)) return@setOnClickListener
            performLogin(email, password)
        }
        binding.tvGoToRegister.setOnClickListener {
            findNavController().navigate(R.id.action_login_to_register)
        }
    }

    private fun validateInputs(email: String, password: String): Boolean {
        if (email.isEmpty()) {
            binding.tilEmail.error = "Email is required"
            return false
        }
        binding.tilEmail.error = null

        if (password.isEmpty()) {
            binding.tilPassword.error = "Password is required"
            return false
        }
        binding.tilPassword.error = null

        return true
    }

    private fun performLogin(email: String, password: String) {
        setLoading(true)

        lifecycleScope.launch {
            try {
                // Step 1 — Login and get JWT token
                val loginResponse = api.login(LoginRequest(email, password))

                if (!loginResponse.isSuccessful) {
                    showError("Invalid email or password")
                    setLoading(false)
                    return@launch
                }

                val token = loginResponse.body()?.accessToken ?: run {
                    showError("Login failed. Please try again.")
                    setLoading(false)
                    return@launch
                }

                // Step 2 — Get user profile with the token
                // Temporarily save token so RetrofitClient interceptor picks it up
                SessionManager(requireContext()).saveSession(
                    token    = token,
                    role     = "",
                    fullName = "",
                    userId   = -1,
                    email    = email
                )

                val meResponse = api.getMe()
                if (!meResponse.isSuccessful) {
                    showError("Could not fetch user profile.")
                    setLoading(false)
                    return@launch
                }

                val user = meResponse.body()!!

                // Step 3 — Save full session info
                session.saveSession(
                    token    = token,
                    role     = user.role,
                    fullName = user.fullName,
                    userId   = user.id,
                    email    = user.email
                )

                // Step 4 — Check if face is already enrolled
                val faceResponse = api.getFaceStatus()
                val isEnrolled   = faceResponse.body()?.enrolled == true

                setLoading(false)

                // Step 5 — Navigate based on face status
                if (isEnrolled) {
                    findNavController().navigate(R.id.action_login_to_home)
                } else {
                    findNavController().navigate(R.id.action_login_to_enrollment)
                }

            } catch (e: Exception) {
                setLoading(false)
                showError("Network error: ${e.message}")
            }
        }
    }

    private fun setLoading(isLoading: Boolean) {
        binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        binding.btnLogin.isEnabled     = !isLoading
        binding.etEmail.isEnabled      = !isLoading
        binding.etPassword.isEnabled   = !isLoading
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
