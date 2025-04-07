package com.example.frontend_kotlin

import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.view.View
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.example.frontend_kotlin.utils.TTS

class DocumentActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_document)
        TTS.initialize(this)

        val responseText = intent.getStringExtra("responseText")
        val textView: TextView = findViewById(R.id.responseTextView)
        textView.text = responseText

        TTS.speak(responseText.toString(), TextToSpeech.QUEUE_FLUSH, null, "utteranceId") {
            runOnUiThread {
                finish()
            }
        }
    }

    fun onReturnClick(view: View) {
        TTS.stop()
        finish()
    }
}