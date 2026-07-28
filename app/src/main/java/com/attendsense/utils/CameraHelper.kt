package com.attendsense.utils

import android.content.Context
import android.util.Log
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * CameraHelper — reusable CameraX wrapper.
 *
 * Used by all 4 camera screens:
 *   FaceEnrollmentFragment, CheckInFragment, ProbeFragment, CheckOutFragment
 *
 * Basic usage:
 *   val camera = CameraHelper(requireContext())
 *   camera.startPreview(previewView, viewLifecycleOwner)
 *   camera.capturePhoto(
 *       onCaptured = { file -> val part = camera.fileToMultipart(file) },
 *       onError    = { msg -> showError(msg) }
 *   )
 */
class CameraHelper(private val context: Context) {

    private var imageCapture: ImageCapture? = null
    private val cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()

    companion object {
        private const val TAG = "CameraHelper"
        private const val FILENAME_FORMAT = "yyyy-MM-dd-HH-mm-ss-SSS"
    }

    /**
     * Starts the front-facing camera and binds it to the given PreviewView.
     * Call this after camera permission is granted, inside onViewCreated.
     */
    fun startPreview(previewView: PreviewView, lifecycleOwner: LifecycleOwner) {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)

        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

            imageCapture = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build()

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    lifecycleOwner,
                    CameraSelector.DEFAULT_FRONT_CAMERA, // Always front camera
                    preview,
                    imageCapture
                )
                Log.d(TAG, "Camera started")
            } catch (e: Exception) {
                Log.e(TAG, "Camera failed to start: ${e.message}")
            }
        }, ContextCompat.getMainExecutor(context))
    }

    /**
     * Takes a photo and returns the saved File via callback.
     * File is saved to app cache dir — Android auto-cleans it.
     */
    fun capturePhoto(onCaptured: (File) -> Unit, onError: (String) -> Unit) {
        val capture = imageCapture ?: run {
            onError("Camera not ready. Wait a moment and try again.")
            return
        }

        val photoFile = File(
            context.cacheDir,
            SimpleDateFormat(FILENAME_FORMAT, Locale.US)
                .format(System.currentTimeMillis()) + ".jpg"
        )

        val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()

        capture.takePicture(
            outputOptions,
            cameraExecutor,
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                    Log.d(TAG, "Photo saved: ${photoFile.absolutePath}")
                    onCaptured(photoFile)
                }

                override fun onError(exc: ImageCaptureException) {
                    Log.e(TAG, "Capture failed: ${exc.message}")
                    onError(exc.message ?: "Photo capture failed")
                }
            }
        )
    }

    /**
     * Converts a File into a Retrofit MultipartBody.Part ready to send to the API.
     * Used for: /face/enroll, /attendance/checkin, /probe/respond, /attendance/checkout
     */
    fun fileToMultipart(file: File, paramName: String = "image"): MultipartBody.Part {
        val requestBody = file.asRequestBody("image/jpeg".toMediaTypeOrNull())
        return MultipartBody.Part.createFormData(paramName, file.name, requestBody)
    }

    fun shutdown() {
        cameraExecutor.shutdown()
    }
}