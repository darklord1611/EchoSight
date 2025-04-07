import cv2
import time
from PIL import Image
import numpy as np
import os

folder = "frames"

frames_dir = os.path.join(os.getcwd(), folder)
os.makedirs(frames_dir, exist_ok=True)

cap = cv2.VideoCapture("video2.mp4")

time.sleep(2)

while True:
    ret, frame = cap.read()
    if ret:
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        cv2.imshow("Video Preview", frame)

        print("Saved current frame")
        path = f"{folder}/frame.jpg"
        cv2.imwrite(path, frame)
    else:
        print("Failed to capture image")
        break

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
