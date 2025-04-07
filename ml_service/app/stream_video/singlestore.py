import singlestoredb as s2
import sounddevice as sd
import soundfile as sf
import numpy as np
import speech_recognition as sr
from openai import OpenAI
import os
import base64
from playsound import playsound
from io import BytesIO

OpenAI.api_key = os.environ["OPENAI_API_KEY"]

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


client = OpenAI()


def frame_description(base64_image, user_prompt):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        },
    ]


def analyze_image(full_analysis, base64_image, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {
                "role": "system",
                "content": """
                You are assisting someone who is visually impaired. Provide a brief, concise description of the image in one sentence, including key details.
                Limit your response to no more than 50 words.
                """,
            },
        ] + full_analysis
        + frame_description(base64_image, user_prompt),
        max_tokens=50,
        stream=True, 
    )

    response_text = ""
    for chunk in response:
        if chunk.choices[0].delta.content:  
            chunk_text = chunk.choices[0].delta.content
            response_text += chunk_text  
            print(chunk_text, end='', flush=True)  
    
    return response_text.strip()


def play_audio(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    response.stream_to_file("audio/output.mp3")
    playsound("audio/output.mp3")


def get_prompt():
    audio_file = open("audio/input.mp3", "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )
    return transcript


def get_input_file(threshold=0.03, silence_duration=3, base64_image=None):
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        print("Listening for speech...")
        recognizer.adjust_for_ambient_noise(mic)
        started = False
        start_time = None
        audio_frames = []

        recording = True

        def callback(indata, frames, time, status):
            nonlocal started, start_time, audio_frames, recording, base64_image
            if np.any(indata > threshold):
                if not started:
                    print("Starting recording...")
                    image_path = "frames/frame.jpg"
                    base64_image = encode_image(image_path)
                    started = True
                    start_time = time.inputBufferAdcTime
                audio_frames.append(indata.copy())
            elif started:
                if time.inputBufferAdcTime - start_time > silence_duration:
                    recording = False
                    raise sd.CallbackAbort

        with sd.InputStream(callback=callback, channels=1):
            while True:
                if not recording:
                    break

        if audio_frames:
            audio_data = np.concatenate(audio_frames, axis=0)
            with BytesIO() as f:
                sf.write(f, audio_data, samplerate=70000, format='WAV')
                f.seek(0)
                with sr.AudioFile(f) as source:
                    audio = recognizer.record(source)
                    with open("audio/input.mp3", "wb") as mp3_file:
                        mp3_file.write(audio.get_wav_data(convert_rate=16000, convert_width=2))
        else:
            print("No speech detected")
        return base64_image


def main():
    full_analysis = []
    conn = s2.connect(
        'admin:Testing123@svc-ca8fa339-0d39-4942-ad73-4463f4110a1c-dml.aws-virginia-5.svc.singlestore.com:3306/testing')

    conn.autocommit(True)
    try:
        while True:
            final_image = get_input_file()
            user_prompt = get_prompt()
            print(user_prompt)
            analysis = analyze_image(full_analysis, final_image, user_prompt)
            print(analysis)
            play_audio(analysis)
            full_analysis.append({"role": "assistant", "content": analysis})

            insert_stmt = 'INSERT INTO OpenAISingleStore (TextValue) VALUES (%s)'

            with conn.cursor() as cur:
                cur.execute(insert_stmt, (user_prompt,))

                cur.execute('SELECT LAST_INSERT_ID()')
                last_id_result = cur.fetchone()
                if last_id_result:
                    last_id = last_id_result[0]
                    print("Last inserted ID:", last_id)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
