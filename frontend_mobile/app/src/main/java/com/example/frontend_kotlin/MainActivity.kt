package com.example.frontend_kotlin

import android.Manifest
import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.PackageManager
import android.media.MediaActionSound
import android.media.MediaRecorder
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.util.Log
import android.view.MotionEvent
import android.view.View
import android.widget.Button
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.lifecycle.lifecycleScope
import com.example.frontend_kotlin.utils.TTS
import com.example.frontend_kotlin.utils.Utils
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.launch
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONObject
import java.io.File
import java.io.IOException

class MainActivity : AppCompatActivity() {
    private lateinit var previewView: PreviewView
    private var selectedButton: MaterialButton? = null
    private var selectedButtonText: String? = null
    private var userTranscribe : String = ""
    private lateinit var imageCapture: ImageCapture
    private lateinit var endpoints: Map<String, String>
    private var isUsingBackCamera = true
    private lateinit var addFaceActivityResultLauncher: ActivityResultLauncher<Intent>

    // Audio recording
    private lateinit var mediaRecorder: MediaRecorder
    private lateinit var audioFile: File
    private val REQUEST_RECORD_AUDIO_PERMISSION = 200
    private var permissionToRecordAccepted = false
    private val permissions: Array<String> = arrayOf(Manifest.permission.RECORD_AUDIO)

    companion object {
        private const val REQUEST_CODE_PERMISSIONS = 10
        private const val BASE_URL = "http://192.168.1.6:8000"
        private val REQUIRED_PERMISSIONS = arrayOf(Manifest.permission.CAMERA)
    }

    private fun requestAudioPermissions() {
        ActivityCompat.requestPermissions(this, permissions, REQUEST_RECORD_AUDIO_PERMISSION)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<out String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            REQUEST_RECORD_AUDIO_PERMISSION -> {
                permissionToRecordAccepted = grantResults[0] == PackageManager.PERMISSION_GRANTED
                if (!permissionToRecordAccepted) finish()
            }
            REQUEST_CODE_PERMISSIONS -> {
                if (allPermissionsGranted()) {
                    startCamera()
                } else {
                    Toast.makeText(this, "Permissions not granted", Toast.LENGTH_SHORT).show()
                    finish()
                }
            }
        }
    }

    @SuppressLint("ClickableViewAccessibility")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)
        previewView = findViewById(R.id.camera_preview)

        TTS.initialize(this)

        requestAudioPermissions()

        val voiceRecordButton: Button = findViewById(R.id.voice_record_button)
        voiceRecordButton.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> startRecording()
                MotionEvent.ACTION_UP -> stopRecordingAndSend()
            }
            true
        }

        endpoints = mapOf(
            getString(R.string.text) to "/document_recognition",
            getString(R.string.money) to "/currency_detection",
            getString(R.string.item) to "/image_captioning",
            getString(R.string.product) to "/product_recognition",
            getString(R.string.distance) to "/distance_estimate",
            getString(R.string.face) to "/face_detection/recognize",
            getString(R.string.add_face) to "/face_detection/register"
            )

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        if (allPermissionsGranted()) {
            startCamera()
        } else {
            requestPermissions()
        }

        val firstButton: MaterialButton = findViewById(R.id.text_button)
        firstButton.performClick()

        addFaceActivityResultLauncher = registerForActivityResult(
            ActivityResultContracts.StartActivityForResult()
        ) { result ->
            Log.d("MainActivity", "addFaceActivityResultLauncher")
            if (result.resultCode == RESULT_OK) {
                val data = result.data
                val name = data?.getStringExtra("name")
                val hometown = data?.getStringExtra("hometown")
                val relationship = data?.getStringExtra("relationship")
                val dateOfBirth = data?.getStringExtra("date_of_birth")
                val photoFilePath = data?.getStringExtra("photoFilePath")

                Log.d("MainActivity", "name: $name, hometown: $hometown, relationship: $relationship, dateOfBirth: $dateOfBirth, photoFilePath: $photoFilePath")

                if (name != null && hometown != null && relationship != null && dateOfBirth != null && photoFilePath != null) {
                    val photoFile = File(photoFilePath)
                    sendImageToEndpoint(photoFile, name, hometown, relationship, dateOfBirth)
                }
            }
        }
    }

    override fun onDestroy() {
        Log.d("MainActivity", "onDestroy")
        TTS.stop()
        super.onDestroy()
    }

    private fun allPermissionsGranted() = REQUIRED_PERMISSIONS.all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }

    private fun requestPermissions() {
        ActivityCompat.requestPermissions(
            this, REQUIRED_PERMISSIONS, REQUEST_CODE_PERMISSIONS
        )
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
            imageCapture = ImageCapture.Builder().build()
            val cameraSelector = if (isUsingBackCamera) {
                CameraSelector.DEFAULT_BACK_CAMERA
            } else {
                CameraSelector.DEFAULT_FRONT_CAMERA
            }
            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageCapture)
            } catch (exc: Exception) {
                Log.e("MainActivity", "Use case binding failed", exc)
                Toast.makeText(this, "Camera initialization failed", Toast.LENGTH_SHORT).show()
            }
        }, ContextCompat.getMainExecutor(this))
    }


    fun onMenuClick(view: View) {
        Toast.makeText(this, "Menu clicked", Toast.LENGTH_SHORT).show()
    }

    fun onChangeCameraClick(view: View) {
        isUsingBackCamera = !isUsingBackCamera
        startCamera()
    }

    fun onButtonClick(view: View) {
        if (view is MaterialButton) {
            selectedButton?.iconTint = ContextCompat.getColorStateList(this, R.color.primary)
            view.iconTint = ContextCompat.getColorStateList(this, R.color.selected)
            selectedButton = view
            selectedButtonText = view.contentDescription.toString()
            Log.d("MainActivity", "Button clicked: $selectedButtonText")
            TTS.speak(selectedButtonText.toString(), TextToSpeech.QUEUE_FLUSH, null, null)
        }
    }

    fun onCaptureClick(view: View) {
        val photoFile = File(externalMediaDirs.firstOrNull(), "${System.currentTimeMillis()}.jpg")
        val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()

        imageCapture.takePicture(
            outputOptions,
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                    val savedUri = output.savedUri ?: Uri.fromFile(photoFile)
                    val msg = "Photo capture succeeded: $savedUri"
                    Log.d("MainActivity", msg)
                    TTS.speak("Chụp ảnh thành công", TextToSpeech.QUEUE_FLUSH, null, null)
                    playCaptureSound()

                    if (selectedButtonText == getString(R.string.add_face)) {
                        Log.d("MainActivity", "Add face activity")
                        val intent = Intent(this@MainActivity, AddFaceActivity::class.java).apply {
                            putExtra("photoFilePath", photoFile.absolutePath)
                        }
                        addFaceActivityResultLauncher.launch(intent)
                    } else {
                        sendImageToEndpoint(photoFile)
                    }
                }

                override fun onError(exception: ImageCaptureException) {
                    Log.e("MainActivity", "Photo capture failed: ${exception.message}", exception)
                }
            }
        )
    }

    private fun playCaptureSound() {
        val sound = MediaActionSound()
        sound.play(MediaActionSound.SHUTTER_CLICK)
    }



    private fun sendImageToEndpoint(photoFile: File) {

        val endpoint = endpoints[selectedButtonText]
        Log.d("sendImageToEndpoint", "Endpoint: $endpoint")
        if (endpoint == null) {
            return
        } else if (selectedButtonText == getString(R.string.distance)) {

            val client = OkHttpClient.Builder()
                .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                .build();
            val mediaType = "image/png".toMediaTypeOrNull()
            Log.e("MainActivity", "User transcribe: $userTranscribe")
            val requestBody = MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", photoFile.name, photoFile.asRequestBody(mediaType))
                .build()

            val request = Request.Builder()
                .url("$BASE_URL$endpoint?transcribe=$userTranscribe")
                .post(requestBody)
                .addHeader("Accept", "application/json")
                .addHeader("Content-Type", "multipart/form-data")
                .build()

            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    Log.e("MainActivity", "Error sending image to endpoint", e)
                }

                @RequiresApi(Build.VERSION_CODES.O)
                override fun onResponse(call: Call, response: Response) {
                    if (!response.isSuccessful) {
                        Log.e("MainActivity", "HTTP error! status: ${response.code}")
                        return
                    } else {
                        Log.d("MainActivity", "HTTP success! status: ${response.code}")
                    }

                    val responseBody = response.body?.string()
                    if (responseBody == null) {
                        Log.e("MainActivity", "Empty response body")
                        return
                    }

                    Log.d("MainActivity", "Response body: $responseBody")

                    val jsonObject = JSONObject(responseBody)
                    val text: String? = jsonObject.optString("text", null)
                    val totalMoney: String? = jsonObject.optString("total_money", null)
                    val description: String? = jsonObject.optString("description", null)

                    val responseText = when (selectedButtonText) {
                        getString(R.string.text) -> text
                        getString(R.string.money) -> totalMoney
                        getString(R.string.item) -> description
                        getString(R.string.product) -> description
                        getString(R.string.distance) -> description
                        getString(R.string.face) -> description
                        else -> "Không thể xử lý yêu cầu"
                    }
                    Log.d("MainActivity", "Response text: $responseText")
                    TTS.speak(responseText.toString(), TextToSpeech.QUEUE_FLUSH, null, "utteranceId")
                }
            })
            return;
        }
        val client = OkHttpClient.Builder()
            .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .build();
        val mediaType = "image/png".toMediaTypeOrNull()

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", photoFile.name, photoFile.asRequestBody(mediaType))
            .build()

        val request = Request.Builder()
            .url("$BASE_URL$endpoint")
            .post(requestBody)
            .addHeader("Accept", "application/json")
            .addHeader("Content-Type", "multipart/form-data")
            .build()


        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("MainActivity", "Error sending image to endpoint", e)
            }

            @RequiresApi(Build.VERSION_CODES.O)
            override fun onResponse(call: Call, response: Response) {
                if (!response.isSuccessful) {
                    Log.e("MainActivity", "HTTP error! status: ${response.code}")
                    return
                } else {
                    Log.d("MainActivity", "HTTP success! status: ${response.code}")
                }

                val responseBody = response.body?.string()
                if (responseBody == null) {
                    Log.e("MainActivity", "Empty response body")
                    return
                }

                Log.d("MainActivity", "Response body: $responseBody")

                val jsonObject = JSONObject(responseBody)
                val text: String? = jsonObject.optString("text", null)
                val totalMoney: String? = jsonObject.optString("total_money", null)
                val description: String? = jsonObject.optString("description", null)

                val responseText = when (selectedButtonText) {
                    getString(R.string.text) -> text
                    getString(R.string.money) -> totalMoney
                    getString(R.string.item) -> description
                    getString(R.string.product) -> description
                    getString(R.string.distance) -> description
                    getString(R.string.face) -> description
                    else -> "Không thể xử lý yêu cầu"
                }
                Log.d("MainActivity", "Response text: $responseText")
                TTS.speak(responseText.toString(), TextToSpeech.QUEUE_FLUSH, null, "utteranceId")

                // document recognition activity screen
                if (selectedButtonText == getString(R.string.text)) {
                    val intent = Intent(this@MainActivity, DocumentActivity::class.java).apply {
                        putExtra("responseText", responseText)
                    }
                    startActivity(intent)
                }
            }
        })
    }

    private fun sendImageToEndpoint(photoFile: File, name: String, hometown: String, relationship: String, dateOfBirth: String) {
        val endpoint = endpoints[selectedButtonText]
        Log.d("MainActivity", "Endpoint: $endpoint")
        if (endpoint == null) {
            return
        }

        val client = OkHttpClient.Builder()
            .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .build()
        val mediaType = "image/png".toMediaTypeOrNull()

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", photoFile.name, photoFile.asRequestBody(mediaType))
            .build()

        val url = "$BASE_URL$endpoint?name=$name&hometown=$hometown&relationship=$relationship&date_of_birth=$dateOfBirth"

        val request = Request.Builder()
            .url(url)
            .post(requestBody)
            .addHeader("Accept", "application/json")
            .addHeader("Content-Type", "multipart/form-data")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("MainActivity", "Error sending image to endpoint", e)
            }

            @RequiresApi(Build.VERSION_CODES.O)
            override fun onResponse(call: Call, response: Response) {
                if (!response.isSuccessful) {
                    Log.e("MainActivity", "HTTP error! status: ${response.code}")
                    return
                } else {
                    Log.d("MainActivity", "HTTP success! status: ${response.code}")
                }

                val responseBody = response.body?.string()
                if (responseBody == null) {
                    Log.e("MainActivity", "Empty response body")
                    return
                }

                Log.d("MainActivity", "Response body: $responseBody")
                TTS.speak("Đã thêm khuôn mặt thành công", TextToSpeech.QUEUE_FLUSH, null, null)
            }
        })
    }

    private fun startRecording() {
//        TTS.speak("Đang ghi âm, bạn muốn làm gì?", TextToSpeech.QUEUE_FLUSH, null, null)
        try {
            audioFile = File(externalCacheDir?.absolutePath + "/voice_command.mp3")
            mediaRecorder = MediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setOutputFile(audioFile.absolutePath)
                prepare()
                start()
            }
        } catch (e: Exception) {
            Log.e("MainActivity", "Error starting recording", e)
            mediaRecorder.release()
        }
    }

    private fun stopRecordingAndSend() {
        if (!this::mediaRecorder.isInitialized) {
            return
        }
        try {
            mediaRecorder.apply {
                stop()
                release()
            }
            if (!this::audioFile.isInitialized) {
                return
            }
            handleCommandResponse(audioFile)
        } catch (e: Exception) {
            Log.e("MainActivity", "Error stopping recording", e)
            mediaRecorder.release()
        }
    }

    private fun handleCommandResponse(audioFile: File) {
        lifecycleScope.launch {
            try {
                val audioFilePath = audioFile.absolutePath
                val transcribe = Utils.getSpeechToText(audioFilePath)
                userTranscribe = transcribe
                Log.d("MainActivity", "Transcribe: $transcribe")
                val command = Utils.getCommand(transcribe)
                Log.d("MainActivity", "Command: $command")
                TTS.speak(command, TextToSpeech.QUEUE_FLUSH, null, null)

                when (command) {
                    "text" -> onButtonClick(findViewById(R.id.text_button))
                    "money" -> onButtonClick(findViewById(R.id.money_button))
                    "item" -> onButtonClick(findViewById(R.id.item_button))
                    "product" -> onButtonClick(findViewById(R.id.product_button))
                    "distance" -> onButtonClick(findViewById(R.id.distance_button))
                    "face" -> onButtonClick(findViewById(R.id.face_button))
                    "add_face" -> onButtonClick(findViewById(R.id.add_face_button))
                    else -> {
                        TTS.speak("Không thể xử lý yêu cầu", TextToSpeech.QUEUE_FLUSH, null, null)
                    }
                }
            } catch (e: Exception) {
                Log.e("MainActivity", "Error handling command response", e)
            }
        }
    }
}
