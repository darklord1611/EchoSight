




def recognize_text(base64_image: str) -> str:
    try:

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