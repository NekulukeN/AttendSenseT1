package com.attendsense.data.api

import android.content.Context
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {

    // Emulator: 10.0.2.2 always maps to your PC's localhost
    private const val BASE_URL_EMULATOR = "http://10.0.2.2:8000/"

    // Physical device: your PC's local IP — update if it changes
    private const val BASE_URL_DEVICE = "http://192.168.1.50:8000/"

    // Set to false when testing on a physical phone
    private const val USE_EMULATOR = false

    private val BASE_URL: String
        get() = if (USE_EMULATOR) BASE_URL_EMULATOR else BASE_URL_DEVICE

    @Volatile
    private var retrofit: Retrofit? = null

    fun getInstance(context: Context): Retrofit {
        return retrofit ?: synchronized(this) {
            retrofit ?: buildRetrofit(context).also { retrofit = it }
        }
    }

    private fun buildRetrofit(context: Context): Retrofit {

        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val authInterceptor = Interceptor { chain ->
            val prefs = context.getSharedPreferences("attendsense_prefs", Context.MODE_PRIVATE)
            val token = prefs.getString("jwt_token", null)

            val request = if (token != null) {
                chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
            } else {
                chain.request()
            }
            chain.proceed(request)
        }

        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()

        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}
