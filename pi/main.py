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
            sx = frame.shape[1] / config.INFER_WIDTH
            sy = frame.shape[0] / config.INFER_HEIGHT
            for (x1, y1, x2, y2, _conf) in boxes:
                x1 = int(x1 * sx)
                y1 = int(y1 * sy)
                x2 = int(x2 * sx)
                y2 = int(y2 * sy)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

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
