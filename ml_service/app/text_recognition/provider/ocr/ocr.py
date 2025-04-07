import os
import mimetypes
import logging
from dataclasses import dataclass
import openai
from dotenv import load_dotenv
import base64

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class RecognitionResult:
    text: str

class OcrRecognition:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def recognize_text(self, file_path: str) -> RecognitionResult:
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            logger.info(f"Detected MIME type: {mime_type}")

            if not mime_type or not mime_type.startswith("image/"):
                raise ValueError(f"Invalid MIME type: {mime_type}. Only image files are supported.")

            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            prompt = (
                "Trích xuất nội dung văn bản từ ảnh tài liệu. "
                "Chỉ trả lại văn bản chính xác như xuất hiện trong tài liệu, không thêm bất kỳ thông tin nào khác."
            )

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": [
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

            return RecognitionResult(text=response.choices[0].message.content.strip())

        except Exception as e:
            logger.error(f"Lỗi trong quá trình nhận dạng văn bản: {str(e)}")
            raise
