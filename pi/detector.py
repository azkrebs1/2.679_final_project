"""YOLO face detector. Returns bounding boxes in input-frame coordinates."""

from ultralytics import YOLO

import config


class FaceDetector:
    def __init__(self, model_path=config.MODEL_PATH, conf=config.DETECTION_CONF):
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, frame):
        """Run inference on a BGR frame. Returns list of (x1, y1, x2, y2, conf)."""
        results = self.model.predict(
            frame, conf=self.conf, verbose=False, imgsz=config.INFER_WIDTH
        )
        boxes = []
        for r in results:
            for b in r.boxes:
                x1, y1, x2, y2 = b.xyxy[0].tolist()
                boxes.append((x1, y1, x2, y2, float(b.conf[0])))
        return boxes

    @staticmethod
    def largest(boxes):
        if not boxes:
            return None
        return max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
