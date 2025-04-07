package com.example.frontend_kotlin

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity
import java.io.File

class AddFaceActivity : AppCompatActivity() {
    private lateinit var photoFile: File

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_add_face)

        val photoFilePath = intent.getStringExtra("photoFilePath")
        if (photoFilePath == null) {
            finish()
            return
        }
        photoFile = File(photoFilePath)

        val nameEditText: EditText = findViewById(R.id.name)
        val hometownEditText: EditText = findViewById(R.id.hometown)
        val relationshipEditText: EditText = findViewById(R.id.relationship)
        val dateOfBirthEditText: EditText = findViewById(R.id.date_of_birth)
        val confirmButton: Button = findViewById(R.id.confirm_button)

        confirmButton.setOnClickListener {
            val name = nameEditText.text.toString()
            val hometown = hometownEditText.text.toString()
            val relationship = relationshipEditText.text.toString()
            val dateOfBirth = dateOfBirthEditText.text.toString()

            val resultIntent = Intent().apply {
                putExtra("name", name)
                putExtra("hometown", hometown)
                putExtra("relationship", relationship)
                putExtra("date_of_birth", dateOfBirth)
                putExtra("photoFilePath", photoFile.absolutePath)
            }
            setResult(RESULT_OK, resultIntent)
            finish()
        }
    }

    fun onReturnClick(view: View) {
        setResult(RESULT_CANCELED)
        finish()
    }
}