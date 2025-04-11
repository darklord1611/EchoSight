import base64
import cv2
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fpdf import FPDF
import numpy as np
import openai
from pydantic import Json
from sympy import content
from .utils.formatter import create_pdf, create_pdf_async, format_response_distance_estimate_with_openai, format_response_product_recognition_with_openai, format_audio_response
from .currency_detection.yolov8.YOLOv8 import YOLOv8
from .config import config
from .text_recognition.provider.ocr.ocr import OcrRecognition
import sys
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from .product_recognition.pipeline import BarcodeProcessor
from deepface import DeepFace
import time
from .image_captioning.provider.gemini.gemini import gen_img_description
import asyncio
from .distance_estimate.stream_video_distance import calculate_focal_length_stream, calculate_distance_from_image
from .face_detection.detectMongo import find_existing_face, process_frame, save_embedding_to_db, connect_mongodb, calculate_focal_length
import json
import mimetypes
from .image_captioning.provider.gpt4.gpt4 import OpenAIProvider
start = time.time()
ocr = OcrRecognition()
currency_detection_model_path = "./models/best8.onnx"
currency_detector = YOLOv8(currency_detection_model_path, conf_thres=0.2, iou_thres=0.3)
barcode_processor = BarcodeProcessor()
distance_estimation_model_path = "./models/yolov8m.onnx"
print(f"All Models loaded in {time.time() - start:.2f} seconds", file=sys.stderr)


app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/document_recognition")
async def document_recognition(file: UploadFile = File(...)):
    try:
        start = time.time()
        mime_type, _ = mimetypes.guess_type(file.filename)
        print(f"MIME Type from original filename: {mime_type}")

        if not mime_type or not mime_type.startswith("image/"):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid MIME type: {mime_type}. Only image files are allowed."
            )

        with NamedTemporaryFile(delete=False, suffix=mimetypes.guess_extension(mime_type)) as temp:
            temp.write(file.file.read())
            temp_path = temp.name

        ocr_result = ocr.recognize_text(temp_path).text
        result = ocr_result

        pdf_path = NamedTemporaryFile(delete=False, suffix=".pdf").name
        asyncio.gather(
            create_pdf_async(result, pdf_path)
        )

        audio_file_path = format_audio_response(result, "text_recognition")
        if audio_file_path:
            return JSONResponse(content={
                "text": result,
                "pdf_path": pdf_path,
                "audio_path": audio_file_path,
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio response")

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/currency_detection")
async def currency_detection(file: UploadFile = File(...)):
    try:
        with NamedTemporaryFile(delete=False) as temp:
            temp.write(file.file.read())
            temp.close()
            img = cv2.imread(temp.name)
            currency_detector(img)
            total_money = currency_detector.get_total_money()

            audio_path = format_audio_response(total_money, "currency_detection")
            if audio_path:
                return JSONResponse(content={
                    "total_money": total_money,
                    "audio_path": audio_path,
                })
            else:
                raise HTTPException(status_code=500, detail="Failed to generate audio response")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.post("/image_captioning")
async def image_captioning(file: UploadFile = File(...)):
    try:
        with NamedTemporaryFile(delete=False) as temp:
            temp.write(file.file.read())
            temp_path = temp.name 

        mime_type, _ = mimetypes.guess_type(file.filename)
        if not mime_type:
            raise HTTPException(status_code=400, detail="Cannot determine the mimetype of the uploaded file.")

        provider = OpenAIProvider() 
        base64_image = provider.encode_image(temp_path)
        if not base64_image:
            raise HTTPException(status_code=500, detail="Failed to encode image")


        description = provider.frame_description(base64_image) 

        if not description:
            raise HTTPException(status_code=500, detail="Failed to generate image description")

        audio_path = format_audio_response(description, "image_captioning")
        if audio_path:
            return JSONResponse(content={
                "description": description,
                "audio_path": audio_path,
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio response")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

    

@app.post("/product_recognition")
async def product_recognition(file: UploadFile = File(...)):
    try:
        with NamedTemporaryFile(delete=False) as temp:
            temp.write(file.file.read())
            temp.flush()
            img = cv2.imread(temp.name)
            if img is None:
                raise HTTPException(status_code=400, detail="Invalid image file")
            result = barcode_processor.process_image(img)
            print(result)
            description = format_response_product_recognition_with_openai(result)
            print(description)

            audio_path = format_audio_response(description, "product_recognition")
            if audio_path:
                return JSONResponse(content={
                    "description": description,
                    "audio_path": audio_path,
                })
            else:
                raise HTTPException(status_code=500, detail="Failed to generate audio response")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

image_path = "./app/dis.jpg"  

calculate_focal_length_stream(image_path)

@app.post("/distance_estimate")
async def calculate_distance(transcribe: str,file: UploadFile = File(...)):
    image_data = await file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    results = calculate_distance_from_image(image_data)
    print(results)
    if results is None:
        raise HTTPException(status_code=400, detail="Không thể xử lý ảnh.")
    results = format_response_distance_estimate_with_openai(results, transcribe, base64_image)
    print(results)
    return JSONResponse(content={
        "description" : results
    })


collection = connect_mongodb()
if collection is None:
    raise HTTPException(status_code=500, detail="Database connection failed")
calculate_focal_length(image_path)

@app.post("/face_detection/register")
async def register(
    name: str,
    hometown: str,
    relationship: str,
    date_of_birth: str,
    file: UploadFile = File(...)
):
    image_data = await file.read()
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    try:
        embedding = DeepFace.represent(image, enforce_detection=False)[0]['embedding']
        
        save_embedding_to_db(
            collection, 
            name, 
            np.array(embedding), 
            hometown=hometown,
            relationship=relationship,
            date_of_birth=date_of_birth
        )

        print(JSONResponse(content={
            "message": f"Registration successful for {name}",
            "hometown": hometown,
            "relationship": relationship,
            "date_of_birth": date_of_birth
        }))
        
        return JSONResponse(content= {
            "description": f"Đã đăng kí thành công nhận diện khuôn mặt đối với {name} với thông tin như sau: Quê quán: {hometown}, Mối quan hệ với người dùng {relationship}, ngày tháng năm sinh: {date_of_birth}"
        })
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to process registration")


# Recognition Endpoint
@app.post("/face_detection/recognize")
async def recognize(file: UploadFile = File(...)):
    image_data = await file.read()
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Generate the embedding
    try:
        embedding = DeepFace.represent(image, enforce_detection=False)[0]['embedding']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {e}")

    try:
        # Process the frame to get response data
        response_data = process_frame(image, collection)
        if "error" in response_data:
            raise HTTPException(status_code=500, detail=response_data['error'])
        
        if response_data:
            data = response_data[0]
            recognized_name = data.get('Name', 'Unknown')
            
            # Find existing face and retrieve additional details
            face_match = find_existing_face(collection, np.array(embedding))
            if face_match:
                matched_name, similarity_score = face_match
                matched_face = collection.find_one({"name": matched_name})
                
                hometown = matched_face.get("hometown", "Unknown")
                relationship = matched_face.get("relationship", "Unknown")
                date_of_birth = matched_face.get("date_of_birth", "Unknown")
                result =  {
                    "message": "Recognition successful",
                    "name": recognized_name,
                    "matched_name": matched_name,
                    "similarity_score": similarity_score.item(),
                    "age": data.get('Age'),
                    "gender": data.get('Gender'),
                    "emotion": data.get('Emotion'),
                    "race": data.get('Race'),
                    "distance": data.get('Distance').item(),
                    "hometown": hometown,
                    "relationship": relationship,
                    "date_of_birth": date_of_birth
                }
                print(result)
                return JSONResponse(content= {
                    "description": f"Nhận diện thành công. Đây là {recognized_name}, cách bạn khoảng {data.get('Distance').item()} inch, quê quán: {hometown}, mối quan h��� với bạn là {relationship}"
                })
        else:
            raise HTTPException(status_code=404, detail="Face not recognized")
    except Exception as e:
        print(f"Error in recognition endpoint: {e}")
        raise HTTPException(status_code=404, detail="Failed to process recognition")


@app.post("music_detection")
async def music_detection(file: UploadFile = File(...)):
    try:
        with NamedTemporaryFile(delete=False) as temp:
            temp.write(file.file.read())
            temp_path = temp.name

        audio_path = format_audio_response(temp_path, "music_recognition")
        if audio_path:
            return JSONResponse(content={
                "audio_path": audio_path,
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio response")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/general_question_answering")
async def general_question_answering(file: UploadFile = File(...)):
    try:
        with NamedTemporaryFile(delete=False) as temp:
            temp.write(file.file.read())
            temp_path = temp.name

        audio_path = format_audio_response(temp_path, "general_question_answering")
        if audio_path:
            return JSONResponse(content={
                "audio_path": audio_path,
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio response")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/download_pdf")
async def download_pdf(pdf_path: str):
    return FileResponse(pdf_path, media_type="application/pdf", filename="document.pdf")


@app.get("/download_audio")
async def download_audio(audio_path: str):
    return FileResponse(audio_path, media_type="audio/mpeg", filename="document.mp3")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT, reload=True)