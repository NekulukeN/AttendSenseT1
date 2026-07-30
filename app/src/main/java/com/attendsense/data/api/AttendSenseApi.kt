package com.attendsense.data.api

import com.attendsense.data.model.AttendanceLogResponse
import com.attendsense.data.model.FaceStatusResponse
import com.attendsense.data.model.RegisterRequest
import com.attendsense.data.model.RegisterResponse
import com.attendsense.data.model.LoginRequest
import com.attendsense.data.model.LoginResponse
import com.attendsense.data.model.MessageResponse
import okhttp3.RequestBody
import com.attendsense.data.model.ProbeRespondResult
import com.attendsense.data.model.PendingProbeResponse
import com.attendsense.data.model.SessionResponse
import com.attendsense.data.model.UserResponse
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.*

/**
 * AttendSenseApi — every endpoint the Android app calls.
 * Maps 1:1 to the FastAPI backend routes.
 */
interface AttendSenseApi {

    // ─── AUTH (/auth) ─────────────────────────────────────────────────────────

    @POST("auth/register")
    suspend fun register(
        @Body request: RegisterRequest
    ): Response<RegisterResponse>

    @POST("auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<LoginResponse>

    @GET("auth/me")
    suspend fun getMe(): Response<UserResponse>

    // ─── FACE (/face) ─────────────────────────────────────────────────────────

    @Multipart
    @POST("face/enroll")
    suspend fun enrollFace(
        @Part image: MultipartBody.Part
    ): Response<MessageResponse>

    @GET("face/status")
    suspend fun getFaceStatus(): Response<FaceStatusResponse>

    // ─── ATTENDANCE (/attendance) ─────────────────────────────────────────────

    @GET("attendance/sessions/all")
    suspend fun getAllSessions(): Response<List<SessionResponse>>

    @Multipart
    @POST("attendance/checkin/{session_id}")
    suspend fun checkIn(
        @Path("session_id") sessionId: Int,
        @Part image: MultipartBody.Part
    ): Response<MessageResponse>

    @Multipart
    @POST("attendance/checkout/{session_id}")
    suspend fun checkOut(
        @Path("session_id") sessionId: Int,
        @Part image: MultipartBody.Part
    ): Response<MessageResponse>

    // ─── PROBE (/probe) ───────────────────────────────────────────────────────

    @GET("probe/pending")
    suspend fun getPendingProbe(): Response<PendingProbeResponse>

    @Multipart
    @POST("probe/respond/{probe_id}")
    suspend fun respondToProbe(
        @Path("probe_id") probeId: Int,
        @Part image: MultipartBody.Part,
        @Part("slide_number") slideNumber: RequestBody
    ): Response<ProbeRespondResult>

    // ─── REPORTS (/reports) ───────────────────────────────────────────────────

    @GET("reports/my-attendance")
    suspend fun getMyAttendance(): Response<List<AttendanceLogResponse>>
}