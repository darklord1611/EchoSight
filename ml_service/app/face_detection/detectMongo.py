import numpy as np
import cv2
from deepface import DeepFace
from pymongo import MongoClient
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys
import json

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)
distance_path = os.path.join(root_dir, "distance_estimate")

from distance_estimate.yolov8.YOLOv8 import YOLOv8

image_path = os.path.join(distance_path, "dis.jpg")
model_path = os.path.join(distance_path, "models", "yolov8m.onnx")
yolov8_detector = YOLOv8(model_path, conf_thres=0.2, iou_thres=0.3) 

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
DB_COLLECTION = os.getenv("DB_COLLECTION")

KNOWN_DISTANCE = 24.0  
KNOWN_WIDTH = 11.0    
focalLength = None

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

def save_embedding_to_db(collection, name, embedding, hometown, relationship, date_of_birth):
    """Save embedding with additional details to MongoDB."""
    try:
        collection.insert_one({
            "name": name,
            "embedding": embedding.tolist(),
            "hometown": hometown,
            "relationship": relationship,
            "date_of_birth": date_of_birth
        })
        print(f"Saved {name} to the database with additional details.")
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")


def find_existing_face(collection, embedding):
    """Find existing faces in the database and return the one with the highest similarity."""
    threshold = 0.5
    matched_faces = []

    existing_faces = collection.find({})
    
    for doc in existing_faces:
        existing_embedding = np.array(doc['embedding'])
        sim = cosine_similarity([embedding], [existing_embedding])[0][0]
        print(f"Similarity with {doc['name']}: {sim}")
        if sim >= threshold:
            matched_faces.append((doc['name'], sim)) 
    
    if matched_faces:
        highest_similarity_face = max(matched_faces, key=lambda x: x[1])  
        return highest_similarity_face  
    return None  

def distance_to_camera(knownWidth, focalLength, perWidth):
    """Tính khoảng cách từ camera đến đối tượng."""
    return (knownWidth * focalLength) / perWidth

def calculate_focal_length(reference_image_path):
    """Tính tiêu cự dựa trên ảnh tham chiếu."""
    global focalLength
    reference_image = cv2.imread(reference_image_path)
    
    if reference_image is None:
        print("Không thể tải ảnh tham chiếu.")
        return None

    boxes, _, _ = yolov8_detector(reference_image)
    
    if len(boxes) > 0:
        first_box = boxes[0]
        first_box_width = first_box[2] - first_box[0]
        focalLength = (first_box_width * KNOWN_DISTANCE) / KNOWN_WIDTH
        print(f"Tiêu cự đã tính: {focalLength}")
    else:
        print("Không phát hiện được đối tượng trong ảnh tham chiếu.")

def detect_and_analyze_face():
    """Detect and analyze a face from the live video feed."""
    collection = connect_mongodb()  
    if collection is None:
        print("Unable to connect to MongoDB. Exiting the program.")
        return
    cap = cv2.VideoCapture(0)

    if focalLength is None:
        print("Focal length not calculated. Please provide a reference image.")
        return

    ret, frame = cap.read()
    if not ret:
        print("Cannot retrieve frame from webcam.")
        cap.release()
        return

    process_frame(frame, collection)
    cap.release()
    cv2.destroyAllWindows()  

def process_frame(frame, collection):
    """Analyze the frame and find or save embeddings."""
    response_data = []
    try:
        representations = DeepFace.represent(frame, enforce_detection=False)
        if isinstance(representations, list) and len(representations) > 0:
            embedding = representations[0]['embedding']

        analysis = DeepFace.analyze(frame, actions=['age', 'gender', 'emotion', 'race'], enforce_detection=False)
        if analysis and isinstance(analysis, list):
            analysis_result = analysis[0]  
            
            age = analysis_result['age']
            dominant_gender = analysis_result['dominant_gender']
            dominant_emotion = analysis_result['dominant_emotion']
            dominant_race = analysis_result['dominant_race']

            highest_similarity_face = find_existing_face(collection, np.array(embedding))
            if highest_similarity_face:
                name, similarity = highest_similarity_face

                boxes, _, _ = yolov8_detector(frame)
                if boxes is not None and len(boxes) > 0:
                    first_box = boxes[0]
                    object_width = first_box[2] - first_box[0]
                    distance = distance_to_camera(KNOWN_WIDTH, focalLength, object_width)
                    
                    response_data.append({
                        "Age": age,
                        "Gender": dominant_gender,
                        "Emotion": dominant_emotion,
                        "Race": dominant_race,
                        "Name": name,
                        "Distance": distance
                    })
        
        return response_data  

    except Exception as e:
        print(f"Error in process_frame: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    calculate_focal_length(image_path)
    
    detect_and_analyze_face()