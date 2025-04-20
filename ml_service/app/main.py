import base64
import cv2
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fpdf import FPDF
import numpy as np
import openai
from pydantic import BaseModel, Json
from sympy import content

from app.article_reading.pipeline import execute_pipeline
from app.question_answering.pipeline import ask_general_question
from app.utils.audio import FEATURE_KEYWORDS_FOR_SEMANTIC_MATCH, FEATURE_LABELS, FEATURE_NAMES, find_navigation_intent, route_query_semantically
from app.utils.deepgram import transcribe_audio
from .utils.formatter import create_pdf, create_pdf_async, format_article_audio_response, format_response_distance_estimate_with_openai, format_response_product_recognition_with_openai, format_audio_response
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
from fastapi import FastAPI, UploadFile, File
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
import os
import tempfile
import requests
from collections import OrderedDict
from .all_task.pipeline import get_llm_response

start = time.time()
# ocr = OcrRecognition()
# currency_detection_model_path = "./models/best8.onnx"
# currency_detector = YOLOv8(currency_detection_model_path, conf_thres=0.2, iou_thres=0.3)
# barcode_processor = BarcodeProcessor()
# distance_estimation_model_path = "./models/yolov8m.onnx"
print(f"All Models loaded in {time.time() - start:.2f} seconds", file=sys.stderr)

app = FastAPI()
# Define allowed origins (frontend URLs)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/document_recognition")
async def document_recognition(file: UploadFile = File(...)):
    try:
        start = time.time()
        image_data = await file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")

        result = get_llm_response(
            query="Extract text from this image.",
            task="text_recognition",
            base64_image=base64_image,
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate text response")

        return JSONResponse(content={
            "status": "success",
            "text": result,
        })

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/currency_detection")
async def currency_detection(file: UploadFile = File(...)):
    try:
        start = time.time()
        image_data = await file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")

        result = get_llm_response(
            query="Extract text from this image.",
            task="currency_detection",
            base64_image=base64_image,
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate text response")

        return JSONResponse(content={
            "status": "success",
            "text": result,
        })

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.post("/image_captioning")
async def image_captioning(file: UploadFile = File(...)):
    try:
        start = time.time()
        image_data = await file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")

        result = get_llm_response(
            query="Extract text from this image.",
            task="image_captioning",
            base64_image=base64_image,
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate text response")

        return JSONResponse(content={
            "status": "success",
            "text": result,
        })

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    

@app.post("/product_recognition")
async def product_recognition(file: UploadFile = File(...)):
    try:
        start = time.time()
        image_data = await file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")

        result = get_llm_response(
            query="Extract text from this image.",
            task="product_recognition",
            base64_image=base64_image,
        )

        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate text response")

        return JSONResponse(content={
            "status": "success",
            "text": result,
        })

    except Exception as e:
        print(f"Lỗi xảy ra: {e}")
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

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# --- Modified API Endpoint ---
# @app.post("/transcribe_audio_v2")
async def process_voice_command(file: UploadFile = File(...), current_feature: str | None = None):
    """
    Processes voice input, distinguishing navigation commands from feature queries.

    Args:
        file: The uploaded audio file (.webm format expected).
        current_feature: The key/name of the feature currently active in the UI (optional).
                         Helps disambiguate queries. e.g., "News", "Text".

    Returns:
        A dictionary containing the transcription, recognized intent ('navigate' or 'query'),
        target feature, confidence score, and original query text if applicable.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        transcript_result = transcribe_audio(tmp_path)

        if not transcript_result or "transcript" not in transcript_result:
             raise HTTPException(status_code=500, detail="Transcription failed.")

        transcript_text = transcript_result.get("transcript", "").strip()

        if not transcript_text:
             raise HTTPException(status_code=400, detail="Empty transcript received.")

        # --- STAGE 1: Check for Navigation Intent ---
        navigation_result = find_navigation_intent(transcript_text)

        if navigation_result:
            # It's a command to navigate!
            return {
                "transcript": transcript_result,
                "intent": navigation_result["intent"],
                "command": navigation_result["target_feature"],
                "confidence": navigation_result["confidence"],
                "query": None # Not a query
            }

        # --- STAGE 2: Treat as Query (if not navigation) ---
        # Option A: If context is known, assume query is for the current feature
        if current_feature and current_feature in FEATURE_NAMES: # Check if valid feature key
             # Simple Action Keywords check within current context (e.g., "stop", "play")
             # These might override semantic routing if they are very clear actions
             if transcript_text.lower() == "stop":
                  return {
                       "transcript": transcript_result,
                       "intent": "action", # Could be a specific 'action' intent
                       "target_feature": current_feature, # Action applies to current feature
                       "command": "Stop", # Specific action identified
                       "confidence": 0.99,
                       "query": transcript_text
                  }
             if transcript_text.lower() == "play":
                   return {
                       "transcript": transcript_result,
                       "intent": "action",
                       "target_feature": current_feature,
                       "command": "Play",
                       "confidence": 0.99,
                       "query": transcript_text
                  }

             # Otherwise, it's a query for the current feature
             return {
                "transcript": transcript_result,
                "intent": "query",
                "command": current_feature, # Route to the active feature
                "confidence": 0.90, # High confidence because context is provided
                "query": transcript_text
             }

        # Option B: Context unknown or it's a query needing routing
        # Use semantic similarity to find the best feature *for the query*
        semantic_routing_result = route_query_semantically(
            transcript_text,
            embedder,
            FEATURE_KEYWORDS_FOR_SEMANTIC_MATCH # Use the detailed keywords here
        )

        return {
            "transcript": transcript_result,
            "intent": semantic_routing_result["intent"],
            "command": semantic_routing_result["target_feature"],
            "confidence": semantic_routing_result["confidence"],
            "query": semantic_routing_result["query"]
        }

    except Exception as e:
        print(f"❌ Error processing voice command: {e}")
        # Log the exception traceback for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {str(e)}")
    finally:
        # Clean up the temporary file
        import os
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
             os.unlink(tmp_path)

from typing import Annotated


@app.post("/transcribe_audio")
async def voice_command(
    file: Annotated[UploadFile, File()],
    current_feature: Annotated[str, Form()]
    ):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        transcript_result = transcribe_audio(tmp_path)
        transcript_text = transcript_result.get("transcript", "").lower()

        print("Transcript:", transcript_text)
        print("Current Feature:", current_feature)

        # Step 1: Exact keyword match
        for label, keywords in FEATURE_LABELS.items():
            for keyword in keywords:
                if keyword.lower() in transcript_text:
                    if label == current_feature:
                        if "read" not in transcript_text.lower():
                            return {
                                "command": current_feature,
                                "intent": "query",
                                "confidence": 0.9,  # high confidence
                                "query": transcript_text
                            }
                        else:
                            return {
                                "command": current_feature,
                                "intent": "read",
                                "confidence": 0.9,  # high confidence
                                "query": transcript_text
                            }
                        
                    return {
                        "command": label,
                        "intent": "navigate",
                        "confidence": 1.0,  # exact match = high confidence
                        "query": transcript_text
                    }

        # Step 2: Semantic similarity fallback
        transcript_embed = embedder.encode(transcript_text, convert_to_tensor=True)
        best_match, best_score = None, -1

        for label, phrases in FEATURE_LABELS.items():
            for phrase in phrases:
                phrase_embed = embedder.encode(phrase, convert_to_tensor=True)
                score = util.cos_sim(transcript_embed, phrase_embed).item()
                if score > best_score:
                    best_match, best_score = label, score

        return {
            "command": best_match,
            "intent": "navigate",
            "confidence": round(best_score, 3),
            "query": transcript_text
        }
    except Exception as e:
        print("❌ Error:", e)
        return {"error": "Failed to process audio."}


class NewsQuery(BaseModel):
    news_query: str

@app.post("/fetching_news")
async def article_reading(news_query: str = Form(...)):

    try:
        if not news_query:
            raise HTTPException(status_code=400, detail="No news query provided")       

        # process audio to extract the news query
        if "error" in news_query:
            raise HTTPException(status_code=400, detail="Failed to transcribe audio")
        
        articles = execute_pipeline(news_query)

        if not articles:
            raise HTTPException(status_code=400, detail="No valid articles found")
        
        res = []

        for i, article in enumerate(articles):
            res.append({
                "title": article.title,
                "text": article.text,
                "summary": article.summary,
                "url": article.url
            })
        

        return JSONResponse(content={
            "articles": res,
            
        },
        status_code=200)  # Explicitly return 200 OK)
    except Exception as e:
        print(e)
        return {"error": "Failed to process audio."}

@app.post("/general_question_answering")
async def general_qa(file: UploadFile = File(...)):
    # Step 1: Save uploaded audio to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Step 2: Transcribe audio to text
        transcript_result = transcribe_audio(tmp_path)

        if "error" in transcript_result:
            raise HTTPException(status_code=400, detail="Failed to transcribe audio")

        question = transcript_result["transcript"]

        # Step 3: Ask the LLM to answer the question
        answer = ask_general_question(question)

        # Step 4: Convert answer back to speech
        audio_path = format_audio_response(answer, "general_question_answering")

        if audio_path:
            return JSONResponse(content={
                "question": question,
                "answer": answer,
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