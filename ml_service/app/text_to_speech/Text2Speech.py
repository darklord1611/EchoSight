import requests
import os
from dotenv import load_dotenv
from config import config

load_dotenv()

def text_to_speech( text, language='vi-vn', format='mp3', speed='0', pitch='0'):
    url = 'https://api.voicerss.org/'
    params = {
        'key': config.VOICE_RSS,
        'hl': language,  # Ngôn ngữ: vi-vn (Tiếng Việt), en-us (Tiếng Anh), v.v.
        'src': text,     # Văn bản cần chuyển đổi
        'r': speed,      # Tốc độ: -10 đến 10
        'p': pitch,      # Độ cao: -10 đến 10
        'c': format      # Định dạng: mp3, wav, v.v.
    }

    response = requests.get(url, params=params)


    if response.status_code == 200:
        filename = 'output.mp3'
        with open(filename, 'wb') as file:
            file.write(response.content)
            return filename
        print('Audio file saved as output.mp3')
    else:
        print(f'Error: {response.status_code} - {response.text}')

text = '500000 VNĐ'
text_to_speech(text)