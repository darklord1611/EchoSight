import time
from imread_from_url import imread_from_url
import cv2
import numpy as np
import onnxruntime
from .utils import draw_detections, xywh2xyxy, multiclass_nms, class_names

class YOLOv8:
    def __init__(self, path, conf_thres=0.7, iou_thres=0.5):
        self.conf_threshold = conf_thres
        self.iou_threshold = iou_thres
        self.session = None
        self.total_money = 0
        self.currency_values = {
            '1000': 1000, '2000': 2000, '5000': 5000, '10000': 10000,
            '20000': 20000, '50000': 50000, '100000': 100000,
            '200000': 200000, '500000': 500000,
            '500': 500
        }
        self.initialize_model(path)

    def __call__(self, image):
        return self.detect_objects(image)

    def initialize_model(self, path):
        self.session = onnxruntime.InferenceSession(path,
                                                    providers=onnxruntime.get_available_providers())
        self.get_input_details()
        self.get_output_details()

    def detect_objects(self, image):
        input_tensor = self.prepare_input(image)
        outputs = self.inference(input_tensor)
        self.boxes, self.scores, self.class_ids = self.process_output(outputs)
        self.calculate_total_money()
        return self.boxes, self.scores, self.class_ids

    def prepare_input(self, image):
        self.img_height, self.img_width = image.shape[:2]
        input_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        input_img = cv2.resize(input_img, (self.input_width, self.input_height))
        input_img = input_img / 255.0
        input_img = input_img.transpose(2, 0, 1)
        input_tensor = input_img[np.newaxis, :, :, :].astype(np.float32)
        return input_tensor

    def inference(self, input_tensor):
        start = time.perf_counter()
        outputs = self.session.run(self.output_names, {self.input_names[0]: input_tensor})
        return outputs

    def process_output(self, output):
        predictions = np.squeeze(output[0]).T
        scores = np.max(predictions[:, 4:], axis=1)
        predictions = predictions[scores > self.conf_threshold, :]
        scores = scores[scores > self.conf_threshold]
        if len(scores) == 0:
            return [], [], []
        class_ids = np.argmax(predictions[:, 4:], axis=1)
        boxes = self.extract_boxes(predictions)
        indices = multiclass_nms(boxes, scores, class_ids, self.iou_threshold)
        return boxes[indices], scores[indices], class_ids[indices]

    def extract_boxes(self, predictions):
        boxes = predictions[:, :4]
        boxes = self.rescale_boxes(boxes)
        boxes = xywh2xyxy(boxes)
        return boxes

    def rescale_boxes(self, boxes):
        input_shape = np.array([self.input_width, self.input_height, self.input_width, self.input_height])
        boxes = np.divide(boxes, input_shape, dtype=np.float32)
        boxes *= np.array([self.img_width, self.img_height, self.img_width, self.img_height])
        return boxes

    def calculate_total_money(self):
        self.total_money = 0
        for class_id in self.class_ids:
            currency_value = self.currency_values[class_names[class_id]]
            self.total_money += currency_value

    def draw_detections(self, image, draw_scores=True, mask_alpha=0.4):
        return draw_detections(image, self.boxes, self.scores,
                               self.class_ids, mask_alpha)

    def get_input_details(self):
        model_inputs = self.session.get_inputs()
        self.input_names = [model_inputs[i].name for i in range(len(model_inputs))]
        self.input_shape = model_inputs[0].shape
        self.input_height = self.input_shape[2]
        self.input_width = self.input_shape[3]

    def get_output_details(self):
        model_outputs = self.session.get_outputs()
        self.output_names = [model_outputs[i].name for i in range(len(model_outputs))]

    def get_total_money(self):
        return self.total_money

def main():
    model_path = '../model/best.onnx'

    start = time.perf_counter()
    yolov8_detector = YOLOv8(model_path, conf_thres=0.2, iou_thres=0.3)

    img_url = "https://vnn-imgs-a1.vgcloud.vn/photo-cms-kienthuc.zadn.vn/zoom/800/Uploaded/nguyenvan/2021_07_01/5/a1_YVAT.jpg?width=0&s=RcMagANp2-BRCjG0o4uLWg"
    img = cv2.imread('img.png')

    yolov8_detector(img)

    total_money = yolov8_detector.get_total_money()
    print(total_money)

    combined_img = yolov8_detector.draw_detections(img)
    cv2.imwrite("Detected Objects.jpg", combined_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()