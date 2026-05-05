"""Entry point: capture -> detect -> (recognize) -> track -> send."""

import cv2

import config
from camera import Camera
from detector import FaceDetector
from serial_link import ArduinoLink
from tracker import PanTiltTracker


def main():
    cam = Camera()
    detector = FaceDetector()
    tracker = PanTiltTracker()
    link = ArduinoLink()

    recognizer = None
    if config.USE_RECOGNITION:
        from recognizer import FaceRecognizer
        recognizer = FaceRecognizer()

    try:
        while True:
            frame = cam.read()
            small = cv2.resize(frame, (config.INFER_WIDTH, config.INFER_HEIGHT))
            boxes = detector.detect(small)

            if recognizer is not None:
                boxes = [b for b in boxes if recognizer.is_known(small, b)]

            target = FaceDetector.largest(boxes)
            pan, tilt = tracker.update(target, config.INFER_WIDTH, config.INFER_HEIGHT)
            link.send(pan, tilt)
    except KeyboardInterrupt:
        pass
    finally:
        link.close()
        cam.close()


if __name__ == "__main__":
    main()
