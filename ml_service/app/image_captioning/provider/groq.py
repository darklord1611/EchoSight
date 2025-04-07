import os
import base64
import logging
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

load_dotenv()

class OpenAIProvider:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ['GROQ_API_KEY']
        )
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def resize_image(image_path: str, max_size: int = 512) -> str:
        """Resize the image to reduce its size."""
        try:
            with Image.open(image_path) as img:
                img.thumbnail((max_size, max_size))
                resized_path = "resized_" + os.path.basename(image_path)
                img.save(resized_path, format="JPEG")
                return resized_path
        except Exception as e:
            logging.error(f"Error resizing image: {str(e)}")
            raise

    @staticmethod
    def encode_image(image_path: str) -> Optional[str]:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logging.error(f"Error encoding image: {str(e)}")
            return None

    def frame_description(self, base64_image: str) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Bạn đang hỗ trợ người khiếm thị. Cung cấp mô tả ngắn gọn, súc tích về hình ảnh trong một câu, bao gồm các chi tiết chính. Trả lời một cách tóm tắt."
                    },
                    {
                        "role": "user",
                        "content": f"Hãy miêu tả bức ảnh này: data:image/jpeg;base64,{base64_image}"
                    }
                ],
            )

            if response.choices and response.choices[0].message:
                return response.choices[0].message.content
            return None

        except Exception as e:
            self.logger.error(f"Error getting image description: {str(e)}")
            return None

    def frame_description_stream(self, base64_image: str) -> str:
        try:
            full_response = ""
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Bạn đang hỗ trợ người khiếm thị. Cung cấp mô tả ngắn gọn, súc tích về hình ảnh trong một câu, bao gồm các chi tiết chính. Trả lời một cách tóm tắt."
                    },
                    {
                        "role": "user",
                        "content": f"Hãy miêu tả bức ảnh này: data:image/jpeg;base64,{base64_image}"
                    }
                ],
                stream=True
            )

            for chunk in response:
                if chunk.choices:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        print(content, end='', flush=True)

            return full_response

        except Exception as e:
            self.logger.error(f"Error in streaming image description: {str(e)}")
            return ""

def main():
    import logging

    logging.basicConfig(level=logging.INFO)

    provider = OpenAIProvider()

    image_path = 'img.png'

    if not os.path.exists(image_path):
        logging.error(f"Image not found: {image_path}")
        return

    try:
        resized_path = provider.resize_image(image_path)
    except Exception:
        logging.error("Failed to resize image")
        return

    base64_image = provider.encode_image(resized_path)
    if not base64_image:
        logging.error("Failed to encode image")
        return

    description = provider.frame_description_stream(base64_image)
    if description:
        print(f"\nFinal description: {description}")
    else:
        print("Failed to get description")

if __name__ == '__main__':
    main()
