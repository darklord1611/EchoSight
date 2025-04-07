package com.example.frontend_kotlin.utils

import android.util.Log
import io.github.cdimascio.dotenv.Dotenv
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.OkHttpClient
import io.github.cdimascio.dotenv.Dotenv
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File
import java.util.concurrent.TimeUnit


data class Message(
    val role: String,
    val content: String
)

data class DeepgramTranscriptionResponse(
    val results: Results
)

data class Results(
    val channels: List<Channel>
)

data class Channel(
    val alternatives: List<Alternative>
)

data class Alternative(
    val transcript: String
)
data class OpenAiRequest(
    val model: String = "gpt-4o-mini",
    val messages: List<Message>,
    val temperature: Double = 0.2,
    @SerializedName("max_tokens") val maxTokens: Int = 50
)

data class OpenAiResponse(
    val choices: List<Choice>
)

data class Choice(
    val message: MessageContent
)

data class MessageContent(
    val content: String?
)



object Utils {
    private val DeepgramApiKey = Dotenv.load()["DEEPGRAM_API_KEY"]
    private val OpenaiApiKey = Dotenv.load()["OPENAI_API_KEY"]
    val gson = Gson()

    suspend fun getSpeechToText(audioFile: String): String = withContext(Dispatchers.IO) {
        Log.d("Utils", "Transcribing audio file: $audioFile")
        val client = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()

        val file = File(audioFile)

        val requestBody = file.asRequestBody("audio/wav".toMediaTypeOrNull())

        val request = Request.Builder()
            .url("https://api.deepgram.com/v1/listen?smart_format=true&model=nova-2&language=vi")
            .post(requestBody)
            .addHeader("Authorization", "Token $DeepgramApiKey")
            .build()

        try {
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    throw RuntimeException("API call failed: ${response.code} - ${response.message}")
                }

                val responseBody = response.body?.string()
                    ?: throw IllegalStateException("Empty response body")

                val transcriptionResponse = gson.fromJson(
                    responseBody,
                    DeepgramTranscriptionResponse::class.java
                )

                return@withContext transcriptionResponse.results.channels[0].alternatives[0].transcript
            }
        } catch (e: Exception) {
            throw RuntimeException("Error processing speech-to-text: ${e.message}", e)
        }
    }

    suspend fun getCommand(transcribe: String): String = withContext(Dispatchers.IO) {
        val client = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

        val gson = Gson()

        val requestBody = OpenAiRequest(
            messages = listOf(
                Message(
                    role = "system",
                    content = """
            Bạn là trợ lý AI chuyên xử lý các yêu cầu từ văn bản chuyển đổi từ giọng nói. 
            Dựa trên nội dung của yêu cầu, hãy trả về ID duy nhất của hành động phù hợp nhất từ danh sách dưới đây:
            
            - 'text' - Nhận diện văn bản.
            - 'money' - Nhận diện tiền mặt.
            - 'item' - Giải thích hình ảnh.
            - 'product' - Nhận diện sản phẩm thông qua mã vạch.
            - 'distance' - Tìm kiếm vị trí của một vật thể và khoảng cách từ vị trí hiện tại.
            - 'add_face' - Đăng ký nhận diện khuôn mặt với người thân, bạn bè của tôi.
            - 'face' - Nhận diện khuôn mặt.

            Quy tắc:
            - Chỉ trả về ID duy nhất. Không thêm bất kỳ văn bản nào khác.
            - Nếu yêu cầu không chắc chắn hoặc không rõ ràng, hãy trả về 'text' làm mặc định.
            - Ưu tiên trả về ID chính xác nhất dựa trên ngữ cảnh của yêu cầu.
            - Nếu không có ID phù hợp trong danh sách, hãy trả về 'text'.
            """.trimIndent()
                ),
                Message(
                    role = "user",
                    content = transcribe
                )
            )
        )

        val jsonRequest = gson.toJson(requestBody)

        val request = Request.Builder()
            .url("https://api.openai.com/v1/chat/completions")
            .addHeader("Content-Type", "application/json")
            .addHeader("Authorization", "Bearer $OpenaiApiKey")
            .post(jsonRequest.toRequestBody("application/json".toMediaTypeOrNull()))
            .build()

        try {
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    Log.e("CommandParser", "API Error: ${response.body?.string()}")
                    return@withContext "text"
                }

                val responseBody = response.body?.string() ?: return@withContext "text"
                val apiResponse = gson.fromJson(responseBody, OpenAiResponse::class.java)
                val content = apiResponse.choices[0].message.content?.trim() ?: return@withContext "text"

                val validIds = setOf(
                    "text",
                    "money",
                    "item",
                    "product",
                    "distance",
                    "face",
                    "add_face"
                )

                return@withContext if (content in validIds) content else "text"
            }
        } catch (e: Exception) {
            Log.e("CommandParser", "Error parsing command", e)
            return@withContext "text"
        }
    }

    fun String.sanitizeCommandId(): String {
        val validIds = setOf(
            "text",
            "money",
            "item",
            "barcode",
            "distance",
            "add_face",
            "face"
        )

        return if (this in validIds) this else "text"
    }
}

suspend fun main() {
//    val audioFilePath = "/home/xuananle/Voice 002.wav"
//    val transcribe = Utils.getSpeechToText(audioFilePath)
//    println(transcribe)
        println(Utils.getCommand("Tôi muốn tìm vị trí của cái kéo đang nằm trước mặt tôi"))
}
