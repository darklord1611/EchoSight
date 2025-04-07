import json
import os
import threading
import asyncio
import queue
import re
from websockets.sync.client import connect
import pyaudio
import requests


class DeepgramSpeaker:
    TIMEOUT = 0.050
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    CHUNK = 8000

    def __init__(self, api_key=None, url=None):
        self.api_key = api_key or os.environ.get("DEEPGRAM_API_KEY")
        self.url = url or f"wss://api.deepgram.com/v1/speak?encoding=linear16&sample_rate={self.RATE}"
        self._socket = None
        self._exit = threading.Event()
        self._receiver_thread = None
        self.speaker = Speaker()

    def connect(self):
        print(f"Connecting to {self.url}")
        self._socket = connect(
            self.url, additional_headers={"Authorization": f"Token {self.api_key}"}
        )

    async def _receiver(self):
        self.speaker.start()
        try:
            while not self._exit.is_set():
                message = self._socket.recv()
                if message is None:
                    continue

                if isinstance(message, str):
                    print(message)
                elif isinstance(message, bytes):
                    self.speaker.play(message)
        except Exception as e:
            print(f"receiver: {e}")
        finally:
            self.speaker.stop()

    def start_receiver(self):
        self._receiver_thread = threading.Thread(target=asyncio.run, args=(self._receiver(),))
        self._receiver_thread.start()

    def speak(self, text):
        if not self._socket:
            raise RuntimeError("Not connected. Call connect() first.")
        print(f"Sending: {text}")
        self._socket.send(json.dumps({"type": "Speak", "text": text}))

    def flush(self):
        print("Flushing...")
        self._socket.send(json.dumps({"type": "Flush"}))

    def close(self):
        self._exit.set()
        if self._socket:
            self._socket.send(json.dumps({"type": "Close"}))
            self._socket.close()
        if self._receiver_thread:
            self._receiver_thread.join()

class Speaker:
    def __init__(
        self,
        rate=DeepgramSpeaker.RATE,
        chunk=DeepgramSpeaker.CHUNK,
        channels=DeepgramSpeaker.CHANNELS,
        output_device_index=None,
    ):
        self._exit = threading.Event()
        self._queue = queue.Queue()
        self._audio = pyaudio.PyAudio()
        self._chunk = chunk
        self._rate = rate
        self._format = DeepgramSpeaker.FORMAT
        self._channels = channels
        self._output_device_index = output_device_index
        self._stream = None
        self._thread = None

    def start(self):
        self._stream = self._audio.open(
            format=self._format,
            channels=self._channels,
            rate=self._rate,
            input=False,
            output=True,
            frames_per_buffer=self._chunk,
            output_device_index=self._output_device_index,
        )
        self._exit.clear()
        self._thread = threading.Thread(
            target=self._play, daemon=True
        )
        self._thread.start()
        self._stream.start_stream()
        return True

    def stop(self):
        self._exit.set()
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._thread:
            self._thread.join()
            self._thread = None
        self._queue = None

    def play(self, data):
        self._queue.put(data)

    def _play(self):
        while not self._exit.is_set():
            try:
                data = self._queue.get(True, DeepgramSpeaker.TIMEOUT)
                self._stream.write(data)
            except queue.Empty:
                pass
            except Exception as e:
                print(f"_play: {e}")


def segment_text_by_sentence(text):
    sentence_boundaries = re.finditer(r'(?<=[.!?])\s+', text)
    boundaries_indices = [boundary.start() for boundary in sentence_boundaries]
    
    segments = []
    start = 0
    for boundary_index in boundaries_indices:
        segments.append(text[start:boundary_index + 1].strip())
        start = boundary_index + 1
    segments.append(text[start:].strip())

    return segments


# TODO: Make this into a stream
def text_to_speech(api_key=None, text=None, output_path = None):
    if os.path.exists(output_path):
        os.remove(output_path)
    else:
        with open(output_path, 'w') as f:
            pass
    DEEPGRAM_URL = 'https://api.deepgram.com/v1/speak?model=aura-helios-en'
    headers = {
    "Authorization": f"Token {api_key}",
    "Content-Type": "application/json"
    }
    segments = segment_text_by_sentence(text)
    with open(output_path, "wb") as f:
        for segment in segments:
            payload = {"text": text}
            with requests.post(DEEPGRAM_URL, stream=True, headers=headers, json=payload) as r:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)


async def text_to_speech_async(api_key=None, text=None, output_path = None):
    await asyncio.to_thread(text_to_speech, api_key, text, output_path)

from config import config

def text_2_speech( text, language='vi-vn', format='mp3', speed='0', pitch='0', output_path=None):
    url = 'https://api.voicerss.org/'
    params = {
        'key': config.VOICE_RSS,  # API key,
        'hl': language,  # Ngôn ngữ: vi-vn (Tiếng Việt), en-us (Tiếng Anh), v.v.
        'src': text,     # Văn bản cần chuyển đổi
        'r': speed,      # Tốc độ: -10 đến 10
        'p': pitch,      # Độ cao: -10 đến 10
        'c': format      # Định dạng: mp3, wav, v.v.
    }

    response = requests.get(url, params=params)
    if os.path.exists(output_path):
        os.remove(output_path)
    else:
        with open(output_path, 'w') as f:
            pass

    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    else:
        print("Failed to convert text to speech")

async def text_2_speech_async(text, language='vi-vn', format='mp3', speed='0', pitch='0',output_path=None):
    await asyncio.to_thread(text_2_speech, text, language, format, speed, pitch, output_path)