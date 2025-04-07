import base64
import openai
import logging
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
class OpenAIProvider:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')  
        self.logger = logging.getLogger(__name__)

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
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Bạn đang hỗ trợ người khiếm thị. Cung cấp mô tả ngắn gọn, súc tích về hình ảnh trong một câu, bao gồm các chi tiết chính. Trả lời một cách tóm tắt."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "hãy miêu tả bức ảnh này."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200
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
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Bạn đang hỗ trợ người khiếm thị. Cung cấp mô tả ngắn gọn, súc tích về hình ảnh trong một câu, bao gồm các chi tiết chính. Trả lời một cách tóm tắt."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "hãy miêu tả bức ảnh này."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=200,
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

    # Khởi tạo provider mà không cần truyền API key trực tiếp
    provider = OpenAIProvider()

    image_path = 'img.png'

    if not os.path.exists(image_path):
        logging.error(f"Image not found: {image_path}")
        return

    base64_image = provider.encode_image(image_path)
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