from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from fpdf import FPDF
from gtts import gTTS
import cv2
import numpy as np
from deepface import DeepFace
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(root_dir)
AI_path = os.path.join(root_dir, "AI")

from ml_service.app.face_detection.detectMongo import detect_and_analyze_face, find_existing_face, process_frame, save_embedding_to_db, connect_mongodb, calculate_focal_length

app = FastAPI()
image_path = "dis.jpg"  

calculate_focal_length(image_path)

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
DB_COLLECTION = os.getenv("DB_COLLECTION")

def connect_mongodb():
    """Connect to the MongoDB database."""
    try:
        mongo_client = MongoClient(MONGODB_URI)
        db = mongo_client[DB_NAME]  
        collection = db[DB_COLLECTION] 
        return collection  
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
    
collection = connect_mongodb()
if collection is None:
    raise HTTPException(status_code=500, detail="Database connection failed")

@app.post("/face_detection/register")
async def register(name: str, file: UploadFile = File(...)):
    image_data = await file.read()
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    
    # Generate embedding
    try:
        embedding = DeepFace.represent(image, enforce_detection=False)[0]['embedding']
        save_embedding_to_db(collection, name, np.array(embedding))

        # Generate success voice
        tts = gTTS(f"Registration successful for {name}", lang="en")
        voice_file = NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(voice_file.name)

        return {"message": "Registration successful", "voice_path": voice_file.name}
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
            
            # Find existing face without using await since it's a synchronous function
            face_match = find_existing_face(collection, np.array(embedding))

            # If a face match is found, unpack the tuple
            if face_match:
                matched_name, similarity_score = face_match
            else:
                matched_name, similarity_score = "No match", None

            # Construct the response with the face match and additional data
            return {
                "message": "Recognition successful",
                "name": recognized_name,
                "matched_name": matched_name,
                "similarity_score": similarity_score,
                "age": data.get('Age'),
                "gender": data.get('Gender'),
                "emotion": data.get('Emotion'),
                "race": data.get('Race'),
                "distance": data.get('Distance')
            }
        else:
            raise HTTPException(status_code=404, detail="Face not recognized")
    except Exception as e:
        print(f"Error in recognition endpoint: {e}")
        raise HTTPException(status_code=404, detail="Failed to process recognition")

# Endpoint to download generated files
@app.get("/face_detection/download_pdf")
async def download_pdf(pdf_path: str):
    return FileResponse(pdf_path, media_type="application/pdf", filename="recognition_result.pdf")

@app.get("/face_detection/download_audio")
async def download_audio(voice_path: str):
    return FileResponse(voice_path, media_type="audio/mpeg", filename="recognition_voice.mp3")