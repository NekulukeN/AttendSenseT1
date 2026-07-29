package com.attendsense.utils

import android.content.Context
import android.content.SharedPreferences

/**
 * SessionManager — stores and retrieves JWT token + user info.
 *
 * Android equivalent of React's localStorage:
 *   localStorage.setItem("token", ...)  →  saveSession(...)
 *   localStorage.getItem("token")       →  getToken()
 *   localStorage.clear()                →  clearSession()
 */
class SessionManager(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("attendsense_prefs", Context.MODE_PRIVATE)

    companion object {
        const val KEY_TOKEN     = "jwt_token"
        const val KEY_ROLE      = "role"
        const val KEY_FULL_NAME = "full_name"
        const val KEY_USER_ID   = "user_id"
        const val KEY_EMAIL     = "email"
    }

    fun saveSession(
        token: String,
        role: String,
        fullName: String,
        userId: Int,
        email: String
    ) {
        prefs.edit().apply {
            putString(KEY_TOKEN, token)
            putString(KEY_ROLE, role)
            putString(KEY_FULL_NAME, fullName)
            putInt(KEY_USER_ID, userId)
            putString(KEY_EMAIL, email)
            apply()
        }
    }

    fun getToken(): String?    = prefs.getString(KEY_TOKEN, null)
    fun getRole(): String?     = prefs.getString(KEY_ROLE, null)
    fun getFullName(): String  = prefs.getString(KEY_FULL_NAME, "Student") ?: "Student"
    fun getUserId(): Int       = prefs.getInt(KEY_USER_ID, -1)
    fun getEmail(): String?    = prefs.getString(KEY_EMAIL, null)

    fun isLoggedIn(): Boolean  = getToken() != null

    fun clearSession() {
        prefs.edit().clear().apply()
    }
}