package com.attendsense.data.model

import com.google.gson.annotations.SerializedName

// ─── AUTH ─────────────────────────────────────────────────────────────────────

data class LoginRequest(
    val email: String,
    val password: String
)

data class LoginResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type")   val tokenType: String
)

data class UserResponse(
    val id: Int,
    @SerializedName("student_id") val studentId: String?,
    @SerializedName("full_name")  val fullName: String,
    val email: String,
    val role: String,               // "student" | "lecturer" | "admin"
    @SerializedName("created_at") val createdAt: String
)

// ─── FACE ─────────────────────────────────────────────────────────────────────

data class FaceStatusResponse(
    val enrolled: Boolean,
    val message: String
)

// ─── SESSIONS ─────────────────────────────────────────────────────────────────

data class SessionResponse(
    val id: Int,
    @SerializedName("class_name")  val className: String,
    @SerializedName("lecturer_id") val lecturerId: Int,
    @SerializedName("start_time")  val startTime: String,
    @SerializedName("end_time")    val endTime: String?,
    val status: String              // "active" | "ended"
)

// ─── ATTENDANCE ───────────────────────────────────────────────────────────────

data class AttendanceLogResponse(
    val id: Int,
    @SerializedName("user_id")        val userId: Int,
    @SerializedName("session_id")     val sessionId: Int,
    @SerializedName("class_name")     val className: String?,
    @SerializedName("check_in_time")  val checkInTime: String?,
    @SerializedName("check_out_time") val checkOutTime: String?,
    val status: String                // "present" | "late" | "absent"
)

// ─── PROBE ────────────────────────────────────────────────────────────────────

data class PendingProbeResponse(
    @SerializedName("has_probe") val hasProbe: Boolean,
    @SerializedName("probe_id")  val id: Int,
    @SerializedName("action")    val probeType: String,
    val message: String? = null,
    @SerializedName("issued_at") val sentTime: String? = null
)

// ─── GENERIC ──────────────────────────────────────────────────────────────────

data class MessageResponse(
    val message: String,
    val status: String? = null
)