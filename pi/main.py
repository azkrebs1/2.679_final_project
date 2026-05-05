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

            # 🔴 DRAW BOXES (scale back up)
            print("BOXES FORMAT: ")
            print(boxes)
            for (x, y, w, h) in boxes:
                x = int(x * frame.shape[1] / config.INFER_WIDTH)
                y = int(y * frame.shape[0] / config.INFER_HEIGHT)
                w = int(w * frame.shape[1] / config.INFER_WIDTH)
                h = int(h * frame.shape[0] / config.INFER_HEIGHT)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # 🔴 SHOW FRAME
            cv2.imshow("Camera", frame)

            # 🔴 REQUIRED: lets window update
            if cv2.waitKey(1) & 0xFF == 27:  # press ESC to exit
                break

            pan, tilt = tracker.update(target, config.INFER_WIDTH, config.INFER_HEIGHT)
            link.send(pan, tilt)
    except KeyboardInterrupt:
        pass
    finally:
        link.close()
        cam.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
