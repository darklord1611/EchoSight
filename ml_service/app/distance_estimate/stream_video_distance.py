import cv2
from pathlib import Path
import numpy as np
from .yolov8.YOLOv8 import YOLOv8
from .yolov8.utils import class_names  

model_path = './models/yolov8m.onnx'
yolov8_detector = YOLOv8(model_path, conf_thres=0.2, iou_thres=0.3)

image_path = "./app/distance_estimate/dis.jpg"  
KNOWN_DISTANCE = 24.0 
KNOWN_WIDTH = 11.0   

focalLength = None

def distance_to_camera(knownWidth, focalLength, perWidth):
    return (knownWidth * focalLength) / perWidth

def calculate_focal_length_stream(reference_image_path):
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
    return focalLength

def apply_extrinsic_transform(points, rotation_matrix, translation_vector):
    transformed_points = np.dot(rotation_matrix, points.T).T + translation_vector
    return transformed_points

def run_realtime_detection():
    global focalLength
    cap = cv2.VideoCapture(0) 
    
    if focalLength is None:
        print("Chưa tính tiêu cự, vui lòng cung cấp ảnh tham chiếu.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Không thể lấy khung hình từ webcam.")
            break
        
        boxes, scores, class_ids = yolov8_detector(frame)

        rotation_matrix = np.eye(3)  
        translation_vector = np.array([0, 0, 0])  

        for i, box in enumerate(boxes):
            object_width = box[2] - box[0]
            
            inches = distance_to_camera(KNOWN_WIDTH, focalLength, object_width)
            
            class_id = class_ids[i]
            class_name = class_names[class_id]
            
            cv2.rectangle(frame, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
            
            label = f"{class_name}: {inches / 12:.2f} ft"  
            cv2.putText(frame, label, (int(box[0]), int(box[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 1)
            
            center_x = (box[0] + box[2]) / 2
            center_y = (box[1] + box[3]) / 2
            object_depth = inches 
            
            object_position_camera = np.array([center_x, center_y, object_depth])
            object_position_world = apply_extrinsic_transform(object_position_camera, rotation_matrix, translation_vector)
            
            position_label = f"Position (World): {object_position_world}"
            cv2.putText(frame, position_label, (10, 30 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Realtime Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def calculate_distance_from_image(image_data):
    global focalLength
    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        
    if image is None:
        print("Không thể tải ảnh.")
        return None
    
    boxes, scores, class_ids = yolov8_detector(image)
    results = []
    rotation_matrix = np.eye(3)  
    translation_vector = np.array([0, 0, 0])  

    for i, box in enumerate(boxes):
        object_width = box[2] - box[0]
            
        inches = distance_to_camera(KNOWN_WIDTH, focalLength, object_width)
            
        class_id = class_ids[i]
        class_name = class_names[class_id]
            
        cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
            
        label = f"{class_name}: {inches / 12:.2f} ft"  
        cv2.putText(image, label, (int(box[0]), int(box[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 1)
            
        center_x = (box[0] + box[2]) / 2
        center_y = (box[1] + box[3]) / 2
        object_depth = inches 
            
        object_position_camera = np.array([center_x, center_y, object_depth])
        object_position_world = apply_extrinsic_transform(object_position_camera, rotation_matrix, translation_vector)
            
        position_label = f"Position (World): {object_position_world}"
        cv2.putText(image, position_label, (10, 30 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        results.append({
            "class": class_name,
            "distance": inches.item(),
            "position": object_position_world.tolist()
        })

    return results

if __name__ == "__main__":
    calculate_focal_length_stream(image_path)
    run_realtime_detection()
