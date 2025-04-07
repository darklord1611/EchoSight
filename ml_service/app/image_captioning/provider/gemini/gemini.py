import google.generativeai as genai
import json
import time
import requests
import os
import dotenv
import mimetypes

dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

generation_config = {
  "temperature": 0.5,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192
}

model = genai.GenerativeModel(model_name = "gemini-1.5-flash-002", generation_config=generation_config)

json_schema = {
    "title": "Image description",
    "description": """Bạn đang hỗ trợ người khiếm thị. Cung cấp mô tả ngắn gọn, súc tích về hình ảnh trong một câu, bao gồm các chi tiết chính. Trả lời một cách tóm tắt.""",
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
            "description": "Mô tả đối tượng chính của ảnh bằng tiếng Việt và bằng 1-2 câu."
        }
    },
    "required": ["description"]
}

def gen_img_description(file_url, mime_type):
    try:
        if os.path.isfile(file_url):
            local_file_path = file_url 
        else:
            response = requests.get(file_url)
            response.raise_for_status()

            
            file_name = os.path.basename(file_url)
            local_file_path = os.path.join("temp_images", file_name) 
            os.makedirs("temp_images", exist_ok=True) 

            with open(local_file_path, 'wb') as f:
                data = response.content
                f.write(data)

        img_file = genai.upload_file(path=local_file_path, mime_type=mime_type)
        while img_file.state.name == "PROCESSING":
            img_file = genai.get_file(img_file.name)
            print(f"Video file state: {img_file.state.name}")

        if img_file.state.name == "FAILED":
            print(f"Error uploading video: {img_file.state.details}") 
            raise ValueError(img_file.state.name)

        prompt = f"Follow JSON schema.<JSONSchema>{json.dumps(json_schema, ensure_ascii=False, indent=2)}</JSONSchema>"

        response = model.generate_content([img_file, prompt], generation_config=genai.GenerationConfig(
            response_mime_type="application/json"), request_options={"timeout": 5000})

        time.sleep(1)
        img_file.delete()
        os.remove(local_file_path) # Xóa file tạm thời sau khi sử dụng
        return response.text

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    image_path = r"C:\Users\admin\Desktop\VisionMate\AI\app\image_captioning\provider\gemini\tay.png"
    mime_type, _ = mimetypes.guess_type(image_path)
    print(mime_type)
    result = gen_img_description(image_path, mime_type)
    print(result)  # In kết quả ra màn hình

if __name__ == "__main__":
    main()
