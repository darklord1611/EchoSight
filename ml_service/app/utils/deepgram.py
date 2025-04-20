
from ..config import config
import os
import requests
import tempfile
from typing import Dict, Any

def transcribe_audio(audio_file_path):

    try:
        # Check if the audio file exists
        if not os.path.exists(audio_file_path):
            print("❌ Audio file not found:", audio_file_path)
            return {"error": "Audio file not found."}

        # Check if the file is a valid audio file
        if not audio_file_path.endswith(('.wav', '.mp3', '.webm')):
            print("❌ Invalid audio file format:", audio_file_path)
            return {"error": "Invalid audio file format."}

        # Send audio file to Deepgram
        headers = {
            "Authorization": f"Token {config.DEEPGRAM_API_KEY}",
            "Content-Type": "audio/webm"
        }

        with open(audio_file_path, "rb") as f:
            response = requests.post(
                "https://api.deepgram.com/v1/listen?model=enhanced-phonecall",
                headers=headers,
                data=f
            )

        if response.status_code != 200:
            print("❌ Deepgram error:", response.text)
            return {"error": "Failed to transcribe audio."}

        result = response.json()
        transcript = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
        print("🎙️ Transcript:", transcript)

        if not transcript:
            return {"error": "No transcript detected."}
        
        return {"transcript": transcript}

    except Exception as e:
        print("❌ Exception:", str(e))
        return {"error": "An error occurred during transcription."}

        

