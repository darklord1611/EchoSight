import base64
import openai
import logging
from typing import Optional
import os
from dotenv import load_dotenv

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