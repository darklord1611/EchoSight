from fastapi import APIRouter, FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(root_dir)
AI_path = os.path.join(root_dir, "AI")

from ml_service.app.distance_estimate.stream_video_distance import calculate_distance_from_image, calculate_focal_length

router = APIRouter()
image_path = "dis.jpg"  

calculate_focal_length(image_path)

@router.post("/distance_estimate")
async def calculate_distance(file: UploadFile = File(...)):
    image_data = await file.read()
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    results = calculate_distance_from_image(image_data)

    if results is None:
        raise HTTPException(status_code=400, detail="Không thể xử lý ảnh.")

    return JSONResponse(content=results)
